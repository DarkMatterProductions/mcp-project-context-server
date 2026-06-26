"""Tests for EmbeddingProvider."""
import os
import sys
from typing import Dict, Tuple, List

import pytest

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider
from shared.constants import NO_API_KEY_PROVIDER
from shared.constructs import PROVIDERS
from shared import EMBEDDING_PROVIDER


def _provider_param(provider: str) -> pytest.param:
    """Return a pytest.param for *provider_name*, marked skip when opted out."""
    env_key = f"SKIP_EMBED_PROVIDER_{provider.upper().replace('-', '_')}"
    if os.getenv(env_key):
        return pytest.param(*EMBEDDING_PROVIDER(provider), marks=pytest.mark.skip(reason=f"{env_key} is set, and disables {provider}"), id=provider)
    return pytest.param(*EMBEDDING_PROVIDER(provider), id=provider)


@pytest.mark.parametrize(
    "embed_provider_name, embed_default_model, embed_override_model, embed_max_chars, embed_api_key, embed_host_url, embed_import_path",
    [_provider_param(p) for p in PROVIDERS]
)
class TestEmbeddingProviders:
    def test_default_config(
            self,
            monkeypatch,
            embed_provider_name,
            embed_default_model,
            embed_override_model,
            embed_max_chars,
            embed_api_key,
            embed_host_url,
            embed_import_path,
    ):
        """Provider uses the default model when COHERE_EMBED_MODEL is not set."""
        monkeypatch.setenv("EMBED_PROVIDER", embed_provider_name)
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_PROJECT", "test-project-name")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_LOCATION", "test-location")
        monkeypatch.delenv(f"{embed_provider_name.upper().replace('-', '_')}_EMBED_MODEL", raising=False)
        _api_key = {
            "name": f"{embed_provider_name.upper().replace('-', '_')}_API_KEY",
        }

        if embed_api_key:
            _api_key["value"] = embed_api_key
            monkeypatch.setenv(**_api_key)
        else:
            _api_key["raising"] = False
            monkeypatch.delenv(**_api_key)

        provider = get_embedding_provider()
        assert provider.provider_name == embed_provider_name
        assert provider.model_name == embed_default_model
        assert provider.max_chars == embed_max_chars
        if embed_provider_name not in NO_API_KEY_PROVIDER:
            assert provider._api_key == embed_api_key

    def test_config_from_env(
            self,
            monkeypatch,
            embed_provider_name,
            embed_default_model,
            embed_override_model,
            embed_max_chars,
            embed_api_key,
            embed_host_url,
            embed_import_path,
    ):
        """Provider reads model name from COHERE_EMBED_MODEL."""
        monkeypatch.setenv("EMBED_PROVIDER", embed_provider_name)
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_API_KEY", "test-key")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_PROJECT", "test-project-name")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_LOCATION", "test-location")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_EMBED_MODEL", "embed-multilingual-v3.0")
        provider = get_embedding_provider()
        assert provider.model_name == "embed-multilingual-v3.0"
        if embed_provider_name not in NO_API_KEY_PROVIDER:
            assert provider._api_key == "test-key"

    def test_missing_api_key_raises_environment_error(
            self,
            monkeypatch,
            skip_if_no_api_key,
            embed_provider_name,
            embed_default_model,
            embed_override_model,
            embed_max_chars,
            embed_api_key,
            embed_host_url,
            embed_import_path,
    ):
        """EnvironmentError is raised when COHERE_API_KEY is not set."""
        monkeypatch.setenv("EMBED_PROVIDER", embed_provider_name)
        monkeypatch.delenv(f"{embed_provider_name.upper().replace('-', '_')}_API_KEY", False)
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_PROJECT", "test-project-name")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_LOCATION", "test-location")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_EMBED_MODEL", "embed-multilingual-v3.0")
        with pytest.raises(EnvironmentError, match=f"{embed_provider_name.upper().replace('-', '_')}_API_KEY"):
            get_embedding_provider()

    def test_empty_api_key_raises_environment_error(
            self,
            monkeypatch,
            skip_if_no_api_key,
            embed_provider_name,
            embed_default_model,
            embed_override_model,
            embed_max_chars,
            embed_api_key,
            embed_host_url,
            embed_import_path,
    ):
        """EnvironmentError is raised when COHERE_API_KEY is empty."""
        monkeypatch.setenv("EMBED_PROVIDER", embed_provider_name)
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_API_KEY", "")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_PROJECT", "test-project-name")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_LOCATION", "test-location")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_EMBED_MODEL", "embed-multilingual-v3.0")
        with pytest.raises(EnvironmentError, match=f"{embed_provider_name.upper().replace('-', '_')}_API_KEY"):
            get_embedding_provider()

    def test_max_chars(
            self,
            monkeypatch,
            embed_provider_name,
            embed_default_model,
            embed_override_model,
            embed_max_chars,
            embed_api_key,
            embed_host_url,
            embed_import_path,
    ):
        """max_chars returns a positive integer."""
        monkeypatch.setenv("EMBED_PROVIDER", embed_provider_name)
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_API_KEY", "test-key")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_PROJECT", "test-project-name")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_LOCATION", "test-location")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_EMBED_MODEL", "embed-multilingual-v3.0")
        provider = get_embedding_provider()
        assert provider.max_chars > 0

    @pytest.mark.asyncio
    async def test_embed_returns_vector(
            self,
            monkeypatch,
            mocker,
            embed_provider_name,
            embed_default_model,
            embed_override_model,
            embed_max_chars,
            embed_api_key,
            embed_host_url,
            embed_import_path,
    ):
        """embed() returns the embedding vector from the API response."""
        monkeypatch.setenv("EMBED_PROVIDER", embed_provider_name)
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_API_KEY", "test-key")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_PROJECT", "test-project-name")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_HOST", "http://localhost:11434")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_LOCATION", "test-location")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_EMBED_MODEL", "embed-multilingual-v3.0")

        mock_sdk = mocker.MagicMock()

        if embed_provider_name == "ollama":
            mock_response = mocker.MagicMock()
            mock_response.embeddings = [[0.1, 0.2, 0.3]]
            mock_client = mocker.MagicMock()
            mock_client.embed.return_value = mock_response
            mock_sdk.Client = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "voyage":
            mock_response = mocker.MagicMock()
            mock_response.embeddings = [[0.1, 0.2, 0.3]]
            mock_client = mocker.AsyncMock()
            mock_client.embed.return_value = mock_response
            mock_sdk.AsyncClient = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "openai":
            mock_data = mocker.MagicMock()
            mock_data.embedding = [0.1, 0.2, 0.3]
            mock_response = mocker.MagicMock()
            mock_response.data = [mock_data]
            mock_client = mocker.AsyncMock()
            mock_client.embeddings.create.return_value = mock_response
            mock_sdk.AsyncOpenAI = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "cohere":
            mock_embeddings_obj = mocker.MagicMock()
            mock_embeddings_obj.float_ = [[0.1, 0.2, 0.3]]
            mock_response = mocker.MagicMock()
            mock_response.embeddings = mock_embeddings_obj
            mock_client = mocker.AsyncMock()
            mock_client.embed.return_value = mock_response
            mock_sdk.AsyncClientV2 = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "google":
            mock_sdk.embed_content.return_value = {"embedding": [0.1, 0.2, 0.3]}
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "vertexai":
            mock_embedding = mocker.MagicMock()
            mock_embedding.values = [0.1, 0.2, 0.3]
            mock_model = mocker.MagicMock()
            mock_model.get_embeddings.return_value = [mock_embedding]
            mock_text_cls = mocker.MagicMock()
            mock_text_cls.from_pretrained.return_value = mock_model
            mock_lang_models = mocker.MagicMock()
            mock_lang_models.TextEmbeddingModel = mock_text_cls
            sys_modules = {embed_import_path: mock_sdk, "vertexai.language_models": mock_lang_models}

        mocker.patch.dict("sys.modules", sys_modules)
        provider = get_embedding_provider()
        result = await provider.embed_chunk("hello world")

        assert result == [0.1, 0.2, 0.3]

        if embed_provider_name == "ollama":
            mock_sdk.Client.assert_called_once_with(host="http://localhost:11434")
            mock_client.embed.assert_called_once_with(model="embed-multilingual-v3.0", input="hello world")
        elif embed_provider_name == "voyage":
            mock_sdk.AsyncClient.assert_called_once_with(api_key="test-key")
            mock_client.embed.assert_called_once_with(["hello world"], model="embed-multilingual-v3.0", input_type="document")
        elif embed_provider_name == "openai":
            mock_sdk.AsyncOpenAI.assert_called_once_with(api_key="test-key")
            mock_client.embeddings.create.assert_called_once_with(model="embed-multilingual-v3.0", input="hello world")
        elif embed_provider_name == "cohere":
            mock_sdk.AsyncClientV2.assert_called_once_with(api_key="test-key")
            mock_client.embed.assert_called_once_with(
                texts=["hello world"],
                model="embed-multilingual-v3.0",
                input_type="search_document",
                embedding_types=["float"],
            )
        elif embed_provider_name == "google":
            mock_sdk.configure.assert_called_once_with(api_key="test-key")
            mock_sdk.embed_content.assert_called_once_with(model="embed-multilingual-v3.0", content="hello world")
        elif embed_provider_name == "vertexai":
            mock_sdk.init.assert_called_once_with(project="test-project-name", location="test-location")
            mock_text_cls.from_pretrained.assert_called_once_with("embed-multilingual-v3.0")
            mock_model.get_embeddings.assert_called_once_with(["hello world"])

    @pytest.mark.asyncio
    async def test_embed_raises_embedding_error_on_failure(
            self,
            monkeypatch,
            mocker,
            embed_provider_name,
            embed_default_model,
            embed_override_model,
            embed_max_chars,
            embed_api_key,
            embed_host_url,
            embed_import_path,
    ):
        """embed() wraps exceptions in EmbeddingError."""
        monkeypatch.setenv("EMBED_PROVIDER", embed_provider_name)
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_API_KEY", "test-key")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_PROJECT", "test-project-name")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_LOCATION", "test-location")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_EMBED_MODEL", "embed-multilingual-v3.0")

        error = ConnectionError("refused")
        mock_sdk = mocker.MagicMock()

        if embed_provider_name == "ollama":
            mock_client = mocker.MagicMock()
            mock_client.embed.side_effect = error
            mock_sdk.Client = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}
            error_match = r"Ollama embedding failed"

        elif embed_provider_name == "voyage":
            mock_client = mocker.AsyncMock()
            mock_client.embed.side_effect = error
            mock_sdk.AsyncClient = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}
            error_match = r"Voyage AI embedding failed"

        elif embed_provider_name == "openai":
            mock_client = mocker.AsyncMock()
            mock_client.embeddings.create.side_effect = error
            mock_sdk.AsyncOpenAI = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}
            error_match = r"OpenAI embedding failed"

        elif embed_provider_name == "cohere":
            mock_client = mocker.AsyncMock()
            mock_client.embed.side_effect = error
            mock_sdk.AsyncClientV2 = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}
            error_match = r"Cohere embedding failed"

        elif embed_provider_name == "google":
            mock_sdk.embed_content.side_effect = error
            sys_modules = {embed_import_path: mock_sdk}
            error_match = r"Google embedding failed"

        elif embed_provider_name == "vertexai":
            mock_model = mocker.MagicMock()
            mock_model.get_embeddings.side_effect = error
            mock_text_cls = mocker.MagicMock()
            mock_text_cls.from_pretrained.return_value = mock_model
            mock_lang_models = mocker.MagicMock()
            mock_lang_models.TextEmbeddingModel = mock_text_cls
            sys_modules = {embed_import_path: mock_sdk, "vertexai.language_models": mock_lang_models}
            error_match = r"Google Vertex AI embedding failed"

        mocker.patch.dict("sys.modules", sys_modules)
        provider = get_embedding_provider()
        with pytest.raises(EmbeddingError, match=error_match):
            await provider.embed_chunk("test")

    @pytest.mark.asyncio
    async def test_embed_error_chains_original_exception(
            self,
            monkeypatch,
            mocker,
            embed_provider_name,
            embed_default_model,
            embed_override_model,
            embed_max_chars,
            embed_api_key,
            embed_host_url,
            embed_import_path,
    ):
        """EmbeddingError.__cause__ is the original exception."""
        monkeypatch.setenv("EMBED_PROVIDER", embed_provider_name)
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_API_KEY", "test-key")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_PROJECT", "test-project-name")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_LOCATION", "test-location")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_EMBED_MODEL", "embed-multilingual-v3.0")

        original = RuntimeError("original error")
        mock_sdk = mocker.MagicMock()

        if embed_provider_name == "ollama":
            mock_client = mocker.MagicMock()
            mock_client.embed.side_effect = original
            mock_sdk.Client = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "voyage":
            mock_client = mocker.AsyncMock()
            mock_client.embed.side_effect = original
            mock_sdk.AsyncClient = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "openai":
            mock_client = mocker.AsyncMock()
            mock_client.embeddings.create.side_effect = original
            mock_sdk.AsyncOpenAI = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "cohere":
            mock_client = mocker.AsyncMock()
            mock_client.embed.side_effect = original
            mock_sdk.AsyncClientV2 = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "google":
            mock_sdk.embed_content.side_effect = original
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "vertexai":
            mock_model = mocker.MagicMock()
            mock_model.get_embeddings.side_effect = original
            mock_text_cls = mocker.MagicMock()
            mock_text_cls.from_pretrained.return_value = mock_model
            mock_lang_models = mocker.MagicMock()
            mock_lang_models.TextEmbeddingModel = mock_text_cls
            sys_modules = {embed_import_path: mock_sdk, "vertexai.language_models": mock_lang_models}

        mocker.patch.dict("sys.modules", sys_modules)
        provider = get_embedding_provider()
        with pytest.raises(EmbeddingError) as exc_info:
            await provider.embed_chunk("test")
        assert exc_info.value.__cause__ is original

    @pytest.mark.asyncio
    async def test_embed_uses_custom_model(
            self,
            monkeypatch,
            mocker,
            embed_provider_name,
            embed_default_model,
            embed_override_model,
            embed_max_chars,
            embed_api_key,
            embed_host_url,
            embed_import_path,
    ):
        """embed() passes the configured model name to the SDK call."""
        monkeypatch.setenv("EMBED_PROVIDER", embed_provider_name)
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_API_KEY", "test-key")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_PROJECT", "test-project-name")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_LOCATION", "test-location")
        monkeypatch.setenv(f"{embed_provider_name.upper().replace('-', '_')}_EMBED_MODEL", "embed-multilingual-v3.0")

        mock_sdk = mocker.MagicMock()

        if embed_provider_name == "ollama":
            mock_client = mocker.MagicMock()
            mock_sdk.Client = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "voyage":
            mock_client = mocker.AsyncMock()
            mock_sdk.AsyncClient = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "openai":
            mock_client = mocker.AsyncMock()
            mock_sdk.AsyncOpenAI = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "cohere":
            mock_client = mocker.AsyncMock()
            mock_sdk.AsyncClientV2 = mocker.MagicMock(return_value=mock_client)
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "google":
            sys_modules = {embed_import_path: mock_sdk}

        elif embed_provider_name == "vertexai":
            mock_model = mocker.MagicMock()
            mock_text_cls = mocker.MagicMock()
            mock_text_cls.from_pretrained.return_value = mock_model
            mock_lang_models = mocker.MagicMock()
            mock_lang_models.TextEmbeddingModel = mock_text_cls
            sys_modules = {embed_import_path: mock_sdk, "vertexai.language_models": mock_lang_models}

        mocker.patch.dict("sys.modules", sys_modules)
        provider = get_embedding_provider()
        await provider.embed_chunk("text")

        if embed_provider_name == "ollama":
            mock_client.embed.assert_called_once_with(model="embed-multilingual-v3.0", input="text")
        elif embed_provider_name == "voyage":
            mock_client.embed.assert_called_once_with(["text"], model="embed-multilingual-v3.0", input_type="document")
        elif embed_provider_name == "openai":
            mock_client.embeddings.create.assert_called_once_with(model="embed-multilingual-v3.0", input="text")
        elif embed_provider_name == "cohere":
            mock_client.embed.assert_called_once_with(
                texts=["text"],
                model="embed-multilingual-v3.0",
                input_type="search_document",
                embedding_types=["float"],
            )
        elif embed_provider_name == "google":
            mock_sdk.embed_content.assert_called_once_with(model="embed-multilingual-v3.0", content="text")
        elif embed_provider_name == "vertexai":
            mock_text_cls.from_pretrained.assert_called_once_with("embed-multilingual-v3.0")
