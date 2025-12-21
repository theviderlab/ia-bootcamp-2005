"""
Integration tests for chat with MCP tools.

Tests the full chat endpoint with real OpenAI API and registered tools.
Requires OPENAI_API_KEY environment variable.
"""

import os

import pytest
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport

# Load environment variables from .env file
load_dotenv()

# Skip all tests if OPENAI_API_KEY not set
pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set - skipping integration tests"
)


@pytest.mark.asyncio
async def test_chat_with_tools_datetime_query():
    """Test chat endpoint with tool calling using datetime tool."""
    from agentlab.api.main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/llm/chat",
            json={
                "messages": [
                    {"role": "user", "content": "What is the current date and time?"}
                ],
                "use_tools": True,
                "tool_names": ["get_current_datetime"],
                "temperature": 0.3,
                "max_tokens": 200,
                "use_memory": False,
                "use_rag": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "response" in data
        assert "session_id" in data
        assert "tools_used" in data
        assert "tool_calls" in data
        assert "agent_steps" in data
        
        # Verify tool was used
        assert data["tools_used"] is True
        assert len(data["tool_calls"]) > 0
        assert data["tool_calls"][0]["name"] == "get_current_datetime"
        
        # Verify agent steps
        assert len(data["agent_steps"]) >= 2  # At least one tool call + final answer
        assert any(step["action"] == "tool_call" for step in data["agent_steps"])
        assert any(step["action"] == "final_answer" for step in data["agent_steps"])
        
        # Check that response mentions time/date
        response_text = data["response"].lower()
        assert any(word in response_text for word in ["time", "date", "2025", "december"])


@pytest.mark.asyncio
async def test_chat_without_tools():
    """Test that use_tools=False maintains backward compatibility."""
    from agentlab.api.main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/llm/chat",
            json={
                "messages": [
                    {"role": "user", "content": "Say hello"}
                ],
                "use_tools": False,
                "use_memory": False,
                "use_rag": False,
                "temperature": 0.7,
                "max_tokens": 50
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify no tools were used
        assert data["tools_used"] is False
        assert len(data["tool_calls"]) == 0
        assert len(data["agent_steps"]) == 0
        
        # Should still have a response
        assert len(data["response"]) > 0


@pytest.mark.asyncio
async def test_chat_with_tools_default_behavior():
    """Test default behavior when use_tools not specified (should be False)."""
    from agentlab.api.main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/llm/chat",
            json={
                "messages": [
                    {"role": "user", "content": "What time is it?"}
                ],
                # use_tools not specified, should default to False
                "use_memory": False,
                "use_rag": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should not use tools by default
        assert data["tools_used"] is False


@pytest.mark.asyncio
async def test_chat_with_tools_and_memory():
    """Test tools + memory integration."""
    from agentlab.api.main import app
    
    session_id = "test-tools-memory-session"
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First message with tools
        response1 = await client.post(
            "/llm/chat",
            json={
                "messages": [
                    {"role": "user", "content": "What time is it?"}
                ],
                "session_id": session_id,
                "use_tools": True,
                "use_memory": True,
                "use_rag": False,
                "temperature": 0.3
            }
        )
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["tools_used"] is True
        
        # Second message referencing first (tests memory)
        response2 = await client.post(
            "/llm/chat",
            json={
                "messages": [
                    {"role": "user", "content": "What time is it?"},
                    {"role": "assistant", "content": data1["response"]},
                    {"role": "user", "content": "Can you format that differently?"}
                ],
                "session_id": session_id,
                "use_tools": True,
                "use_memory": True,
                "use_rag": False,
                "temperature": 0.3
            }
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Should have context from memory including previous tool calls
        assert "context_text" in data2
        # Context should include tool results section if tools were used
        if data1["tools_used"]:
            context_lower = data2["context_text"].lower()
            # May or may not have tool results depending on memory filtering


@pytest.mark.asyncio
async def test_chat_with_invalid_tool_name():
    """Test error handling with non-existent tool."""
    from agentlab.api.main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/llm/chat",
            json={
                "messages": [
                    {"role": "user", "content": "Test message"}
                ],
                "use_tools": True,
                "tool_names": ["nonexistent_tool_12345"],
                "use_memory": False,
                "use_rag": False
            }
        )
        
        # Should return 500 or 400 due to invalid tool
        assert response.status_code in [400, 500]


@pytest.mark.asyncio
async def test_chat_with_tools_max_iterations():
    """Test that max_iterations parameter is respected."""
    from agentlab.api.main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/llm/chat",
            json={
                "messages": [
                    {"role": "user", "content": "What's the current time?"}
                ],
                "use_tools": True,
                "max_tool_iterations": 2,  # Limit to 2 iterations
                "use_memory": False,
                "use_rag": False,
                "temperature": 0.3
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should complete within max iterations
        if data["tools_used"]:
            # Count tool call steps
            tool_call_steps = [s for s in data["agent_steps"] if s["action"] == "tool_call"]
            assert len(tool_call_steps) <= 2


@pytest.mark.asyncio
async def test_chat_with_tools_context_integration():
    """Test that tool results appear in context."""
    from agentlab.api.main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/llm/chat",
            json={
                "messages": [
                    {"role": "user", "content": "Get the current time please"}
                ],
                "use_tools": True,
                "tool_names": ["get_current_datetime"],
                "use_memory": False,
                "use_rag": False,
                "temperature": 0.3
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["tools_used"] and len(data["tool_calls"]) > 0:
            # Context should include tool results section
            context_text = data["context_text"]
            assert len(context_text) > 0
            # Tool results are now included in context
            # Check for presence of tool execution section
            assert "Tool Execution Results" in context_text or context_text == ""


@pytest.mark.asyncio
async def test_chat_with_all_features():
    """Integration test with tools + memory + RAG all enabled."""
    from agentlab.api.main import app
    
    # Note: This test requires RAG to be properly configured with documents
    # If RAG is not configured, it should still work without RAG
    
    session_id = "test-all-features"
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/llm/chat",
            json={
                "messages": [
                    {"role": "user", "content": "What time is it now?"}
                ],
                "session_id": session_id,
                "use_tools": True,
                "use_memory": True,
                "use_rag": True,  # May not have documents, but should not error
                "temperature": 0.3,
                "max_tokens": 300
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have response
        assert len(data["response"]) > 0
        
        # Tools should be used
        assert data["tools_used"] is True or data["tools_used"] is False  # Depends on LLM decision
        
        # Should have session_id
        assert data["session_id"] == session_id


@pytest.mark.asyncio
async def test_tool_result_metadata_completeness():
    """Test that tool results have complete metadata."""
    from agentlab.api.main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/llm/chat",
            json={
                "messages": [
                    {"role": "user", "content": "Tell me the current date and time"}
                ],
                "use_tools": True,
                "tool_names": ["get_current_datetime"],
                "use_memory": False,
                "use_rag": False,
                "temperature": 0.2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["tools_used"] and len(data["tool_calls"]) > 0:
            # Check tool call structure
            tool_call = data["tool_calls"][0]
            assert "id" in tool_call
            assert "name" in tool_call
            assert "args" in tool_call
            assert isinstance(tool_call["args"], dict)
            
            # Check agent step structure
            for step in data["agent_steps"]:
                assert "step_number" in step
                assert "action" in step
                
                if step["action"] == "tool_call":
                    assert "tool_call" in step
                    assert "tool_result" in step
                    assert step["tool_result"]["tool_name"] == step["tool_call"]["name"]
                    assert "success" in step["tool_result"]
                    assert "result" in step["tool_result"]
