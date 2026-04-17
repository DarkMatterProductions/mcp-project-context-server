import pytest
from unittest.mock import AsyncMock, patch
from mcp_project_context_server.tools.index_context import handle

@pytest.mark.asyncio
async def test_index_context():
    arguments = {"project_path": "/some/path"}
    
    with patch("mcp_project_context_server.tools.index_context.index_project_context", new_callable=AsyncMock) as mock_index:
        mock_index.return_value = "Indexed 5 files."
        
        result = await handle(arguments)
        
        assert len(result) == 1
        assert result[0].text == "Indexed 5 files."
        mock_index.assert_called_once_with("/some/path")
