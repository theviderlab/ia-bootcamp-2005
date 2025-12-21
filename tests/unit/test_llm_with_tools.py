"""
Unit tests for LLM tool calling functionality.

Tests the chat_with_tools method of LangChainLLM with mocked tools and LLM responses.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from agentlab.core.llm_interface import LangChainLLM
from agentlab.models import ChatMessage, ToolCall, ToolResult, AgentStep


@pytest.fixture
def llm():
    """Create LangChainLLM instance with valid API key."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        return LangChainLLM()


@pytest.fixture
def sample_messages():
    """Sample chat messages for testing."""
    return [
        ChatMessage(
            role="user",
            content="What time is it?",
            timestamp=datetime.now()
        )
    ]


@pytest.mark.asyncio
async def test_chat_with_tools_basic_flow(llm, sample_messages):
    """Test basic flow with single tool call and final answer."""
    # Mock tool registry
    mock_tool = Mock()
    mock_tool.execute = AsyncMock(return_value={
        "success": True,
        "datetime": "2025-12-21T10:30:00",
        "format": "iso"
    })
    
    mock_registry = Mock()
    mock_registry.get_tool.return_value = mock_tool
    mock_registry.get_langchain_tools.return_value = [Mock()]
    
    # Mock LLM responses
    mock_tool_call_response = Mock()
    mock_tool_call_response.tool_calls = [
        {
            "id": "call_123",
            "name": "get_current_datetime",
            "args": {"format": "iso"}
        }
    ]
    mock_tool_call_response.content = ""
    
    mock_final_response = Mock()
    mock_final_response.tool_calls = []
    mock_final_response.content = "It is currently 10:30 AM on December 21, 2025."
    
    with patch("agentlab.core.llm_interface.get_registry", return_value=mock_registry):
        with patch("agentlab.core.llm_interface.ChatOpenAI") as mock_chat_openai:
            mock_llm_instance = Mock()
            mock_llm_instance.bind_tools.return_value = mock_llm_instance
            mock_llm_instance.ainvoke = AsyncMock(
                side_effect=[mock_tool_call_response, mock_final_response]
            )
            mock_chat_openai.return_value = mock_llm_instance
            
            # Execute
            response, agent_steps, tool_results = await llm.chat_with_tools(
                sample_messages,
                tool_names=["get_current_datetime"]
            )
            
            # Assertions
            assert response == "It is currently 10:30 AM on December 21, 2025."
            assert len(agent_steps) == 2
            assert agent_steps[0].action == "tool_call"
            assert agent_steps[0].tool_call.name == "get_current_datetime"
            assert agent_steps[1].action == "final_answer"
            
            assert len(tool_results) == 1
            assert tool_results[0].success is True
            assert tool_results[0].tool_name == "get_current_datetime"


@pytest.mark.asyncio
async def test_chat_with_tools_no_tools_available(llm, sample_messages):
    """Test error handling when no tools are available."""
    mock_registry = Mock()
    mock_registry.get_langchain_tools.return_value = []
    mock_registry.list_tools.return_value = []
    
    with patch("agentlab.core.llm_interface.get_registry", return_value=mock_registry):
        with pytest.raises(ValueError, match="No tools available"):
            await llm.chat_with_tools(sample_messages)


@pytest.mark.asyncio
async def test_chat_with_tools_immediate_answer(llm, sample_messages):
    """Test when LLM provides answer without using tools."""
    mock_registry = Mock()
    mock_registry.get_langchain_tools.return_value = [Mock()]
    
    mock_response = Mock()
    mock_response.tool_calls = []
    mock_response.content = "I don't need tools to answer that."
    
    with patch("agentlab.core.llm_interface.get_registry", return_value=mock_registry):
        with patch("agentlab.core.llm_interface.ChatOpenAI") as mock_chat_openai:
            mock_llm_instance = Mock()
            mock_llm_instance.bind_tools.return_value = mock_llm_instance
            mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
            mock_chat_openai.return_value = mock_llm_instance
            
            response, agent_steps, tool_results = await llm.chat_with_tools(sample_messages)
            
            assert response == "I don't need tools to answer that."
            assert len(agent_steps) == 1
            assert agent_steps[0].action == "final_answer"
            assert len(tool_results) == 0


