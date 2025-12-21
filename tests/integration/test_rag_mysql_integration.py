"""
Integration tests for RAG system MySQL synchronization.

Tests that documents added to Pinecone are properly tracked in MySQL.
"""

import os
from pathlib import Path

import pytest

from agentlab.config.rag_config import RAGConfig
from agentlab.core.llm_interface import LangChainLLM
from agentlab.core.rag_service import RAGServiceImpl
from agentlab.database.crud import (
    bulk_insert_knowledge_documents,
    delete_all_knowledge_base,
    query_knowledge_base_documents,
)


@pytest.fixture
def test_namespace():
    """Test namespace for isolation."""
    return "test_mysql_sync"


@pytest.fixture
def rag_service():
    """Create RAG service instance."""
    # Skip if RAG not configured
    if not os.getenv("PINECONE_API_KEY") or not os.getenv("OPENAI_API_KEY"):
        pytest.skip("RAG service not configured")

    llm = LangChainLLM(temperature=0.7, max_tokens=500)
    config = RAGConfig.from_env()
    return RAGServiceImpl(llm=llm, config=config)


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data before and after tests."""
    # Cleanup before test
    delete_all_knowledge_base()
    yield
    # Cleanup after test
    delete_all_knowledge_base()


def test_bulk_insert_knowledge_documents():
    """Test bulk insert CRUD operation."""
    documents = [
        {
            "doc_id": "test_doc_1",
            "content": "This is test document 1",
            "filename": "test1.txt",
            "namespace": "test_namespace",
            "chunk_count": 3,
            "file_size": 1024,
            "metadata": {"source": "test1.txt"},
        },
        {
            "doc_id": "test_doc_2",
            "content": "This is test document 2",
            "filename": "test2.txt",
            "namespace": "test_namespace",
            "chunk_count": 5,
            "file_size": 2048,
            "metadata": {"source": "test2.txt"},
        },
    ]

    rows_affected = bulk_insert_knowledge_documents(documents)
    assert rows_affected >= 2, "Should insert at least 2 documents"

    # Query back
    result = query_knowledge_base_documents(namespace="test_namespace", limit=10)
    assert result["total_count"] >= 2
    assert len(result["documents"]) >= 2

    # Verify document structure
    doc = result["documents"][0]
    assert "id" in doc
    assert "filename" in doc
    assert "namespace" in doc
    assert "chunk_count" in doc
    assert doc["namespace"] == "test_namespace"


def test_add_documents_creates_mysql_records(rag_service, test_namespace):
    """Test that add_documents creates MySQL records."""
    # Add a simple text document
    test_content = "This is a test document for MySQL integration testing."

    # Create a temporary file
    test_file = Path("test_doc.txt")
    test_file.write_text(test_content)

    try:
        # Add document
        rag_service.add_documents(
            documents=[test_file], namespace=test_namespace, chunk_size=100, chunk_overlap=20
        )

        # Query MySQL to verify document was tracked
        result = query_knowledge_base_documents(namespace=test_namespace, limit=10)

        assert result["total_count"] >= 1, "Should have at least 1 document in MySQL"
        assert len(result["documents"]) >= 1

        doc = result["documents"][0]
        assert doc["filename"] == "test_doc.txt"
        assert doc["namespace"] == test_namespace
        assert doc["chunk_count"] > 0
        assert doc["file_size"] > 0

    finally:
        # Cleanup test file
        if test_file.exists():
            test_file.unlink()


def test_list_documents_returns_added_documents(rag_service, test_namespace):
    """Test that list_documents returns documents added via add_documents."""
    # Add multiple test files
    test_files = []
    for i in range(3):
        test_file = Path(f"test_doc_{i}.txt")
        test_file.write_text(f"Test document {i} content for MySQL integration.")
        test_files.append(test_file)

    try:
        # Add documents
        rag_service.add_documents(
            documents=test_files, namespace=test_namespace, chunk_size=100, chunk_overlap=20
        )

        # Use RAG service list_documents method
        result = rag_service.list_documents(namespace=test_namespace, limit=10)

        assert result["total_count"] == 3, "Should have exactly 3 documents"
        assert len(result["documents"]) == 3

        # Verify all test files are listed
        filenames = {doc["filename"] for doc in result["documents"]}
        expected_filenames = {f"test_doc_{i}.txt" for i in range(3)}
        assert filenames == expected_filenames

    finally:
        # Cleanup test files
        for test_file in test_files:
            if test_file.exists():
                test_file.unlink()


def test_upsert_behavior():
    """Test that duplicate doc_id updates instead of inserting."""
    doc = {
        "doc_id": "test_upsert_doc",
        "content": "Original content",
        "filename": "test.txt",
        "namespace": "test",
        "chunk_count": 1,
        "file_size": 100,
    }

    # First insert
    bulk_insert_knowledge_documents([doc])

    result = query_knowledge_base_documents(namespace="test", limit=10)
    assert result["total_count"] == 1
    original_id = result["documents"][0]["id"]

    # Update with more chunks
    doc["chunk_count"] = 5
    doc["file_size"] = 500
    bulk_insert_knowledge_documents([doc])

    result = query_knowledge_base_documents(namespace="test", limit=10)
    assert result["total_count"] == 1, "Should still have only 1 document (upsert)"

    updated_doc = result["documents"][0]
    assert updated_doc["id"] == original_id, "Should be same document ID"
    assert updated_doc["chunk_count"] == 5, "Chunk count should be updated"
    assert updated_doc["file_size"] == 500, "File size should be updated"


def test_namespace_filtering():
    """Test that namespace filtering works correctly."""
    documents = [
        {
            "doc_id": "ns1_doc1",
            "content": "Namespace 1 doc",
            "filename": "ns1.txt",
            "namespace": "namespace1",
            "chunk_count": 1,
        },
        {
            "doc_id": "ns2_doc1",
            "content": "Namespace 2 doc",
            "filename": "ns2.txt",
            "namespace": "namespace2",
            "chunk_count": 1,
        },
    ]

    bulk_insert_knowledge_documents(documents)

    # Query namespace1
    result1 = query_knowledge_base_documents(namespace="namespace1", limit=10)
    assert result1["total_count"] == 1
    assert result1["documents"][0]["namespace"] == "namespace1"

    # Query namespace2
    result2 = query_knowledge_base_documents(namespace="namespace2", limit=10)
    assert result2["total_count"] == 1
    assert result2["documents"][0]["namespace"] == "namespace2"

    # Query all namespaces
    result_all = query_knowledge_base_documents(namespace=None, limit=10)
    assert result_all["total_count"] >= 2
