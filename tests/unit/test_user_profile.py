"""
Unit tests for user profile functionality.

Tests profile extraction, storage, and retrieval.
"""

import json
from unittest.mock import Mock, patch

import pytest

from agentlab.agents.memory_processor import LongTermMemoryProcessor
from agentlab.config.memory_config import MemoryConfig
from agentlab.models import ChatMessage


@pytest.fixture
def mock_config():
    """Create mock memory configuration."""
    return MemoryConfig(
        openai_api_key="test-key",
        enable_long_term=True,
        enable_profile=True,
        semantic_storage="mysql",
    )


@pytest.fixture
def mock_llm():
    """Create mock LLM."""
    llm = Mock()
    response = Mock()
    response.content = json.dumps({
        "user_name": "John",
        "age": 30,
        "interests": ["Python", "AI", "Machine Learning"],
        "occupation": "Software Engineer",
        "expertise_areas": ["Backend Development", "Data Science"],
    })
    llm.invoke.return_value = response
    return llm


@pytest.fixture
def sample_messages():
    """Create sample chat messages."""
    return [
        ChatMessage(
            role="user",
            content="Hi, I'm John. I'm a software engineer.",
            timestamp=None,
        ),
        ChatMessage(
            role="assistant",
            content="Nice to meet you John! What kind of software do you work on?",
            timestamp=None,
        ),
        ChatMessage(
            role="user",
            content="I specialize in backend development and data science. I love working with Python.",
            timestamp=None,
        ),
        ChatMessage(
            role="assistant",
            content="That's great! Python is excellent for both areas.",
            timestamp=None,
        ),
        ChatMessage(
            role="user",
            content="Yes! I'm particularly interested in AI and machine learning applications.",
            timestamp=None,
        ),
    ]


def test_load_profile_schema(mock_config):
    """Test loading profile schema from file."""
    processor = LongTermMemoryProcessor(config=mock_config)
    
    assert processor.profile_schema is not None
    assert "name" in processor.profile_schema
    assert "parameters" in processor.profile_schema
    assert "properties" in processor.profile_schema["parameters"]


def test_extract_profile_from_messages(mock_config, mock_llm, sample_messages):
    """Test profile extraction from messages."""
    processor = LongTermMemoryProcessor(config=mock_config)
    processor.llm = mock_llm
    
    profile = processor.extract_profile_from_messages(sample_messages)
    
    assert profile is not None
    assert profile["user_name"] == "John"
    assert profile["age"] == 30
    assert "Python" in profile["interests"]
    assert profile["occupation"] == "Software Engineer"
    
    # Verify LLM was called
    mock_llm.invoke.assert_called_once()


def test_extract_profile_with_existing_profile(mock_config, mock_llm, sample_messages):
    """Test profile extraction in patch mode."""
    processor = LongTermMemoryProcessor(config=mock_config)
    processor.llm = mock_llm
    
    existing_profile = {
        "user_name": "John",
        "age": 29,
        "home": "San Francisco",
    }
    
    # Mock LLM to return updated age
    mock_llm.invoke.return_value.content = json.dumps({
        "age": 30,
        "interests": ["Python", "AI"],
    })
    
    profile = processor.extract_profile_from_messages(sample_messages, existing_profile)
    
    # Should merge with existing profile
    assert profile["user_name"] == "John"  # Kept from existing
    assert profile["age"] == 30  # Updated
    assert profile["home"] == "San Francisco"  # Kept from existing
    assert "Python" in profile["interests"]  # Added


def test_extract_profile_handles_json_with_markdown(mock_config, mock_llm, sample_messages):
    """Test profile extraction handles markdown code blocks."""
    processor = LongTermMemoryProcessor(config=mock_config)
    processor.llm = mock_llm
    
    # Mock LLM to return JSON wrapped in markdown
    mock_llm.invoke.return_value.content = """```json
{
    "user_name": "John",
    "age": 30
}
```"""
    
    profile = processor.extract_profile_from_messages(sample_messages)
    
    assert profile["user_name"] == "John"
    assert profile["age"] == 30


def test_extract_profile_handles_invalid_json(mock_config, mock_llm, sample_messages):
    """Test profile extraction handles invalid JSON gracefully."""
    processor = LongTermMemoryProcessor(config=mock_config)
    processor.llm = mock_llm
    
    # Mock LLM to return invalid JSON
    mock_llm.invoke.return_value.content = "Not valid JSON"
    
    profile = processor.extract_profile_from_messages(sample_messages)
    
    # Should return empty dict on error
    assert profile == {}


def test_extract_profile_without_llm(mock_config, sample_messages):
    """Test profile extraction without LLM returns empty."""
    config = MemoryConfig(
        enable_long_term=True,
        enable_profile=True,
        semantic_storage="mysql",
    )
    processor = LongTermMemoryProcessor(config=config)
    
    profile = processor.extract_profile_from_messages(sample_messages)
    
    assert profile == {}


@patch("agentlab.agents.memory_processor.db_get_user_profile")
def test_get_user_profile_loads_from_db(mock_db_get, mock_config):
    """Test get_user_profile loads from database."""
    processor = LongTermMemoryProcessor(config=mock_config)
    
    # Mock database return
    mock_db_get.return_value = {
        "id": 1,
        "profile_data": {"user_name": "John", "age": 30},
        "version": 1,
    }
    
    profile = processor.get_user_profile()
    
    assert profile["user_name"] == "John"
    assert profile["age"] == 30
    mock_db_get.assert_called_once()


@patch("agentlab.agents.memory_processor.db_get_user_profile")
def test_get_user_profile_returns_empty_if_not_exists(mock_db_get, mock_config):
    """Test get_user_profile returns empty dict if no profile exists."""
    processor = LongTermMemoryProcessor(config=mock_config)
    
    # Mock database return None
    mock_db_get.return_value = None
    
    profile = processor.get_user_profile()
    
    assert profile == {}
    mock_db_get.assert_called_once()


@patch("agentlab.agents.memory_processor.db_create_or_update_user_profile")
@patch("agentlab.agents.memory_processor.db_get_user_profile")
@patch("agentlab.agents.memory_processor.get_chat_history")
def test_extract_and_store_profile(
    mock_get_history, mock_db_get, mock_db_create, mock_config, mock_llm, sample_messages
):
    """Test extract_and_store_profile full workflow."""
    processor = LongTermMemoryProcessor(config=mock_config)
    processor.llm = mock_llm
    
    # Mock no existing profile
    mock_db_get.return_value = None
    
    # Mock chat history
    mock_get_history.return_value = [
        {
            "id": i + 1,
            "role": msg.role,
            "content": msg.content,
            "created_at": None,
            "metadata": None,
        }
        for i, msg in enumerate(sample_messages)
    ]
    
    profile = processor.extract_and_store_profile("test-session", incremental=False)
    
    assert profile["user_name"] == "John"
    assert profile["age"] == 30
    
    # Verify database was called
    mock_db_create.assert_called_once()
    call_args = mock_db_create.call_args
    assert call_args[0][0]["user_name"] == "John"
    assert call_args[0][1] == 5  # Last message ID


def test_profile_schema_allows_extensibility(mock_config):
    """Test that profile schema supports additional fields."""
    processor = LongTermMemoryProcessor(config=mock_config)
    
    schema = processor.profile_schema
    instructions = schema.get("instructions", "")
    
    # Verify schema encourages extensibility
    assert "additional" in instructions.lower() or "add" in instructions.lower()
