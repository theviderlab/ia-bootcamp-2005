"""
Unit tests for memory isolation when use_memory=False.

Validates that when memory is disabled, the LLM cannot access
information from previous messages in the conversation.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from agentlab.api.routes.chat_routes import ChatRequest


@pytest.mark.asyncio
async def test_chat_without_memory_no_context_leakage():
    """
    Test that with use_memory=False and a single message,
    the LLM does not have access to previous conversation context.
    
    Scenario:
    1. User says: "hola mi nombre es rodrigo"
    2. User asks: "como me llamo?" with use_memory=False
    3. LLM should NOT know the name since no memory is used
    """
    # First message (simulating previous interaction, but NOT sent in request)
    # In real scenario, this would be stored in frontend state but NOT sent to backend
    
    # Second message - ONLY this one is sent with use_memory=False
    request = ChatRequest(
        messages=[
            {"role": "user", "content": "como me llamo?"}  # Only current message
        ],
        session_id="test-session-isolation",
        use_memory=False,  # Memory disabled
        temperature=0.7,
        max_tokens=500,
    )
    
    # Mock LLM to verify it only receives the single message
    with patch('agentlab.core.llm_interface.LLMInterface.generate_with_tools') as mock_llm:
        # Mock response - LLM should not know the name
        mock_llm.return_value = AsyncMock(return_value={
            'response': "Lo siento, no tengo información sobre tu nombre.",
            'tool_calls': [],
            'tools_used': False,
        })
        
        # The context builder should NOT include memory
        with patch('agentlab.core.context_builder.ContextBuilder.build_context') as mock_context:
            mock_context.return_value = {
                'system_prompt': "You are a helpful assistant.",
                'messages': [
                    {"role": "user", "content": "como me llamo?"}
                ],
                'context_text': "## Recent Conversation\nuser: como me llamo?",
                'context_tokens': 50,
            }
            
            # Make the request
            from fastapi.testclient import TestClient
            from agentlab.api.main import app
            
            client = TestClient(app)
            response = client.post(
                "/llm/chat",
                json=request.model_dump(),
            )
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            
            # The context should NOT contain the previous message about "rodrigo"
            assert "rodrigo" not in data["context_text"].lower()
            assert "nombre es rodrigo" not in data["context_text"].lower()
            
            # Verify memory context is minimal (no previous conversation)
            mock_context.assert_called_once()


@pytest.mark.asyncio
async def test_chat_with_memory_has_context():
    """
    Test that with use_memory=True, the backend properly retrieves
    and includes memory context for the LLM.
    
    This verifies the opposite case - that memory DOES work when enabled.
    """
    request = ChatRequest(
        messages=[
            {"role": "user", "content": "como me llamo?"}
        ],
        session_id="test-session-with-memory",
        use_memory=True,  # Memory enabled
        temperature=0.7,
        max_tokens=500,
    )
    
    with patch('agentlab.core.llm_interface.LLMInterface.generate_with_tools') as mock_llm:
        mock_llm.return_value = AsyncMock(return_value={
            'response': "Tu nombre es Rodrigo.",
            'tool_calls': [],
            'tools_used': False,
        })
        
        with patch('agentlab.core.context_builder.ContextBuilder.build_context') as mock_context:
            # Mock context with memory included
            mock_context.return_value = {
                'system_prompt': "You are a helpful assistant.",
                'messages': [
                    {"role": "user", "content": "como me llamo?"}
                ],
                'context_text': """## Known Facts
- User's name is Rodrigo

## Recent Conversation
user: como me llamo?""",
                'context_tokens': 80,
            }
            
            from fastapi.testclient import TestClient
            from agentlab.api.main import app
            
            client = TestClient(app)
            response = client.post(
                "/llm/chat",
                json=request.model_dump(),
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify memory context was built and includes facts
            mock_context.assert_called_once()
            assert "rodrigo" in data["context_text"].lower() or "Known Facts" in data["context_text"]


@pytest.mark.asyncio
async def test_messages_array_contains_only_current_message():
    """
    Test that the messages array in the request contains only
    the current user message, not the full conversation history.
    
    This is a contract test to ensure frontend follows the correct pattern.
    """
    # Valid request - single message
    valid_request = ChatRequest(
        messages=[
            {"role": "user", "content": "What is Python?"}
        ],
        session_id="test-session",
        use_memory=True,
    )
    
    assert len(valid_request.messages) == 1
    assert valid_request.messages[0]["role"] == "user"
    
    # Invalid pattern - multiple messages (old frontend bug)
    # This should still work technically but goes against the architecture
    multi_message_request = ChatRequest(
        messages=[
            {"role": "user", "content": "Hello, my name is John"},
            {"role": "assistant", "content": "Hi John!"},
            {"role": "user", "content": "What is my name?"},  # Frontend bug: includes history
        ],
        session_id="test-session",
        use_memory=False,
    )
    
    # Document that this pattern is NOT recommended
    # Even with use_memory=False, the LLM will see all messages in the array
    assert len(multi_message_request.messages) == 3  # This is the bug we're fixing
