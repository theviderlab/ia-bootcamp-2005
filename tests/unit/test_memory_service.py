"""
Unit tests for memory service.

Tests short-term and integrated memory functionality with mocked
database and LangGraph components.
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch, call

import pytest

from agentlab.config.memory_config import MemoryConfig
from agentlab.core.memory_service import (
    IntegratedMemoryService,
    ShortTermMemoryService,
)
from agentlab.models import ChatMessage, MemoryContext


@pytest.fixture
def mock_config():
    """Create a mock memory configuration."""
    return MemoryConfig(
        db_host="localhost",
        db_port=3306,
        db_user="test_user",
        db_password="test_pass",
        db_name="test_db",
        memory_type="buffer",
        short_term_window_size=10,
        max_token_limit=2000,
        enable_long_term=False,
        semantic_storage="mysql",
        openai_api_key="test-key",
    )


@pytest.fixture
def sample_messages():
    """Create sample chat messages."""
    return [
        ChatMessage(
            role="user",
            content="Hello, how are you?",
            timestamp=datetime.now(),
        ),
        ChatMessage(
            role="assistant",
            content="I'm doing well, thank you!",
            timestamp=datetime.now(),
        ),
        ChatMessage(
            role="user",
            content="Can you help me with Python?",
            timestamp=datetime.now(),
        ),
    ]


class TestShortTermMemoryService:
    """Test short-term memory service with LangGraph."""

    @patch("agentlab.core.memory_service.MemorySaver")
    @patch("agentlab.core.memory_service.StateGraph")
    def test_initialization_buffer(
        self, mock_state_graph, mock_memory_saver, mock_config
    ):
        """Test initialization with buffer memory type."""
        # Setup mock graph
        mock_workflow = Mock()
        mock_compiled_graph = Mock()
        mock_state_graph.return_value = mock_workflow
        mock_workflow.compile.return_value = mock_compiled_graph

        service = ShortTermMemoryService(config=mock_config)

        assert service.config == mock_config
        assert service.config.memory_type == "buffer"
        assert service.checkpointer is not None
        assert service.graph is not None

    @patch("agentlab.core.memory_service.create_chat_message")
    @patch("agentlab.core.memory_service.MemorySaver")
    @patch("agentlab.core.memory_service.StateGraph")
    def test_add_user_message(
        self,
        mock_state_graph,
        mock_memory_saver,
        mock_create_message,
        mock_config,
        sample_messages,
    ):
        """Test adding a user message via LangGraph."""
        # Setup mock graph
        mock_workflow = Mock()
        mock_compiled_graph = Mock()
        mock_state_graph.return_value = mock_workflow
        mock_workflow.compile.return_value = mock_compiled_graph

        service = ShortTermMemoryService(config=mock_config)
        user_message = sample_messages[0]

        # Add message
        service.add_message("test-session", user_message)

        # Verify graph was invoked
        mock_compiled_graph.invoke.assert_called_once()
        call_args = mock_compiled_graph.invoke.call_args
        
        # Verify message content
        assert "messages" in call_args[0][0]
        assert call_args[0][0]["session_id"] == "test-session"
        
        # Verify config has thread_id
        assert call_args[1]["config"]["configurable"]["thread_id"] == "test-session"

    @patch("agentlab.core.memory_service.create_chat_message")
    @patch("agentlab.core.memory_service.MemorySaver")
    @patch("agentlab.core.memory_service.StateGraph")
    def test_add_assistant_message(
        self,
        mock_state_graph,
        mock_memory_saver,
        mock_create_message,
        mock_config,
        sample_messages,
    ):
        """Test adding an assistant message via LangGraph."""
        # Setup mock graph
        mock_workflow = Mock()
        mock_compiled_graph = Mock()
        mock_state_graph.return_value = mock_workflow
        mock_workflow.compile.return_value = mock_compiled_graph

        service = ShortTermMemoryService(config=mock_config)
        assistant_message = sample_messages[1]

        # Add message
        service.add_message("test-session", assistant_message)

        # Verify graph was invoked
        mock_compiled_graph.invoke.assert_called_once()

    @patch("agentlab.core.memory_service.get_chat_history")
    @patch("agentlab.core.memory_service.MemorySaver")
    @patch("agentlab.core.memory_service.StateGraph")
    def test_get_messages(
        self,
        mock_state_graph,
        mock_memory_saver,
        mock_get_history,
        mock_config,
    ):
        """Test retrieving conversation history from MySQL."""
        # Setup mock graph
        mock_workflow = Mock()
        mock_compiled_graph = Mock()
        mock_state_graph.return_value = mock_workflow
        mock_workflow.compile.return_value = mock_compiled_graph

        # Setup mock data
        mock_get_history.return_value = [
            {
                "role": "user",
                "content": "Hello",
                "created_at": datetime.now(),
                "metadata": None,
            },
            {
                "role": "assistant",
                "content": "Hi there!",
                "created_at": datetime.now(),
                "metadata": None,
            },
        ]

        service = ShortTermMemoryService(config=mock_config)
        messages = service.get_messages("test-session", limit=10)

        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[0].content == "Hello"
        assert messages[1].role == "assistant"
        mock_get_history.assert_called_once_with("test-session", 10)

    @patch("agentlab.core.memory_service.delete_chat_history")
    @patch("agentlab.core.memory_service.MemorySaver")
    @patch("agentlab.core.memory_service.StateGraph")
    def test_clear_session(
        self,
        mock_state_graph,
        mock_memory_saver,
        mock_delete,
        mock_config,
    ):
        """Test clearing session memory and checkpoints."""
        # Setup mock graph and checkpointer
        mock_workflow = Mock()
        mock_compiled_graph = Mock()
        mock_checkpointer = Mock()
        mock_state_graph.return_value = mock_workflow
        mock_workflow.compile.return_value = mock_compiled_graph
        mock_memory_saver.return_value = mock_checkpointer

        service = ShortTermMemoryService(config=mock_config)
        service.clear_session("test-session")

        # Verify MySQL history deleted
        mock_delete.assert_called_once_with("test-session")
        
        # Verify checkpointer delete attempted
        # (may not be called if checkpointer doesn't have delete method)

    @patch("agentlab.core.memory_service.get_chat_stats")
    @patch("agentlab.core.memory_service.MemorySaver")
    @patch("agentlab.core.memory_service.StateGraph")
    def test_get_stats(
        self,
        mock_state_graph,
        mock_memory_saver,
        mock_get_stats,
        mock_config,
    ):
        """Test getting memory statistics."""
        # Setup mock graph
        mock_workflow = Mock()
        mock_compiled_graph = Mock()
        mock_state_graph.return_value = mock_workflow
        mock_workflow.compile.return_value = mock_compiled_graph

        # Setup mock stats
        mock_get_stats.return_value = {
            "message_count": 10,
            "oldest_message": datetime(2024, 1, 1),
            "newest_message": datetime(2024, 1, 2),
        }

        service = ShortTermMemoryService(config=mock_config)
        stats = service.get_stats("test-session")

        assert stats.message_count == 10
        assert stats.oldest_message_date == datetime(2024, 1, 1)
        assert stats.newest_message_date == datetime(2024, 1, 2)
        mock_get_stats.assert_called_once_with("test-session")

    @patch("agentlab.core.memory_service.get_chat_stats")
    @patch("agentlab.core.memory_service.get_chat_history")
    @patch("agentlab.core.memory_service.MemorySaver")
    @patch("agentlab.core.memory_service.StateGraph")
    def test_get_context_with_checkpointer(
        self,
        mock_state_graph,
        mock_memory_saver,
        mock_get_history,
        mock_get_stats,
        mock_config,
        sample_messages,
    ):
        """Test getting context from checkpointer state."""
        # Setup mock graph
        mock_workflow = Mock()
        mock_compiled_graph = Mock()
        mock_state_graph.return_value = mock_workflow
        mock_workflow.compile.return_value = mock_compiled_graph

        # Setup mock checkpointer with state
        from langchain_core.messages import HumanMessage, AIMessage
        
        mock_checkpointer = Mock()
        mock_state = Mock()
        mock_state.values = {
            "messages": [
                HumanMessage(content="Hello"),
                AIMessage(content="Hi there!"),
            ],
            "summary": "Test summary",
        }
        mock_checkpointer.get.return_value = mock_state
        mock_memory_saver.return_value = mock_checkpointer

        # Setup stats
        mock_get_stats.return_value = {
            "message_count": 2,
            "oldest_message": None,
            "newest_message": None,
        }

        service = ShortTermMemoryService(config=mock_config)
        context = service.get_context("test-session")

        assert context.session_id == "test-session"
        assert "user: Hello" in context.short_term_context
        assert "assistant: Hi there!" in context.short_term_context
        assert context.episodic_summary == "Test summary"

    @patch("agentlab.core.memory_service.SqliteSaver")
    @patch("agentlab.core.memory_service.StateGraph")
    def test_create_checkpointer_window_mode(
        self, mock_state_graph, mock_sqlite_saver, mock_config
    ):
        """Test that window mode creates SqliteSaver."""
        # Setup mock graph
        mock_workflow = Mock()
        mock_compiled_graph = Mock()
        mock_state_graph.return_value = mock_workflow
        mock_workflow.compile.return_value = mock_compiled_graph

        config = MemoryConfig(
            **{**mock_config.__dict__, "memory_type": "window"}
        )

        service = ShortTermMemoryService(config=config)

        # Verify SqliteSaver was created for window mode
        mock_sqlite_saver.from_conn_string.assert_called_once()


class TestIntegratedMemoryService:
    """Test integrated memory service with long-term support."""

    @patch("agentlab.core.memory_service.LongTermMemoryProcessor")
    @patch("agentlab.core.memory_service.ShortTermMemoryService")
    def test_initialization_with_long_term(
        self, mock_short_term, mock_long_term, mock_config
    ):
        """Test initialization with long-term memory enabled."""
        config_with_lt = MemoryConfig(
            **{**mock_config.__dict__, "enable_long_term": True}
        )

        service = IntegratedMemoryService(config=config_with_lt)

        assert service.long_term is not None
        mock_long_term.assert_called_once()

    @patch("agentlab.core.memory_service.ShortTermMemoryService")
    def test_initialization_without_long_term(
        self, mock_short_term, mock_config
    ):
        """Test initialization with long-term memory disabled."""
        service = IntegratedMemoryService(config=mock_config)

        assert service.long_term is None

    @patch("agentlab.core.memory_service.ShortTermMemoryService")
    def test_add_message_delegates(
        self, mock_short_term_class, mock_config, sample_messages
    ):
        """Test that add_message delegates to short-term service."""
        mock_short_term = Mock()
        mock_short_term_class.return_value = mock_short_term

        service = IntegratedMemoryService(config=mock_config)
        message = sample_messages[0]

        service.add_message("test-session", message)

        mock_short_term.add_message.assert_called_once_with(
            "test-session", message
        )

    @patch("agentlab.core.memory_service.LongTermMemoryProcessor")
    @patch("agentlab.core.memory_service.ShortTermMemoryService")
    def test_get_context_with_long_term(
        self, mock_short_term_class, mock_long_term_class, sample_messages
    ):
        """Test getting context with long-term memory enrichment."""
        # Setup mocks
        mock_short_term = Mock()
        mock_long_term = Mock()
        mock_short_term_class.return_value = mock_short_term
        mock_long_term_class.return_value = mock_long_term

        # Mock short-term context
        base_context = MemoryContext(
            session_id="test-session",
            short_term_context="Recent conversation",
            semantic_facts=[],
            user_profile={},
            total_messages=5,
        )
        mock_short_term.get_context.return_value = base_context
        mock_short_term.get_messages.return_value = sample_messages

        # Mock long-term extraction
        mock_long_term.extract_semantic_facts.return_value = [
            "User likes Python"
        ]
        mock_long_term.get_user_profile.return_value = {
            "language": "Python"
        }
        mock_long_term.get_episodic_summary.return_value = "Discussed coding"
        mock_long_term.get_procedural_patterns.return_value = [
            "asks_questions"
        ]

        # Create config with long-term enabled
        config = MemoryConfig(
            db_host="localhost",
            db_port=3306,
            db_user="test",
            db_password="test",
            db_name="test",
            enable_long_term=True,
            semantic_storage="mysql",
        )

        service = IntegratedMemoryService(config=config)
        context = service.get_context("test-session")

        # Verify enrichment
        assert context.semantic_facts == ["User likes Python"]
        assert context.user_profile == {"language": "Python"}
        assert context.episodic_summary == "Discussed coding"
        assert context.procedural_patterns == ["asks_questions"]

    @patch("agentlab.core.memory_service.ShortTermMemoryService")
    def test_search_semantic_without_long_term(
        self, mock_short_term, mock_config
    ):
        """Test semantic search returns empty when long-term disabled."""
        service = IntegratedMemoryService(config=mock_config)
        results = service.search_semantic("Python programming")

        assert results == []

    @patch("agentlab.core.memory_service.LongTermMemoryProcessor")
    @patch("agentlab.core.memory_service.ShortTermMemoryService")
    def test_search_semantic_with_long_term(
        self, mock_short_term, mock_long_term_class, mock_config
    ):
        """Test semantic search delegates to long-term processor."""
        # Setup mocks
        mock_long_term = Mock()
        mock_long_term_class.return_value = mock_long_term
        mock_long_term.search_semantic.return_value = [
            {"fact": "User likes Python", "score": 0.9}
        ]

        # Create config with long-term enabled
        config = MemoryConfig(
            **{**mock_config.__dict__, "enable_long_term": True}
        )

        service = IntegratedMemoryService(config=config)
        results = service.search_semantic("Python", "test-session", top_k=3)

        mock_long_term.search_semantic.assert_called_once_with(
            "Python", "test-session", 3
        )
        assert len(results) == 1
        assert results[0]["fact"] == "User likes Python"

    @patch("agentlab.core.memory_service.LongTermMemoryProcessor")
    @patch("agentlab.core.memory_service.ShortTermMemoryService")
    def test_get_context_respects_session_config(
        self, mock_short_term_class, mock_long_term_class
    ):
        """Test that get_context respects session memory configuration."""
        # Setup short-term mock
        mock_short_term = Mock()
        mock_short_term.get_context.return_value = MemoryContext(
            session_id="test-session",
            short_term_context="Recent chat",
            semantic_facts=[],
            user_profile={},
            total_messages=1,
        )
        mock_short_term.get_stats.return_value = Mock(message_count=1)
        mock_short_term.get_messages.return_value = []
        mock_short_term_class.return_value = mock_short_term
        
        # Setup long-term mock
        mock_long_term = Mock()
        mock_long_term.extract_semantic_facts.return_value = ["Fact 1"]
        mock_long_term.get_user_profile.return_value = {"name": "Test"}
        mock_long_term.get_episodic_summary.return_value = "Summary"
        mock_long_term.get_procedural_patterns.return_value = ["Pattern 1"]
        mock_long_term_class.return_value = mock_long_term
        
        # Create service with long-term enabled
        config = MemoryConfig(
            db_host="localhost",
            db_port=3306,
            db_user="test",
            db_password="test",
            db_name="test",
            enable_long_term=True,
        )
        service = IntegratedMemoryService(config=config)
        
        # Test 1: All memory disabled
        memory_config = {
            "enable_short_term": False,
            "enable_semantic": False,
            "enable_episodic": False,
            "enable_profile": False,
            "enable_procedural": False,
        }
        
        context = service.get_context("test-session", memory_config=memory_config)
        
        # Verify all memory is disabled
        assert context.short_term_context == ""
        assert context.semantic_facts == []
        assert context.user_profile == {}
        assert context.episodic_summary is None
        assert context.procedural_patterns is None
        
        # Test 2: Only semantic enabled
        memory_config = {
            "enable_short_term": False,
            "enable_semantic": True,
            "enable_episodic": False,
            "enable_profile": False,
            "enable_procedural": False,
        }
        
        context = service.get_context("test-session", memory_config=memory_config)
        
        # Verify only semantic is populated
        assert context.short_term_context == ""
        assert context.semantic_facts == ["Fact 1"]
        assert context.user_profile == {}
        assert context.episodic_summary is None
        assert context.procedural_patterns is None
        
        # Test 3: Only short-term enabled (default behavior with long-term disabled)
        memory_config = {
            "enable_short_term": True,
            "enable_semantic": False,
            "enable_episodic": False,
            "enable_profile": False,
            "enable_procedural": False,
        }
        
        context = service.get_context("test-session", memory_config=memory_config)
        
        # Verify only short-term is populated
        assert context.short_term_context == "Recent chat"
        assert context.semantic_facts == []
        assert context.user_profile == {}
        assert context.episodic_summary is None
        assert context.procedural_patterns is None