@pytest.mark.asyncio
async def test_chat_with_tools_multiple_calls(llm, sample_messages):
    """Test multiple tool calls in sequence."""
    mock_tool = Mock()
    mock_tool.execute = AsyncMock(side_effect=[
        {"success": True, "result": "data1"},
        {"success": True, "result": "data2"}
    ])
    
    mock_registry = Mock()
    mock_registry.get_tool.return_value = mock_tool
    mock_registry.get_langchain_tools.return_value = [Mock()]
    
    # Three responses: 2 tool calls + 1 final answer
    mock_tool_response_1 = Mock()
    mock_tool_response_1.tool_calls = [
        {"id": "call_1", "name": "tool_a", "args": {}}
    ]
    mock_tool_response_1.content = ""
    
    mock_tool_response_2 = Mock()
    mock_tool_response_2.tool_calls = [
        {"id": "call_2", "name": "tool_b", "args": {}}
    ]
    mock_tool_response_2.content = ""
    
    mock_final = Mock()
    mock_final.tool_calls = []
    mock_final.content = "Final answer using both tools."
    
    with patch("agentlab.core.llm_interface.get_registry", return_value=mock_registry):
        with patch("agentlab.core.llm_interface.ChatOpenAI") as mock_chat_openai:
            mock_llm_instance = Mock()
            mock_llm_instance.bind_tools.return_value = mock_llm_instance
            mock_llm_instance.ainvoke = AsyncMock(
                side_effect=[mock_tool_response_1, mock_tool_response_2, mock_final]
            )
            mock_chat_openai.return_value = mock_llm_instance
            
            response, agent_steps, tool_results = await llm.chat_with_tools(sample_messages)
            
            assert len(agent_steps) == 3  # 2 tool calls + 1 final answer
            assert len(tool_results) == 2
            assert all(step.action == "tool_call" for step in agent_steps[:2])
            assert agent_steps[2].action == "final_answer"


@pytest.mark.asyncio
async def test_chat_with_tools_max_iterations(llm, sample_messages):
    """Test max iterations guard to prevent infinite loops."""
    mock_tool = Mock()
    mock_tool.execute = AsyncMock(return_value={"success": True, "data": "result"})
    
    mock_registry = Mock()
    mock_registry.get_tool.return_value = mock_tool
    mock_registry.get_langchain_tools.return_value = [Mock()]
    
    # Always return tool calls (simulating infinite loop)
    mock_tool_response = Mock()
    mock_tool_response.tool_calls = [
        {"id": "call_loop", "name": "tool", "args": {}}
    ]
    mock_tool_response.content = ""
    
    # Final forced response after max iterations
    mock_forced_final = Mock()
    mock_forced_final.content = "Forced final answer after max iterations."
    
    with patch("agentlab.core.llm_interface.get_registry", return_value=mock_registry):
        with patch("agentlab.core.llm_interface.ChatOpenAI") as mock_chat_openai:
            mock_llm_instance = Mock()
            mock_llm_instance.bind_tools.return_value = mock_llm_instance
            # Return tool calls for max_iterations (3 times), then final forced response
            mock_llm_instance.ainvoke = AsyncMock(
                side_effect=[mock_tool_response, mock_tool_response, mock_tool_response, mock_forced_final]
            )
            mock_chat_openai.return_value = mock_llm_instance
            
            response, agent_steps, tool_results = await llm.chat_with_tools(
                sample_messages,
                max_iterations=3
            )
            
            # Should have final answer step with max iterations reasoning
            assert any("Max iterations" in (step.reasoning or "") for step in agent_steps)
            # Should have 3 tool call steps + 1 final answer step
            assert len(agent_steps) == 4


@pytest.mark.asyncio
async def test_chat_with_tools_tool_not_found(llm, sample_messages):
    """Test handling of tool not found in registry."""
    mock_registry = Mock()
    mock_registry.get_tool.return_value = None  # Tool not found
    mock_registry.get_langchain_tools.return_value = [Mock()]
    
    mock_tool_call_response = Mock()
    mock_tool_call_response.tool_calls = [
        {"id": "call_123", "name": "nonexistent_tool", "args": {}}
    ]
    mock_tool_call_response.content = ""
    
    mock_final_response = Mock()
    mock_final_response.tool_calls = []
    mock_final_response.content = "Tool not available."
    
    with patch("agentlab.core.llm_interface.get_registry", return_value=mock_registry):
        with patch("agentlab.core.llm_interface.ChatOpenAI") as mock_chat_openai:
            mock_llm_instance = Mock()
            mock_llm_instance.bind_tools.return_value = mock_llm_instance
            mock_llm_instance.ainvoke = AsyncMock(
                side_effect=[mock_tool_call_response, mock_final_response]
            )
            mock_chat_openai.return_value = mock_llm_instance
            
            response, agent_steps, tool_results = await llm.chat_with_tools(sample_messages)
            
            assert len(tool_results) == 1
            assert tool_results[0].success is False
            assert "not found" in tool_results[0].error.lower()


