"""
Unit tests for memory_routes module.

Tests API endpoints for memory management and context retrieval.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from agentlab.api.main import app
from agentlab.api.routes import memory_routes

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_global_instances():
    """Reset global LLM and memory instances before each test."""
    memory_routes._llm_instance = None
    memory_routes._memory_instance = None
    yield
    memory_routes._llm_instance = None
    memory_routes._memory_instance = None


# ============================================================================
# Memory Context Tests
# ============================================================================


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_get_memory_context_success(mock_llm_class, mock_memory_class):
    """Test successful memory context retrieval."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory = Mock()
    mock_context = Mock()
    mock_context.session_id = "test-session"
    mock_context.short_term_context = "Recent conversation"
    mock_context.semantic_facts = ["User likes Python", "User works with AI"]
    mock_context.user_profile = {"name": "Test User", "expertise": "Python"}
    mock_context.episodic_summary = "User asked about ML topics"
    mock_context.procedural_patterns = ["Always asks for examples"]
    mock_context.total_messages = 10
    mock_memory.get_context.return_value = mock_context
    mock_memory_class.return_value = mock_memory
    
    response = client.post(
        "/llm/memory/context",
        json={
            "session_id": "test-session",
            "max_tokens": 2000
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-session"
    assert data["short_term_context"] == "Recent conversation"
    assert len(data["semantic_facts"]) == 2
    assert data["user_profile"]["name"] == "Test User"
    assert data["episodic_summary"] == "User asked about ML topics"
    assert data["total_messages"] == 10
    
    mock_memory.get_context.assert_called_once_with(
        session_id="test-session",
        max_tokens=2000
    )


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_get_memory_context_with_defaults(mock_llm_class, mock_memory_class):
    """Test memory context with default max_tokens."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory = Mock()
    mock_context = Mock()
    mock_context.session_id = "test-session"
    mock_context.short_term_context = ""
    mock_context.semantic_facts = []
    mock_context.user_profile = {}
    mock_context.episodic_summary = None
    mock_context.procedural_patterns = None
    mock_context.total_messages = 0
    mock_memory.get_context.return_value = mock_context
    mock_memory_class.return_value = mock_memory
    
    response = client.post(
        "/llm/memory/context",
        json={"session_id": "test-session"}
    )
    
    assert response.status_code == 200
    mock_memory.get_context.assert_called_once_with(
        session_id="test-session",
        max_tokens=2000
    )


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_get_memory_context_failure(mock_llm_class, mock_memory_class):
    """Test memory context retrieval failure."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory = Mock()
    mock_memory.get_context.side_effect = RuntimeError("Database error")
    mock_memory_class.return_value = mock_memory
    
    response = client.post(
        "/llm/memory/context",
        json={"session_id": "test-session"}
    )
    
    assert response.status_code == 500
    assert "Failed to get context" in response.json()["detail"]


# ============================================================================
# Conversation History Tests
# ============================================================================


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_get_conversation_history_success(mock_llm_class, mock_memory_class):
    """Test successful conversation history retrieval."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory = Mock()
    mock_msg1 = Mock()
    mock_msg1.role = "user"
    mock_msg1.content = "Hello"
    mock_msg1.timestamp = datetime(2025, 12, 20, 10, 0, 0)
    mock_msg1.metadata = {}
    
    mock_msg2 = Mock()
    mock_msg2.role = "assistant"
    mock_msg2.content = "Hi there!"
    mock_msg2.timestamp = datetime(2025, 12, 20, 10, 0, 5)
    mock_msg2.metadata = {}
    
    mock_memory.get_messages.return_value = [mock_msg1, mock_msg2]
    mock_memory_class.return_value = mock_memory
    
    response = client.get("/llm/memory/history/test-session")
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-session"
    assert data["total_count"] == 2
    assert len(data["messages"]) == 2
    assert data["messages"][0]["role"] == "user"
    assert data["messages"][0]["content"] == "Hello"
    assert data["messages"][1]["role"] == "assistant"
    
    mock_memory.get_messages.assert_called_once_with("test-session", limit=50)


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_get_conversation_history_with_limit(mock_llm_class, mock_memory_class):
    """Test conversation history with custom limit."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory = Mock()
    mock_memory.get_messages.return_value = []
    mock_memory_class.return_value = mock_memory
    
    response = client.get("/llm/memory/history/test-session?limit=10")
    
    assert response.status_code == 200
    mock_memory.get_messages.assert_called_once_with("test-session", limit=10)


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_get_conversation_history_empty(mock_llm_class, mock_memory_class):
    """Test conversation history for empty session."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory = Mock()
    mock_memory.get_messages.return_value = []
    mock_memory_class.return_value = mock_memory
    
    response = client.get("/llm/memory/history/empty-session")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 0
    assert len(data["messages"]) == 0


# ============================================================================
# Memory Clearing Tests
# ============================================================================


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_clear_conversation_memory_success(mock_llm_class, mock_memory_class):
    """Test successful memory clearing."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory = Mock()
    mock_memory_class.return_value = mock_memory
    
    response = client.delete("/llm/memory/test-session")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "test-session" in data["message"]
    
    mock_memory.clear_session.assert_called_once_with("test-session")


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_clear_conversation_memory_failure(mock_llm_class, mock_memory_class):
    """Test memory clearing failure."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory = Mock()
    mock_memory.clear_session.side_effect = RuntimeError("Database error")
    mock_memory_class.return_value = mock_memory
    
    response = client.delete("/llm/memory/test-session")
    
    assert response.status_code == 500
    assert "Failed to clear memory" in response.json()["detail"]


# ============================================================================
# Memory Statistics Tests
# ============================================================================


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_get_memory_statistics_success(mock_llm_class, mock_memory_class):
    """Test successful memory statistics retrieval."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory = Mock()
    mock_stats = Mock()
    mock_stats.session_id = "test-session"
    mock_stats.message_count = 50
    mock_stats.token_count = 5000
    mock_stats.semantic_facts_count = 10
    mock_stats.profile_attributes_count = 5
    mock_stats.oldest_message_date = datetime(2025, 12, 1, 10, 0, 0)
    mock_stats.newest_message_date = datetime(2025, 12, 20, 10, 0, 0)
    mock_memory.get_stats.return_value = mock_stats
    mock_memory_class.return_value = mock_memory
    
    response = client.get("/llm/memory/stats/test-session")
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-session"
    assert data["message_count"] == 50
    assert data["token_count"] == 5000
    assert data["semantic_facts_count"] == 10
    assert data["profile_attributes_count"] == 5
    assert data["oldest_message"] is not None
    assert data["newest_message"] is not None
    
    mock_memory.get_stats.assert_called_once_with("test-session")


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_get_memory_statistics_empty_session(mock_llm_class, mock_memory_class):
    """Test memory statistics for empty session."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory = Mock()
    mock_stats = Mock()
    mock_stats.session_id = "empty-session"
    mock_stats.message_count = 0
    mock_stats.token_count = 0
    mock_stats.semantic_facts_count = 0
    mock_stats.profile_attributes_count = 0
    mock_stats.oldest_message_date = None
    mock_stats.newest_message_date = None
    mock_memory.get_stats.return_value = mock_stats
    mock_memory_class.return_value = mock_memory
    
    response = client.get("/llm/memory/stats/empty-session")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message_count"] == 0
    assert data["oldest_message"] is None
    assert data["newest_message"] is None


# ============================================================================
# Semantic Search Tests
# ============================================================================


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_search_semantic_memory_success(mock_llm_class, mock_memory_class):
    """Test successful semantic memory search."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory = Mock()
    mock_memory.search_semantic.return_value = [
        {
            "content": "User likes Python programming",
            "score": 0.95,
            "timestamp": "2025-12-20T10:00:00"
        },
        {
            "content": "User works with machine learning",
            "score": 0.87,
            "timestamp": "2025-12-19T15:00:00"
        }
    ]
    mock_memory_class.return_value = mock_memory
    
    response = client.post(
        "/llm/memory/search",
        json={
            "query": "programming interests",
            "session_id": "test-session",
            "top_k": 5
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "programming interests"
    assert data["total_results"] == 2
    assert len(data["results"]) == 2
    assert data["results"][0]["score"] == 0.95
    
    mock_memory.search_semantic.assert_called_once_with(
        query="programming interests",
        session_id="test-session",
        top_k=5
    )


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_search_semantic_memory_without_session(mock_llm_class, mock_memory_class):
    """Test semantic search across all sessions."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory = Mock()
    mock_memory.search_semantic.return_value = []
    mock_memory_class.return_value = mock_memory
    
    response = client.post(
        "/llm/memory/search",
        json={"query": "test query"}
    )
    
    assert response.status_code == 200
    mock_memory.search_semantic.assert_called_once_with(
        query="test query",
        session_id=None,
        top_k=5
    )


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_search_semantic_memory_empty_results(mock_llm_class, mock_memory_class):
    """Test semantic search with no results."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory = Mock()
    mock_memory.search_semantic.return_value = []
    mock_memory_class.return_value = mock_memory
    
    response = client.post(
        "/llm/memory/search",
        json={"query": "nonexistent topic"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] == 0
    assert len(data["results"]) == 0


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_search_semantic_memory_failure(mock_llm_class, mock_memory_class):
    """Test semantic search failure."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory = Mock()
    mock_memory.search_semantic.side_effect = RuntimeError("Search error")
    mock_memory_class.return_value = mock_memory
    
    response = client.post(
        "/llm/memory/search",
        json={"query": "test query"}
    )
    
    assert response.status_code == 500
    assert "Failed to search memory" in response.json()["detail"]


# ============================================================================
# Service Initialization Tests
# ============================================================================


@patch("agentlab.api.routes.memory_routes.IntegratedMemoryService")
@patch("agentlab.api.routes.memory_routes.LangChainLLM")
def test_memory_service_initialization_failure(mock_llm_class, mock_memory_class):
    """Test memory service initialization failure."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_memory_class.side_effect = ValueError("Missing configuration")
    
    response = client.post(
        "/llm/memory/context",
        json={"session_id": "test-session"}
    )
    
    # Service returns None on init failure, causing AttributeError
    assert response.status_code == 500
