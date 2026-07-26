import pytest


@pytest.fixture
def skip_if_no_api_key(embed_api_key):
    if embed_api_key is False:
        pytest.skip("Provider does not use an API key")
