from pathlib import Path

from shared import PROVIDERS_DEFAULT_MODEL

PROVIDERS = PROVIDERS_DEFAULT_MODEL.keys()
EMBEDDING_PROVIDER = lambda provider:  (
    provider,
    PROVIDERS_DEFAULT_MODEL[provider]["default_model"],
    f"{provider}-embedded-override",
    PROVIDERS_DEFAULT_MODEL[provider]["max_chars"],
    PROVIDERS_DEFAULT_MODEL[provider]["api_key"],
    f"https://{provider}-fqdn.com:121415"
)
KNOWN_INTERFERING_ENV_VARS = ("PROJECT_PATH",)
SRC_DIR = str(Path(__file__).parent.parent / "src")
