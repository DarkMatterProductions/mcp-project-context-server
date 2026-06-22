from pathlib import Path
from importlib import import_module

KNOWN_INTERFERING_ENV_VARS = ("PROJECT_PATH",)
SRC_DIR = str(Path(__file__).parent.parent / "src")

PROVIDERS_DEFAULT_MODEL = {
    "ollama": ("nomic-embed-text", 32_000),
    "voyage": ("voyage-code-3", 24_000),
    "openai": ("text-embedding-3-small", 24_000),
    "cohere": ("embed-english-v3.0", 20_000),
    "google": ("text-embedding-004", 24_000),
    "vertexai": ("text-embedding-004", 24_000),
}

PROVIDERS = PROVIDERS_DEFAULT_MODEL.keys()

EMBEDDING_PROVIDER = lambda provider: (
    provider,
    PROVIDERS_DEFAULT_MODEL[provider][0],
    f"{provider}-embedded-override",
    PROVIDERS_DEFAULT_MODEL[provider][1],
    f"{provider}-api-key-default",
    f"https://{provider}-fqdn.com:121415"
)
