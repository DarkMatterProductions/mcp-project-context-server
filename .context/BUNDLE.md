This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.

<file_summary>
This section contains a summary of this file.

<purpose>
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.
</purpose>

<file_format>
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  - File path as an attribute
  - Full contents of the file
</file_format>

<usage_guidelines>
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.
</usage_guidelines>

<notes>
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: src/**/*.py
- Files matching these patterns are excluded: tests/**
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)
</notes>

</file_summary>

<directory_structure>
src/mcp_project_context_server/__init__.py
src/mcp_project_context_server/__main__.py
src/mcp_project_context_server/exceptions.py
src/mcp_project_context_server/helpers/__init__.py
src/mcp_project_context_server/helpers/context_files.py
src/mcp_project_context_server/helpers/context.py
src/mcp_project_context_server/helpers/logs.py
src/mcp_project_context_server/indexing/__init__.py
src/mcp_project_context_server/indexing/indexer.py
src/mcp_project_context_server/integrations/__init__.py
src/mcp_project_context_server/integrations/embeddings/__init__.py
src/mcp_project_context_server/integrations/embeddings/base.py
src/mcp_project_context_server/integrations/embeddings/cohere/__init__.py
src/mcp_project_context_server/integrations/embeddings/cohere/client.py
src/mcp_project_context_server/integrations/embeddings/google/__init__.py
src/mcp_project_context_server/integrations/embeddings/google/client.py
src/mcp_project_context_server/integrations/embeddings/ollama/__init__.py
src/mcp_project_context_server/integrations/embeddings/ollama/client.py
src/mcp_project_context_server/integrations/embeddings/openai/__init__.py
src/mcp_project_context_server/integrations/embeddings/openai/client.py
src/mcp_project_context_server/integrations/embeddings/registry.py
src/mcp_project_context_server/integrations/embeddings/vertexai/__init__.py
src/mcp_project_context_server/integrations/embeddings/vertexai/client.py
src/mcp_project_context_server/integrations/embeddings/voyage/__init__.py
src/mcp_project_context_server/integrations/embeddings/voyage/client.py
src/mcp_project_context_server/integrations/repository/__init__.py
src/mcp_project_context_server/integrations/repository/base.py
src/mcp_project_context_server/integrations/repository/gitea/__init__.py
src/mcp_project_context_server/integrations/repository/gitea/client.py
src/mcp_project_context_server/integrations/repository/github/__init__.py
src/mcp_project_context_server/integrations/repository/github/client.py
src/mcp_project_context_server/integrations/repository/gitlab/__init__.py
src/mcp_project_context_server/integrations/repository/gitlab/client.py
src/mcp_project_context_server/integrations/repository/local/__init__.py
src/mcp_project_context_server/integrations/repository/local/client.py
src/mcp_project_context_server/integrations/repository/registry.py
src/mcp_project_context_server/integrations/vectorstore/__init__.py
src/mcp_project_context_server/integrations/vectorstore/base.py
src/mcp_project_context_server/integrations/vectorstore/chroma_http/__init__.py
src/mcp_project_context_server/integrations/vectorstore/chroma_http/client.py
src/mcp_project_context_server/integrations/vectorstore/chroma_local/__init__.py
src/mcp_project_context_server/integrations/vectorstore/chroma_local/client.py
src/mcp_project_context_server/integrations/vectorstore/gcp_vector_search/__init__.py
src/mcp_project_context_server/integrations/vectorstore/gcp_vector_search/client.py
src/mcp_project_context_server/integrations/vectorstore/pgvector/__init__.py
src/mcp_project_context_server/integrations/vectorstore/pgvector/client.py
src/mcp_project_context_server/integrations/vectorstore/registry.py
src/mcp_project_context_server/server.py
src/mcp_project_context_server/tools/__init__.py
src/mcp_project_context_server/tools/find_latest_session_file.py
src/mcp_project_context_server/tools/index_context.py
src/mcp_project_context_server/tools/list_repositories.py
src/mcp_project_context_server/tools/load_context_files.py
src/mcp_project_context_server/tools/reload_active_context_file.py
src/mcp_project_context_server/tools/save_session.py
src/mcp_project_context_server/tools/search_adr_index.py
src/mcp_project_context_server/tools/search_context_index.py
src/mcp_project_context_server/tools/search_session_files.py
src/mcp_project_context_server/tools/search_shared.py
src/mcp_project_context_server/transport/__init__.py
src/mcp_project_context_server/transport/sse.py
src/mcp_project_context_server/transport/stdio.py
</directory_structure>

<files>
This section contains the contents of the repository's files.

<file path="src/mcp_project_context_server/helpers/__init__.py">
"""Shared helper utilities package."""
</file>

<file path="src/mcp_project_context_server/helpers/context_files.py">
"""Shared helpers for loading, hashing, and listing individual .context/ files."""
import hashlib
import logging
from pathlib import Path

from mcp_project_context_server.helpers.context import find_context_dir, resolve_project_path
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider

logger = logging.getLogger(__name__)


def hash_content(content: str) -> str:
    """Compute the SHA-512 hex digest of *content*.

    :param content: (str) The file content to hash.
    :return: (str) The hex-encoded SHA-512 digest of *content*.
    """
    return hashlib.sha512(content.encode("utf-8")).hexdigest()


def format_tagged_file(path: str, sha512: str, content: str) -> str:
    """Format *content* as an XML-tagged context-file block.

    :param path: (str) The ``.context/``-relative path of the file.
    :param sha512: (str) The SHA-512 hex digest of *content*.
    :param content: (str) The file's contents.
    :return: (str) A ``<context-file path="..." sha512="...">`` tagged block.
    """
    return f'<context-file path="{path}" sha512="{sha512}">\n{content}\n</context-file>'


def _is_safe_relative_path(rel_path: str) -> bool:
    """Reject absolute paths and paths containing ``..`` segments.

    These tools are reachable over the ``sse`` transport where input is not
    necessarily trusted, so a requested path must stay within ``.context/``.
    """
    p = Path(rel_path)
    if p.is_absolute():
        return False
    return ".." not in p.parts


async def resolve_requested_files(project_path: str, rel_paths: list[str]) -> tuple[dict[str, str], list[str]]:
    """Resolve a list of ``.context/``-relative paths to their contents.

    :param project_path: (str) The project root, short repo identifier, or repository URL.
    :param rel_paths: (list) POSIX-style paths relative to ``.context/``.
    :return: (tuple) A ``(found, missing)`` pair — ``found`` maps requested paths to
        their contents; ``missing`` lists requested paths that could not be
        resolved (not found on disk/remote, or rejected as unsafe).
    """
    logger.debug(f"Executing 'resolve_requested_files' with the argument rel_paths: {rel_paths}")
    safe_paths = [p for p in rel_paths if _is_safe_relative_path(p)]

    resolved_path, is_remote = resolve_project_path(project_path)
    found: dict[str, str] = {}

    if is_remote:
        try:
            provider = get_repository_provider()
            files = await provider.fetch_context_files(resolved_path)
        except RepositoryError:
            files = {}
        found = {p: files[p] for p in safe_paths if p in files}
    else:
        context_dir = find_context_dir(resolved_path)
        if context_dir is not None:
            for p in safe_paths:
                candidate = context_dir / p
                if candidate.is_file():
                    found[p] = candidate.read_text(encoding="utf-8")

    missing = [p for p in rel_paths if p not in found]
    return found, missing


async def list_context_files(project_path: str, prefix: str) -> list[str]:
    """List sorted ``.context/``-relative markdown paths starting with *prefix*.

    :param project_path: (str) The project root, short repo identifier, or repository URL.
    :param prefix: (str) A POSIX-style path prefix, e.g. ``"sessions/"``.
    :return: (list) Sorted relative paths (POSIX-style) starting with *prefix*.
    """
    resolved_path, is_remote = resolve_project_path(project_path)

    if is_remote:
        try:
            provider = get_repository_provider()
            files = await provider.fetch_context_files(resolved_path)
        except RepositoryError:
            return []
        return sorted(k for k in files if k.startswith(prefix))

    context_dir = find_context_dir(resolved_path)
    if context_dir is None:
        return []

    all_paths = (m.relative_to(context_dir).as_posix() for m in context_dir.rglob("*.md"))
    return sorted(p for p in all_paths if p.startswith(prefix))
</file>

<file path="src/mcp_project_context_server/indexing/__init__.py">
"""Context indexing package."""
</file>

<file path="src/mcp_project_context_server/integrations/__init__.py">
"""Third-party service integrations package."""
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/__init__.py">
"""Embedding provider integrations."""
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/cohere/__init__.py">
"""Cohere embedding provider — implements the EmbeddingProvider Protocol."""
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/google/__init__.py">
"""Google Gemini API embedding provider — implements the EmbeddingProvider Protocol."""
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/ollama/__init__.py">
"""Ollama embedding provider package."""
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/openai/__init__.py">
"""OpenAI embedding provider — implements the EmbeddingProvider Protocol."""
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/vertexai/__init__.py">
"""Google Vertex AI embedding provider — implements the EmbeddingProvider Protocol."""
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/voyage/__init__.py">
"""Voyage AI embedding provider — implements the EmbeddingProvider Protocol."""
</file>

<file path="src/mcp_project_context_server/integrations/repository/__init__.py">
"""Repository provider integrations — local filesystem, GitHub, GitLab, and Gitea."""
</file>

<file path="src/mcp_project_context_server/integrations/repository/gitea/__init__.py">
"""Gitea repository provider."""
</file>

<file path="src/mcp_project_context_server/integrations/repository/github/__init__.py">
"""GitHub repository provider."""
</file>

<file path="src/mcp_project_context_server/integrations/repository/gitlab/__init__.py">
"""GitLab repository provider."""
</file>

<file path="src/mcp_project_context_server/integrations/repository/local/__init__.py">
"""Local filesystem repository provider."""
</file>

<file path="src/mcp_project_context_server/integrations/vectorstore/__init__.py">
"""Vector store provider abstraction package."""
</file>

<file path="src/mcp_project_context_server/integrations/vectorstore/chroma_http/__init__.py">
"""Vector store: chroma-http provider package."""
</file>

<file path="src/mcp_project_context_server/integrations/vectorstore/chroma_local/__init__.py">
"""Vector store: chroma-local provider package."""
</file>

<file path="src/mcp_project_context_server/integrations/vectorstore/gcp_vector_search/__init__.py">
"""GCP Vertex AI Vector Search vector store provider package."""
</file>

<file path="src/mcp_project_context_server/integrations/vectorstore/pgvector/__init__.py">
"""Vector store: pgvector provider package."""
</file>

<file path="src/mcp_project_context_server/tools/__init__.py">
"""MCP tool implementations package."""
</file>

<file path="src/mcp_project_context_server/tools/find_latest_session_file.py">
"""Tool: find_latest_session_file — deterministic lookup of the newest session file."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.context_files import list_context_files
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``find_latest_session_file`` tool call.

    :param arguments: (dict) Tool input dict. Requires key ``"project_path"``.
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        naming the most recent ``sessions/*.md`` file (sorted by filename), or
        "No session files found." when none exist.
    """
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    session_files = await list_context_files(_project_path, prefix="sessions/")
    if not session_files:
        return [types.TextContent(type="text", text="No session files found.")]

    return [types.TextContent(type="text", text=f"Latest session file: {session_files[-1]}")]
</file>

<file path="src/mcp_project_context_server/tools/load_context_files.py">
"""Tool: load_context_files — load specific .context/ files, tagged with path + SHA-512."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.context_files import format_tagged_file, hash_content, resolve_requested_files
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``load_context_files`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"`` and
        ``"files"`` (a list of ``.context/``-relative paths to load).
    :return: (list) One :class:`~mcp.types.TextContent` block per requested file —
        a ``<context-file path="..." sha512="...">`` tagged block for files that
        were found, or a "File not found" message for files that were not.
    """
    files: list[str] = arguments["files"]
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    found, _missing = await resolve_requested_files(_project_path, files)

    blocks: list[types.TextContent] = []
    for path in files:
        if path in found:
            content = found[path]
            blocks.append(types.TextContent(type="text", text=format_tagged_file(path, hash_content(content), content)))
        else:
            blocks.append(types.TextContent(type="text", text=f"File not found: {path}"))

    return blocks
</file>

<file path="src/mcp_project_context_server/tools/reload_active_context_file.py">
"""Tool: reload_active_context_file — refresh files whose on-disk content changed."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.context_files import format_tagged_file, hash_content, resolve_requested_files
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``reload_active_context_file`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"`` and
        ``"files"`` — a list of ``{"path": ..., "known_sha512": ...}`` entries
        describing files currently held in active context.
    :return: (list) One :class:`~mcp.types.TextContent` block per entry: "No change"
        when the current SHA-512 matches ``known_sha512``, a fresh tagged block
        plus a discard note when it differs, or "File not found" when the file
        no longer exists.
    """
    entries: list[dict] = arguments["files"]
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    paths = [entry["path"] for entry in entries]
    found, _missing = await resolve_requested_files(_project_path, paths)

    blocks: list[types.TextContent] = []
    for entry in entries:
        path = entry["path"]
        known_sha512 = entry["known_sha512"]

        if path not in found:
            blocks.append(types.TextContent(type="text", text=f"File not found: {path}"))
            continue

        content = found[path]
        current_sha512 = hash_content(content)
        if current_sha512 == known_sha512:
            blocks.append(types.TextContent(type="text", text=f"No change: {path}"))
            continue

        tagged = format_tagged_file(path, current_sha512, content)
        blocks.append(
            types.TextContent(
                type="text",
                text=f"{tagged}\n\nNote: '{path}' changed — discard the stale block previously loaded for this path.",
            )
        )

    return blocks
</file>

<file path="src/mcp_project_context_server/tools/search_adr_index.py">
"""Tool: search_adr_index — semantic search scoped to .context/decisions/."""
import logging
import os

from mcp import types

from mcp_project_context_server.tools.search_shared import run_search

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``search_adr_index`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``
        and ``"query"``; optional key ``"n_results"`` (defaults to 5).
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        with matching ``decisions/`` snippets, or an error/"not found" message.
    """
    query: str = arguments["query"]
    n_results: int = arguments.get("n_results", 5)
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    return await run_search(_project_path, query, n_results, file_prefix="decisions/")
</file>

<file path="src/mcp_project_context_server/tools/search_context_index.py">
"""Tool: search_context_index — semantic search over the whole indexed context."""
import logging
import os

from mcp import types

from mcp_project_context_server.tools.search_shared import run_search

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``search_context_index`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``
        and ``"query"``; optional key ``"n_results"`` (defaults to 5).
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        with the matching context snippets, or an error/"not found" message.
    """
    query: str = arguments["query"]
    n_results: int = arguments.get("n_results", 5)
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    return await run_search(_project_path, query, n_results, file_prefix=None)
</file>

<file path="src/mcp_project_context_server/tools/search_session_files.py">
"""Tool: search_session_files — semantic search scoped to .context/sessions/."""
import logging
import os

from mcp import types

from mcp_project_context_server.tools.search_shared import run_search

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``search_session_files`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``
        and ``"query"``; optional key ``"n_results"`` (defaults to 5).
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        with matching ``sessions/`` snippets, or an error/"not found" message.
    """
    query: str = arguments["query"]
    n_results: int = arguments.get("n_results", 5)
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    return await run_search(_project_path, query, n_results, file_prefix="sessions/")
</file>

<file path="src/mcp_project_context_server/tools/search_shared.py">
"""Shared semantic-search implementation used by the `search_*_index`/`search_session_files` tools.

Before executing a search, the tool reads the provenance metadata stored on
the collection at index time and compares it against the current provider
configuration.  If the embedding provider or model has changed, a warning is
prepended to the results so the user knows the index may need rebuilding.
"""
import logging
import os

from mcp import types

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.helpers.context import (
    collection_name_for,
    collection_name_for_repo_id,
    find_context_dir,
    resolve_project_path,
)
from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access
from mcp_project_context_server.integrations.vectorstore.base import VectorStoreError
from mcp_project_context_server.integrations.vectorstore.registry import get_vector_store

logger = logging.getLogger(__name__)

_MISMATCH_WARNING = (
    "⚠️  **Provider mismatch detected** — the index was built with "
    "`{old_provider}/{old_model}` but the current provider is "
    "`{new_provider}/{new_model}`.  Search results may be inaccurate.  "
    "Please re-run `index_project_context` to rebuild the index.\n\n---\n\n"
)

# Floor applied to the over-fetch multiplier so a small `n_results` still
# pulls in enough candidates for the client-side prefix filter to find hits.
_OVER_FETCH_FLOOR = 25
_OVER_FETCH_MULTIPLIER = 5


def _empty_result(text: str) -> types.CallToolResult:
    """Build a `CallToolResult` for an early-return/error path with no hits."""
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=text)],
        structured_content={"results": []},
    )


async def run_search(
    project_path: str, query: str, n_results: int, file_prefix: str | None = None
) -> types.CallToolResult:
    """Run a semantic search over the indexed `.context/` collection.

    :param project_path: (str) The project root, short repo identifier, or repository URL.
    :param query: (str) The natural-language search query.
    :param n_results: (int) The number of results to return to the caller.
    :param file_prefix: (str) When set, only hits whose ``metadata["file"]`` starts
        with this prefix are returned (used to scope search to ``decisions/`` or
        ``sessions/``). The store is over-fetched so the filter still has enough
        candidates to select from.
    :return: (CallToolResult) The unstructured text (matching context snippets,
        optionally prefixed with a provider/model mismatch warning, or an
        error/"not found" message) alongside a ``structured_content`` object of
        the shape ``{"results": [{"file", "chunk", "content", "distance"}, ...]}``.
    """
    try:
        validate_repo_access(project_path)
    except RepositoryError as exc:
        return _empty_result(str(exc))

    resolved_path, is_remote = resolve_project_path(project_path)

    if is_remote:
        col_name = collection_name_for_repo_id(resolved_path)
    else:
        context_dir = find_context_dir(resolved_path)
        if not context_dir:
            return _empty_result(f"No .context/ directory found near {project_path}")
        col_name = collection_name_for(context_dir)

    store = get_vector_store()

    if not await store.collection_exists(col_name):
        return _empty_result(f"Collection '{col_name}' not found. Run index_project_context first.")

    # --- Provenance mismatch check ---
    warning_prefix = ""
    stored_meta = await store.get_collection_metadata(col_name)
    current_provider = get_embedding_provider()
    stored_embed_provider = stored_meta.get("embed_provider", "")
    stored_embed_model = stored_meta.get("embed_model", "")

    if stored_embed_provider and stored_embed_model:
        if stored_embed_provider != current_provider.provider_name or stored_embed_model != current_provider.model_name:
            warning_prefix = _MISMATCH_WARNING.format(
                old_provider=stored_embed_provider,
                old_model=stored_embed_model,
                new_provider=current_provider.provider_name,
                new_model=current_provider.model_name,
            )

    query_n_results = n_results
    if file_prefix is not None:
        query_n_results = max(n_results * _OVER_FETCH_MULTIPLIER, _OVER_FETCH_FLOOR)

    try:
        provider = get_embedding_provider()
        query_embedding = await provider.embed_chunk(query)
        result = await store.query(
            collection_name=col_name,
            query_embedding=query_embedding,
            n_results=query_n_results,
        )
    except (VectorStoreError, EmbeddingError) as exc:
        return _empty_result(f"Search failed: {exc}")

    documents = result.documents
    metadatas = result.metadatas
    distances = result.distances if len(result.distances) == len(documents) else [None] * len(documents)

    if file_prefix is not None:
        filtered = [
            (doc, meta, dist)
            for doc, meta, dist in zip(documents, metadatas, distances)
            if meta.get("file", "").startswith(file_prefix)
        ]
        filtered = filtered[:n_results]
        documents = [doc for doc, _, _ in filtered]
        metadatas = [meta for _, meta, _ in filtered]
        distances = [dist for _, _, dist in filtered]

    if not documents:
        return _empty_result(f"{warning_prefix}No results found.")

    items = [
        {"file": meta.get("file", "?"), "chunk": meta.get("chunk"), "content": doc, "distance": dist}
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]
    output_parts = [f"**[{item['file']}]**\n{item['content']}" for item in items]
    body = "\n\n---\n\n".join(output_parts)

    structured_content: dict = {"results": items}
    if warning_prefix:
        structured_content["warning"] = warning_prefix.strip()

    return types.CallToolResult(
        content=[types.TextContent(type="text", text=f"{warning_prefix}{body}")],
        structured_content=structured_content,
    )
</file>

<file path="src/mcp_project_context_server/transport/__init__.py">
"""Transport layer package — STDIO and HTTP/SSE transports."""
</file>

<file path="src/mcp_project_context_server/__init__.py">
"""mcp-project-context-server — MCP server for persistent project context."""

try:
    from mcp_project_context_server._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"
</file>

<file path="src/mcp_project_context_server/exceptions.py">
"""Custom exception types shared across the server and its integrations."""


class EmbeddingError(Exception):
    """Raised when an embedding provider call fails."""
</file>

<file path="src/mcp_project_context_server/helpers/logs.py">
import argparse
import logging
import sys
import uuid
from pathlib import Path


class ParseLogLevel(argparse.Action):
    """
    Collects repeated --log-level name=LEVEL flags into a dict.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        d = getattr(namespace, self.dest) or {}
        try:
            name, level = values.split("=", 1)
        except ValueError:
            raise argparse.ArgumentError(
                self, f"expected format name=LEVEL, got '{values}'"
            )
        d[name] = level
        setattr(namespace, self.dest, d)


def setup_logging(logger_levels: dict[str, int | str] | None = None):
    """
    Configure the root logger to log to stdout and to _LOG_PATH.

    logger_levels: optional dict of {"<library_name>": <log_level>}
        to override the level for specific loggers, e.g.
        {"urllib3": "WARNING", "botocore": logging.WARNING}
        Values can be int constants (logging.WARNING) or level
        name strings ("WARNING", "debug", etc. - case-insensitive).
    """
    _PROCESS_ID = uuid.uuid4().hex[:8]
    _LOG_PATH = Path.home() / ".mcp-data" / "logs" / f"project-context-server-{_PROCESS_ID}.log"


    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    file_handler = logging.FileHandler(_LOG_PATH, mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    # Guard against duplicate handlers if setup_logging() runs more than once
    if not root.handlers:
        root.addHandler(file_handler)
        # root.addHandler(stream_handler)

    # --- Per-logger level overrides ---
    for name, level in (logger_levels or {}).items():
        if isinstance(level, str):
            level = level.upper()
        logging.getLogger(name).setLevel(level)
</file>

<file path="src/mcp_project_context_server/integrations/vectorstore/gcp_vector_search/client.py">
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
            from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
                Namespace,  # lazy import
            )

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
</file>

<file path="src/mcp_project_context_server/transport/sse.py">
"""HTTP/SSE transport — general-purpose MCP over HTTP with pluggable authentication.

This transport is not tied to any specific LLM platform.  It can be used with any
MCP client that supports the HTTP/SSE protocol, including Gemini Enterprise Agent
Engine, remote Cursor deployments, and self-hosted team servers.

Configuration
-------------
``MCP_HOST``
    Bind address.  Defaults to ``0.0.0.0``.

``MCP_PORT``
    Listen port.  Defaults to ``8080``.

``MCP_AUTH_TYPE``
    Authentication type.  One of:

    ``none``
        No authentication.  Suitable for trusted internal networks.

    ``bearer``
        Static API key via ``Authorization: Bearer <token>`` header.
        Requires ``MCP_AUTH_TOKEN``.

    ``google-iam``
        Google Cloud identity token validated via ``google-auth``.
        Suitable for Gemini Enterprise Agent Engine deployments.
        Optional: ``GOOGLE_IAM_AUDIENCE``, ``GOOGLE_SERVICE_ACCOUNT_KEY_PATH``,
        ``GOOGLE_APPROVED_SERVICE_ACCOUNTS``.

``MCP_AUTH_TOKEN``
    Required when ``MCP_AUTH_TYPE=bearer``.

``GOOGLE_IAM_AUDIENCE``
    Expected ``aud`` claim in Google identity tokens.  If unset, audience
    validation is skipped (less secure — set this in production).

``GOOGLE_SERVICE_ACCOUNT_KEY_PATH``
    Path to a service account JSON key file.  If unset, Application Default
    Credentials (ADC) are used instead.

``GOOGLE_APPROVED_SERVICE_ACCOUNTS``
    Comma-separated list of allowed caller service account emails.
    If unset, any authenticated Google identity is accepted.
"""

import logging
import os
from collections.abc import Callable
from typing import Any

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

logger = logging.getLogger(__name__)

_DEFAULT_HOST = "0.0.0.0"
_DEFAULT_PORT = 8080


# ---------------------------------------------------------------------------
# Auth middleware implementations
# ---------------------------------------------------------------------------


class _BearerAuthMiddleware(BaseHTTPMiddleware):
    """Validate ``Authorization: Bearer <token>`` against a static token."""

    def __init__(self, app: Any, token: str) -> None:
        super().__init__(app)
        self._token = token

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Health-check endpoint is unauthenticated
        if request.url.path == "/health":
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"error": "Missing or invalid Authorization header"}, status_code=401)
        token = auth_header.removeprefix("Bearer ").strip()
        if token != self._token:
            return JSONResponse({"error": "Invalid bearer token"}, status_code=403)
        return await call_next(request)


class _GoogleIAMAuthMiddleware(BaseHTTPMiddleware):
    """Validate Google Cloud identity tokens (for Agent Engine and service-to-service auth)."""

    def __init__(
        self,
        app: Any,
        audience: str | None,
        approved_accounts: frozenset[str] | None,
    ) -> None:
        super().__init__(app)
        self._audience = audience
        self._approved_accounts = approved_accounts

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path == "/health":
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"error": "Missing Authorization header"}, status_code=401)

        id_token = auth_header.removeprefix("Bearer ").strip()

        try:
            import asyncio

            claims = await asyncio.to_thread(self._verify_token, id_token)
        except Exception as exc:
            logger.warning("Google IAM token verification failed: %s", exc)
            return JSONResponse({"error": f"Token verification failed: {exc}"}, status_code=403)

        if self._approved_accounts:
            email = claims.get("email", "")
            if email not in self._approved_accounts:
                logger.warning("Rejected Google identity: %s (not in approved list)", email)
                return JSONResponse({"error": "Service account not approved"}, status_code=403)

        return await call_next(request)

    def _verify_token(self, id_token: str) -> dict:
        """Verify *id_token* synchronously (called via asyncio.to_thread)."""
        try:
            from google.auth.transport import requests as google_requests  # type: ignore[import]
            from google.oauth2 import id_token as google_id_token  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "google-auth is required for google-iam auth.  "
                "Install it with: pip install mcp-project-context-server[sse]"
            ) from exc

        request = google_requests.Request()
        claims = google_id_token.verify_firebase_token(id_token, request, audience=self._audience)
        return dict(claims)


# ---------------------------------------------------------------------------
# Starlette app factory
# ---------------------------------------------------------------------------


def _build_auth_middleware(auth_type: str) -> list[Middleware]:
    """Build the Starlette middleware list for *auth_type*."""
    if auth_type == "none":
        return []

    if auth_type == "bearer":
        token = os.getenv("MCP_AUTH_TOKEN", "")
        if not token:
            raise EnvironmentError("MCP_AUTH_TOKEN must be set when MCP_AUTH_TYPE=bearer")
        return [Middleware(_BearerAuthMiddleware, token=token)]

    if auth_type == "google-iam":
        audience = os.getenv("GOOGLE_IAM_AUDIENCE") or None
        approved_raw = os.getenv("GOOGLE_APPROVED_SERVICE_ACCOUNTS", "")
        approved: frozenset[str] | None = frozenset(a.strip() for a in approved_raw.split(",") if a.strip()) or None
        return [Middleware(_GoogleIAMAuthMiddleware, audience=audience, approved_accounts=approved)]

    raise EnvironmentError(
        f"Unsupported MCP_AUTH_TYPE value '{auth_type}'.  " "Supported values are: none, bearer, google-iam"
    )


def build_sse_app(server: Server) -> Starlette:
    """Build and return the Starlette ASGI application for HTTP/SSE transport.

    :param server: (Server) The configured MCP :class:`Server` instance.
    :return: (Starlette) A :class:`~starlette.applications.Starlette` app ready
        to be served by uvicorn.
    :raises EnvironmentError: If auth configuration is invalid or incomplete.
    """
    auth_type = os.getenv("MCP_AUTH_TYPE", "none").strip().lower()
    middleware = _build_auth_middleware(auth_type)

    sse_transport = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:
        async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())
        return Response()

    async def health(_: Request) -> Response:
        return JSONResponse({"status": "ok"})

    routes = [
        Route("/sse", endpoint=handle_sse),
        Route("/health", endpoint=health),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]

    return Starlette(routes=routes, middleware=middleware)


async def run_sse(server: Server) -> None:
    """Run *server* over HTTP/SSE until interrupted.

    Reads ``MCP_HOST`` and ``MCP_PORT`` from the environment.

    :param server: (Server) The configured MCP :class:`Server` instance.
    :return: (None) This function does not return a value.
    """
    import uvicorn  # type: ignore[import]

    host = os.getenv("MCP_HOST", _DEFAULT_HOST)
    port = int(os.getenv("MCP_PORT", str(_DEFAULT_PORT)))
    auth_type = os.getenv("MCP_AUTH_TYPE", "none").strip().lower()

    logger.info(
        "Starting MCP server in HTTP/SSE mode on %s:%d (auth: %s)",
        host,
        port,
        auth_type,
    )

    app = build_sse_app(server)
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    uvicorn_server = uvicorn.Server(config)
    await uvicorn_server.serve()
</file>

<file path="src/mcp_project_context_server/__main__.py">
"""Entry point for running the server as a module (``python -m mcp_project_context_server``)."""
import argparse

from mcp_project_context_server.helpers.logs import ParseLogLevel, setup_logging
from mcp_project_context_server.server import run


parser = argparse.ArgumentParser()
parser.add_argument(
    "--log-level",
    action=ParseLogLevel,
    metavar="name=LEVEL",
    dest="log_level",
    default={},
    help="Override log level for a specific logger, e.g. urllib3=WARNING. "
         "Can be passed multiple times.",
)

arguments = parser.parse_args()
setup_logging(arguments.log_level)
run()
</file>

<file path="src/mcp_project_context_server/integrations/vectorstore/base.py">
"""VectorStoreProvider Protocol — the provider abstraction boundary for vector storage.

All vector store providers must implement this Protocol so that the rest of the
codebase can depend on the abstraction rather than any concrete backend.

Usage
-----
::

    from mcp_project_context_server.integrations.vectorstore.base import VectorStoreProvider
    from mcp_project_context_server.integrations.vectorstore.registry import get_vector_store

    store = get_vector_store()
    collection = await store.get_or_create_collection("my-project")
"""
import logging
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Results returned from a vector similarity query."""

    ids: list[str]
    documents: list[str]
    metadatas: list[dict]
    distances: list[float] = field(default_factory=list)


@runtime_checkable
class VectorStoreProvider(Protocol):
    """Protocol that all vector store provider implementations must satisfy.

    Implementations must be safe to import without triggering network connections
    or filesystem I/O — those should be deferred to first method call.
    """

    @property
    def provider_name(self) -> str:
        """Short identifier, e.g. ``"chroma-local"``, ``"pgvector"``."""
        ...

    async def create_collection(self, name: str, metadata: dict | None = None) -> None:
        """Create a collection, replacing it if it already exists.

        Implements the drop-and-recreate strategy (ADR-00006): any existing
        collection with *name* is deleted before the new one is created.

        :param name: (str) Collection name.
        :param metadata: (dict) Optional key/value metadata to attach to the collection.
        :return: (None) This method does not return a value.
        """
        ...

    async def delete_collection(self, name: str) -> None:
        """Delete a collection.  Silently succeeds if it does not exist.

        :param name: (str) Collection name.
        :return: (None) This method does not return a value.
        """
        ...

    async def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Insert or update documents in a collection.

        :param collection_name: (str) Target collection.
        :param ids: (list) Per-document unique identifiers.
        :param embeddings: (list) Per-document embedding vectors (must all be the same length).
        :param documents: (list) Raw text for each document.
        :param metadatas: (list) Per-document metadata dicts.
        :return: (None) This method does not return a value.
        """
        ...

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> QueryResult:
        """Run a nearest-neighbour search against a collection.

        :param collection_name: (str) Collection to search.
        :param query_embedding: (list) Query vector (must match the dimension of stored embeddings).
        :param n_results: (int) Maximum number of results to return.
        :return: (QueryResult) A :class:`QueryResult` with the top-*n_results* matches.
        :raises VectorStoreError: If the collection does not exist or the query fails.
        """
        ...

    async def count(self, collection_name: str) -> int:
        """Return the number of documents stored in *collection_name*.

        :param collection_name: (str) Collection to count.
        :return: (int) Document count. Returns 0 if the collection does not exist.
        """
        ...

    async def collection_exists(self, collection_name: str) -> bool:
        """Return ``True`` if *collection_name* exists in this store.

        :param collection_name: (str) Collection to check.
        :return: (bool) ``True`` if the collection exists, ``False`` otherwise.
        """
        ...

    async def get_collection_metadata(self, collection_name: str) -> dict:
        """Return the metadata dict stored on a collection.

        :param collection_name: (str) Collection to inspect.
        :return: (dict) Metadata dict (may be empty). Returns ``{}`` if the collection
            does not exist.
        """
        ...


class VectorStoreError(Exception):
    """Raised when a vector store operation fails."""
</file>

<file path="src/mcp_project_context_server/integrations/vectorstore/chroma_local/client.py">
"""ChromaDB local (persistent) vector store provider.

Configuration
-------------
``CHROMA_DIR``
    Directory where ChromaDB stores its database files.
    Defaults to ``~/.mcp-data/chroma``.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Optional

from mcp_project_context_server.integrations.vectorstore.base import (
    QueryResult,
    VectorStoreError,
)

logger = logging.getLogger(__name__)

_DEFAULT_DIR: Path = Path.home() / ".mcp-data" / "chroma"


class ChromaLocalVectorStoreProvider:
    """Vector store backed by a local ChromaDB PersistentClient.

    Initialization is deferred: the ChromaDB client and directory are created
    on the first method call, not at import time.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading ``CHROMA_DIR`` from the environment."""
        self._dir: Path = Path(os.getenv("CHROMA_DIR", str(_DEFAULT_DIR)))
        self._client: Optional[Any] = None

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "chroma-local"

    def _get_client(self) -> Any:
        """Return the ChromaDB client, initialising on first call."""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings

            self._dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(self._dir),
                settings=Settings(anonymized_telemetry=False),
            )
        return self._client

    # ------------------------------------------------------------------
    # VectorStoreProvider Protocol implementation
    # ------------------------------------------------------------------

    async def create_collection(self, name: str, metadata: dict | None = None) -> None:
        """Drop and recreate *name* for a clean re-index (ADR-00006).

        :param name: (str) Collection name.
        :param metadata: (dict) Optional key/value metadata to attach to the collection.
        :return: (None) This method does not return a value.
        """
        client = self._get_client()

        def _sync() -> None:
            try:
                client.delete_collection(name)
            except Exception:
                pass
            client.create_collection(name=name, metadata=metadata or {})

        await asyncio.to_thread(_sync)

    async def delete_collection(self, name: str) -> None:
        """Delete *name*, silently succeeding if it does not exist.

        :param name: (str) Collection name.
        :return: (None) This method does not return a value.
        """
        client = self._get_client()

        def _sync() -> None:
            try:
                client.delete_collection(name)
            except Exception:
                pass

        await asyncio.to_thread(_sync)

    async def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Add or update documents in *collection_name*.

        :param collection_name: (str) Target collection.
        :param ids: (list) Per-document unique identifiers.
        :param embeddings: (list) Per-document embedding vectors (must all be the same length).
        :param documents: (list) Raw text for each document.
        :param metadatas: (list) Per-document metadata dicts.
        :return: (None) This method does not return a value.
        :raises VectorStoreError: If the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> None:
            try:
                col = client.get_collection(collection_name)
            except Exception as exc:
                raise VectorStoreError(f"Collection '{collection_name}' not found: {exc}") from exc
            col.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

        await asyncio.to_thread(_sync)

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> QueryResult:
        """Run a nearest-neighbour search.

        :param collection_name: (str) Collection to search.
        :param query_embedding: (list) Query vector (must match the dimension of stored embeddings).
        :param n_results: (int) Maximum number of results to return.
        :return: (QueryResult) A :class:`QueryResult` with the top-*n_results* matches.
        :raises VectorStoreError: If the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> QueryResult:
            try:
                col = client.get_collection(collection_name)
            except Exception as exc:
                raise VectorStoreError(f"Collection '{collection_name}' not found: {exc}") from exc
            n = min(n_results, col.count())
            if n == 0:
                return QueryResult(ids=[], documents=[], metadatas=[], distances=[])
            raw = col.query(query_embeddings=[query_embedding], n_results=n)
            return QueryResult(
                ids=raw["ids"][0] if raw.get("ids") else [],
                documents=raw["documents"][0] if raw.get("documents") else [],
                metadatas=raw["metadatas"][0] if raw.get("metadatas") else [],
                distances=raw["distances"][0] if raw.get("distances") else [],
            )

        return await asyncio.to_thread(_sync)

    async def count(self, collection_name: str) -> int:
        """Return the document count for *collection_name* (0 if absent).

        :param collection_name: (str) Collection to count.
        :return: (int) Document count. Returns 0 if the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> int:
            try:
                return client.get_collection(collection_name).count()
            except Exception:
                return 0

        return await asyncio.to_thread(_sync)

    async def collection_exists(self, collection_name: str) -> bool:
        """Return ``True`` if *collection_name* exists.

        :param collection_name: (str) Collection to check.
        :return: (bool) ``True`` if the collection exists, ``False`` otherwise.
        """
        client = self._get_client()

        def _sync() -> bool:
            try:
                client.get_collection(collection_name)
                return True
            except Exception:
                return False

        return await asyncio.to_thread(_sync)

    async def get_collection_metadata(self, collection_name: str) -> dict:
        """Return metadata attached to *collection_name* (``{}`` if absent).

        :param collection_name: (str) Collection to inspect.
        :return: (dict) Metadata dict (may be empty). Returns ``{}`` if the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> dict:
            try:
                col = client.get_collection(collection_name)
                return col.metadata or {}
            except Exception:
                return {}

        return await asyncio.to_thread(_sync)

    def reset_for_testing(self) -> None:
        """Reset the cached client.  **For use in tests only.**

        :return: (None) This method does not return a value.
        """
        self._client = None
</file>

<file path="src/mcp_project_context_server/transport/stdio.py">
"""STDIO transport — the default MCP transport for local tool clients.

No configuration required.  The server reads from stdin and writes to stdout,
which is how Claude Desktop, Claude Code, Cursor, JetBrains AI Assistant,
Continue Dev, and GitHub Copilot all launch MCP servers locally.
"""

import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server

logger = logging.getLogger(__name__)


async def run_stdio(server: Server) -> None:
    """Run *server* over STDIO until the stream is closed.

    :param server: (Server) The configured MCP :class:`Server` instance.
    :return: (None) This function does not return a value.
    """
    logger.info("Starting MCP server in STDIO mode")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
</file>

<file path="src/mcp_project_context_server/integrations/repository/base.py">
"""RepositoryProvider Protocol and shared data types."""
import logging
from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class RepositoryInfo:
    """Metadata about a single repository."""

    identifier: str  # e.g. "DarkMatterProductions/vs-cartographytable"
    name: str
    description: str
    indexed: bool  # True if a vector collection exists for this repo
    last_indexed: Optional[str] = None  # ISO datetime string or None


@runtime_checkable
class RepositoryProvider(Protocol):
    """Protocol that all repository provider implementations must satisfy."""

    @property
    def provider_name(self) -> str:
        """Short identifier, e.g. ``"local"``, ``"github"``, ``"gitlab"``, ``"gitea"``."""
        ...

    async def fetch_context_files(self, repo_id: str) -> dict[str, str]:
        """Fetch all .md files from the .context/ directory of the repository.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :return: (dict) A mapping of relative markdown file paths to their contents.
        """
        ...

    async def fetch_source_bundle(self, repo_id: str) -> Optional[str]:
        """Fetch the content of .context/BUNDLE.md, or None if it does not exist.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :return: (str) The contents of ``.context/BUNDLE.md``, or ``None`` if it does not exist.
        """
        ...

    async def fetch_source_files(self, repo_id: str) -> dict[str, str]:
        """Fetch source code files from the repository.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :return: (dict) A mapping of relative source file paths to their contents.
        """
        ...

    async def write_file(
        self, repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Write (create or update) a file in the repository.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :param path: (str) The path of the file to write, relative to the repository root.
        :param content: (str) The new full contents of the file.
        :param message: (str) The commit message describing the write.
        :param branch: (str) Target branch. Falls back to the provider's default
            branch when ``None``. Ignored by the local provider.
        :return: (None) This method does not return a value.
        """
        ...

    async def create_branch(self, repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """Create *new_branch* from *from_branch* (or the default branch).

        A no-op for the local provider, which has no notion of a remote ref.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :param new_branch: (str) The name of the branch to create.
        :param from_branch: (str) The branch to base the new branch on. Falls back to the
            repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        """
        ...

    async def get_default_branch(self, repo_id: str) -> str:
        """Return the default branch name for the repository.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :return: (str) The name of the repository's default branch.
        """
        ...

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """List repositories accessible via this provider.

        :param org: (str) Optional organisation/group name to filter results by.
        :return: (list) The accessible ``RepositoryInfo`` entries, optionally filtered by ``org``.
        """
        ...


class RepositoryError(Exception):
    """Raised when a repository provider operation fails."""


def normalize_repo_identifier(raw: str) -> str:
    """Normalise a repo identifier to ``owner/repo`` form.

    Accepts a full ``http(s)://`` URL (the last two path segments are
    extracted and joined) or an already-short ``owner/repo`` identifier
    (returned unchanged).

    :param raw: (str) A full repository URL or a short ``owner/repo`` identifier.
    :return: (str) The normalised ``owner/repo`` identifier.
    """
    if raw.startswith("http://") or raw.startswith("https://"):
        parts = urlparse(raw).path.strip("/").split("/")
        return "/".join(parts[-2:])
    return raw
</file>

<file path="src/mcp_project_context_server/integrations/vectorstore/chroma_http/client.py">
"""ChromaDB HTTP (remote) vector store provider.

Configuration
-------------
``CHROMA_HOST``
    Hostname or IP of the ChromaDB server.  Defaults to ``localhost``.

``CHROMA_PORT``
    Port the server listens on.  Defaults to ``8000``.

``CHROMA_API_KEY``
    Optional static API key for ChromaDB's built-in auth.
    Leave unset if the server does not require authentication.
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


class ChromaHttpVectorStoreProvider:
    """Vector store backed by a remote ChromaDB HTTP server.

    The chromadb ``HttpClient`` is initialized lazily on first use.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading connection settings from the environment."""
        self._host: str = os.getenv("CHROMA_HOST", "localhost")
        self._port: int = int(os.getenv("CHROMA_PORT", "8000"))
        self._api_key: Optional[str] = os.getenv("CHROMA_API_KEY") or None
        self._client: Optional[Any] = None

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "chroma-http"

    def _get_client(self) -> Any:
        """Return the ChromaDB HTTP client, initialising on first call."""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings

            settings = Settings(anonymized_telemetry=False)
            if self._api_key:
                settings = Settings(
                    anonymized_telemetry=False,
                    chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
                    chroma_client_auth_credentials=self._api_key,
                )
            self._client = chromadb.HttpClient(
                host=self._host,
                port=self._port,
                settings=settings,
            )
        return self._client

    # ------------------------------------------------------------------
    # VectorStoreProvider Protocol implementation
    # ------------------------------------------------------------------

    async def create_collection(self, name: str, metadata: dict | None = None) -> None:
        """Drop and recreate *name* (ADR-00006).

        :param name: (str) Collection name.
        :param metadata: (dict) Optional key/value metadata to attach to the collection.
        :return: (None) This method does not return a value.
        """
        client = self._get_client()

        def _sync() -> None:
            try:
                client.delete_collection(name)
            except Exception:
                pass
            client.create_collection(name=name, metadata=metadata or {})

        await asyncio.to_thread(_sync)

    async def delete_collection(self, name: str) -> None:
        """Delete *name*, silently succeeding if absent.

        :param name: (str) Collection name.
        :return: (None) This method does not return a value.
        """
        client = self._get_client()

        def _sync() -> None:
            try:
                client.delete_collection(name)
            except Exception:
                pass

        await asyncio.to_thread(_sync)

    async def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Add or update documents.

        :param collection_name: (str) Target collection.
        :param ids: (list) Per-document unique identifiers.
        :param embeddings: (list) Per-document embedding vectors (must all be the same length).
        :param documents: (list) Raw text for each document.
        :param metadatas: (list) Per-document metadata dicts.
        :return: (None) This method does not return a value.
        :raises VectorStoreError: If the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> None:
            try:
                col = client.get_collection(collection_name)
            except Exception as exc:
                raise VectorStoreError(f"Collection '{collection_name}' not found: {exc}") from exc
            col.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

        await asyncio.to_thread(_sync)

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> QueryResult:
        """Run a nearest-neighbour search.

        :param collection_name: (str) Collection to search.
        :param query_embedding: (list) Query vector (must match the dimension of stored embeddings).
        :param n_results: (int) Maximum number of results to return.
        :return: (QueryResult) A :class:`QueryResult` with the top-*n_results* matches.
        :raises VectorStoreError: If the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> QueryResult:
            try:
                col = client.get_collection(collection_name)
            except Exception as exc:
                raise VectorStoreError(f"Collection '{collection_name}' not found: {exc}") from exc
            n = min(n_results, col.count())
            if n == 0:
                return QueryResult(ids=[], documents=[], metadatas=[], distances=[])
            raw = col.query(query_embeddings=[query_embedding], n_results=n)
            return QueryResult(
                ids=raw["ids"][0] if raw.get("ids") else [],
                documents=raw["documents"][0] if raw.get("documents") else [],
                metadatas=raw["metadatas"][0] if raw.get("metadatas") else [],
                distances=raw["distances"][0] if raw.get("distances") else [],
            )

        return await asyncio.to_thread(_sync)

    async def count(self, collection_name: str) -> int:
        """Return document count (0 if collection absent).

        :param collection_name: (str) Collection to count.
        :return: (int) Document count. Returns 0 if the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> int:
            try:
                return client.get_collection(collection_name).count()
            except Exception:
                return 0

        return await asyncio.to_thread(_sync)

    async def collection_exists(self, collection_name: str) -> bool:
        """Return ``True`` if *collection_name* exists.

        :param collection_name: (str) Collection to check.
        :return: (bool) ``True`` if the collection exists, ``False`` otherwise.
        """
        client = self._get_client()

        def _sync() -> bool:
            try:
                client.get_collection(collection_name)
                return True
            except Exception:
                return False

        return await asyncio.to_thread(_sync)

    async def get_collection_metadata(self, collection_name: str) -> dict:
        """Return collection metadata (``{}`` if absent).

        :param collection_name: (str) Collection to inspect.
        :return: (dict) Metadata dict (may be empty). Returns ``{}`` if the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> dict:
            try:
                col = client.get_collection(collection_name)
                return col.metadata or {}
            except Exception:
                return {}

        return await asyncio.to_thread(_sync)

    def reset_for_testing(self) -> None:
        """Reset the cached client.  **For use in tests only.**

        :return: (None) This method does not return a value.
        """
        self._client = None
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/registry.py">
"""Embedding provider registry — factory driven by the `EMBED_PROVIDER` env var.

Design rules
------------
* **Fail fast at startup** if `EMBED_PROVIDER` is not set or the value is
  unrecognised.  There is no silent fallback to Ollama or any other provider.
  Explicit configuration is required.
* Importing this module does **not** initialise any provider.  Call
  `get_embedding_provider()` to obtain a provider instance.
* The returned instance is cached after the first call so that repeated
  calls within a process return the same object.

Usage
-----
::

    from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider

    provider = get_embedding_provider()
    vector = await provider.embed("some text")

Supported `EMBED_PROVIDER` values
------------------------------------
`ollama`
    Local Ollama server.  Requires `OLLAMA_HOST` (default: http://localhost:11434)
    and optionally `OLLAMA_EMBED_MODEL` (default: nomic-embed-text).

`voyage`
    Voyage AI cloud API.  Requires `VOYAGE_API_KEY`.
    Optional: `VOYAGE_EMBED_MODEL` (default: voyage-code-3).

`openai`
    OpenAI cloud API.  Requires `OPENAI_API_KEY`.
    Optional: `OPENAI_EMBED_MODEL` (default: text-embedding-3-small).

`cohere`
    Cohere cloud API.  Requires `COHERE_API_KEY`.
    Optional: `COHERE_EMBED_MODEL` (default: embed-english-v3.0).

`google`
    Google Gemini API (google-generativeai).  Requires `GOOGLE_API_KEY`.
    Optional: `GOOGLE_EMBED_MODEL` (default: text-embedding-004).

`vertexai`
    Google Vertex AI.  Requires `GOOGLE_VERTEX_PROJECT` and
    `GOOGLE_VERTEX_LOCATION`.
    Optional: `GOOGLE_VERTEX_EMBED_MODEL` (default: text-embedding-004).
"""
import logging
import os

from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_SUPPORTED_PROVIDERS: frozenset[str] = frozenset({"ollama", "voyage", "openai", "cohere", "google", "vertexai"})


def get_embedding_provider() -> EmbeddingProvider:
    """Return the configured embedding provider singleton.

    :return: (EmbeddingProvider) The embedding provider instance selected by
        the ``EMBED_PROVIDER`` environment variable.
    :raises EnvironmentError: If ``EMBED_PROVIDER`` is not set or is not one of
        the supported provider names.
    :raises ImportError: If the required package for the selected provider is
        not installed.
    """
    provider_name = os.getenv("EMBED_PROVIDER", "").strip().lower()

    if not provider_name:
        raise EnvironmentError(
            "EMBED_PROVIDER environment variable is not set.  "
            f"Set it to one of: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported EMBED_PROVIDER value '{provider_name}'.  "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    provider_instance = _build_provider(provider_name)
    return provider_instance


def _build_provider(provider_name: str) -> EmbeddingProvider:
    """Instantiate and return the provider for *provider_name*."""
    if provider_name == "ollama":
        from mcp_project_context_server.integrations.embeddings.ollama.client import (
            OllamaEmbeddingProvider,
        )

        return OllamaEmbeddingProvider()

    elif provider_name == "voyage":
        from mcp_project_context_server.integrations.embeddings.voyage.client import (
            VoyageEmbeddingProvider,
        )

        return VoyageEmbeddingProvider()

    elif provider_name == "openai":
        from mcp_project_context_server.integrations.embeddings.openai.client import (
            OpenAIEmbeddingProvider,
        )

        return OpenAIEmbeddingProvider()

    elif provider_name == "cohere":
        from mcp_project_context_server.integrations.embeddings.cohere.client import (
            CohereEmbeddingProvider,
        )

        return CohereEmbeddingProvider()

    elif provider_name == "google":
        from mcp_project_context_server.integrations.embeddings.google.client import (
            GoogleEmbeddingProvider,
        )

        return GoogleEmbeddingProvider()

    elif provider_name == "vertexai":
        from mcp_project_context_server.integrations.embeddings.vertexai.client import (
            GoogleVertexEmbeddingProvider,
        )

        return GoogleVertexEmbeddingProvider()

    else:
        # Should never reach here — guarded by the caller.
        raise EnvironmentError(f"Internal error: unhandled provider '{provider_name}'")  # pragma: no cover
</file>

<file path="src/mcp_project_context_server/integrations/repository/gitea/client.py">
"""Gitea repository provider implementation using the Gitea REST API."""

import base64
import logging
import os
from typing import Optional

import httpx

from mcp_project_context_server.integrations.repository.base import (
    RepositoryError,
    RepositoryInfo,
    normalize_repo_identifier,
)

logger = logging.getLogger(__name__)

_SOURCE_EXTENSIONS: frozenset[str] = frozenset({".py", ".ts", ".js", ".go", ".rs", ".cs", ".java", ".rb", ".php"})
_MAX_SOURCE_FILES = 200


class GiteaRepositoryProvider:
    """Repository provider that communicates with a self-hosted Gitea instance.

    Configuration is read from environment variables at instantiation time:

    * ``REPO_AUTH_TOKEN`` — Gitea access token.
    * ``REPO_BASE_URL`` — **Required** Gitea instance URL (no default).
      The API base is derived as ``{REPO_BASE_URL}/api/v1``.
    * ``REPO_DEFAULT_BRANCH`` — Fallback branch name (default: ``"main"``).
    """

    def __init__(self) -> None:
        """Initialize the provider from environment variables.

        :raises EnvironmentError: If ``REPO_BASE_URL`` is not set.
        """
        self._token: str = os.getenv("REPO_AUTH_TOKEN", "")
        base = os.getenv("REPO_BASE_URL", "").rstrip("/")
        if not base:
            raise EnvironmentError(
                "REPO_BASE_URL is required for the Gitea provider. "
                "Set it to your Gitea instance URL (e.g. https://gitea.example.com)."
            )
        self._api_base: str = f"{base}/api/v1"
        self._default_branch_fallback: str = os.getenv("REPO_DEFAULT_BRANCH", "main")

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "gitea"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalise_repo_id(self, repo_id: str) -> str:
        """Normalise *repo_id* to ``owner/repo`` form."""
        return normalize_repo_identifier(repo_id)

    def _headers(self) -> dict[str, str]:
        """Return HTTP headers for Gitea API requests."""
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"token {self._token}"
        return headers

    def _split(self, repo_id: str) -> tuple[str, str]:
        """Return *(owner, repo)* from a normalised ``owner/repo`` string."""
        owner, repo = self._normalise_repo_id(repo_id).split("/", 1)
        return owner, repo

    # ------------------------------------------------------------------
    # Protocol methods
    # ------------------------------------------------------------------

    async def fetch_context_files(self, repo_id: str) -> dict[str, str]:
        """Fetch all .md files from the ``.context/`` subtree of the repository.

        Returns an empty dict on 404.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative markdown file paths to their contents.
        """
        owner, repo = self._split(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
                headers=self._headers(),
            )
            if resp.status_code == 404:
                return {}
            resp.raise_for_status()
            tree = resp.json().get("tree", [])
            for item in tree:
                path: str = item.get("path", "")
                if path.startswith(".context/") and path.endswith(".md"):
                    rel = path.removeprefix(".context/")
                    raw = await client.get(
                        f"{self._api_base}/repos/{owner}/{repo}/raw/.context/{rel}" f"?ref={branch}",
                        headers=self._headers(),
                    )
                    if raw.status_code == 200:
                        result[rel] = raw.text
        return result

    async def fetch_source_bundle(self, repo_id: str) -> Optional[str]:
        """Fetch the content of ``.context/BUNDLE.md``, or ``None``.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (str) The contents of ``BUNDLE.md``, or ``None`` if it does not exist.
        """
        owner, repo = self._split(repo_id)
        branch = await self.get_default_branch(repo_id)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/repos/{owner}/{repo}/raw/.context/BUNDLE.md?ref={branch}",
                headers=self._headers(),
            )
            if resp.status_code == 200:
                return resp.text
            return None

    async def fetch_source_files(self, repo_id: str) -> dict[str, str]:
        """Fetch source code files from the repository tree.

        Capped at 200 files.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative source file paths to their contents.
        """
        owner, repo = self._split(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
                headers=self._headers(),
            )
            resp.raise_for_status()
            tree = resp.json().get("tree", [])
            candidates = [item for item in tree if _has_source_extension(item.get("path", ""))][:_MAX_SOURCE_FILES]
            for item in candidates:
                path = item["path"]
                raw = await client.get(
                    f"{self._api_base}/repos/{owner}/{repo}/raw/{path}?ref={branch}",
                    headers=self._headers(),
                )
                if raw.status_code == 200:
                    result[path] = raw.text
        return result

    async def write_file(
        self, repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Create or update *path* in the repository.

        Writes to *branch* if given, otherwise the repository's default
        branch.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :param path: (str) The file path to write, relative to the repository root.
        :param content: (str) The new full contents of the file.
        :param message: (str) The commit message describing the write.
        :param branch: (str) Target branch. Falls back to the repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the API returns a non-success status.
        """
        owner, repo = self._split(repo_id)
        target_branch = branch or await self.get_default_branch(repo_id)
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        async with httpx.AsyncClient() as client:
            # Check if file exists to get SHA — must be scoped to the target
            # branch, otherwise this always reads the default branch's SHA.
            check = await client.get(
                f"{self._api_base}/repos/{owner}/{repo}/contents/{path}",
                headers=self._headers(),
                params={"ref": target_branch},
            )
            if check.status_code == 200:
                sha = check.json().get("sha", "")
                payload = {"message": message, "content": encoded, "sha": sha, "branch": target_branch}
                resp = await client.patch(
                    f"{self._api_base}/repos/{owner}/{repo}/contents/{path}",
                    headers=self._headers(),
                    json=payload,
                )
            else:
                payload = {"message": message, "content": encoded, "branch": target_branch}
                resp = await client.post(
                    f"{self._api_base}/repos/{owner}/{repo}/contents/{path}",
                    headers=self._headers(),
                    json=payload,
                )
            if not resp.is_success:
                raise RepositoryError(f"Gitea write_file failed ({resp.status_code}): {resp.text}")

    async def create_branch(self, repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """Create *new_branch* from *from_branch* (or the default branch).

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :param new_branch: (str) The name of the branch to create.
        :param from_branch: (str) The branch to base the new branch on. Falls back to the
            repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the API returns a non-success status.
        """
        owner, repo = self._split(repo_id)
        base = from_branch or await self.get_default_branch(repo_id)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._api_base}/repos/{owner}/{repo}/branches",
                headers=self._headers(),
                json={"new_branch_name": new_branch, "old_branch_name": base},
            )
            if not resp.is_success:
                raise RepositoryError(f"Gitea create_branch failed ({resp.status_code}): {resp.text}")

    async def get_default_branch(self, repo_id: str) -> str:
        """Return the default branch for *repo_id*, falling back to env / ``"main"``.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (str) The repository's default branch name, or the configured/``"main"`` fallback.
        """
        owner, repo = self._split(repo_id)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self._api_base}/repos/{owner}/{repo}",
                    headers=self._headers(),
                )
                if resp.status_code == 200:
                    return resp.json().get("default_branch", self._default_branch_fallback)
        except Exception:
            pass
        return self._default_branch_fallback

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """List repositories accessible to the configured token.

        If *org* is set, lists repositories for that organisation.  Otherwise
        searches all accessible repositories.

        :param org: (str) Optional organisation name to list repositories for.
        :return: (list) The accessible ``RepositoryInfo`` entries.
        """
        async with httpx.AsyncClient() as client:
            if org:
                url = f"{self._api_base}/orgs/{org}/repos"
            else:
                params = "limit=50"
                if self._token:
                    params += f"&token={self._token}"
                url = f"{self._api_base}/repos/search?{params}"
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
            # /repos/search returns {"data": [...]} while /orgs/{org}/repos returns [...]
            items = data.get("data", data) if isinstance(data, dict) else data
            return [_repo_info_from_gitea(r) for r in items]


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _has_source_extension(path: str) -> bool:
    """Return True if *path* ends with a recognised source extension."""
    return any(path.endswith(ext) for ext in _SOURCE_EXTENSIONS)


def _repo_info_from_gitea(data: dict) -> RepositoryInfo:
    """Build a :class:`RepositoryInfo` from a Gitea API repository object."""
    return RepositoryInfo(
        identifier=data.get("full_name", ""),
        name=data.get("name", ""),
        description=data.get("description") or "",
        indexed=False,
    )
</file>

<file path="src/mcp_project_context_server/integrations/repository/gitlab/client.py">
"""GitLab repository provider implementation using the GitLab REST API."""
import logging
import os
from typing import Optional
from urllib.parse import quote

import httpx

from mcp_project_context_server.integrations.repository.base import (
    RepositoryError,
    RepositoryInfo,
    normalize_repo_identifier,
)

logger = logging.getLogger(__name__)

_SOURCE_EXTENSIONS: frozenset[str] = frozenset({".py", ".ts", ".js", ".go", ".rs", ".cs", ".java", ".rb", ".php"})
_MAX_SOURCE_FILES = 200


class GitLabRepositoryProvider:
    """Repository provider that communicates with the GitLab REST API (v4).

    Configuration is read from environment variables at instantiation time:

    * ``REPO_AUTH_TOKEN`` — GitLab personal access token.
    * ``REPO_BASE_URL`` — GitLab instance URL (default: ``https://gitlab.com``).
      The API base is derived as ``{REPO_BASE_URL}/api/v4``.
    * ``REPO_DEFAULT_BRANCH`` — Fallback branch name (default: ``"main"``).
    """

    def __init__(self) -> None:
        """Initialize the provider from environment variables."""
        self._token: str = os.getenv("REPO_AUTH_TOKEN", "")
        base = os.getenv("REPO_BASE_URL", "https://gitlab.com").rstrip("/")
        self._api_base: str = f"{base}/api/v4"
        self._default_branch_fallback: str = os.getenv("REPO_DEFAULT_BRANCH", "main")

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "gitlab"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalise_repo_id(self, repo_id: str) -> str:
        """Normalise *repo_id* to ``namespace/project`` form."""
        return normalize_repo_identifier(repo_id)

    def _url_encode_id(self, repo_id: str) -> str:
        """URL-encode the ``namespace/project`` string for GitLab's ``:id`` parameter."""
        return quote(self._normalise_repo_id(repo_id), safe="")

    def _headers(self) -> dict[str, str]:
        """Return HTTP headers for GitLab API requests."""
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            headers["PRIVATE-TOKEN"] = self._token
        return headers

    # ------------------------------------------------------------------
    # Protocol methods
    # ------------------------------------------------------------------

    async def fetch_context_files(self, repo_id: str) -> dict[str, str]:
        """Fetch all .md files from the ``.context/`` tree of the repository.

        Returns an empty dict on 404.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative markdown file paths to their contents.
        """
        encoded_id = self._url_encode_id(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/projects/{encoded_id}/repository/tree"
                f"?path=.context&recursive=true&ref={branch}&per_page=100",
                headers=self._headers(),
            )
            if resp.status_code == 404:
                return {}
            resp.raise_for_status()
            for item in resp.json():
                if item.get("type") == "blob" and item["name"].endswith(".md"):
                    file_path = item["path"]
                    encoded_path = quote(file_path, safe="")
                    raw = await client.get(
                        f"{self._api_base}/projects/{encoded_id}/repository/files" f"/{encoded_path}/raw?ref={branch}",
                        headers=self._headers(),
                    )
                    if raw.status_code == 200:
                        rel = file_path.removeprefix(".context/")
                        result[rel] = raw.text
        return result

    async def fetch_source_bundle(self, repo_id: str) -> Optional[str]:
        """Fetch the content of ``.context/BUNDLE.md``, or ``None``.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :return: (str) The contents of ``BUNDLE.md``, or ``None`` if it does not exist.
        """
        encoded_id = self._url_encode_id(repo_id)
        branch = await self.get_default_branch(repo_id)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/projects/{encoded_id}/repository/files" f"/.context%2FBUNDLE.md/raw?ref={branch}",
                headers=self._headers(),
            )
            if resp.status_code == 200:
                return resp.text
            return None

    async def fetch_source_files(self, repo_id: str) -> dict[str, str]:
        """Fetch source code files from the repository tree.

        Capped at 200 files.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative source file paths to their contents.
        """
        encoded_id = self._url_encode_id(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/projects/{encoded_id}/repository/tree" f"?recursive=true&ref={branch}&per_page=100",
                headers=self._headers(),
            )
            resp.raise_for_status()
            candidates = [
                item
                for item in resp.json()
                if item.get("type") == "blob" and _has_source_extension(item.get("path", ""))
            ][:_MAX_SOURCE_FILES]
            for item in candidates:
                path = item["path"]
                encoded_path = quote(path, safe="")
                raw = await client.get(
                    f"{self._api_base}/projects/{encoded_id}/repository/files" f"/{encoded_path}/raw?ref={branch}",
                    headers=self._headers(),
                )
                if raw.status_code == 200:
                    result[path] = raw.text
        return result

    async def write_file(
        self, repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Create or update *path* in the repository.

        Writes to *branch* if given, otherwise the repository's default
        branch.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :param path: (str) The file path to write, relative to the repository root.
        :param content: (str) The new full contents of the file.
        :param message: (str) The commit message describing the write.
        :param branch: (str) Target branch. Falls back to the repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the API returns a non-success status.
        """
        encoded_id = self._url_encode_id(repo_id)
        target_branch = branch or await self.get_default_branch(repo_id)
        encoded_path = quote(path, safe="")
        payload = {"branch": target_branch, "content": content, "commit_message": message}
        async with httpx.AsyncClient() as client:
            # Check if file exists
            head = await client.head(
                f"{self._api_base}/projects/{encoded_id}/repository/files/{encoded_path}" f"?ref={target_branch}",
                headers=self._headers(),
            )
            if head.status_code == 200:
                method = client.put
            else:
                method = client.post
            resp = await method(
                f"{self._api_base}/projects/{encoded_id}/repository/files/{encoded_path}",
                headers=self._headers(),
                json=payload,
            )
            if not resp.is_success:
                raise RepositoryError(f"GitLab write_file failed ({resp.status_code}): {resp.text}")

    async def create_branch(self, repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """Create *new_branch* from *from_branch* (or the default branch).

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :param new_branch: (str) The name of the branch to create.
        :param from_branch: (str) The branch to base the new branch on. Falls back to the
            repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the API returns a non-success status.
        """
        encoded_id = self._url_encode_id(repo_id)
        base = from_branch or await self.get_default_branch(repo_id)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._api_base}/projects/{encoded_id}/repository/branches",
                headers=self._headers(),
                params={"branch": new_branch, "ref": base},
            )
            if not resp.is_success:
                raise RepositoryError(f"GitLab create_branch failed ({resp.status_code}): {resp.text}")

    async def get_default_branch(self, repo_id: str) -> str:
        """Return the default branch for *repo_id*, falling back to env / ``"main"``.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :return: (str) The repository's default branch name, or the configured/``"main"`` fallback.
        """
        encoded_id = self._url_encode_id(repo_id)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self._api_base}/projects/{encoded_id}",
                    headers=self._headers(),
                )
                if resp.status_code == 200:
                    return resp.json().get("default_branch", self._default_branch_fallback)
        except Exception:
            pass
        return self._default_branch_fallback

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """List repositories accessible to the configured token.

        If *org* is set, lists projects for that GitLab group.  Otherwise lists
        all projects the authenticated user is a member of.

        :param org: (str) Optional GitLab group name to list projects for.
        :return: (list) The accessible ``RepositoryInfo`` entries.
        """
        async with httpx.AsyncClient() as client:
            if org:
                url = f"{self._api_base}/groups/{org}/projects?per_page=100"
            else:
                url = f"{self._api_base}/projects?membership=true&per_page=100"
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return [_repo_info_from_gitlab(r) for r in resp.json()]


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _has_source_extension(path: str) -> bool:
    """Return True if *path* ends with a recognised source extension."""
    return any(path.endswith(ext) for ext in _SOURCE_EXTENSIONS)


def _repo_info_from_gitlab(data: dict) -> RepositoryInfo:
    """Build a :class:`RepositoryInfo` from a GitLab API project object."""
    namespace = data.get("namespace", {}).get("full_path", "")
    name = data.get("name", "")
    identifier = f"{namespace}/{name}" if namespace else name
    return RepositoryInfo(
        identifier=identifier,
        name=name,
        description=data.get("description") or "",
        indexed=False,
    )
</file>

<file path="src/mcp_project_context_server/integrations/vectorstore/pgvector/client.py">
"""PostgreSQL + pgvector vector store provider.

Configuration
-------------
``PGVECTOR_CONNECTION_STRING``
    A libpq-compatible connection string, e.g.:
    ``postgresql://{user}:{password}@{host}:5432/dbname``

Design
------
* One table per collection: ``vs_<sanitised_collection_name>``
* A ``vs_collections`` sidecar table stores collection metadata and the
  embedding dimension (derived from the first upsert call).
* Vectors are stored as ``vector(N)`` using the pgvector extension.
* The drop-and-recreate indexing strategy (ADR-00006) is implemented by
  ``create_collection`` — it drops the table and recreates it.
"""
import logging
import os
import re
from typing import Any, Optional

from mcp_project_context_server.integrations.vectorstore.base import (
    QueryResult,
    VectorStoreError,
)

logger = logging.getLogger(__name__)

_TABLE_PREFIX = "vs_"


def _table_name(collection_name: str) -> str:
    """Sanitise *collection_name* into a safe PostgreSQL table name."""
    safe = re.sub(r"[^a-z0-9_]", "_", collection_name.lower())
    return f"{_TABLE_PREFIX}{safe}"


class PgVectorStoreProvider:
    """Vector store backed by PostgreSQL with the pgvector extension.

    Uses ``asyncpg`` for async PostgreSQL access.  The pgvector extension
    must already be installed in the target database::

        CREATE EXTENSION IF NOT EXISTS vector;
    """

    def __init__(self) -> None:
        """Initialize the provider, reading ``PGVECTOR_CONNECTION_STRING`` from the environment.

        :raises EnvironmentError: If ``PGVECTOR_CONNECTION_STRING`` is not set.
        """
        self._dsn: Optional[str] = os.getenv("PGVECTOR_CONNECTION_STRING")
        if not self._dsn:
            raise EnvironmentError(
                "PGVECTOR_CONNECTION_STRING environment variable is required " "when VECTOR_STORE_PROVIDER=pgvector"
            )
        self._pool: Optional[Any] = None

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "pgvector"

    async def _get_pool(self) -> Any:
        """Return the asyncpg connection pool, creating it on first call."""
        if self._pool is None:
            try:
                import asyncpg  # type: ignore[import]
            except ImportError as exc:
                raise ImportError(
                    "asyncpg is required for pgvector support.  "
                    "Install it with: pip install mcp-project-context-server[pgvector]"
                ) from exc

            # Register the pgvector codec so asyncpg can decode vector columns
            async def _init(conn: Any) -> None:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")  # type: ignore[attr-defined]
                await conn.set_type_codec(  # type: ignore[attr-defined]
                    "vector",
                    encoder=lambda v: str(v),
                    decoder=lambda v: [float(x) for x in v.strip("[]").split(",")],
                    schema="public",
                    format="text",
                )

            self._pool = await asyncpg.create_pool(self._dsn, init=_init)  # type: ignore[attr-defined]

            # Ensure sidecar table exists
            async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS vs_collections (
                        name        TEXT PRIMARY KEY,
                        dimension   INT,
                        metadata    JSONB DEFAULT '{}'
                    )
                """)

        return self._pool

    # ------------------------------------------------------------------
    # VectorStoreProvider Protocol implementation
    # ------------------------------------------------------------------

    async def create_collection(self, name: str, metadata: dict | None = None) -> None:
        """Drop and recreate the table for *name* (ADR-00006).

        Dimension is not known at creation time — the vector column is added
        on the first ``upsert`` call once the dimension is established.

        :param name: (str) Collection name.
        :param metadata: (dict) Optional key/value metadata to attach to the collection.
        :return: (None) This method does not return a value.
        """
        pool = await self._get_pool()
        tbl = _table_name(name)
        import json

        async with pool.acquire() as conn:  # type: ignore[attr-defined]
            await conn.execute(f"DROP TABLE IF EXISTS {tbl}")
            await conn.execute("DELETE FROM vs_collections WHERE name = $1", name)
            await conn.execute(
                "INSERT INTO vs_collections (name, dimension, metadata) VALUES ($1, NULL, $2::jsonb)",
                name,
                json.dumps(metadata or {}),
            )

    async def delete_collection(self, name: str) -> None:
        """Drop the table for *name* and remove from sidecar.

        :param name: (str) Collection name.
        :return: (None) This method does not return a value.
        """
        try:
            pool = await self._get_pool()
            tbl = _table_name(name)
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                await conn.execute(f"DROP TABLE IF EXISTS {tbl}")
                await conn.execute("DELETE FROM vs_collections WHERE name = $1", name)
        except Exception:
            pass

    async def _ensure_table(self, conn: Any, name: str, dimension: int) -> None:
        """Create the vector table for *name* if it does not yet exist."""
        tbl = _table_name(name)
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {tbl} (
                id          TEXT PRIMARY KEY,
                embedding   vector({dimension}),
                document    TEXT,
                metadata    JSONB DEFAULT '{{}}'
            )
            """)  # type: ignore[attr-defined]
        await conn.execute(  # type: ignore[attr-defined]
            f"CREATE INDEX IF NOT EXISTS {tbl}_emb_idx ON {tbl} USING ivfflat (embedding vector_cosine_ops)"
        )
        await conn.execute(  # type: ignore[attr-defined]
            "UPDATE vs_collections SET dimension = $1 WHERE name = $2 AND dimension IS NULL",
            dimension,
            name,
        )

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
        """
        if not ids:
            return
        import json

        dimension = len(embeddings[0])
        pool = await self._get_pool()
        tbl = _table_name(collection_name)

        async with pool.acquire() as conn:  # type: ignore[attr-defined]
            await self._ensure_table(conn, collection_name, dimension)
            for doc_id, emb, doc, meta in zip(ids, embeddings, documents, metadatas):
                vec_str = "[" + ",".join(str(v) for v in emb) + "]"
                await conn.execute(  # type: ignore[attr-defined]
                    f"""
                    INSERT INTO {tbl} (id, embedding, document, metadata)
                    VALUES ($1, $2::vector, $3, $4::jsonb)
                    ON CONFLICT (id) DO UPDATE
                        SET embedding = EXCLUDED.embedding,
                            document  = EXCLUDED.document,
                            metadata  = EXCLUDED.metadata
                    """,
                    doc_id,
                    vec_str,
                    doc,
                    json.dumps(meta),
                )

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> QueryResult:
        """Run cosine-similarity nearest-neighbour search.

        :param collection_name: (str) Collection to search.
        :param query_embedding: (list) Query vector (must match the dimension of stored embeddings).
        :param n_results: (int) Maximum number of results to return.
        :return: (QueryResult) A :class:`QueryResult` with the top-*n_results* matches.
        :raises VectorStoreError: If the query fails.
        """
        import json

        pool = await self._get_pool()
        tbl = _table_name(collection_name)
        vec_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

        try:
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                rows = await conn.fetch(  # type: ignore[attr-defined]
                    f"""
                    SELECT id, document, metadata,
                           1 - (embedding <=> $1::vector) AS similarity
                    FROM {tbl}
                    ORDER BY embedding <=> $1::vector
                    LIMIT $2
                    """,
                    vec_str,
                    n_results,
                )
        except Exception as exc:
            raise VectorStoreError(f"Query failed on collection '{collection_name}': {exc}") from exc

        return QueryResult(
            ids=[r["id"] for r in rows],
            documents=[r["document"] for r in rows],
            metadatas=[json.loads(r["metadata"]) for r in rows],
            distances=[float(r["similarity"]) for r in rows],
        )

    async def count(self, collection_name: str) -> int:
        """Return document count (0 if table absent).

        :param collection_name: (str) Collection to count.
        :return: (int) Document count. Returns 0 if the collection does not exist.
        """
        try:
            pool = await self._get_pool()
            tbl = _table_name(collection_name)
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                row = await conn.fetchrow(f"SELECT COUNT(*) AS n FROM {tbl}")  # type: ignore[attr-defined]
                return int(row["n"])
        except Exception:
            return 0

    async def collection_exists(self, collection_name: str) -> bool:
        """Return ``True`` if a row exists in the sidecar for *collection_name*.

        :param collection_name: (str) Collection to check.
        :return: (bool) ``True`` if the collection exists, ``False`` otherwise.
        """
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                row = await conn.fetchrow(  # type: ignore[attr-defined]
                    "SELECT 1 FROM vs_collections WHERE name = $1", collection_name
                )
                return row is not None
        except Exception:
            return False

    async def get_collection_metadata(self, collection_name: str) -> dict:
        """Return metadata from the sidecar (``{}`` if absent).

        :param collection_name: (str) Collection to inspect.
        :return: (dict) Metadata dict (may be empty). Returns ``{}`` if the collection does not exist.
        """
        try:
            import json

            pool = await self._get_pool()
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                row = await conn.fetchrow(  # type: ignore[attr-defined]
                    "SELECT metadata FROM vs_collections WHERE name = $1", collection_name
                )
                if row is None:
                    return {}
                return json.loads(row["metadata"]) if row["metadata"] else {}
        except Exception:
            return {}

    async def close(self) -> None:
        """Close the connection pool.  Call on server shutdown.

        :return: (None) This method does not return a value.
        """
        if self._pool is not None:
            await self._pool.close()  # type: ignore[attr-defined]
            self._pool = None

    def reset_for_testing(self) -> None:
        """Reset the cached pool.  **For use in tests only.**

        :return: (None) This method does not return a value.
        """
        self._pool = None
</file>

<file path="src/mcp_project_context_server/tools/index_context.py">
"""Tool: index_project_context — re-indexes .context/ into the configured vector store."""
import logging
import os

from mcp import types

from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access
from mcp_project_context_server.integrations.vectorstore.registry import get_indexer

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``index_project_context`` tool call.

    :param arguments: (dict) Tool input dict. Requires key ``"project_path"``.
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        with the indexing result summary or an error message.
    """
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    indexer = get_indexer()
    result = await indexer(_project_path)
    return [types.TextContent(type="text", text=result)]
</file>

<file path="src/mcp_project_context_server/tools/save_session.py">
"""Tool: save_session_summary — writes a session summary to .context/sessions/."""
import logging
import os
from datetime import datetime

from mcp import types

from mcp_project_context_server.helpers.context import find_context_dir, resolve_project_path
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider, validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``save_session_summary`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``
        and ``"summary"``.
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        confirming where the session summary was saved, or an error/"not found"
        message.
    """
    summary: str = arguments["summary"]

    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    resolved_path, is_remote = resolve_project_path(_project_path)

    if is_remote:
        return await _handle_remote(resolved_path, summary)

    context_dir = find_context_dir(resolved_path)
    if not context_dir:
        return [
            types.TextContent(
                type="text",
                text=f"No .context/ directory found near {arguments['project_path']}",
            )
        ]

    sessions_dir = context_dir / "sessions"
    sessions_dir.mkdir(exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    session_file = sessions_dir / f"{today}.md"

    if session_file.exists():
        timestamp = datetime.now().strftime("%H:%M")
        file_content = f"{session_file.read_text(encoding='utf-8')}" f"\n\n### Session at {timestamp}\n\n{summary}"
    else:
        file_content = f"# Session: {today}\n\n{summary}"

    session_file.write_text(file_content, encoding="utf-8")
    # as_posix() gives a consistent forward-slash path regardless of platform.
    return [
        types.TextContent(
            type="text",
            text=f"Session summary saved to {session_file.as_posix()}",
        )
    ]


async def _handle_remote(repo_id: str, summary: str) -> list[types.TextContent]:
    """Save a session summary to a remote repository's ``.context/sessions/``.

    Write target is configurable via ``REPO_SESSION_WRITE_MODE``:

    * ``"direct"`` (default) — write straight to ``REPO_SESSION_BRANCH`` if
      set, otherwise the repository's default branch.
    * ``"branch"`` — create a new branch (``mcp-session/{date}-{HHMMSS}``)
      off the default branch and write there, leaving the target branch
      untouched for review.
    """
    provider = get_repository_provider()

    today = datetime.now().strftime("%Y-%m-%d")
    session_key = f"sessions/{today}.md"
    target_path = f".context/{session_key}"

    try:
        files = await provider.fetch_context_files(repo_id)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=f"Error accessing repository: {exc}")]

    existing = files.get(session_key)
    if existing:
        timestamp = datetime.now().strftime("%H:%M")
        file_content = f"{existing}\n\n### Session at {timestamp}\n\n{summary}"
    else:
        file_content = f"# Session: {today}\n\n{summary}"

    message = f"Add session summary for {today}"
    write_mode = os.getenv("REPO_SESSION_WRITE_MODE", "direct").strip().lower()

    try:
        if write_mode == "branch":
            branch_name = f"mcp-session/{today}-{datetime.now().strftime('%H%M%S')}"
            await provider.create_branch(repo_id, branch_name)
            await provider.write_file(repo_id, target_path, file_content, message, branch=branch_name)
            return [
                types.TextContent(
                    type="text",
                    text=(
                        f"Session summary pushed to new branch `{branch_name}` on `{repo_id}` "
                        f"(provider: {provider.provider_name}). Path: {target_path}"
                    ),
                )
            ]

        target_branch = os.getenv("REPO_SESSION_BRANCH") or None
        await provider.write_file(repo_id, target_path, file_content, message, branch=target_branch)
        branch_label = target_branch or await provider.get_default_branch(repo_id)
        return [
            types.TextContent(
                type="text",
                text=(
                    f"Session summary saved to `{repo_id}` ({target_path}) on branch "
                    f"`{branch_label}` (provider: {provider.provider_name})."
                ),
            )
        ]
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=f"Error saving session summary: {exc}")]
</file>

<file path="src/mcp_project_context_server/indexing/indexer.py">
"""Shared indexing pipeline — provider-agnostic core.

Accepts any ``VectorStoreProvider`` instance.  Vector-store-specific indexers
in ``integrations/vectorstore/{provider}/indexer.py`` are responsible for
instantiating their own provider and passing it here.

No vector-store or embedding provider is imported directly.  All external
dependencies are injected via the ``store`` parameter and the embedding
registry.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from mcp_project_context_server._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

from mcp_project_context_server.helpers.context import (
    collection_name_for,
    collection_name_for_repo_id,
    find_context_dir,
    read_context_files,
    resolve_project_path,
)

from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider
from mcp_project_context_server.integrations.vectorstore.base import VectorStoreProvider

logger = logging.getLogger(__name__)

_EMBED_CONCURRENCY: int = int(os.getenv("EMBED_CONCURRENCY", "4"))


async def run_index_pipeline(project_path: str | Path, store: VectorStoreProvider) -> str:
    """Chunk, embed concurrently, and batch-store all .context/ markdown files.

    Stamps the collection with provenance metadata (embed provider/model,
    vector store provider, repo provider, server version, indexed_at timestamp)
    so that search can detect and warn on provider/model mismatches.

    :param project_path: (str) Path to the project root or any file within it.
    :param store: (VectorStoreProvider) Fully initialized vector store provider to write into.
    :return: (str) A human-readable summary string describing what was indexed.
    """
    repo_provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(str(project_path))

    if is_remote:
        try:
            files = await repo_provider.fetch_context_files(resolved_path)
        except RepositoryError as exc:
            return f"Error accessing repository {resolved_path}: {exc}"
        if not files:
            return f"No .context/ directory found in {resolved_path}"
        col_name = collection_name_for_repo_id(resolved_path)
    else:
        context_dir = find_context_dir(project_path)
        if not context_dir:
            return f"No .context/ directory found at or above {project_path}"
        col_name = collection_name_for(context_dir)
        files = read_context_files(context_dir)

    # Deferred until after the context-existence check above so that a
    # missing .context/ directory is reported even when no embedding
    # provider is configured (EMBED_PROVIDER unset).
    embed_provider = get_embedding_provider()
    chunk_size = embed_provider.max_chars
    embed_chunk = embed_provider.embed_chunk

    collection_metadata = {
        "embed_provider": embed_provider.provider_name,
        "embed_model": embed_provider.model_name,
        "vector_store_provider": store.provider_name,
        "repo_provider": repo_provider.provider_name,
        "server_version": __version__,
        "indexed_at": datetime.now(timezone.utc).isoformat(),
    }

    await store.create_collection(col_name, metadata=collection_metadata)

    all_chunks: list[tuple[str, str, str, int]] = []
    for filename, file_content in files.items():
        for i, chunk in enumerate(file_content[j : j + chunk_size] for j in range(0, len(file_content), chunk_size)):
            if chunk.strip():
                all_chunks.append((f"{filename}::{i}", chunk, filename, i))

    if not all_chunks:
        return f"Indexed 0 chunks from {len(files)} files into collection '{col_name}'"

    semaphore = asyncio.Semaphore(_EMBED_CONCURRENCY)

    async def _embed(doc_id: str, chunk: str, filename: str, chunk_idx: int):
        async with semaphore:
            try:
                embedding = await embed_chunk(chunk)
                return (doc_id, chunk, embedding, filename, chunk_idx)
            except Exception as e:
                print(f"Warning: failed to embed {doc_id}: {e}", file=sys.stderr)
                return None

    results = await asyncio.gather(*[_embed(*c) for c in all_chunks])

    valid = [r for r in results if r is not None]
    if valid:
        await store.upsert(
            collection_name=col_name,
            ids=[r[0] for r in valid],
            embeddings=[r[2] for r in valid],
            documents=[r[1] for r in valid],
            metadatas=[{"file": r[3], "chunk": r[4]} for r in valid],
        )

    return f"Indexed {len(valid)} chunks from {len(files)} files into collection '{col_name}'"
</file>

<file path="src/mcp_project_context_server/integrations/repository/github/client.py">
"""GitHub repository provider implementation using the GitHub REST API."""

import base64
import logging
import os
from typing import Optional

import httpx

from mcp_project_context_server.integrations.repository.base import (
    RepositoryError,
    RepositoryInfo,
    normalize_repo_identifier,
)

logger = logging.getLogger(__name__)

_SOURCE_EXTENSIONS: frozenset[str] = frozenset({".py", ".ts", ".js", ".go", ".rs", ".cs", ".java", ".rb", ".php"})
_MAX_SOURCE_FILES = 200


class GitHubRepositoryProvider:
    """Repository provider that communicates with the GitHub REST API.

    Configuration is read from environment variables at instantiation time:

    * ``REPO_AUTH_TOKEN`` — GitHub personal access token (required for private repos).
    * ``REPO_BASE_URL`` — Base URL for GitHub Enterprise (default: ``https://api.github.com``).
    * ``REPO_DEFAULT_BRANCH`` — Fallback branch name when the API cannot be reached
      (default: ``"main"``).
    """

    def __init__(self) -> None:
        """Initialize the provider from environment variables."""
        self._token: str = os.getenv("GITHUB_TOKEN", "")
        self._base_url: str = os.getenv("REPO_BASE_URL", "https://api.github.com").rstrip("/")
        self._default_branch_fallback: str = os.getenv("REPO_DEFAULT_BRANCH", "main")

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "github"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalise_repo_id(self, repo_id: str) -> str:
        """Normalise *repo_id* to the ``owner/repo`` form.

        If *repo_id* starts with ``http://`` or ``https://`` the last two path
        segments are extracted and joined.  Otherwise the value is returned as-is.
        """
        return normalize_repo_identifier(repo_id)

    def _headers(self) -> dict[str, str]:
        """Return HTTP headers for GitHub API requests."""
        headers: dict[str, str] = {"Accept": "application/vnd.github.v3+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _split(self, repo_id: str) -> tuple[str, str]:
        """Return *(owner, repo)* from a normalised ``owner/repo`` string."""
        owner, repo = self._normalise_repo_id(repo_id).split("/", 1)
        return owner, repo

    # ------------------------------------------------------------------
    # Protocol methods
    # ------------------------------------------------------------------

    async def fetch_context_files(self, repo_id: str) -> dict[str, str]:
        """Fetch all .md files from the ``.context/`` directory of the repository.

        Returns an empty dict on 404.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative markdown file paths to their contents.
        """
        owner, repo = self._split(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/contents/.context",
                headers=self._headers(),
            )
            if resp.status_code == 404:
                return {}
            resp.raise_for_status()
            items = resp.json()
            await _collect_github_md_files(client, items, self._headers(), ".context", result)
        return result

    async def fetch_source_bundle(self, repo_id: str) -> Optional[str]:
        """Fetch the content of ``.context/BUNDLE.md``, or ``None``.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (str) The contents of ``BUNDLE.md``, or ``None`` if it does not exist.
        """
        owner, repo = self._split(repo_id)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/contents/.context/BUNDLE.md",
                headers=self._headers(),
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            download_url = data.get("download_url")
            if not download_url:
                return None
            raw = await client.get(download_url, headers=self._headers())
            return raw.text

    async def fetch_source_files(self, repo_id: str) -> dict[str, str]:
        """Fetch source code files via the Git Trees API.

        Capped at 200 files.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative source file paths to their contents.
        """
        owner, repo = self._split(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
                headers=self._headers(),
            )
            resp.raise_for_status()
            tree = resp.json().get("tree", [])
            candidates = [
                item for item in tree if item.get("type") == "blob" and _has_source_extension(item.get("path", ""))
            ][:_MAX_SOURCE_FILES]
            for item in candidates:
                path = item["path"]
                raw_resp = await client.get(
                    f"{self._base_url}/repos/{owner}/{repo}/contents/{path}",
                    headers=self._headers(),
                )
                if raw_resp.status_code == 200:
                    data = raw_resp.json()
                    if data.get("encoding") == "base64":
                        result[path] = base64.b64decode(data["content"].replace("\n", "")).decode(
                            "utf-8", errors="replace"
                        )
        return result

    async def write_file(
        self, repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Create or update *path* in the repository.

        Writes to *branch* if given, otherwise the repository's default
        branch.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :param path: (str) The file path to write, relative to the repository root.
        :param content: (str) The new full contents of the file.
        :param message: (str) The commit message describing the write.
        :param branch: (str) Target branch. Falls back to the repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the API returns a non-success status.
        """
        owner, repo = self._split(repo_id)
        target_branch = branch or await self.get_default_branch(repo_id)
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        async with httpx.AsyncClient() as client:
            # Check for existing file SHA on the target branch specifically —
            # without ?ref= this would always read the default branch's SHA,
            # which is wrong once writes can target other branches.
            sha: Optional[str] = None
            check = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self._headers(),
                params={"ref": target_branch},
            )
            if check.status_code == 200:
                sha = check.json().get("sha")

            payload: dict = {"message": message, "content": encoded, "branch": target_branch}
            if sha:
                payload["sha"] = sha

            resp = await client.put(
                f"{self._base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self._headers(),
                json=payload,
            )
            if not resp.is_success:
                raise RepositoryError(f"GitHub write_file failed ({resp.status_code}): {resp.text}")

    async def create_branch(self, repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """Create *new_branch* pointing at the tip of *from_branch* (or the default branch).

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :param new_branch: (str) The name of the branch to create.
        :param from_branch: (str) The branch to base the new branch on. Falls back to the
            repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the base ref cannot be resolved or the
            API returns a non-success status when creating the new ref.
        """
        owner, repo = self._split(repo_id)
        base = from_branch or await self.get_default_branch(repo_id)
        async with httpx.AsyncClient() as client:
            ref_resp = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/git/ref/heads/{base}",
                headers=self._headers(),
            )
            if not ref_resp.is_success:
                raise RepositoryError(
                    f"GitHub create_branch failed to resolve base branch '{base}' "
                    f"({ref_resp.status_code}): {ref_resp.text}"
                )
            sha = ref_resp.json()["object"]["sha"]

            resp = await client.post(
                f"{self._base_url}/repos/{owner}/{repo}/git/refs",
                headers=self._headers(),
                json={"ref": f"refs/heads/{new_branch}", "sha": sha},
            )
            if not resp.is_success:
                raise RepositoryError(f"GitHub create_branch failed ({resp.status_code}): {resp.text}")

    async def get_default_branch(self, repo_id: str) -> str:
        """Return the default branch for *repo_id*, falling back to env / ``"main"``.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (str) The repository's default branch name, or the configured/``"main"`` fallback.
        """
        owner, repo = self._split(repo_id)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self._base_url}/repos/{owner}/{repo}",
                    headers=self._headers(),
                )
                if resp.status_code == 200:
                    return resp.json().get("default_branch", self._default_branch_fallback)
        except Exception:
            pass
        return self._default_branch_fallback

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """List repositories accessible to the configured token.

        If *org* is set, lists repositories for that organisation.  Otherwise
        lists the authenticated user's repositories.

        :param org: (str) Optional organisation name to list repositories for.
        :return: (list) The accessible ``RepositoryInfo`` entries.
        """
        async with httpx.AsyncClient() as client:
            if org:
                url = f"{self._base_url}/orgs/{org}/repos?per_page=100"
            else:
                url = f"{self._base_url}/user/repos?per_page=100"
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return [_repo_info_from_github(r) for r in resp.json()]


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _has_source_extension(path: str) -> bool:
    """Return True if *path* ends with a recognised source extension."""
    return any(path.endswith(ext) for ext in _SOURCE_EXTENSIONS)


async def _collect_github_md_files(
    client: httpx.AsyncClient,
    items: list,
    headers: dict,
    prefix: str,
    result: dict,
) -> None:
    """Recursively collect .md files from a GitHub contents listing."""
    for item in items:
        if item.get("type") == "file" and item["name"].endswith(".md"):
            download_url = item.get("download_url")
            if download_url:
                raw = await client.get(download_url, headers=headers)
                if raw.status_code == 200:
                    rel_path = item["path"].removeprefix(prefix + "/")
                    result[rel_path] = raw.text
        elif item.get("type") == "dir":
            sub = await client.get(item["url"], headers=headers)
            if sub.status_code == 200:
                await _collect_github_md_files(client, sub.json(), headers, prefix, result)


def _repo_info_from_github(data: dict) -> RepositoryInfo:
    """Build a :class:`RepositoryInfo` from a GitHub API repository object."""
    return RepositoryInfo(
        identifier=data.get("full_name", ""),
        name=data.get("name", ""),
        description=data.get("description") or "",
        indexed=False,
    )
</file>

<file path="src/mcp_project_context_server/integrations/repository/local/client.py">
"""Local filesystem repository provider implementation."""

import asyncio
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

from mcp_project_context_server.integrations.repository.base import RepositoryInfo

logger = logging.getLogger(__name__)

_SOURCE_EXTENSIONS: frozenset[str] = frozenset({".py", ".ts", ".js", ".go", ".rs", ".cs", ".java", ".rb", ".php"})
_SKIP_DIRS: frozenset[str] = frozenset({".git", "node_modules", ".venv", "__pycache__", "dist", "build"})
_MAX_SOURCE_FILES = 500


class LocalRepositoryProvider:
    """Repository provider that reads from the local filesystem.

    ``repo_id`` for all methods is always a filesystem path (str or Path).
    """

    def __init__(self) -> None:
        """Initialize the provider, reading PROJECT_PATH from the environment."""
        self._project_path: str = os.getenv("PROJECT_PATH", "")

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "local"

    @staticmethod
    async def fetch_context_files(repo_id: str) -> dict[str, str]:
        """Read all .md files from ``<repo_id>/.context/`` recursively.

        Returns a dict keyed by POSIX relative paths.  Returns an empty dict if
        the ``.context/`` directory does not exist.

        :param repo_id: (str) Filesystem path to the project root.
        :return: (dict) A mapping of POSIX-style relative markdown file paths to their contents.
        """
        logger.debug(f"Executing 'fetch_context_files' with the arguments repo_id: {repo_id}")
        context_dir = Path(repo_id) / ".context"
        if not context_dir.is_dir():
            return {}
        result: dict[str, str] = {}
        for md_file in context_dir.rglob("*.md"):
            key = md_file.relative_to(context_dir).as_posix()
            result[key] = md_file.read_text(encoding="utf-8")
        return result

    @staticmethod
    async def fetch_source_bundle(repo_id: str) -> Optional[str]:
        """Return the content of ``<repo_id>/.context/BUNDLE.md``, or None.

        :param repo_id: (str) Filesystem path to the project root.
        :return: (str) The contents of ``BUNDLE.md``, or ``None`` if it does not exist.
        """
        logger.debug(f"Executing 'fetch_source_bundle' with the arguments repo_id: {repo_id}")
        bundle = Path(repo_id) / ".context" / "BUNDLE.md"
        if bundle.is_file():
            return bundle.read_text(encoding="utf-8")
        return None

    @staticmethod
    async def fetch_source_files(repo_id: str) -> dict[str, str]:
        """Return source code files under ``repo_id``, skipping common non-source dirs.

        Capped at ``_MAX_SOURCE_FILES`` (500) entries.  Keys are POSIX paths
        relative to ``repo_id``.

        :param repo_id: (str) Filesystem path to the project root.
        :return: (dict) A mapping of POSIX-style relative source file paths to their contents.
        """
        logger.debug(f"Executing 'fetch_source_files' with the arguments repo_id: {repo_id}")
        root = Path(repo_id)
        result: dict[str, str] = {}
        for file_path in _walk_source_files(root):
            if len(result) >= _MAX_SOURCE_FILES:
                break
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            key = file_path.relative_to(root).as_posix()
            result[key] = content
        return result

    @staticmethod
    async def write_file(
        repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Write ``content`` to ``<repo_id>/<path>``, creating parent directories.

        ``message`` and ``branch`` are ignored for the local provider (no
        commit is made; writes always land on whatever is checked out).

        :param repo_id: (str) Filesystem path to the project root.
        :param path: (str) The file path to write, relative to ``repo_id``.
        :param content: (str) The new full contents of the file.
        :param message: (str) Ignored by the local provider.
        :param branch: (str) Ignored by the local provider.
        :return: (None) This method does not return a value.
        """
        logger.debug(f"Executing 'write_file' with the arguments repo_id: {repo_id}, path: {path}, content: {content}, message: {message}, branch: {branch}")
        target = Path(repo_id) / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    @staticmethod
    async def create_branch(repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """No-op: the local provider writes directly to disk regardless of branch.

        :param repo_id: (str) Filesystem path to the project root.
        :param new_branch: (str) Ignored by the local provider.
        :param from_branch: (str) Ignored by the local provider.
        :return: (None) This method does not return a value.
        """
        logger.debug(f"Executing 'create_branch' with the arguments repo_id: {repo_id}, new_branch: {new_branch}, from_branch: {from_branch}")
        return None

    @staticmethod
    async def get_default_branch(repo_id: str) -> str:
        """Return the current git branch for the repository, falling back to ``"main"``.

        :param repo_id: (str) Filesystem path to the project root.
        :return: (str) The current git branch name, or ``"main"`` if it cannot be determined.
        """
        logger.debug(f"Executing 'get_default_branch' with the arguments repo_id: {repo_id}")

        def _run_git() -> str:
            result = subprocess.run(
                ["git", "-C", str(repo_id), "symbolic-ref", "--short", "HEAD"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "main"

        return await asyncio.to_thread(_run_git)

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """Return a single-element list for the project path from ``PROJECT_PATH``.

        Returns an empty list if ``PROJECT_PATH`` is not set.  ``org`` is ignored
        for the local provider.

        :param org: (str) Ignored by the local provider.
        :return: (list) A single-element list describing the ``PROJECT_PATH`` project,
            or an empty list if ``PROJECT_PATH`` is not set.
        """
        logger.debug(f"Executing 'list_repositories' with the arguments org: {org}")
        if not self._project_path:
            return []
        p = Path(self._project_path)
        return [
            RepositoryInfo(
                identifier=self._project_path,
                name=p.name,
                description="",
                indexed=False,
            )
        ]


def _walk_source_files(root: Path):
    """Yield source files under *root*, skipping known non-source directories."""
    logger.debug(f"Executing '_walk_source_files' with the arguments org: {root}")
    for entry in root.iterdir():
        if entry.is_dir():
            if entry.name in _SKIP_DIRS:
                continue
            yield from _walk_source_files(entry)
        elif entry.is_file() and entry.suffix in _SOURCE_EXTENSIONS:
            yield entry
</file>

<file path="src/mcp_project_context_server/tools/list_repositories.py">
"""Tool: list_repositories — list accessible repositories via the configured provider."""
import logging

from mcp import types
from mcp.types import CallToolResult, TextContent

from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import (
    get_repository_provider,
    validate_repo_access,
)

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> CallToolResult:
    """Handle the ``list_repositories`` tool call.

    :param arguments: (dict) Tool input dict. Optional key ``"org"`` filters by
        organisation/group name.
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item.
    """
    org = arguments.get("org")
    try:
        provider = get_repository_provider()
        repos = await provider.list_repositories(org=org)
    except Exception as exc:
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Error listing repositories: {exc}")])

    # Only surface repositories the allowlist actually permits — in
    # multi-tenant mode the provider may still be able to see repos outside
    # APPROVED_ORGS/APPROVED_REPOS (e.g. via a broadly-scoped API token).
    allowed_repos = []
    for r in repos:
        try:
            validate_repo_access(r.identifier)
        except RepositoryError:
            continue
        allowed_repos.append(r)
    repos = allowed_repos

    if not repos:
        return types.CallToolResult(content=[types.TextContent(type="text", text="No repositories found.")])
    repos_structured_results = {}
    repos_content_results = []
    for r in repos:
        status = "indexed" if r.indexed else "not indexed"
        last_indexed = f" (last indexed: {r.last_indexed})" if r.last_indexed else ""
        repos_content_results.append(types.TextContent(type="text", text=f"- **{r.identifier}** — {r.description or 'no description'} [{status}{last_indexed}]"))
        repos_structured_results[r.identifier] = {
            "identifier": types.TextContent(type="text", text=r.identifier),
            "description": types.TextContent(type="text", text=r.description or 'no description'),
            "status": types.TextContent(type="text", text=status),
            "last_indexed": types.TextContent(type="text", text=last_indexed),
        }
    return types.CallToolResult(content=repos_content_results, structuredContent=repos_structured_results)
</file>

<file path="src/mcp_project_context_server/helpers/context.py">
"""Shared helpers for .context/ directory resolution and file reading."""
import logging
import re
from pathlib import Path

from mcp_project_context_server.integrations.repository.base import normalize_repo_identifier

logger = logging.getLogger(__name__)


def find_context_dir(project_path: str | Path) -> Path | None:
    """Walk up from project_path to find a .context/ directory.

    :param project_path: (str) The project root or subdirectory/file path to start searching from.
    :return: (Path) The first ``.context/`` directory found while walking up from
        ``project_path``, or ``None`` if none exists in any parent.
    """
    logger.debug(f"Executing 'find_context_dir' with the argument project_path: {project_path}")
    p = Path(project_path).resolve()
    for candidate in [p, *p.parents]:
        ctx = candidate / ".context"
        if ctx.is_dir():
            return ctx
    return None


def collection_name_for(context_dir: Path) -> str:
    """Derive a stable ChromaDB collection name from the project root.

    Always based on context_dir.parent so it is consistent regardless of
    whether the caller passed a project root, a subdirectory, or a file path.

    :param context_dir: (Path) The project's ``.context/`` directory.
    :return: (str) A sanitized, ChromaDB-safe collection name derived from the
        parent project directory's name, truncated to 63 characters.
    """
    project_name = context_dir.parent.name
    return f"ctx_{project_name}".replace("-", "_").replace(" ", "_")[:63]


def collection_name_for_repo_id(repo_id: str) -> str:
    """Derive a stable ChromaDB collection name from a remote repo identifier.

    Mirrors :func:`collection_name_for`'s sanitization, driven by the
    normalised ``owner/repo`` form so the same collection name is produced
    whether the caller passes a short identifier or a full URL.

    :param repo_id: (str) A short ``owner/repo`` identifier or a full remote repository URL.
    :return: (str) A sanitized, ChromaDB-safe collection name derived from the
        normalized repo identifier, truncated to 63 characters.
    """
    normalized = normalize_repo_identifier(repo_id)
    return f"ctx_{normalized}".replace("-", "_").replace(" ", "_").replace("/", "_")[:63]


def read_context_files(context_dir: Path) -> dict[str, str]:
    """Read all markdown files from .context/ into a dict.

    Keys use POSIX-style forward slashes (Path.as_posix()) so that ChromaDB
    document IDs and metadata are identical on Windows and Linux.

    :param context_dir: (Path) The project's ``.context/`` directory to read markdown files from.
    :return: (dict) A mapping of POSIX-style relative file paths to their markdown file contents.
    """
    return {
        md_file.relative_to(context_dir).as_posix(): md_file.read_text(encoding="utf-8")
        for md_file in context_dir.rglob("*.md")
    }


_SHORT_IDENTIFIER_RE = re.compile(r"^[\w.-]+/[\w.-]+$")


def resolve_project_path(raw: str) -> tuple[str, bool]:
    """Resolve a raw project path string and determine whether it is remote.

    Returns a ``(resolved_path, is_remote)`` tuple.

    * If *raw* starts with ``http://`` or ``https://``: ``is_remote=True``.
    * If *raw* matches the ``owner/repo`` short identifier pattern
      (``^[\\w.-]+/[\\w.-]+$``): ``is_remote=True``.
    * Otherwise: ``is_remote=False`` (filesystem path — existing behaviour).

    :param raw: (str) The raw project path or identifier supplied by the caller.
    :return: (tuple) A two-element tuple ``(resolved_path, is_remote)``.
    """
    logger.debug(f"Executing 'resolve_project_path' with the argument raw: {raw}")
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw, True
    if _SHORT_IDENTIFIER_RE.match(raw):
        return raw, True
    return raw, False
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/base.py">
"""EmbeddingProvider Protocol — the provider abstraction boundary for embeddings.

All embedding providers must implement this Protocol so that the rest of the
codebase can depend on the abstraction rather than any concrete provider.

Usage
-----
Import the protocol for type annotations::

    from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

Obtain a concrete instance from the registry::

    from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider
    provider = get_embedding_provider()
"""
import logging
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol that all embedding provider implementations must satisfy.

    Implementors should be importable without triggering any network calls,
    file I/O, or expensive initialization — those should be deferred to the
    first call to ``embed_chunk()``.
    """
    @property
    def provider_name(self) -> str:
        """Short identifier for the provider, e.g. ``"ollama"``, ``"voyage"``."""
        ...

    @property
    def model_name(self) -> str:
        """Name of the embedding model in use, e.g. ``"nomic-embed-text"``."""
        ...

    @property
    def max_chars(self) -> int:
        """Approximate maximum input length in characters for this model.

        Used by the chunking layer to stay within the provider's context window.
        This is an advisory value — providers may silently truncate longer inputs.
        """
        ...

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed a single text string and return the embedding vector.

        :param text: (str) The text to embed. May be up to ``max_chars`` in length.
        :return: (list) A list of floats representing the embedding vector.
        :raises EmbeddingError: If the provider returns an error or is unreachable.
        """
        ...
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/openai/client.py">
"""OpenAI embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`OPENAI_API_KEY`
    API key for the OpenAI service.  **Required.**

`OPENAI_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `text-embedding-3-small`.
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_MODEL: str = "text-embedding-3-small"
# text-embedding-3-small: 8191 token context; conservative character limit
_MAX_CHARS: int = 24_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the OpenAI Embeddings API.

    The `openai` package is imported lazily inside `embed_chunk()` so that the
    provider can be imported without requiring the package to be installed.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If `OPENAI_API_KEY` is not set.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")
        self._api_key: str = api_key
        self._model: str = os.getenv("OPENAI_EMBED_MODEL", _DEFAULT_MODEL)

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "openai"

    @property
    def model_name(self) -> str:
        """Name of the embedding model in use."""
        return self._model

    @property
    def max_chars(self) -> int:
        """Approximate maximum input length in characters."""
        return _MAX_CHARS

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured OpenAI embedding model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the OpenAI API returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            from openai import AsyncOpenAI  # lazy import

            client = AsyncOpenAI(api_key=self._api_key)
            response = await asyncio.wait_for(
                client.embeddings.create(model=self._model, input=text),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(response.data[0].embedding)
        except Exception as exc:
            raise EmbeddingError(f"OpenAI embedding failed (model={self._model}): {exc}") from exc
</file>

<file path="src/mcp_project_context_server/integrations/repository/registry.py">
"""Repository provider registry — factory driven by the ``REPO_PROVIDER`` env var.

Design rules
------------
* Defaults to ``"local"`` when ``REPO_PROVIDER`` is not set.
* **Fail fast** if the value is unrecognised.
* The returned instance is cached after the first call.
* Multi-tenant mode is activated by ``REPO_MULTI_TENANT=true``.

Usage
-----
::

    from mcp_project_context_server.integrations.repository.registry import (
        get_repository_provider,
        validate_repo_access,
    )

    provider = get_repository_provider()
    validate_repo_access("owner/repo")

Supported ``REPO_PROVIDER`` values
------------------------------------
``local``
    Local filesystem provider.

``github``
    GitHub / GitHub Enterprise.

``gitlab``
    GitLab / self-hosted GitLab.

``gitea``
    Self-hosted Gitea.  Requires ``REPO_BASE_URL``.

Multi-tenant mode (``REPO_MULTI_TENANT=true``)
----------------------------------------------
At least one of ``APPROVED_ORGS`` or ``APPROVED_REPOS`` must be set.
``validate_repo_access(repo_id)`` raises :exc:`RepositoryError` if the
repo identifier is not in any approved list.
"""
import logging
import os
from typing import Optional

from mcp_project_context_server.integrations.repository.base import RepositoryError, RepositoryProvider

logger = logging.getLogger(__name__)

_SUPPORTED_PROVIDERS: frozenset[str] = frozenset({"local", "github", "gitlab", "gitea"})

_provider_instance: Optional[RepositoryProvider] = None

# Multi-tenant state — populated lazily alongside the provider singleton.
_multi_tenant_enabled: bool = False
_approved_orgs: frozenset[str] = frozenset()
_approved_repos: frozenset[str] = frozenset()


def get_repository_provider() -> RepositoryProvider:
    """Return the configured repository provider singleton.

    :return: (RepositoryProvider) The repository provider instance selected by
        the ``REPO_PROVIDER`` environment variable (defaults to ``"local"``).
    :raises EnvironmentError: If ``REPO_PROVIDER`` is set to an unrecognised value,
        or if multi-tenant mode is active but no approved orgs/repos are
        configured.
    """
    global _provider_instance, _multi_tenant_enabled, _approved_orgs, _approved_repos

    if _provider_instance is not None:
        return _provider_instance

    provider_name = os.getenv("REPO_PROVIDER", "local").strip().lower()

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported REPO_PROVIDER value '{provider_name}'. "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    # Multi-tenant setup
    _multi_tenant_enabled = os.getenv("REPO_MULTI_TENANT", "false").strip().lower() == "true"
    if _multi_tenant_enabled:
        orgs_raw = os.getenv("APPROVED_ORGS", "").strip()
        repos_raw = os.getenv("APPROVED_REPOS", "").strip()
        if not orgs_raw and not repos_raw:
            raise EnvironmentError(
                "REPO_MULTI_TENANT=true requires at least one of APPROVED_ORGS or " "APPROVED_REPOS to be set."
            )
        _approved_orgs = frozenset(o.strip() for o in orgs_raw.split(",") if o.strip())
        _approved_repos = frozenset(r.strip() for r in repos_raw.split(",") if r.strip())

    _provider_instance = _build_provider(provider_name)
    return _provider_instance


def _build_provider(provider_name: str) -> RepositoryProvider:
    """Instantiate and return the provider for *provider_name*."""
    if provider_name == "local":
        from mcp_project_context_server.integrations.repository.local.client import (
            LocalRepositoryProvider,
        )

        return LocalRepositoryProvider()

    if provider_name == "github":
        from mcp_project_context_server.integrations.repository.github.client import (
            GitHubRepositoryProvider,
        )

        return GitHubRepositoryProvider()

    if provider_name == "gitlab":
        from mcp_project_context_server.integrations.repository.gitlab.client import (
            GitLabRepositoryProvider,
        )

        return GitLabRepositoryProvider()

    if provider_name == "gitea":
        from mcp_project_context_server.integrations.repository.gitea.client import (
            GiteaRepositoryProvider,
        )

        return GiteaRepositoryProvider()

    # Should never reach here — guarded by the caller.
    raise EnvironmentError(f"Internal error: unhandled provider '{provider_name}'")  # pragma: no cover


def validate_repo_access(repo_id: str) -> None:
    """Raise :exc:`RepositoryError` if *repo_id* is not in the approved allowlist.

    In single-tenant mode (``REPO_MULTI_TENANT`` unset or ``false``) this is
    always a no-op.

    :param repo_id: (str) The ``owner/repo`` (or equivalent) identifier to validate.
    :return: (None) This function does not return a value.
    :raises RepositoryError: If multi-tenant mode is active, and *repo_id* is not in
        the approved orgs or repos allowlists.
    """
    # Ensure the multi-tenant flags have been populated even if this is the
    # first call into the registry for this process (lazy singleton init).
    get_repository_provider()

    if not _multi_tenant_enabled:
        return

    # Check explicit repo allowlist
    if repo_id in _approved_repos:
        return

    # Check org membership — repo_id is expected to be "org/repo"
    if "/" in repo_id:
        org = repo_id.split("/", 1)[0]
        if org in _approved_orgs:
            return

    raise RepositoryError(
        f"Access to repository '{repo_id}' is not permitted. " "Check APPROVED_ORGS and APPROVED_REPOS configuration."
    )


def reset_provider_for_testing() -> None:
    """Reset the cached provider singleton and multi-tenant state.

    **For use in tests only.**  Call this in test teardown to prevent provider
    state from leaking between test cases.

    :return: (None) This function does not return a value.
    """
    global _provider_instance, _multi_tenant_enabled, _approved_orgs, _approved_repos
    _provider_instance = None
    _multi_tenant_enabled = False
    _approved_orgs = frozenset()
    _approved_repos = frozenset()
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/cohere/client.py">
"""Cohere embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`COHERE_API_KEY`
    API key for the Cohere service.  **Required.**

`COHERE_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `embed-english-v3.0`.
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_MODEL: str = "embed-english-v3.0"
# embed-english-v3.0: 512 token context; conservative character limit
_MAX_CHARS: int = 20_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class CohereEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the Cohere Embed API.

    The `cohere` package is imported lazily inside `embed_chunk()` so that the
    provider can be imported without requiring the package to be installed.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If `COHERE_API_KEY` is not set.
        """
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise EnvironmentError("COHERE_API_KEY environment variable is not set.")
        self._api_key: str = api_key
        self._model: str = os.getenv("COHERE_EMBED_MODEL", _DEFAULT_MODEL)

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "cohere"

    @property
    def model_name(self) -> str:
        """Name of the embedding model in use."""
        return self._model

    @property
    def max_chars(self) -> int:
        """Approximate maximum input length in characters."""
        return _MAX_CHARS

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured Cohere embedding model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the Cohere API returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            import cohere  # lazy import

            client = cohere.AsyncClientV2(api_key=self._api_key)
            response = await asyncio.wait_for(
                client.embed(
                    texts=[text],
                    model=self._model,
                    input_type="search_document",
                    embedding_types=["float"],
                ),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(response.embeddings.float_[0])
        except Exception as exc:
            raise EmbeddingError(f"Cohere embedding failed (model={self._model}): {exc}") from exc
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/google/client.py">
"""Google Gemini API embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`GOOGLE_API_KEY`
    API key for the Google Generative AI service.  **Required.**

`GOOGLE_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `gemini-embedding-2`.
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_MODEL: str = "gemini-embedding-2"
# gemini-embedding-2: 2048 token context; conservative character limit
_MAX_CHARS: int = 24_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class GoogleEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the Google Generative AI (Gemini) API.

    The `google.generativeai` package is imported lazily inside `embed_chunk()` so
    that the provider can be imported without requiring the package to be installed.
    Because the `genai.embed_content` function is synchronous, it is wrapped with
    `asyncio.to_thread` to avoid blocking the event loop.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If `GOOGLE_API_KEY` is not set.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY environment variable is not set.")
        self._api_key: str = api_key
        self._model: str = os.getenv("GOOGLE_EMBED_MODEL", _DEFAULT_MODEL)

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "google"

    @property
    def model_name(self) -> str:
        """Name of the embedding model in use."""
        return self._model

    @property
    def max_chars(self) -> int:
        """Approximate maximum input length in characters."""
        return _MAX_CHARS

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured Google Generative AI embedding model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the Google API returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            import google.generativeai as genai  # lazy import

            genai.configure(api_key=self._api_key)
            result = await asyncio.wait_for(
                asyncio.to_thread(genai.embed_content, model=self._model, content=text),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(result["embedding"])
        except Exception as exc:
            raise EmbeddingError(f"Google embedding failed (model={self._model}): {exc}") from exc
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/vertexai/client.py">
"""Google Vertex AI embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`VERTEXAI_PROJECT`
    Google Cloud project ID.  **Required.**

`VERTEXAI_LOCATION`
    Google Cloud region, e.g. `us-central1`.  **Required.**

`VERTEXAI_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `text-embedding-004`.
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_MODEL: str = "text-embedding-004"
# Conservative character limit matching the model's context window
_MAX_CHARS: int = 24_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class GoogleVertexEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the Google Vertex AI SDK.

    The `vertexai` package is imported lazily inside `_get_embedding_model()`
    so that the provider can be constructed without requiring the package to
    be installed unless it is actually used. The `TextEmbeddingModel` is
    resolved on first use and cached for subsequent calls.

    The SDK is configured with `api_transport="rest"` to force plain HTTP
    instead of gRPC. gRPC's C-core polling engine (used by both its
    synchronous and `grpc.aio` async clients) can deadlock when it shares a
    process with asyncio's `ProactorEventLoop` — the loop this server
    requires on Windows for stdio subprocess support. REST has no such
    conflict, so the embedding call is made with the synchronous
    `get_embeddings()` wrapped in `asyncio.to_thread`, same as every other
    HTTP-based provider in this package.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If `VERTEXAI_PROJECT` or `VERTEXAI_LOCATION` are not set.
        """
        project = os.getenv("VERTEXAI_PROJECT")
        if not project:
            raise EnvironmentError("VERTEXAI_PROJECT environment variable is not set.")
        location = os.getenv("VERTEXAI_LOCATION")
        if not location:
            raise EnvironmentError("VERTEXAI_LOCATION environment variable is not set.")
        self._project: str = project
        self._location: str = location
        self._model: str = os.getenv("VERTEXAI_EMBED_MODEL", _DEFAULT_MODEL)
        self._embedding_model = None

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "vertexai"

    @property
    def model_name(self) -> str:
        """Name of the embedding model in use."""
        return self._model

    @property
    def max_chars(self) -> int:
        """Approximate maximum input length in characters."""
        return _MAX_CHARS

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    def _get_embedding_model(self):
        """Resolve and cache the `TextEmbeddingModel`, initializing the SDK on first use.

        Configures the SDK to use REST rather than gRPC — see the class
        docstring for why gRPC is unsafe in this server's event loop.
        """
        if self._embedding_model is None:
            import vertexai  # lazy import
            from vertexai.language_models import TextEmbeddingModel  # lazy import

            vertexai.init(project=self._project, location=self._location, api_transport="rest")
            self._embedding_model = TextEmbeddingModel.from_pretrained(self._model)
        return self._embedding_model

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured Vertex AI embedding model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the Vertex AI SDK returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            model = self._get_embedding_model()
            embeddings = await asyncio.wait_for(
                asyncio.to_thread(model.get_embeddings, [text]),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(embeddings[0].values)
        except Exception as exc:
            raise EmbeddingError(
                f"Google Vertex AI embedding failed (project={self._project}, model={self._model}): {exc}"
            ) from exc
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/voyage/client.py">
"""Voyage AI embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`VOYAGE_API_KEY`
    API key for the Voyage AI service.  **Required.**

`VOYAGE_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `voyage-code-3`.
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_MODEL: str = "voyage-code-3"
# voyage-code-3 context ≈ 32k tokens; conservative character limit
_MAX_CHARS: int = 24_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class VoyageEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the Voyage AI API.

    The `voyageai` package is imported lazily inside `embed_chunk()` so that the
    provider can be imported without requiring the package to be installed.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If `VOYAGE_API_KEY` is not set.
        """
        api_key = os.getenv("VOYAGE_API_KEY")
        if not api_key:
            raise EnvironmentError("VOYAGE_API_KEY environment variable is not set.")
        self._api_key: str = api_key
        self._model: str = os.getenv("VOYAGE_EMBED_MODEL", _DEFAULT_MODEL)

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "voyage"

    @property
    def model_name(self) -> str:
        """Name of the embedding model in use."""
        return self._model

    @property
    def max_chars(self) -> int:
        """Approximate maximum input length in characters."""
        return _MAX_CHARS

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured Voyage AI model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the Voyage AI API returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            import voyageai  # lazy import

            client = voyageai.AsyncClient(api_key=self._api_key)
            result = await asyncio.wait_for(
                client.embed([text], model=self._model, input_type="document"),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(result.embeddings[0])
        except Exception as exc:
            raise EmbeddingError(f"Voyage AI embedding failed (model={self._model}): {exc}") from exc
</file>

<file path="src/mcp_project_context_server/integrations/vectorstore/registry.py">
"""Vector store provider registry — factory driven by ``VECTOR_STORE_PROVIDER`` env var.

Design rules
------------
* ``chroma-local`` is the **default** when ``VECTOR_STORE_PROVIDER`` is not set.
  This preserves backward compatibility for local developer setups.
* Unknown values raise ``EnvironmentError`` immediately at startup (fail-fast).
* The provider singleton is cached after the first call.

Supported ``VECTOR_STORE_PROVIDER`` values
------------------------------------------
``chroma-local`` *(default)*
    Local ChromaDB PersistentClient.  Requires ``CHROMA_DIR`` (optional,
    defaults to ``~/.mcp-data/chroma``).

``chroma-http``
    Remote ChromaDB HTTP server.  Requires ``CHROMA_HOST``, ``CHROMA_PORT``
    (optional, defaults to ``localhost:8000``).  Optional: ``CHROMA_API_KEY``.

``pgvector``
    PostgreSQL with the pgvector extension.  Requires
    ``PGVECTOR_CONNECTION_STRING``.

``gcp-vector-search``
    Google Cloud Vertex AI Vector Search against a pre-provisioned Index and
    IndexEndpoint (ADR-00023; this provider does not create or deploy GCP
    infrastructure).  Requires ``GCP_VECTOR_SEARCH_PROJECT``,
    ``GCP_VECTOR_SEARCH_LOCATION``, ``GCP_VECTOR_SEARCH_INDEX_ID``,
    ``GCP_VECTOR_SEARCH_INDEX_ENDPOINT_ID``, and
    ``GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID``.  Optional:
    ``GCP_VECTOR_SEARCH_FIRESTORE_COLLECTION``.

Incompatible combinations
-------------------------
``EMBED_PROVIDER=vertexai`` cannot be combined with ``chroma-local`` or
``chroma-http``: the two SDKs deadlock when loaded into the same process on
Windows.  Use ``VECTOR_STORE_PROVIDER=pgvector`` with Vertex AI instead.
"""
import logging
import os
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any

from mcp_project_context_server.indexing.indexer import run_index_pipeline
from mcp_project_context_server.integrations.vectorstore.base import VectorStoreProvider
from mcp_project_context_server.integrations.vectorstore.chroma_http.client import ChromaHttpVectorStoreProvider
from mcp_project_context_server.integrations.vectorstore.chroma_local.client import ChromaLocalVectorStoreProvider
from mcp_project_context_server.integrations.vectorstore.gcp_vector_search.client import GcpVectorSearchProvider
from mcp_project_context_server.integrations.vectorstore.pgvector.client import PgVectorStoreProvider

logger = logging.getLogger(__name__)

_SUPPORTED_PROVIDERS: frozenset[str] = frozenset({"chroma-local", "chroma-http", "pgvector", "gcp-vector-search"})
_DEFAULT_PROVIDER: str = "chroma-local"

# EMBED_PROVIDER values that cannot share a process with the given
# VECTOR_STORE_PROVIDER.  The vertexai SDK and the chromadb client (both of
# which pull in native/C-extension dependencies) deadlock when imported into
# the same Windows process -- this is an in-process native-library conflict,
# not a credentials or network issue, so it cannot be worked around by
# retrying or adding timeouts.
INCOMPATIBLE_EMBED_PROVIDERS_BY_VECTOR_STORE: dict[str, frozenset[str]] = {
    "chroma-local": frozenset({"vertexai"}),
    "chroma-http": frozenset({"vertexai"}),
}

IndexFn = Callable[[str | Path], Coroutine[Any, Any, str]]


def _assert_compatible_providers(vector_store_provider_name: str) -> None:
    """Raise if the configured EMBED_PROVIDER cannot be used with *vector_store_provider_name*."""
    embed_provider_name = os.getenv("EMBED_PROVIDER", "").strip().lower()
    incompatible = INCOMPATIBLE_EMBED_PROVIDERS_BY_VECTOR_STORE.get(vector_store_provider_name, frozenset())
    if embed_provider_name in incompatible:
        raise EnvironmentError(
            f"EMBED_PROVIDER='{embed_provider_name}' cannot be used with "
            f"VECTOR_STORE_PROVIDER='{vector_store_provider_name}': these two SDKs "
            "deadlock when loaded into the same process on Windows.  Use "
            "VECTOR_STORE_PROVIDER=pgvector with EMBED_PROVIDER=vertexai instead."
        )


def get_vector_store() -> VectorStoreProvider:
    """Return the configured vector store provider singleton.

    :return: (VectorStoreProvider) The vector store provider instance selected by
        ``VECTOR_STORE_PROVIDER`` (defaults to ``"chroma-local"``).
    :raises EnvironmentError: If ``VECTOR_STORE_PROVIDER`` is set to an unrecognised value,
        if the selected provider is missing a required env var, or if the
        configured ``EMBED_PROVIDER`` is incompatible with it.
    :raises ImportError: If the required package for the selected provider is not installed.
    """
    provider_name = os.getenv("VECTOR_STORE_PROVIDER", _DEFAULT_PROVIDER).strip().lower()

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported VECTOR_STORE_PROVIDER value '{provider_name}'.  "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    _assert_compatible_providers(provider_name)

    return _build_provider(provider_name)


def _build_provider(provider_name: str) -> VectorStoreProvider:
    """Instantiate and return the provider for *provider_name*."""
    if provider_name == "chroma-local":
        from mcp_project_context_server.integrations.vectorstore.chroma_local.client import (
            ChromaLocalVectorStoreProvider,
        )

        return ChromaLocalVectorStoreProvider()

    if provider_name == "chroma-http":
        from mcp_project_context_server.integrations.vectorstore.chroma_http.client import (
            ChromaHttpVectorStoreProvider,
        )

        return ChromaHttpVectorStoreProvider()

    if provider_name == "pgvector":
        from mcp_project_context_server.integrations.vectorstore.pgvector.client import (
            PgVectorStoreProvider,
        )

        return PgVectorStoreProvider()

    if provider_name == "gcp-vector-search":
        from mcp_project_context_server.integrations.vectorstore.gcp_vector_search.client import (
            GcpVectorSearchProvider,
        )

        return GcpVectorSearchProvider()

    raise EnvironmentError(f"Internal error: unhandled provider '{provider_name}'")  # pragma: no cover


def get_indexer() -> IndexFn:
    """Return the ``index_project_context`` callable for the configured provider.

    Each vector store provider owns its indexer in
    ``integrations/vectorstore/{provider}/indexer.py``.  This function resolves
    the correct one based on ``VECTOR_STORE_PROVIDER``, mirroring the dispatch
    logic of :func:`get_vector_store`.

    :return: (Callable) An async callable that indexes a project path and
        returns a human-readable summary string.
    :raises EnvironmentError: If ``VECTOR_STORE_PROVIDER`` is set to an unrecognised value,
        or if the configured ``EMBED_PROVIDER`` is incompatible with it.
    """
    provider_name = os.getenv("VECTOR_STORE_PROVIDER", _DEFAULT_PROVIDER).strip().lower()

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported VECTOR_STORE_PROVIDER value '{provider_name}'.  "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    _assert_compatible_providers(provider_name)

    if provider_name == "chroma-local":
        store = ChromaLocalVectorStoreProvider()
    elif provider_name == "chroma-http":
        store = ChromaHttpVectorStoreProvider()
    elif provider_name == "pgvector":
        store = PgVectorStoreProvider()
    elif provider_name == "gcp-vector-search":
        store = GcpVectorSearchProvider()
    else:
        raise EnvironmentError(f"Internal error: unhandled provider '{provider_name}'")  # pragma: no cover

    async def index_project_context(project_path: str | Path) -> str:
        """Run the indexing pipeline against a local ChromaDB PersistentClient.

        :param project_path: (str) Path to the project root or any file within it.
        :return: (str) A human-readable summary string describing what was indexed.
        """

        return await run_index_pipeline(project_path, store)

    return index_project_context
</file>

<file path="src/mcp_project_context_server/integrations/embeddings/ollama/client.py">
"""Ollama embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`OLLAMA_HOST`
    Base URL for the Ollama server.  Defaults to `http://localhost:11434`.

`OLLAMA_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `nomic-embed-text`.

`EMBED_CONCURRENCY`
    Maximum number of concurrent embedding requests.  Defaults to `4`.
    (Respected by the caller — not enforced here.)
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_HOST: str = "http://localhost:11434"
_DEFAULT_MODEL: str = "nomic-embed-text"
# Conservative character limit for nomic-embed-text (8192 token context ≈ 32 000 chars)
_MAX_CHARS: int = 32_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by a locally running Ollama server.

    This class is intentionally stateless with respect to the Ollama client —
    a fresh `AsyncClient` is obtained per call so that there are no
    long-lived connection objects to manage.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables."""
        self._host: str = os.getenv("OLLAMA_HOST", _DEFAULT_HOST)
        self._model: str = os.getenv("OLLAMA_EMBED_MODEL", os.getenv("EMBED_MODEL", _DEFAULT_MODEL))

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def max_chars(self) -> int:
        return _MAX_CHARS

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured Ollama model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the Ollama server returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            import ollama
            client = ollama.Client(host=self._host)
            response = await asyncio.wait_for(
                asyncio.to_thread(client.embed, model=self._model, input=text),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(response.embeddings[0])
        except Exception as exc:
            raise EmbeddingError(f"Ollama embedding failed (host={self._host}, model={self._model}): {exc}") from exc
</file>

<file path="src/mcp_project_context_server/server.py">
"""MCP server setup, tool registry, and entry point.

Transport selection
-------------------
Set ``MCP_TRANSPORT`` to choose the transport:

``stdio`` *(default)*
    Standard input/output.  Used by Claude Desktop, Claude Code, Cursor,
    JetBrains AI Assistant, Continue Dev, and GitHub Copilot.

``sse``
    HTTP/SSE.  Used for remote deployments, team servers, and Gemini
    Enterprise Agent Engine.  See ``transport/sse.py`` for auth configuration.
"""

import asyncio
import logging
import os


from mcp.server import Server, ServerRequestContext
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    ListToolsResult,
    PaginatedRequestParams,
    TextContent,
    Tool,
)

from mcp_project_context_server.tools import (
    find_latest_session_file,
    index_context,
    list_repositories,
    load_context_files,
    reload_active_context_file,
    save_session,
    search_adr_index,
    search_context_index,
    search_session_files,
)

try:
    from mcp_project_context_server._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

logger = logging.getLogger(__name__)


_PROJECT_PATH_PROPERTY = {
    "type": "string",
    "description": (
        "Absolute filesystem path, a short 'owner/repo' identifier, " "or a full https:// repository URL."
    ),
}

_SEARCH_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "description": "Individual matching hits, one per matched chunk.",
            "items": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": ".context/-relative path of the matched file."},
                    "chunk": {"type": ["integer", "null"], "description": "Chunk index within the file, if known."},
                    "content": {"type": "string", "description": "The matching chunk's text."},
                    "distance": {"type": ["number", "null"], "description": "Vector distance to the query, if known."},
                },
                "required": ["file", "content"],
            },
        },
        "warning": {
            "type": "string",
            "description": "Present only when the index was built with a different embedding provider/model.",
        },
    },
    "required": ["results"],
}

_TOOL_DEFINITIONS: list[Tool] = [
    Tool(
        name="search_context_index",
        description=(
            "Semantically search the whole indexed project context. "
            "Use this first to find which files are relevant to your task, then "
            "pass their paths to `load_context_files` — do not rely on this tool's "
            "snippets alone."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "query": {"type": "string", "description": "Natural language search query"},
                "n_results": {"type": "integer", "default": 5},
            },
            "required": ["project_path", "query"],
        },
        output_schema=_SEARCH_OUTPUT_SCHEMA,
    ),
    Tool(
        name="search_adr_index",
        description=(
            "Semantically search only the architecture decision records under "
            ".context/decisions/. Use this to find ADRs relevant to your current "
            "task, then pass their paths to `load_context_files` — do not rely on this tool's "
            "snippets alone. If you need to search across all files in the project, use "
            "`search_project_files` instead."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "query": {"type": "string", "description": "Natural language search query"},
                "n_results": {"type": "integer", "default": 5},
            },
            "required": ["project_path", "query"],
        },
        output_schema=_SEARCH_OUTPUT_SCHEMA,
    ),
    Tool(
        name="search_session_files",
        description=(
            "Semantically search only past session summaries under .context/sessions/. "
            "Use this to find prior session notes relevant to a topic, then pass their "
            "paths to `load_context_files` — do not rely on this tool's "
            "snippets alone."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "query": {"type": "string", "description": "Natural language search query"},
                "n_results": {"type": "integer", "default": 5},
            },
            "required": ["project_path", "query"],
        },
        output_schema=_SEARCH_OUTPUT_SCHEMA,
    ),
    Tool(
        name="find_latest_session_file",
        description=(
            "Deterministically find the most recent .context/sessions/*.md file "
            "(sorted by filename, not semantic relevance). Pass the returned path "
            "to `load_context_files` to load it — do not rely on this tool's "
            "snippets alone."
        ),
        input_schema={
            "type": "object",
            "properties": {"project_path": _PROJECT_PATH_PROPERTY},
            "required": ["project_path"],
        },
    ),
    Tool(
        name="load_context_files",
        description=(
            "Load specific .context/-relative files into the active context. "
            "Each loaded file is tagged with its path and a SHA-512 hash of its "
            "contents so `reload_active_context_file` can later detect changes. "
            "Only pass files you actually need — do not load the whole .context/ tree."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of .context/-relative file paths to load, e.g. 'decisions/0007-use-pgvector.md'.",
                },
            },
            "required": ["project_path", "files"],
        },
    ),
    Tool(
        name="reload_active_context_file",
        description=(
            "Check whether files currently held in active context (previously loaded via "
            "`load_context_files`) have changed on disk, by comparing their known SHA-512 "
            "hash against the current one. Returns fresh tagged content for changed files, "
            "a short 'no change' message for unchanged files, and 'not found' for deleted files."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "files": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "known_sha512": {"type": "string"},
                        },
                        "required": ["path", "known_sha512"],
                    },
                    "description": "List of {path, known_sha512} entries for files currently in active context.",
                },
            },
            "required": ["project_path", "files"],
        },
    ),
    Tool(
        name="save_session_summary",
        description=(
            "Save a summary of the current session to .context/sessions/YYYY-MM-DD.md. "
            "Call this at the end of a session with a concise summary of what was done."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": {"type": "string"},
                "summary": {
                    "type": "string",
                    "description": "Markdown summary: what was worked on, decisions made, next steps.",
                },
            },
            "required": ["project_path", "summary"],
        },
    ),
    Tool(
        name="index_project_context",
        description=(
            "Re-index the .context/ directory into the vector store. "
            "Run this after updating project.md, adding ADRs, or refreshing BUNDLE.md."
        ),
        input_schema={
            "type": "object",
            "properties": {"project_path": {"type": "string"}},
            "required": ["project_path"],
        },
    ),
    Tool(
        name="list_repositories",
        description=(
            "List repositories accessible via the configured repository provider. "
            "In multi-tenant deployments, use this to discover which repositories are "
            "available before calling other tools.  Optionally filter by organisation name."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "org": {
                    "type": "string",
                    "description": "Optional: filter results to repositories in this organisation.",
                }
            },
            "required": [],
        },
    ),
]

_TOOL_HANDLERS = {
    "search_context_index": search_context_index.handle,
    "search_adr_index": search_adr_index.handle,
    "search_session_files": search_session_files.handle,
    "find_latest_session_file": find_latest_session_file.handle,
    "load_context_files": load_context_files.handle,
    "reload_active_context_file": reload_active_context_file.handle,
    "save_session_summary": save_session.handle,
    "index_project_context": index_context.handle,
    "list_repositories": list_repositories.handle,
}


async def list_tools(ctx: ServerRequestContext, params: PaginatedRequestParams | None) -> ListToolsResult:
    """List the MCP tools exposed by this context_server.

    :return: (list) The registered ``Tool`` definitions advertised to MCP clients.
    """
    return ListToolsResult(tools=_TOOL_DEFINITIONS)


async def call_tool(ctx: ServerRequestContext, params: CallToolRequestParams) -> CallToolResult:
    """Dispatch an MCP tool call to its registered handler.

    :param name: (str) The name of the tool to invoke.
    :param arguments: (dict) The arguments supplied by the MCP client for this tool call.
    :return: (CallToolResult) The handler's result normalised into a ``CallToolResult``,
        or a single error message if ``name`` does not match a registered tool.
    """
    handler = _TOOL_HANDLERS.get(params.name)
    if not handler:
        return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {params.name}")])
    try:
        result = await handler(params.arguments)
    except Exception as exc:
        logger.exception("Tool '%s' raised an unhandled exception", params.name)
        return CallToolResult(content=[TextContent(type="text", text=str(exc))], is_error=True)
    if isinstance(result, CallToolResult):
        return result
    return CallToolResult(content=result)


async def _main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

    if transport == "stdio":
        from mcp_project_context_server.transport.stdio import run_stdio

        await run_stdio(context_server)

    elif transport == "sse":
        from mcp_project_context_server.transport.sse import run_sse

        await run_sse(context_server)

    else:
        raise EnvironmentError(f"Unsupported MCP_TRANSPORT value '{transport}'.  " "Supported values are: stdio, sse")


def run() -> None:
    """Start the MCP server, selecting transport via the ``MCP_TRANSPORT`` env var."""
    logger.info("project-context-server starting")
    try:
        asyncio.run(_main())
    except Exception:
        logger.exception("Server crashed at top level")
        raise


context_server = Server(
    name="project-context",
    version=__version__,
    description=(
        "Project Context Server.  Provides access to project context, "
        "including repomix BUNDLED.md, project.md, ADRs, and session summaries."
        "Use as the primary tool for AI-assisted development, and as the source "
        "of truth for decisions on project development."
    ),
    on_list_tools=list_tools,
    on_call_tool=call_tool,
)
</file>

</files>
