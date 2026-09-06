"""GCP Vertex AI Vector Search vector store provider.

See ADR-00023 for the full design rationale. Summary:

Configuration
-------------
``GCP_VECTOR_SEARCH_PROJECT``
    Google Cloud project ID.  **Required.**

``GCP_VECTOR_SEARCH_LOCATION``
    Google Cloud region, e.g. ``us-central1``.  **Required.**

``GCP_VECTOR_SEARCH_INDEX_ID``
    Resource ID (or full resource name) of a pre-provisioned Vertex AI
    ``MatchingEngineIndex``.  **Required.**  The index must use
    ``index_update_method="STREAM_UPDATE"`` -- batch-update indexes do not
    support the real-time ``upsert_datapoints``/``remove_datapoints`` calls
    this provider relies on.

``GCP_VECTOR_SEARCH_INDEX_ENDPOINT_ID``
    Resource ID (or full resource name) of a pre-provisioned
    ``MatchingEngineIndexEndpoint``.  **Required.**

``GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID``
    The ``deployed_index_id`` under which the index above is deployed to the
    endpoint.  **Required.**

``GCP_VECTOR_SEARCH_FIRESTORE_COLLECTION``
    Firestore collection name used as the document/metadata sidecar.
    Optional, defaults to ``vector_store_documents``.

Design
------
This provider **never creates, deploys, or deletes Vertex AI infrastructure**
(ADR-00023).  It targets an Index/IndexEndpoint that must already exist;
``create_collection`` and ``upsert`` raise a clear error if they don't.

Vertex AI Vector Search has no native notion of a "collection" and its
``find_neighbors`` query only returns datapoint IDs and distances -- no
document text or metadata.  Two mechanisms fill that gap:

* **Multi-collection namespacing**: every datapoint is tagged with a
  ``restricts`` entry in the ``"collection"`` namespace equal to its
  collection name, and every query applies a matching restrict filter.  This
  lets multiple logical collections share one physical index.
* **Firestore sidecar**: document text and metadata are stored in Firestore,
  keyed by datapoint ID, and looked up after each ``find_neighbors`` call.
  A second, per-collection Firestore document (in a ``"{collection}__meta"``
  companion collection) holds the collection-level metadata dict and the set
  of known datapoint IDs, so ``create_collection``/``delete_collection`` know
  which datapoints to remove from the index without a native "list by
  restrict" API.
"""

import asyncio
import logging
import os
from typing import Any, Optional

from mcp_project_context_server.integrations.vectorstore.base import (
    QueryResult,
    VectorStoreError,
)

logger = logging.getLogger(__name__)

_COLLECTION_NAMESPACE = "collection"
_DEFAULT_FIRESTORE_COLLECTION = "vector_store_documents"
_REQUIRED_ENV_VARS = (
    "GCP_VECTOR_SEARCH_PROJECT",
    "GCP_VECTOR_SEARCH_LOCATION",
    "GCP_VECTOR_SEARCH_INDEX_ID",
    "GCP_VECTOR_SEARCH_INDEX_ENDPOINT_ID",
    "GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID",
)


