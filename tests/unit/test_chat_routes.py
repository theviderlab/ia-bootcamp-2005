"""
Unit tests for chat_routes module.

Tests API endpoints for LLM text generation and chat.

NOTE: RAG endpoint tests moved to test_rag_routes.py
NOTE: Memory endpoint tests moved to test_memory_routes.py
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from agentlab.api.main import app
from agentlab.api.routes import chat_routes

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_global_instances():
    """Reset global LLM instance before each test."""
    chat_routes._llm_instance = None
    chat_routes._rag_instance = None
    chat_routes._memory_instance = None
    yield
    chat_routes._llm_instance = None
    chat_routes._rag_instance = None
    chat_routes._memory_instance = None


@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_generate_endpoint_success(mock_llm_class):
    """Test successful text generation."""
    mock_llm = Mock()
    mock_llm.generate.return_value = "Generated response text"
    mock_llm_class.return_value = mock_llm
    
    response = client.post(
        "/llm/generate",
        json={
            "prompt": "Tell me a joke",
            "temperature": 0.7,
            "max_tokens": 100
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Generated response text"
    assert data["prompt"] == "Tell me a joke"
    
    mock_llm.generate.assert_called_once_with(
        prompt="Tell me a joke",
        temperature=0.7,
        max_tokens=100
    )


@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_generate_endpoint_with_defaults(mock_llm_class):
    """Test generation with default parameters."""
    mock_llm = Mock()
    mock_llm.generate.return_value = "Generated response text"
    mock_llm_class.return_value = mock_llm
    
    response = client.post(
        "/llm/generate",
        json={"prompt": "Hello"}
    )
    
    assert response.status_code == 200
    mock_llm.generate.assert_called_once_with(
        prompt="Hello",
        temperature=0.7,
        max_tokens=1000
    )


@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_generate_endpoint_empty_prompt(mock_llm_class):
    """Test generation with empty prompt."""
    mock_llm = Mock()
    mock_llm.generate.side_effect = ValueError("Prompt cannot be empty")
    mock_llm_class.return_value = mock_llm
    
    response = client.post(
        "/llm/generate",
        json={"prompt": ""}
    )
    
    assert response.status_code == 422  # Validation error


@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_chat_endpoint_success(mock_llm_class):
    """Test successful chat conversation."""
    mock_llm = Mock()
    mock_llm.chat.return_value = "Chat response text"
    mock_llm_class.return_value = mock_llm
    
    response = client.post(
        "/llm/chat",
        json={
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"}
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Chat response text"
    assert "session_id" in data
    
    mock_llm.chat.assert_called_once()


@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_chat_endpoint_with_session_id(mock_llm_class):
    """Test chat with existing session ID."""
    mock_llm = Mock()
    mock_llm.chat.return_value = "Chat response text"
    mock_llm_class.return_value = mock_llm
    session_id = "test-session-123"
    
    response = client.post(
        "/llm/chat",
        json={
            "messages": [{"role": "user", "content": "Hello"}],
            "session_id": session_id
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id


@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_chat_endpoint_invalid_role(mock_llm_class):
    """Test chat with invalid message role."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    response = client.post(
        "/llm/chat",
        json={
            "messages": [{"role": "invalid", "content": "Hello"}]
        }
    )
    
    assert response.status_code == 422
    assert "Invalid role" in response.json()["detail"]


@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_chat_endpoint_missing_content(mock_llm_class):
    """Test chat with missing message content."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    response = client.post(
        "/llm/chat",
        json={
            "messages": [{"role": "user"}]
        }
    )
    
    assert response.status_code == 422


@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_chat_endpoint_empty_messages(mock_llm_class):
    """Test chat with empty messages list."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    response = client.post(
        "/llm/chat",
        json={"messages": []}
    )
    
    assert response.status_code == 422  # Validation error


@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_chat_endpoint_with_custom_parameters(mock_llm_class):
    """Test chat with custom temperature and max_tokens."""
    mock_llm = Mock()
    mock_llm.chat.return_value = "Chat response text"
    mock_llm_class.return_value = mock_llm
    
    response = client.post(
        "/llm/chat",
        json={
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.3,
            "max_tokens": 200
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Chat response text"
    
    # Verify that the custom parameters were passed to llm.chat()
    mock_llm.chat.assert_called_once()
    call_args = mock_llm.chat.call_args
    assert call_args.kwargs["temperature"] == 0.3
    assert call_args.kwargs["max_tokens"] == 200


@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_chat_endpoint_with_default_parameters(mock_llm_class):
    """Test chat uses default temperature and max_tokens."""
    mock_llm = Mock()
    mock_llm.chat.return_value = "Chat response text"
    mock_llm_class.return_value = mock_llm
    
    response = client.post(
        "/llm/chat",
        json={
            "messages": [{"role": "user", "content": "Hello"}]
        }
    )
    
    assert response.status_code == 200
    
    # Verify default parameters are used
    mock_llm.chat.assert_called_once()
    call_args = mock_llm.chat.call_args
    assert call_args.kwargs["temperature"] == 0.7
    assert call_args.kwargs["max_tokens"] == 500
