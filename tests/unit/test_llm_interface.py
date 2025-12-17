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


def test_init_with_custom_temperature_and_max_tokens(mock_chat_openai):
    """Test LLM initialization with custom temperature and max_tokens."""
    llm = LangChainLLM(
        api_key="test-key",
        temperature=0.5,
        max_tokens=500
    )
    
    assert llm.temperature == 0.5
    assert llm.max_tokens == 500


def test_init_with_default_parameters(mock_chat_openai):
    """Test LLM initialization with default temperature and max_tokens."""
    llm = LangChainLLM(api_key="test-key")
    
    assert llm.temperature == 0.7
    assert llm.max_tokens == 1000


def test_init_invalid_temperature_raises():
    """Test that invalid temperature raises ValueError."""
    with pytest.raises(ValueError, match="temperature must be between 0.0 and 1.0"):
        LangChainLLM(api_key="test-key", temperature=1.5)
    
    with pytest.raises(ValueError, match="temperature must be between 0.0 and 1.0"):
        LangChainLLM(api_key="test-key", temperature=-0.1)


def test_init_invalid_max_tokens_raises():
    """Test that invalid max_tokens raises ValueError."""
    with pytest.raises(ValueError, match="max_tokens must be between 1 and 4000"):
        LangChainLLM(api_key="test-key", max_tokens=0)
    
    with pytest.raises(ValueError, match="max_tokens must be between 1 and 4000"):
        LangChainLLM(api_key="test-key", max_tokens=5000)


def test_generate_with_instance_defaults(mock_chat_openai):
    """Test generate() uses instance default parameters."""
    mock_response = Mock()
    mock_response.content = "Response"
    mock_chat_openai.invoke.return_value = mock_response
    
    llm = LangChainLLM(api_key="test-key", temperature=0.3, max_tokens=200)
    result = llm.generate("Test prompt")
    
    assert result == "Response"


def test_generate_with_override_parameters(mock_chat_openai):
    """Test generate() with override parameters."""
    mock_response = Mock()
    mock_response.content = "Response"
    mock_chat_openai.invoke.return_value = mock_response
    
    llm = LangChainLLM(api_key="test-key", temperature=0.7, max_tokens=1000)
    result = llm.generate("Test prompt", temperature=0.2, max_tokens=100)
    
    assert result == "Response"


def test_generate_invalid_temperature_raises():
    """Test generate() with invalid temperature raises ValueError."""
    llm = LangChainLLM(api_key="test-key")
    
    with pytest.raises(ValueError, match="temperature must be between 0.0 and 1.0"):
        llm.generate("Test", temperature=2.0)


def test_generate_invalid_max_tokens_raises():
    """Test generate() with invalid max_tokens raises ValueError."""
    llm = LangChainLLM(api_key="test-key")
    
    with pytest.raises(ValueError, match="max_tokens must be between 1 and 4000"):
        llm.generate("Test", max_tokens=-10)


def test_chat_with_instance_defaults(mock_chat_openai):
    """Test chat() uses instance default parameters."""
    mock_response = Mock()
    mock_response.content = "Chat response"
    mock_chat_openai.invoke.return_value = mock_response
    
    messages = [
        ChatMessage(role="user", content="Hello", timestamp=datetime.now())
    ]
    
    llm = LangChainLLM(api_key="test-key", temperature=0.3, max_tokens=200)
    result = llm.chat(messages)
    
    assert result == "Chat response"


def test_chat_with_override_parameters(mock_chat_openai):
    """Test chat() with override parameters."""
    mock_response = Mock()
    mock_response.content = "Chat response"
    mock_chat_openai.invoke.return_value = mock_response
    
    messages = [
        ChatMessage(role="user", content="Hello", timestamp=datetime.now())
    ]
    
    llm = LangChainLLM(api_key="test-key", temperature=0.7, max_tokens=1000)
    result = llm.chat(messages, temperature=0.2, max_tokens=100)
    
    assert result == "Chat response"


def test_chat_invalid_temperature_raises():
    """Test chat() with invalid temperature raises ValueError."""
    llm = LangChainLLM(api_key="test-key")
    messages = [ChatMessage(role="user", content="Hello", timestamp=datetime.now())]
    
    with pytest.raises(ValueError, match="temperature must be between 0.0 and 1.0"):
        llm.chat(messages, temperature=1.5)


def test_chat_invalid_max_tokens_raises():
    """Test chat() with invalid max_tokens raises ValueError."""
    llm = LangChainLLM(api_key="test-key")
    messages = [ChatMessage(role="user", content="Hello", timestamp=datetime.now())]
    
    with pytest.raises(ValueError, match="max_tokens must be between 1 and 4000"):
        llm.chat(messages, max_tokens=5000)
