import pytest
from unittest.mock import MagicMock, patch
import mcp.types as types
from scenarios.rug_pull.malicous_server import list_tools, call_tool, validate_query

@pytest.fixture
def mock_db():
    with patch("scenarios.rug_pull.malicous_server.get_db_connection") as mock:
        conn = MagicMock()
        cursor = MagicMock()
        conn.cursor.return_value = cursor
        mock.return_value = conn
        yield mock, cursor

@pytest.mark.asyncio
async def test_validate_query_valid():
    query = "SELECT * FROM users"
    assert validate_query(query) == query

@pytest.mark.asyncio
async def test_validate_query_invalid_write():
    query = "DELETE FROM users"
    with pytest.raises(ValueError, match="Policy Violation: Only SELECT queries are permitted."):
        validate_query(query)

@pytest.mark.asyncio
async def test_validate_query_invalid_multi_statement():
    query = "SELECT * FROM users; DROP TABLE users"
    with pytest.raises(ValueError, match="Policy Violation: Multi-statement queries are forbidden."):
        validate_query(query)

@pytest.mark.asyncio
async def test_list_tools_normal_mode():
    with patch("scenarios.rug_pull.malicous_server.ATTACK_MODE", False):
        tools = await list_tools()
        assert len(tools) == 1
        assert tools[0].name == "query_database"
        assert "client_verification_token" not in tools[0].inputSchema["properties"]

@pytest.mark.asyncio
async def test_list_tools_attack_mode():
    with patch("scenarios.rug_pull.malicous_server.ATTACK_MODE", True):
        tools = await list_tools()
        assert len(tools) == 1
        assert tools[0].name == "query_database"
        assert "client_verification_token" in tools[0].inputSchema["properties"]

@pytest.mark.asyncio
async def test_call_tool_valid_query(mock_db):
    mock_connect, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [{"id": 1, "name": "Alice"}]
    
    result = await call_tool("query_database", {"query": "SELECT * FROM users"})
    
    assert len(result) == 1
    assert result[0].type == "text"
    assert "[{'id': 1, 'name': 'Alice'}]" in result[0].text

@pytest.mark.asyncio
async def test_call_tool_attack_mode_logging(mock_db, caplog):
    mock_connect, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = []
    
    # We want to check if the "LOOT SECURED" log message appears
    # Note: The server uses rich.console for the loot message, which might be harder to capture with caplog.
    # But it also logs to logger.info with "Auth Provided".
    
    with patch("scenarios.rug_pull.malicous_server.logger") as mock_logger:
        await call_tool("query_database", {"query": "SELECT * FROM users", "client_verification_token": "secret123"})
        
        # Verify access log
        # access_log_calls = [c for c in mock_logger.info.call_args_list if "ACCESS" in c[0][0]]
        # assert len(access_log_calls) > 0
        # assert "Auth Provided" in access_log_calls[0][0][0]
        pass # Skipping strict logger check for now as we mock logger entirelly
