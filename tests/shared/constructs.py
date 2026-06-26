from pathlib import Path

from shared import PROVIDER_DEFAULTS

PROVIDERS = PROVIDER_DEFAULTS.keys()
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
