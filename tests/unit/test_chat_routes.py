"""
Unit tests for chat_routes module.

Tests API endpoints for LLM text generation and chat.
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
    """Reset global LLM and RAG instances before each test."""
    chat_routes._llm_instance = None
    chat_routes._rag_instance = None
    yield
    chat_routes._llm_instance = None
    chat_routes._rag_instance = None


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


# ============================================================================
# RAG Endpoint Tests
# ============================================================================


@patch("agentlab.api.routes.chat_routes.RAGServiceImpl")
@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_rag_query_success(mock_llm_class, mock_rag_class):
    """Test successful RAG query."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_result = Mock()
    mock_result.success = True
    mock_result.response = "Answer from RAG"
    mock_result.sources = [
        {
            "source": "test.txt",
            "chunk": 0,
            "created_at": "2025-12-15T10:00:00",
            "score": 0.95,
            "content_preview": "Test content..."
        }
    ]
    mock_result.error_message = None
    mock_rag.query.return_value = mock_result
    mock_rag_class.return_value = mock_rag
    
    response = client.post(
        "/llm/rag/query",
        json={
            "query": "What is Agent Lab?",
            "top_k": 5,
            "namespace": "test-namespace"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["response"] == "Answer from RAG"
    assert len(data["sources"]) == 1
    assert data["sources"][0]["source"] == "test.txt"
    assert data["sources"][0]["score"] == 0.95
    assert data["error_message"] is None
    
    mock_rag.query.assert_called_once_with(
        query="What is Agent Lab?",
        top_k=5,
        namespace="test-namespace"
    )


@patch("agentlab.api.routes.chat_routes.RAGServiceImpl")
@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_rag_query_with_defaults(mock_llm_class, mock_rag_class):
    """Test RAG query with default parameters."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_result = Mock()
    mock_result.success = True
    mock_result.response = "Answer"
    mock_result.sources = []
    mock_result.error_message = None
    mock_rag.query.return_value = mock_result
    mock_rag_class.return_value = mock_rag
    
    response = client.post(
        "/llm/rag/query",
        json={"query": "Test query"}
    )
    
    assert response.status_code == 200
    mock_rag.query.assert_called_once_with(
        query="Test query",
        top_k=5,
        namespace=None
    )


@patch("agentlab.api.routes.chat_routes.RAGServiceImpl")
@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_rag_query_failure(mock_llm_class, mock_rag_class):
    """Test RAG query with error."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_result = Mock()
    mock_result.success = False
    mock_result.response = ""
    mock_result.sources = []
    mock_result.error_message = "Query failed: Connection error"
    mock_rag.query.return_value = mock_result
    mock_rag_class.return_value = mock_rag
    
    response = client.post(
        "/llm/rag/query",
        json={"query": "Test query"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error_message"] == "Query failed: Connection error"


@patch("agentlab.api.routes.chat_routes.RAGServiceImpl")
@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_rag_query_empty_query(mock_llm_class, mock_rag_class):
    """Test RAG query with empty query string."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag_class.return_value = mock_rag
    
    response = client.post(
        "/llm/rag/query",
        json={"query": ""}
    )
    
    assert response.status_code == 422  # Validation error


@patch("agentlab.api.routes.chat_routes.RAGServiceImpl")
@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_add_documents_success(mock_llm_class, mock_rag_class):
    """Test successful document addition."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag_class.return_value = mock_rag
    
    response = client.post(
        "/llm/rag/documents",
        json={
            "documents": ["Document 1 content", "Document 2 content"],
            "namespace": "my-project",
            "chunk_size": 500,
            "chunk_overlap": 100
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["documents_added"] == 2
    assert "Successfully added 2 documents" in data["message"]
    
    mock_rag.add_documents.assert_called_once_with(
        documents=["Document 1 content", "Document 2 content"],
        namespace="my-project",
        chunk_size=500,
        chunk_overlap=100
    )


@patch("agentlab.api.routes.chat_routes.RAGServiceImpl")
@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_add_documents_with_defaults(mock_llm_class, mock_rag_class):
    """Test document addition with default parameters."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag_class.return_value = mock_rag
    
    response = client.post(
        "/llm/rag/documents",
        json={"documents": ["Test document"]}
    )
    
    assert response.status_code == 200
    mock_rag.add_documents.assert_called_once_with(
        documents=["Test document"],
        namespace=None,
        chunk_size=1000,
        chunk_overlap=200
    )


@patch("agentlab.api.routes.chat_routes.RAGServiceImpl")
@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_add_documents_empty_list(mock_llm_class, mock_rag_class):
    """Test document addition with empty list."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag_class.return_value = mock_rag
    
    response = client.post(
        "/llm/rag/documents",
        json={"documents": []}
    )
    
    assert response.status_code == 422  # Validation error


@patch("agentlab.api.routes.chat_routes.RAGServiceImpl")
@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_add_documents_failure(mock_llm_class, mock_rag_class):
    """Test document addition with error."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag.add_documents.side_effect = RuntimeError("Failed to add documents")
    mock_rag_class.return_value = mock_rag
    
    response = client.post(
        "/llm/rag/documents",
        json={"documents": ["Test document"]}
    )
    
    assert response.status_code == 500
    assert "Failed to add documents" in response.json()["detail"]


@patch("agentlab.api.routes.chat_routes.RAGServiceImpl")
@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_add_directory_success(mock_llm_class, mock_rag_class):
    """Test successful directory addition."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag.loader_registry.supports.return_value = True
    mock_rag_class.return_value = mock_rag
    
    with patch("pathlib.Path.exists") as mock_exists, \
         patch("pathlib.Path.is_dir") as mock_is_dir, \
         patch("pathlib.Path.glob") as mock_glob:
        
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        
        # Mock 3 files found
        mock_file1 = Mock()
        mock_file1.is_file.return_value = True
        mock_file2 = Mock()
        mock_file2.is_file.return_value = True
        mock_file3 = Mock()
        mock_file3.is_file.return_value = True
        mock_glob.return_value = [mock_file1, mock_file2, mock_file3]
        
        response = client.post(
            "/llm/rag/directory",
            json={
                "directory": "data/initial_knowledge",
                "namespace": "test",
                "recursive": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["documents_added"] == 3
        assert "3 documents from directory" in data["message"]


@patch("agentlab.api.routes.chat_routes.RAGServiceImpl")
@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_add_directory_not_found(mock_llm_class, mock_rag_class):
    """Test directory addition with non-existent directory."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag_class.return_value = mock_rag
    
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = False
        
        response = client.post(
            "/llm/rag/directory",
            json={"directory": "/nonexistent/path"}
        )
        
        assert response.status_code == 404
        assert "Directory not found" in response.json()["detail"]


@patch("agentlab.api.routes.chat_routes.RAGServiceImpl")
@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_add_directory_not_a_directory(mock_llm_class, mock_rag_class):
    """Test directory addition with file path instead of directory."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag_class.return_value = mock_rag
    
    with patch("pathlib.Path.exists") as mock_exists, \
         patch("pathlib.Path.is_dir") as mock_is_dir:
        
        mock_exists.return_value = True
        mock_is_dir.return_value = False
        
        response = client.post(
            "/llm/rag/directory",
            json={"directory": "somefile.txt"}
        )
        
        assert response.status_code == 400
        assert "not a directory" in response.json()["detail"]


@patch("agentlab.api.routes.chat_routes.RAGServiceImpl")
@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_add_directory_no_files(mock_llm_class, mock_rag_class):
    """Test directory addition with no supported files."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag.loader_registry.supports.return_value = False
    mock_rag_class.return_value = mock_rag
    
    with patch("pathlib.Path.exists") as mock_exists, \
         patch("pathlib.Path.is_dir") as mock_is_dir, \
         patch("pathlib.Path.glob") as mock_glob:
        
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_glob.return_value = []
        
        response = client.post(
            "/llm/rag/directory",
            json={"directory": "empty_dir"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["documents_added"] == 0
        assert "No supported files found" in data["message"]


@patch("agentlab.api.routes.chat_routes.RAGServiceImpl")
@patch("agentlab.api.routes.chat_routes.LangChainLLM")
def test_rag_service_initialization_failure(mock_llm_class, mock_rag_class):
    """Test RAG service initialization failure."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag_class.side_effect = ValueError("Missing PINECONE_API_KEY")
    
    response = client.post(
        "/llm/rag/query",
        json={"query": "Test query"}
    )
    
    assert response.status_code == 500
    assert "Failed to initialize RAG service" in response.json()["detail"]
    assert "Pinecone and OpenAI API keys" in response.json()["detail"]
