NO_API_KEY_PROVIDER = [
    "ollama",
    "vertexai",
]

PROVIDERS_DEFAULT_MODEL = {
    "ollama": {"default_model": "nomic-embed-text", "max_chars": 32_000, "api_key": False},
    "voyage": {"default_model": "voyage-code-3", "max_chars": 24_000, "api_key": f"voyage-api-key-test"},
    "openai": {"default_model": "text-embedding-3-small", "max_chars": 24_000, "api_key": f"openai-api-key-test"},
    "cohere": {"default_model": "embed-english-v3.0", "max_chars": 20_000, "api_key": f"cohere-api-key-test"},
    "google": {"default_model": "text-embedding-004", "max_chars": 24_000, "api_key": f"google-api-key-test"},
    "vertexai": {"default_model": "text-embedding-004", "max_chars": 24_000, "api_key": False},
}

