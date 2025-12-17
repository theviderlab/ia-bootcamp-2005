"""
Unit tests for long-term memory processor.

Tests semantic extraction, profile building, and hybrid storage.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from agentlab.agents.memory_processor import LongTermMemoryProcessor
from agentlab.config.memory_config import MemoryConfig
from agentlab.models import ChatMessage


@pytest.fixture
def mock_config_mysql():
    """Create mock config with MySQL storage."""
    return MemoryConfig(
        db_host="localhost",
        db_port=3306,
        db_user="test",
        db_password="test",
        db_name="test",
        semantic_storage="mysql",
        enable_long_term=True,
        openai_api_key="test-key",
    )


@pytest.fixture
def mock_config_hybrid():
    """Create mock config with hybrid storage."""
    return MemoryConfig(
        db_host="localhost",
        db_port=3306,
        db_user="test",
        db_password="test",
        db_name="test",
        semantic_storage="hybrid",
        pinecone_api_key="test-pinecone-key",
        pinecone_index_name="test-index",
        openai_api_key="test-openai-key",
        enable_long_term=True,
    )


@pytest.fixture
def sample_messages():
    """Create sample messages for testing."""
    return [
        ChatMessage(
            role="user",
            content="I love programming in Python",
            timestamp=datetime(2024, 1, 1, 10, 0),
        ),
        ChatMessage(
            role="assistant",
            content="Python is a great language!",
            timestamp=datetime(2024, 1, 1, 10, 1),
        ),
        ChatMessage(
            role="user",
            content="Can you help me with data science?",
            timestamp=datetime(2024, 1, 1, 10, 2),
        ),
    ]


class TestLongTermMemoryProcessor:
    """Test long-term memory processor."""

    def test_initialization_mysql_only(self, mock_config_mysql):
        """Test initialization with MySQL-only storage."""
        processor = LongTermMemoryProcessor(config=mock_config_mysql)

        assert processor.config.semantic_storage == "mysql"
        assert processor.embeddings is None
        assert processor.pc is None

    @patch("agentlab.agents.memory_processor.Pinecone")
    @patch("agentlab.agents.memory_processor.OpenAIEmbeddings")
    def test_initialization_hybrid(
        self, mock_embeddings, mock_pinecone, mock_config_hybrid
    ):
        """Test initialization with hybrid storage."""
        processor = LongTermMemoryProcessor(config=mock_config_hybrid)

        assert processor.config.semantic_storage == "hybrid"
        mock_embeddings.assert_called_once()
        mock_pinecone.assert_called_once()

    @patch("agentlab.agents.memory_processor.ChatOpenAI")
    def test_extract_semantic_facts(
        self, mock_chat_openai, mock_config_mysql, sample_messages
    ):
        """Test extracting semantic facts from conversation."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = '["User likes Python", "Interested in data science"]'
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm

        processor = LongTermMemoryProcessor(config=mock_config_mysql)
        facts = processor.extract_semantic_facts("test-session", sample_messages)

        assert len(facts) == 2
        assert "User likes Python" in facts
        assert "Interested in data science" in facts

    @patch("agentlab.agents.memory_processor.get_chat_history")
    def test_get_user_profile(
        self, mock_get_history, mock_config_mysql, sample_messages
    ):
        """Test building user profile from conversation."""
        # Mock database history
        mock_get_history.return_value = [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.timestamp,
                "metadata": None,
            }
            for msg in sample_messages
        ]

        processor = LongTermMemoryProcessor(config=mock_config_mysql)
        profile = processor.get_user_profile("test-session")

        assert profile["session_id"] == "test-session"
        assert profile["total_messages"] == 3
        assert profile["user_messages"] == 2
        assert "top_topics" in profile

    @patch("agentlab.agents.memory_processor.ChatOpenAI")
    @patch("agentlab.agents.memory_processor.get_chat_history")
    def test_get_episodic_summary(
        self, mock_get_history, mock_chat_openai, mock_config_mysql, sample_messages
    ):
        """Test generating episodic summary."""
        # Mock database
        mock_get_history.return_value = [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.timestamp,
                "metadata": None,
            }
            for msg in sample_messages
        ]

        # Mock LLM
        mock_response = Mock()
        mock_response.content = "User discussed Python and data science."
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm

        processor = LongTermMemoryProcessor(config=mock_config_mysql)
        summary = processor.get_episodic_summary("test-session")

        assert summary == "User discussed Python and data science."

    @patch("agentlab.agents.memory_processor.get_chat_history")
    def test_get_procedural_patterns(
        self, mock_get_history, mock_config_mysql
    ):
        """Test identifying procedural patterns."""
        # Mock messages with questions
        mock_get_history.return_value = [
            {
                "role": "user",
                "content": "What is Python?",
                "created_at": datetime.now(),
                "metadata": None,
            },
            {
                "role": "user",
                "content": "How do I use it?",
                "created_at": datetime.now(),
                "metadata": None,
            },
            {
                "role": "user",
                "content": "Can you show me code?",
                "created_at": datetime.now(),
                "metadata": None,
            },
        ]

        processor = LongTermMemoryProcessor(config=mock_config_mysql)
        patterns = processor.get_procedural_patterns("test-session")

        assert "frequently_asks_questions" in patterns
        assert "discusses_code" in patterns

    @patch("agentlab.agents.memory_processor.Pinecone")
    @patch("agentlab.agents.memory_processor.OpenAIEmbeddings")
    def test_store_semantic_embedding(
        self, mock_embeddings, mock_pinecone, mock_config_hybrid
    ):
        """Test storing semantic embedding in Pinecone."""
        # Mock embeddings
        mock_embed_instance = Mock()
        mock_embed_instance.embed_query.return_value = [0.1] * 1536
        mock_embeddings.return_value = mock_embed_instance

        # Mock Pinecone
        mock_index = Mock()
        mock_pc_instance = Mock()
        mock_pc_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc_instance

        processor = LongTermMemoryProcessor(config=mock_config_hybrid)
        processor.store_semantic_embedding(
            session_id="test-session",
            text="Important fact",
            metadata={"source": "conversation"},
        )

        # Verify upsert was called
        mock_index.upsert.assert_called_once()
        call_args = mock_index.upsert.call_args
        vectors = call_args[1]["vectors"]
        assert len(vectors) == 1
        assert vectors[0][1] == [0.1] * 1536  # embedding

    @patch("agentlab.agents.memory_processor.Pinecone")
    @patch("agentlab.agents.memory_processor.OpenAIEmbeddings")
    def test_search_semantic(
        self, mock_embeddings, mock_pinecone, mock_config_hybrid
    ):
        """Test searching semantic memory."""
        # Mock embeddings
        mock_embed_instance = Mock()
        mock_embed_instance.embed_query.return_value = [0.1] * 1536
        mock_embeddings.return_value = mock_embed_instance

        # Mock Pinecone search results
        mock_index = Mock()
        mock_index.query.return_value = {
            "matches": [
                {
                    "id": "doc1",
                    "score": 0.95,
                    "metadata": {
                        "text": "Python is great",
                        "session_id": "test-session",
                    },
                },
                {
                    "id": "doc2",
                    "score": 0.85,
                    "metadata": {
                        "text": "Data science tools",
                        "session_id": "test-session",
                    },
                },
            ]
        }
        mock_pc_instance = Mock()
        mock_pc_instance.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc_instance

        processor = LongTermMemoryProcessor(config=mock_config_hybrid)
        results = processor.search_semantic(
            query="Python programming", session_id="test-session", top_k=5
        )

        assert len(results) == 2
        assert results[0]["text"] == "Python is great"
        assert results[0]["score"] == 0.95
        assert results[1]["text"] == "Data science tools"
