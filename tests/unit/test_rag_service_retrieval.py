"""
Unit tests for RAGServiceImpl.retrieve_documents() method.

Tests document retrieval without LLM generation.
"""

from unittest.mock import Mock, patch

import pytest
from langchain_core.documents import Document

from agentlab.core.rag_service import RAGServiceImpl
from agentlab.config.rag_config import RAGConfig


@pytest.fixture
def mock_llm():
    """Create a mock LLM instance."""
    llm = Mock()
    llm.generate.return_value = "Mocked response"
    return llm


@pytest.fixture
def mock_rag_config():
    """Create a mock RAG configuration."""
    config = Mock(spec=RAGConfig)
    config.pinecone_api_key = "test-key"
    config.openai_api_key = "test-openai-key"
    config.index_name = "test-index"
    config.namespace = "default"
    config.dimension = 1536
    config.metric = "cosine"
    config.cloud = "aws"
    config.region = "us-east-1"
    return config


@pytest.fixture
def mock_vectorstore():
    """Create a mock vector store."""
    vectorstore = Mock()
    return vectorstore


@pytest.fixture
def rag_service(mock_llm, mock_rag_config):
    """Create a RAGServiceImpl instance with mocked dependencies."""
    with patch("agentlab.core.rag_service.Pinecone"):
        with patch("agentlab.core.rag_service.OpenAIEmbeddings"):
            with patch("agentlab.core.rag_service.PineconeVectorStore") as mock_vs:
                with patch("agentlab.core.rag_service.DocumentLoaderRegistry"):
                    service = RAGServiceImpl(llm=mock_llm, config=mock_rag_config)
                    service.vectorstore = mock_vs.return_value
                    yield service


# ============================================================================
# retrieve_documents() Tests
# ============================================================================


def test_retrieve_documents_success(rag_service, mock_vectorstore):
    """Test successful document retrieval without LLM generation."""
    # Arrange
    query = "What is machine learning?"
    
    mock_docs = [
        (
            Document(
                page_content="Machine learning is a subset of AI",
                metadata={"source": "ml_basics.txt", "chunk": 0, "created_at": "2025-12-15T10:00:00"}
            ),
            0.95
        ),
        (
            Document(
                page_content="Neural networks are the foundation of deep learning",
                metadata={"source": "deep_learning.txt", "chunk": 1, "created_at": "2025-12-15T11:00:00"}
            ),
            0.87
        ),
    ]
    
    rag_service.vectorstore.similarity_search_with_score = Mock(return_value=mock_docs)
    
    # Act
    sources = rag_service.retrieve_documents(query, top_k=2, namespace="test-ns")
    
    # Assert - No LLM calls should be made
    rag_service.llm.generate.assert_not_called()
    rag_service.llm.chat.assert_not_called() if hasattr(rag_service.llm, 'chat') else None
    
    # Assert - Returns list of source dictionaries
    assert isinstance(sources, list)
    assert len(sources) == 2
    
    # Assert - First source has required fields
    assert sources[0]["source"] == "ml_basics.txt"
    assert sources[0]["chunk"] == 0
    assert sources[0]["score"] == 0.95
    assert "content_preview" in sources[0]
    assert "Machine learning is a subset of AI" in sources[0]["content_preview"]
    
    # Assert - Second source
    assert sources[1]["source"] == "deep_learning.txt"
    assert sources[1]["chunk"] == 1
    assert sources[1]["score"] == 0.87
    
    # Assert - Vector store called with correct namespace
    rag_service.vectorstore.similarity_search_with_score.assert_called_once()
    call_kwargs = rag_service.vectorstore.similarity_search_with_score.call_args[1]
    assert call_kwargs["namespace"] == "test-ns"
    assert call_kwargs["k"] == 2


def test_retrieve_documents_empty_query(rag_service):
    """Test retrieve_documents with empty query returns empty list."""
    # Act
    sources = rag_service.retrieve_documents("", top_k=5)
    
    # Assert
    assert sources == []
    rag_service.llm.generate.assert_not_called()


def test_retrieve_documents_whitespace_query(rag_service):
    """Test retrieve_documents with whitespace-only query returns empty list."""
    # Act
    sources = rag_service.retrieve_documents("   \n\t  ", top_k=5)
    
    # Assert
    assert sources == []
    rag_service.llm.generate.assert_not_called()


def test_retrieve_documents_no_results(rag_service):
    """Test retrieve_documents when no matching documents found."""
    # Arrange
    rag_service.vectorstore.similarity_search_with_score = Mock(return_value=[])
    
    # Act
    sources = rag_service.retrieve_documents("unknown query", top_k=5)
    
    # Assert
    assert sources == []
    rag_service.llm.generate.assert_not_called()


