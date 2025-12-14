"""Unit tests for LLM interface."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from agentlab.core.llm_interface import LangChainLLM
from agentlab.models import ChatMessage


@pytest.fixture
def mock_chat_openai():
    """Create a mock ChatOpenAI instance."""
    with patch("agentlab.core.llm_interface.ChatOpenAI") as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance


def test_init_with_api_key(mock_chat_openai):
    """Test LLM initialization with explicit API key."""
    llm = LangChainLLM(model_name="gpt-4", api_key="test-key-123")
    
    assert llm.model_name == "gpt-4"
    assert llm.api_key == "test-key-123"


def test_init_without_api_key_raises():
    """Test LLM initialization without API key raises error."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            LangChainLLM()


def test_generate_success(mock_chat_openai):
    """Test successful text generation."""
    mock_response = Mock()
    mock_response.content = "Generated response text"
    mock_chat_openai.invoke.return_value = mock_response
    
    llm = LangChainLLM(api_key="test-key")
    result = llm.generate("Test prompt")
    
    assert result == "Generated response text"
    assert mock_chat_openai.invoke.called


def test_generate_empty_prompt_raises():
    """Test that empty prompt raises ValueError."""
    llm = LangChainLLM(api_key="test-key")
    
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        llm.generate("")


def test_chat_success(mock_chat_openai):
    """Test successful chat generation."""
    mock_response = Mock()
    mock_response.content = "Chat response"
    mock_chat_openai.invoke.return_value = mock_response
    
    messages = [
        ChatMessage(
            role="user",
            content="Hello",
            timestamp=datetime.now()
        ),
        ChatMessage(
            role="assistant",
            content="Hi there!",
            timestamp=datetime.now()
        ),
    ]
    
    llm = LangChainLLM(api_key="test-key")
    result = llm.chat(messages)
    
    assert result == "Chat response"
    assert mock_chat_openai.invoke.called


def test_chat_empty_messages_raises():
    """Test that empty messages list raises ValueError."""
    llm = LangChainLLM(api_key="test-key")
    
    with pytest.raises(ValueError, match="Messages list cannot be empty"):
        llm.chat([])


def test_convert_messages():
    """Test message conversion from ChatMessage to LangChain format."""
    messages = [
        ChatMessage(role="system", content="You are helpful", timestamp=datetime.now()),
        ChatMessage(role="user", content="Hello", timestamp=datetime.now()),
        ChatMessage(role="assistant", content="Hi!", timestamp=datetime.now()),
    ]
    
    llm = LangChainLLM(api_key="test-key")
    converted = llm._convert_messages(messages)
    
    assert len(converted) == 3
    assert converted[0].content == "You are helpful"
    assert converted[1].content == "Hello"
    assert converted[2].content == "Hi!"