@pytest.mark.asyncio
async def test_chat_with_tools_tool_execution_error(llm, sample_messages):
    """Test handling of tool execution errors."""
    mock_tool = Mock()
    mock_tool.execute = AsyncMock(side_effect=RuntimeError("Tool crashed"))
    
    mock_registry = Mock()
    mock_registry.get_tool.return_value = mock_tool
    mock_registry.get_langchain_tools.return_value = [Mock()]
    
    mock_tool_call_response = Mock()
    mock_tool_call_response.tool_calls = [
        {"id": "call_123", "name": "buggy_tool", "args": {}}
    ]
    mock_tool_call_response.content = ""
    
    mock_final_response = Mock()
    mock_final_response.tool_calls = []
    mock_final_response.content = "Tool failed, but I can still answer."
    
    with patch("agentlab.core.llm_interface.get_registry", return_value=mock_registry):
        with patch("agentlab.core.llm_interface.ChatOpenAI") as mock_chat_openai:
            mock_llm_instance = Mock()
            mock_llm_instance.bind_tools.return_value = mock_llm_instance
            mock_llm_instance.ainvoke = AsyncMock(
                side_effect=[mock_tool_call_response, mock_final_response]
            )
            mock_chat_openai.return_value = mock_llm_instance
            
            response, agent_steps, tool_results = await llm.chat_with_tools(sample_messages)
            
            assert len(tool_results) == 1
            assert tool_results[0].success is False
            assert "Tool crashed" in tool_results[0].error


@pytest.mark.asyncio
async def test_chat_with_tools_validation_errors(llm):
    """Test parameter validation."""
    # Empty messages
    with pytest.raises(ValueError, match="empty"):
        await llm.chat_with_tools([])
    
    # Invalid max_iterations
    with pytest.raises(ValueError, match="max_iterations"):
        await llm.chat_with_tools(
            [ChatMessage(role="user", content="test", timestamp=datetime.now())],
            max_iterations=0
        )


@pytest.mark.asyncio
async def test_chat_with_tools_metadata_tracking(llm, sample_messages):
    """Test that tool calls and results have proper metadata."""
    mock_tool = Mock()
    mock_tool.execute = AsyncMock(return_value={"success": True, "value": 42})
    
    mock_registry = Mock()
    mock_registry.get_tool.return_value = mock_tool
    mock_registry.get_langchain_tools.return_value = [Mock()]
    
    mock_tool_call_response = Mock()
    mock_tool_call_response.tool_calls = [
        {"id": "call_xyz", "name": "test_tool", "args": {"param": "value"}}
    ]
    mock_tool_call_response.content = ""
    
    mock_final_response = Mock()
    mock_final_response.tool_calls = []
    mock_final_response.content = "Done."
    
    with patch("agentlab.core.llm_interface.get_registry", return_value=mock_registry):
        with patch("agentlab.core.llm_interface.ChatOpenAI") as mock_chat_openai:
            mock_llm_instance = Mock()
            mock_llm_instance.bind_tools.return_value = mock_llm_instance
            mock_llm_instance.ainvoke = AsyncMock(
                side_effect=[mock_tool_call_response, mock_final_response]
            )
            mock_chat_openai.return_value = mock_llm_instance
            
            response, agent_steps, tool_results = await llm.chat_with_tools(sample_messages)
            
            # Check ToolCall metadata
            tool_call = agent_steps[0].tool_call
            assert tool_call.id == "call_xyz"
            assert tool_call.name == "test_tool"
            assert tool_call.args == {"param": "value"}
            assert tool_call.timestamp is not None
            
            # Check ToolResult metadata
            tool_result = tool_results[0]
            assert tool_result.tool_call_id == "call_xyz"
            assert tool_result.tool_name == "test_tool"
            assert tool_result.success is True
            assert tool_result.result == {"success": True, "value": 42}
            assert tool_result.timestamp is not None
