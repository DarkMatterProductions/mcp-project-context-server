from pathlib import Path

from mcp_project_context_server.integrations.vectorstore.registry import (
    INCOMPATIBLE_EMBED_PROVIDERS_BY_VECTOR_STORE,
)

from shared import PROVIDER_DEFAULTS

PROVIDERS = PROVIDER_DEFAULTS.keys()
# Embed providers usable with the default (chroma-local) vector store.  Excludes
# providers that deadlock in-process with chromadb (see registry docstring).
CHROMA_COMPATIBLE_PROVIDERS = [
    p for p in PROVIDERS if p not in INCOMPATIBLE_EMBED_PROVIDERS_BY_VECTOR_STORE.get("chroma-local", frozenset())
]
EMBEDDING_PROVIDER = lambda provider: (
    provider,
    PROVIDER_DEFAULTS[provider]["default_model"],
    f"{provider}-embedded-override",
    PROVIDER_DEFAULTS[provider]["max_chars"],
    PROVIDER_DEFAULTS[provider]["api_key"],
    f"https://{provider}-fqdn.com:121415",
    PROVIDER_DEFAULTS[provider]["import_path"],
)
KNOWN_INTERFERING_ENV_VARS = ("PROJECT_PATH",)
SRC_DIR = str(Path(__file__).parent.parent / "src")
