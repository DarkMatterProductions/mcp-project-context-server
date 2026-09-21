"""Voyage AI embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`VOYAGE_API_KEY`
    API key for the Voyage AI service.  **Required.**

`VOYAGE_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `voyage-code-3`.

`VOYAGE_BACKOFF_INITIAL_DELAY`
    Initial backoff delay, in seconds, applied when Voyage AI returns a
    transient error (HTTP 429, 5xx, timeout, or connection reset). Doubles on
    each retry, up to 4 attempts total.  Defaults to `300`.
"""

import asyncio
import logging
import os
import random

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_MODEL: str = "voyage-code-3"
# voyage-code-3 context ≈ 32k tokens; conservative character limit
_MAX_CHARS: int = 24_000
_EMBED_TIMEOUT_SECONDS: float = 60.0

_DEFAULT_BACKOFF_INITIAL_DELAY_SECONDS: float = 300.0
_BACKOFF_MULTIPLIER: float = 2.0
_BACKOFF_JITTER: float = 0.1
_MAX_BACKOFF_ATTEMPTS: int = 4

# Set once per process the first time an `x-api-warning` header is observed
# on a failed request (R7 — surface the reduced-tier warning once, not per
# request).
_tier_warning_logged: bool = False


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
        self._backoff_initial_delay: float = float(
            os.getenv("VOYAGE_BACKOFF_INITIAL_DELAY", str(_DEFAULT_BACKOFF_INITIAL_DELAY_SECONDS))
        )

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
    # Failure logging (R6 / R7)
    # ------------------------------------------------------------------

    def _log_failure_headers(self, exc: Exception) -> None:
        """Surface `x-request-id` (R6) and the reduced-tier warning (R7).

        `voyageai.error.VoyageError` carries the real HTTP response headers
        on `.headers`; other exceptions (e.g. import failures) do not.
        """
        headers = getattr(exc, "headers", None)
        if not headers:
            return
        request_id = headers.get("x-request-id")
        if request_id:
            logger.warning("Voyage AI request %s failed (model=%s).", request_id, self._model)
        warning = headers.get("x-api-warning")
        if warning:
            self._warn_tier_limit_once(warning)

    @staticmethod
    def _warn_tier_limit_once(warning_text: str) -> None:
        global _tier_warning_logged
        if _tier_warning_logged:
            return
        _tier_warning_logged = True
        logger.warning("Voyage AI rate-limit tier warning: %s", warning_text)

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured Voyage AI model.

        Retries with exponential backoff on transient errors (HTTP 429, 5xx,
        timeout, connection reset — see `VOYAGE-AI-RATELIMIT-HANDLING.md`
        §6.1). All other errors (bad API key, unsupported model, malformed
        input, ...) fail immediately with no retry.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the Voyage AI API returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            import voyageai  # lazy import

            client = voyageai.AsyncClient(api_key=self._api_key)
        except Exception as exc:
            raise EmbeddingError(f"Voyage AI embedding failed (model={self._model}): {exc}") from exc

        retryable_errors = (
            voyageai.error.RateLimitError,  # 429
            voyageai.error.ServerError,  # 5xx
            voyageai.error.ServiceUnavailableError,  # 502/503/504
            voyageai.error.APIConnectionError,  # connection reset
            voyageai.error.Timeout,  # SDK-side timeout
            voyageai.error.TryAgain,  # explicit vendor retry hint
            asyncio.TimeoutError,  # our own asyncio.wait_for timeout
        )

        delay = self._backoff_initial_delay
        total_waited = 0.0
        for attempt in range(1, _MAX_BACKOFF_ATTEMPTS + 1):
            try:
                result = await asyncio.wait_for(
                    client.embed([text], model=self._model, input_type="document"),
                    timeout=_EMBED_TIMEOUT_SECONDS,
                )
                return list(result.embeddings[0])
            except retryable_errors as exc:
                self._log_failure_headers(exc)
                if attempt == _MAX_BACKOFF_ATTEMPTS:
                    raise EmbeddingError(
                        f"Voyage AI embedding failed (model={self._model}): giving up after "
                        f"{attempt} attempts over {total_waited:.0f}s on transient "
                        f"{type(exc).__name__}: {exc}"
                    ) from exc
                sleep_for = delay * random.uniform(1 - _BACKOFF_JITTER, 1 + _BACKOFF_JITTER)
                logger.warning(
                    "Voyage AI transient error (%s) on attempt %d/%d for model=%s; retrying in %.0fs.",
                    type(exc).__name__,
                    attempt,
                    _MAX_BACKOFF_ATTEMPTS,
                    self._model,
                    sleep_for,
                )
                await asyncio.sleep(sleep_for)
                total_waited += sleep_for
                delay *= _BACKOFF_MULTIPLIER
            except Exception as exc:
                self._log_failure_headers(exc)
                raise EmbeddingError(f"Voyage AI embedding failed (model={self._model}): {exc}") from exc
