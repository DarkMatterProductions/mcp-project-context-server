"""Custom exception types shared across the server and its integrations."""


class EmbeddingError(Exception):
    """Raised when an embedding provider call fails."""