class GcpVectorSearchProvider:
    """Vector store backed by a pre-provisioned Vertex AI Vector Search Index + IndexEndpoint.

    See the module docstring and ADR-00023 for the collection-namespacing and
    Firestore-sidecar design this provider relies on.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If any of the required
            ``GCP_VECTOR_SEARCH_*`` environment variables are not set.
        """
        values = {name: os.getenv(name) for name in _REQUIRED_ENV_VARS}
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variable(s) for VECTOR_STORE_PROVIDER=gcp-vector-search: "
                f"{', '.join(missing)}. This provider targets a pre-provisioned Vertex AI Index and "
                "IndexEndpoint (ADR-00023) -- it does not create or deploy GCP infrastructure. Provision "
                "the Index/IndexEndpoint yourself (Terraform, gcloud, or Console), then set these "
                "variables to the resulting resource IDs."
            )

        self._project: str = values["GCP_VECTOR_SEARCH_PROJECT"]  # type: ignore[assignment]
        self._location: str = values["GCP_VECTOR_SEARCH_LOCATION"]  # type: ignore[assignment]
        self._index_id: str = values["GCP_VECTOR_SEARCH_INDEX_ID"]  # type: ignore[assignment]
        self._index_endpoint_id: str = values["GCP_VECTOR_SEARCH_INDEX_ENDPOINT_ID"]  # type: ignore[assignment]
        self._deployed_index_id: str = values["GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID"]  # type: ignore[assignment]
        self._firestore_collection: str = os.getenv(
            "GCP_VECTOR_SEARCH_FIRESTORE_COLLECTION", _DEFAULT_FIRESTORE_COLLECTION
        )

        self._index: Optional[Any] = None
        self._endpoint: Optional[Any] = None
        self._firestore: Optional[Any] = None

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "gcp-vector-search"

    @property
    def _meta_collection(self) -> str:
        """Firestore collection name holding per-collection metadata and known datapoint IDs."""
        return f"{self._firestore_collection}__meta"

    # ------------------------------------------------------------------
    # Lazy client construction
    # ------------------------------------------------------------------

    def _get_index(self) -> Any:
        """Return the ``MatchingEngineIndex`` handle, initialising the SDK on first use."""
        if self._index is None:
            from google.cloud import aiplatform  # lazy import

            aiplatform.init(project=self._project, location=self._location)
            self._index = aiplatform.MatchingEngineIndex(index_name=self._index_id)
        return self._index

    def _get_endpoint(self) -> Any:
        """Return the ``MatchingEngineIndexEndpoint`` handle, initialising the SDK on first use."""
        if self._endpoint is None:
            from google.cloud import aiplatform  # lazy import

            aiplatform.init(project=self._project, location=self._location)
            self._endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=self._index_endpoint_id)
        return self._endpoint

    def _get_firestore(self) -> Any:
        """Return the Firestore client, initialising it on first use."""
        if self._firestore is None:
            from google.cloud import firestore  # lazy import

            self._firestore = firestore.Client(project=self._project)
        return self._firestore

    # ------------------------------------------------------------------
    # VectorStoreProvider Protocol implementation
    # ------------------------------------------------------------------

    async def create_collection(self, name: str, metadata: dict | None = None) -> None:
        """Clear and re-register *name* for a clean re-index (ADR-00006).

        Removes every datapoint currently tagged with this collection from
        the Vertex AI index and clears its Firestore sidecar documents. Does
        **not** create, deploy, or otherwise modify the underlying Vertex AI
        Index or IndexEndpoint resources -- see ADR-00023.

        :param name: (str) Collection name.
        :param metadata: (dict) Optional key/value metadata to attach to the collection.
        :return: (None) This method does not return a value.
        :raises VectorStoreError: If the Vertex AI or Firestore API calls fail.
        """
        try:
            await self._remove_all_datapoints(name)

            def _write_meta() -> None:
                db = self._get_firestore()
                db.collection(self._meta_collection).document(name).set(
                    {"metadata": metadata or {}, "datapoint_ids": []}
                )

            await asyncio.to_thread(_write_meta)
        except Exception as exc:
            raise VectorStoreError(f"Failed to create/clear collection '{name}': {exc}") from exc

    async def delete_collection(self, name: str) -> None:
        """Remove all datapoints and sidecar data for *name*.  Silently succeeds if it does not exist.

        :param name: (str) Collection name.
        :return: (None) This method does not return a value.
        """
        try:
            await self._remove_all_datapoints(name)

            def _delete_meta() -> None:
                db = self._get_firestore()
                db.collection(self._meta_collection).document(name).delete()

            await asyncio.to_thread(_delete_meta)
        except Exception:
            pass

    async def _remove_all_datapoints(self, name: str) -> None:
        """Remove every datapoint and document tagged with collection *name*."""
        datapoint_ids = await self._get_known_datapoint_ids(name)
        if not datapoint_ids:
            return

        def _sync() -> None:
            index = self._get_index()
            index.remove_datapoints(datapoint_ids=datapoint_ids)
            db = self._get_firestore()
            for doc_id in datapoint_ids:
                db.collection(self._firestore_collection).document(doc_id).delete()

        await asyncio.to_thread(_sync)

    async def _get_known_datapoint_ids(self, name: str) -> list[str]:
        """Return the datapoint IDs previously recorded for collection *name*."""

        def _sync() -> list[str]:
            db = self._get_firestore()
            doc = db.collection(self._meta_collection).document(name).get()
            if not doc.exists:
                return []
            return list(doc.to_dict().get("datapoint_ids") or [])

        return await asyncio.to_thread(_sync)

    async def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Insert or update documents in *collection_name*.

        :param collection_name: (str) Target collection.
        :param ids: (list) Per-document unique identifiers.
        :param embeddings: (list) Per-document embedding vectors (must all be the same length).
        :param documents: (list) Raw text for each document.
        :param metadatas: (list) Per-document metadata dicts.
        :return: (None) This method does not return a value.
        :raises VectorStoreError: If the Vertex AI or Firestore API calls fail.
        """
        if not ids:
            return

        def _sync() -> None:
            index = self._get_index()
            datapoints = [
                {
                    "datapoint_id": doc_id,
                    "feature_vector": embedding,
                    "restricts": [{"namespace": _COLLECTION_NAMESPACE, "allow": [collection_name]}],
                }
                for doc_id, embedding in zip(ids, embeddings)
            ]
            index.upsert_datapoints(datapoints=datapoints)

            db = self._get_firestore()
            batch = db.batch()
            for doc_id, document, meta in zip(ids, documents, metadatas):
                ref = db.collection(self._firestore_collection).document(doc_id)
                batch.set(ref, {"collection": collection_name, "document": document, "metadata": meta})
            batch.commit()

            meta_ref = db.collection(self._meta_collection).document(collection_name)
            meta_doc = meta_ref.get()
            existing_ids = set(meta_doc.to_dict().get("datapoint_ids") or []) if meta_doc.exists else set()
            meta_ref.set(
                {
                    "metadata": meta_doc.to_dict().get("metadata", {}) if meta_doc.exists else {},
                    "datapoint_ids": sorted(existing_ids | set(ids)),
                }
            )

        try:
            await asyncio.to_thread(_sync)
        except Exception as exc:
            raise VectorStoreError(f"Upsert failed on collection '{collection_name}': {exc}") from exc

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> QueryResult:
        """Run a ``find_neighbors`` nearest-neighbour search scoped to *collection_name*.

        :param collection_name: (str) Collection to search.
        :param query_embedding: (list) Query vector (must match the dimension of stored embeddings).
        :param n_results: (int) Maximum number of results to return.
        :return: (QueryResult) A :class:`QueryResult` with the top-*n_results* matches.
        :raises VectorStoreError: If the collection does not exist or the query fails.
        """

        def _sync() -> QueryResult:
            from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import Namespace  # lazy import

            endpoint = self._get_endpoint()
            response = endpoint.find_neighbors(
                deployed_index_id=self._deployed_index_id,
                queries=[query_embedding],
                num_neighbors=n_results,
                filter=[Namespace(name=_COLLECTION_NAMESPACE, allow_tokens=[collection_name])],
            )
            neighbors = response[0] if response else []
            ids = [n.id for n in neighbors]
            distances = [float(n.distance) for n in neighbors]

            db = self._get_firestore()
            documents: list[str] = []
            metadatas: list[dict] = []
            for doc_id in ids:
                snap = db.collection(self._firestore_collection).document(doc_id).get()
                data = snap.to_dict() if snap.exists else {}
                documents.append(data.get("document", ""))
                metadatas.append(data.get("metadata", {}))

            return QueryResult(ids=ids, documents=documents, metadatas=metadatas, distances=distances)

        try:
            return await asyncio.to_thread(_sync)
        except Exception as exc:
            raise VectorStoreError(f"Query failed on collection '{collection_name}': {exc}") from exc

    async def count(self, collection_name: str) -> int:
        """Return the number of datapoints known for *collection_name* (0 if absent).

        :param collection_name: (str) Collection to count.
        :return: (int) Document count. Returns 0 if the collection does not exist.
        """
        try:
            return len(await self._get_known_datapoint_ids(collection_name))
        except Exception:
            return 0

    async def collection_exists(self, collection_name: str) -> bool:
        """Return ``True`` if a sidecar metadata document exists for *collection_name*.

        :param collection_name: (str) Collection to check.
        :return: (bool) ``True`` if the collection exists, ``False`` otherwise.
        """

        def _sync() -> bool:
            db = self._get_firestore()
            return db.collection(self._meta_collection).document(collection_name).get().exists

        try:
            return await asyncio.to_thread(_sync)
        except Exception:
            return False

    async def get_collection_metadata(self, collection_name: str) -> dict:
        """Return the metadata dict stored for *collection_name* (``{}`` if absent).

        :param collection_name: (str) Collection to inspect.
        :return: (dict) Metadata dict (may be empty). Returns ``{}`` if the collection does not exist.
        """

        def _sync() -> dict:
            db = self._get_firestore()
            doc = db.collection(self._meta_collection).document(collection_name).get()
            if not doc.exists:
                return {}
            return doc.to_dict().get("metadata") or {}

        try:
            return await asyncio.to_thread(_sync)
        except Exception:
            return {}

    def reset_for_testing(self) -> None:
        """Reset cached SDK handles.  **For use in tests only.**

        :return: (None) This method does not return a value.
        """
        self._index = None
        self._endpoint = None
        self._firestore = None
