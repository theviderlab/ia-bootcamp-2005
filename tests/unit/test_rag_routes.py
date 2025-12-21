"""
Unit tests for rag_routes module.

Tests API endpoints for RAG document management and queries.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from agentlab.api.main import app
from agentlab.api.routes import rag_routes

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_global_instances():
    """Reset global LLM and RAG instances before each test."""
    rag_routes._llm_instance = None
    rag_routes._rag_instance = None
    yield
    rag_routes._llm_instance = None
    rag_routes._rag_instance = None


# ============================================================================
# RAG Query Tests
# ============================================================================


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
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


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
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


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
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


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
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
    
    assert response.status_code == 422


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
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


# ============================================================================
# Document Management Tests
# ============================================================================


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
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


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
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


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
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
    
    assert response.status_code == 422


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
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


# ============================================================================
# Directory Management Tests
# ============================================================================


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
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


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
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


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
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


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
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


# ============================================================================
# Namespace Management Tests
# ============================================================================


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
def test_get_namespace_stats_success(mock_llm_class, mock_rag_class):
    """Test successful namespace statistics retrieval."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag.get_namespace_stats.return_value = {
        "success": True,
        "namespace": "test-namespace",
        "vector_count": 100,
        "dimension": 1536,
        "exists": True
    }
    mock_rag_class.return_value = mock_rag
    
    response = client.get("/llm/rag/namespace/test-namespace/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["namespace"] == "test-namespace"
    assert data["vector_count"] == 100
    assert data["dimension"] == 1536
    assert data["exists"] is True


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
def test_delete_namespace_success(mock_llm_class, mock_rag_class):
    """Test successful namespace deletion."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag.delete_namespace.return_value = {
        "success": True,
        "namespace": "test-namespace",
        "message": "Namespace deleted successfully"
    }
    mock_rag_class.return_value = mock_rag
    
    response = client.delete("/llm/rag/namespace/test-namespace")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["namespace"] == "test-namespace"
    assert "deleted successfully" in data["message"]


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
def test_list_namespaces_success(mock_llm_class, mock_rag_class):
    """Test successful namespace listing with real data."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag.list_namespaces.return_value = [
        {
            "name": "default",
            "document_count": 10,
            "total_chunks": 150,
            "last_updated": "2025-12-20T10:00:00",
        },
        {
            "name": "docs",
            "document_count": 5,
            "total_chunks": 75,
            "last_updated": "2025-12-19T15:30:00",
        },
    ]
    mock_rag_class.return_value = mock_rag
    
    response = client.get("/llm/rag/namespaces")
    
    assert response.status_code == 200
    data = response.json()
    assert "namespaces" in data
    assert isinstance(data["namespaces"], list)
    assert len(data["namespaces"]) == 2
    assert data["namespaces"][0]["name"] == "default"
    assert data["namespaces"][0]["document_count"] == 10
    assert data["namespaces"][0]["total_chunks"] == 150
    assert data["namespaces"][1]["name"] == "docs"
    
    mock_rag.list_namespaces.assert_called_once()


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
def test_list_namespaces_empty(mock_llm_class, mock_rag_class):
    """Test namespace listing when no namespaces exist."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag.list_namespaces.return_value = []
    mock_rag_class.return_value = mock_rag
    
    response = client.get("/llm/rag/namespaces")
    
    assert response.status_code == 200
    data = response.json()
    assert data["namespaces"] == []


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
def test_list_namespaces_service_unavailable(mock_llm_class, mock_rag_class):
    """Test namespace listing when RAG service is unavailable."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag_class.return_value = None
    
    response = client.get("/llm/rag/namespaces")
    
    assert response.status_code == 500
    assert "not available" in response.json()["detail"].lower()


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
def test_list_namespaces_error(mock_llm_class, mock_rag_class):
    """Test namespace listing error handling."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag.list_namespaces.side_effect = RuntimeError("Pinecone connection failed")
    mock_rag_class.return_value = mock_rag
    
    response = client.get("/llm/rag/namespaces")
    
    assert response.status_code == 500
    assert "Failed to list namespaces" in response.json()["detail"]


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
def test_list_documents_success(mock_llm_class, mock_rag_class):
    """Test successful document listing with pagination."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag.list_documents.return_value = {
        "documents": [
            {
                "id": "doc-123",
                "filename": "sample.txt",
                "namespace": "default",
                "chunk_count": 10,
                "file_size": 1024,
                "uploaded_at": "2025-12-20T10:00:00",
            },
            {
                "id": "doc-456",
                "filename": "readme.md",
                "namespace": "docs",
                "chunk_count": 5,
                "file_size": 512,
                "uploaded_at": "2025-12-19T14:30:00",
            },
        ],
        "total_count": 25,
        "limit": 100,
        "offset": 0,
        "has_more": False,
    }
    mock_rag_class.return_value = mock_rag
    
    response = client.get("/llm/rag/documents?limit=100&offset=0")
    
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert isinstance(data["documents"], list)
    assert len(data["documents"]) == 2
    assert data["documents"][0]["id"] == "doc-123"
    assert data["documents"][0]["filename"] == "sample.txt"
    assert data["documents"][0]["namespace"] == "default"
    assert data["documents"][0]["chunk_count"] == 10
    assert data["total_count"] == 25
    assert data["limit"] == 100
    assert data["offset"] == 0
    assert data["has_more"] is False
    
    mock_rag.list_documents.assert_called_once_with(
        namespace=None,
        limit=100,
        offset=0,
    )


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
def test_list_documents_with_namespace_filter(mock_llm_class, mock_rag_class):
    """Test document listing with namespace filter."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag.list_documents.return_value = {
        "documents": [
            {
                "id": "doc-789",
                "filename": "api.md",
                "namespace": "docs",
                "chunk_count": 8,
                "file_size": 2048,
                "uploaded_at": "2025-12-20T09:00:00",
            },
        ],
        "total_count": 5,
        "limit": 50,
        "offset": 0,
        "has_more": False,
    }
    mock_rag_class.return_value = mock_rag
    
    response = client.get("/llm/rag/documents?namespace=docs&limit=50")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["documents"]) == 1
    assert data["documents"][0]["namespace"] == "docs"
    assert data["total_count"] == 5
    
    mock_rag.list_documents.assert_called_once_with(
        namespace="docs",
        limit=50,
        offset=0,
    )


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
def test_list_documents_pagination(mock_llm_class, mock_rag_class):
    """Test document listing with pagination parameters."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag.list_documents.return_value = {
        "documents": [],
        "total_count": 250,
        "limit": 50,
        "offset": 100,
        "has_more": True,
    }
    mock_rag_class.return_value = mock_rag
    
    response = client.get("/llm/rag/documents?limit=50&offset=100")
    
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 50
    assert data["offset"] == 100
    assert data["total_count"] == 250
    assert data["has_more"] is True
    
    mock_rag.list_documents.assert_called_once_with(
        namespace=None,
        limit=50,
        offset=100,
    )


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
def test_list_documents_invalid_limit(mock_llm_class, mock_rag_class):
    """Test document listing with invalid limit parameter."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag_class.return_value = mock_rag
    
    # Test limit too large
    response = client.get("/llm/rag/documents?limit=2000")
    assert response.status_code == 400
    assert "between 1 and 1000" in response.json()["detail"]
    
    # Test limit too small
    response = client.get("/llm/rag/documents?limit=0")
    assert response.status_code == 400


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
def test_list_documents_empty(mock_llm_class, mock_rag_class):
    """Test document listing when no documents exist."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag.list_documents.return_value = {
        "documents": [],
        "total_count": 0,
        "limit": 100,
        "offset": 0,
        "has_more": False,
    }
    mock_rag_class.return_value = mock_rag
    
    response = client.get("/llm/rag/documents")
    
    assert response.status_code == 200
    data = response.json()
    assert data["documents"] == []
    assert data["total_count"] == 0


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
def test_list_documents_service_unavailable(mock_llm_class, mock_rag_class):
    """Test document listing when RAG service is unavailable."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag_class.return_value = None
    
    response = client.get("/llm/rag/documents")
    
    assert response.status_code == 500
    assert "not available" in response.json()["detail"].lower()


@patch("agentlab.api.routes.rag_routes.RAGServiceImpl")
@patch("agentlab.api.routes.rag_routes.LangChainLLM")
def test_list_documents_database_error(mock_llm_class, mock_rag_class):
    """Test document listing database error handling."""
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    mock_rag = Mock()
    mock_rag.list_documents.side_effect = RuntimeError("Database connection failed")
    mock_rag_class.return_value = mock_rag
    
    response = client.get("/llm/rag/documents")
    
    assert response.status_code == 500
    assert "Failed to list documents" in response.json()["detail"]