def test_retrieve_documents_default_namespace(rag_service):
    """Test retrieve_documents uses default namespace when none specified."""
    # Arrange
    mock_docs = [
        (
            Document(
                page_content="Test content",
                metadata={"source": "test.txt", "chunk": 0}
            ),
            0.9
        )
    ]
    rag_service.vectorstore.similarity_search_with_score = Mock(return_value=mock_docs)
    
    # Act
    sources = rag_service.retrieve_documents("test query")
    
    # Assert
    call_kwargs = rag_service.vectorstore.similarity_search_with_score.call_args[1]
    assert call_kwargs["namespace"] == "default"  # From mock_rag_config


def test_retrieve_documents_top_k_parameter(rag_service):
    """Test retrieve_documents respects top_k parameter."""
    # Arrange
    mock_docs = [
        (Document(page_content=f"Content {i}", metadata={"source": f"doc{i}.txt", "chunk": i}), 0.9 - i * 0.1)
        for i in range(10)
    ]
    rag_service.vectorstore.similarity_search_with_score = Mock(return_value=mock_docs)
    
    # Act
    sources = rag_service.retrieve_documents("test query", top_k=3)
    
    # Assert
    call_kwargs = rag_service.vectorstore.similarity_search_with_score.call_args[1]
    assert call_kwargs["k"] == 3


def test_retrieve_documents_scores_sorted_descending(rag_service):
    """Test retrieve_documents returns sources sorted by score (highest first)."""
    # Arrange - Unsorted mock results
    mock_docs = [
        (
            Document(page_content="Low score", metadata={"source": "doc1.txt", "chunk": 0}),
            0.5
        ),
        (
            Document(page_content="High score", metadata={"source": "doc2.txt", "chunk": 0}),
            0.95
        ),
        (
            Document(page_content="Medium score", metadata={"source": "doc3.txt", "chunk": 0}),
            0.75
        ),
    ]
    rag_service.vectorstore.similarity_search_with_score = Mock(return_value=mock_docs)
    
    # Act
    sources = rag_service.retrieve_documents("test query", top_k=3)
    
    # Assert - Should be sorted by score descending
    assert sources[0]["score"] == 0.95
    assert sources[1]["score"] == 0.75
    assert sources[2]["score"] == 0.5


def test_retrieve_documents_error_handling(rag_service):
    """Test retrieve_documents raises RuntimeError on failure."""
    # Arrange
    rag_service.vectorstore.similarity_search_with_score = Mock(
        side_effect=Exception("Vector store error")
    )
    
    # Act & Assert
    with pytest.raises(RuntimeError, match="Document retrieval failed"):
        rag_service.retrieve_documents("test query")
    
    # Assert - No LLM calls made even on error
    rag_service.llm.generate.assert_not_called()


def test_retrieve_documents_content_preview(rag_service):
    """Test retrieve_documents creates proper content previews."""
    # Arrange
    long_content = "A" * 300  # Content longer than 200 chars
    short_content = "Short content"
    
    mock_docs = [
        (
            Document(page_content=long_content, metadata={"source": "long.txt", "chunk": 0}),
            0.9
        ),
        (
            Document(page_content=short_content, metadata={"source": "short.txt", "chunk": 1}),
            0.8
        ),
    ]
    rag_service.vectorstore.similarity_search_with_score = Mock(return_value=mock_docs)
    
    # Act
    sources = rag_service.retrieve_documents("test query", top_k=2)
    
    # Assert - Long content is truncated with "..."
    assert len(sources[0]["content_preview"]) == 203  # 200 chars + "..."
    assert sources[0]["content_preview"].endswith("...")
    
    # Assert - Short content is not truncated
    assert sources[1]["content_preview"] == short_content
    assert not sources[1]["content_preview"].endswith("...")


# ============================================================================
# Integration Tests: retrieve_documents() vs query()
# ============================================================================


def test_query_uses_retrieve_documents_internally(rag_service):
    """Test that query() method uses retrieve_documents() internally."""
    # Arrange
    mock_docs = [
        (
            Document(
                page_content="Test content",
                metadata={"source": "test.txt", "chunk": 0}
            ),
            0.9
        )
    ]
    rag_service.vectorstore.similarity_search_with_score = Mock(return_value=mock_docs)
    rag_service.llm.generate = Mock(return_value="Generated response")
    
    # Act
    result = rag_service.query("test query", top_k=1)
    
    # Assert - query() makes exactly one LLM call for generation
    assert rag_service.llm.generate.call_count == 1
    
    # Assert - Result contains both response and sources
    assert result.success is True
    assert result.response == "Generated response"
    assert len(result.sources) == 1
    assert result.sources[0]["source"] == "test.txt"


def test_query_without_results_calls_llm_once(rag_service):
    """Test query() with no results makes only one LLM call (no redundancy)."""
    # Arrange
    rag_service.vectorstore.similarity_search_with_score = Mock(return_value=[])
    rag_service.llm.generate = Mock(return_value="No context response")
    
    # Act
    result = rag_service.query("unknown query", top_k=5)
    
    # Assert - Only one LLM call made (for no-context response)
    assert rag_service.llm.generate.call_count == 1
    assert result.success is True
    assert result.response == "No context response"
    assert result.sources == []
