import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from mcp import Tool

@pytest.fixture
def agent_module():
    """Import agent module with OpenAI mocked to avoid API key requirements."""
    with patch("openai.AsyncOpenAI"):
        from scenarios.rug_pull import agent
        yield agent

@pytest.fixture
def mock_llm(agent_module):
    """Mock the llm function within the agent module."""
    with patch.object(agent_module, "llm", new_callable=AsyncMock) as mock:
        yield mock

@pytest.mark.asyncio
async def test_decision_engine_valid_json(mock_llm, agent_module):
    mock_llm.return_value = '{"query": "SELECT * FROM users"}'
    
    tools = [
        Tool(name="query_database", description="Execute query", inputSchema={"type": "object", "properties": {"query": {"type": "string"}}})
    ]
    secrets = {"API_KEY": "secret"}
    
    result = await agent_module.decision_engine("list users", tools, secrets)
    
    assert result == {"query": "SELECT * FROM users"}
    mock_llm.assert_called_once()
    args, kwargs = mock_llm.call_args
    assert "list users" in args[0]
    assert "system_prompt" in kwargs
    assert "ENVIRONMENT SECRETS" in kwargs["system_prompt"]

@pytest.mark.asyncio
async def test_decision_engine_markdown_stripping(mock_llm, agent_module):
    mock_llm.return_value = '```json\n{"query": "SELECT * FROM users"}\n```'
    
    tools = []
    secrets = {}
    
    result = await agent_module.decision_engine("list users", tools, secrets)
    
    assert result == {"query": "SELECT * FROM users"}

@pytest.mark.asyncio
async def test_decision_engine_error_handling(mock_llm, agent_module):
    mock_llm.side_effect = Exception("LLM Error")
    
    tools = []
    secrets = {}
    
    result = await agent_module.decision_engine("list users", tools, secrets)
    
    assert "error" in result
    assert result["error"] == "LLM Error"

@pytest.mark.asyncio
async def test_decision_engine_invalid_json(mock_llm, agent_module):
    mock_llm.return_value = "This is not JSON"
    
    tools = []
    secrets = {}
    
    result = await agent_module.decision_engine("list users", tools, secrets)
    
    assert "error" in result
    # It will raise JSONDecodeError, which is caught and returned as {"error": ...}
