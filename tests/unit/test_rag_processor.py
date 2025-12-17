"""
Unit tests for RAG processor functions.

Tests document chunking, embedding generation, and text preprocessing
with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, MagicMock
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from agentlab.agents.rag_processor import (
    chunk_document,
    calculate_similarity,
    preprocess_text,
    generate_document_id,
    generate_embedding,
)


class TestChunkDocument:
    """Tests for chunk_document function."""

    def test_basic_chunking(self):
        """Test basic document chunking."""
        document = "This is a test document. " * 100  # ~2500 chars
        chunks = chunk_document(document, chunk_size=500, overlap=50)

        assert len(chunks) > 1
        assert all(isinstance(chunk, Document) for chunk in chunks)
        assert all("chunk" in chunk.metadata for chunk in chunks)
        assert all("created_at" in chunk.metadata for chunk in chunks)

    def test_chunking_with_source(self):
        """Test chunking includes source metadata."""
        document = "Test content " * 100
        source = "test_file.txt"
        chunks = chunk_document(document, source=source)

        assert all(chunk.metadata["source"] == source for chunk in chunks)

    def test_small_document_single_chunk(self):
        """Test small document creates single chunk."""
        document = "Short document"
        chunks = chunk_document(document, chunk_size=1000)

        assert len(chunks) == 1
        assert chunks[0].page_content == document

    def test_chunk_metadata_indexing(self):
        """Test chunks have sequential indices."""
        document = "Content. " * 200
        chunks = chunk_document(document, chunk_size=100, overlap=20)

        indices = [chunk.metadata["chunk"] for chunk in chunks]
        assert indices == list(range(len(chunks)))

    def test_invalid_chunk_size(self):
        """Test invalid chunk_size raises ValueError."""
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            chunk_document("test", chunk_size=0)

        with pytest.raises(ValueError, match="chunk_size must be positive"):
            chunk_document("test", chunk_size=-100)

    def test_invalid_overlap(self):
        """Test invalid overlap raises ValueError."""
        with pytest.raises(ValueError, match="overlap must be non-negative"):
            chunk_document("test", chunk_size=100, overlap=-10)

        with pytest.raises(
            ValueError, match="overlap must be non-negative and less than chunk_size"
        ):
            chunk_document("test", chunk_size=100, overlap=150)


class TestCalculateSimilarity:
    """Tests for calculate_similarity function."""

    def test_identical_vectors(self):
        """Test similarity of identical vectors is 1.0."""
        vec = [1.0, 2.0, 3.0, 4.0]
        similarity = calculate_similarity(vec, vec)

        assert similarity == pytest.approx(1.0, abs=0.01)

    def test_orthogonal_vectors(self):
        """Test similarity of orthogonal vectors is ~0.5."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        similarity = calculate_similarity(vec1, vec2)

        # Normalized to 0-1 range, orthogonal should be ~0.5
        assert similarity == pytest.approx(0.5, abs=0.01)

    def test_opposite_vectors(self):
        """Test similarity of opposite vectors is ~0.0."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [-1.0, -2.0, -3.0]
        similarity = calculate_similarity(vec1, vec2)

        assert similarity == pytest.approx(0.0, abs=0.01)

    def test_empty_vectors_error(self):
        """Test empty vectors raise ValueError."""
        with pytest.raises(ValueError, match="Embeddings cannot be empty"):
            calculate_similarity([], [1.0, 2.0])

        with pytest.raises(ValueError, match="Embeddings cannot be empty"):
            calculate_similarity([1.0, 2.0], [])

    def test_different_dimensions_error(self):
        """Test vectors with different dimensions raise ValueError."""
        with pytest.raises(ValueError, match="Embedding dimensions must match"):
            calculate_similarity([1.0, 2.0], [1.0, 2.0, 3.0])


class TestPreprocessText:
    """Tests for preprocess_text function."""

    def test_basic_preprocessing(self):
        """Test basic whitespace normalization."""
        text = "  Multiple   spaces   between   words  "
        result = preprocess_text(text)

        assert result == "Multiple spaces between words"

    def test_newline_normalization(self):
        """Test newlines are converted to spaces."""
        text = "Line one\nLine two\nLine three"
        result = preprocess_text(text)

        assert result == "Line one Line two Line three"

    def test_mixed_whitespace(self):
        """Test mixed whitespace (tabs, newlines, spaces) normalization."""
        text = "Word1\t\tWord2\n\nWord3   Word4"
        result = preprocess_text(text)

        assert result == "Word1 Word2 Word3 Word4"

    def test_empty_string(self):
        """Test empty string returns empty."""
        assert preprocess_text("") == ""
        assert preprocess_text("   ") == ""


class TestGenerateDocumentId:
    """Tests for generate_document_id function."""

    def test_stable_id_generation(self):
        """Test same content generates same ID."""
        content = "This is test content"
        source = "test.txt"

        id1 = generate_document_id(content, source)
        id2 = generate_document_id(content, source)

        assert id1 == id2
        assert len(id1) == 64  # SHA-256 hex length

    def test_different_content_different_id(self):
        """Test different content generates different ID."""
        source = "test.txt"

        id1 = generate_document_id("Content 1", source)
        id2 = generate_document_id("Content 2", source)

        assert id1 != id2

    def test_different_source_different_id(self):
        """Test different source generates different ID."""
        content = "Same content"

        id1 = generate_document_id(content, "file1.txt")
        id2 = generate_document_id(content, "file2.txt")

        assert id1 != id2

    def test_no_source(self):
        """Test ID generation without source."""
        content = "Content without source"
        doc_id = generate_document_id(content)

        assert len(doc_id) == 64
        assert isinstance(doc_id, str)


class TestGenerateEmbedding:
    """Tests for generate_embedding function."""

    def test_successful_embedding(self):
        """Test successful embedding generation."""
        mock_embeddings = Mock(spec=OpenAIEmbeddings)
        mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]

        result = generate_embedding("test text", mock_embeddings)

        assert result == [0.1, 0.2, 0.3]
        mock_embeddings.embed_query.assert_called_once_with("test text")

    def test_empty_text_error(self):
        """Test empty text raises ValueError."""
        mock_embeddings = Mock(spec=OpenAIEmbeddings)

        with pytest.raises(ValueError, match="Text cannot be empty"):
            generate_embedding("", mock_embeddings)

        with pytest.raises(ValueError, match="Text cannot be empty"):
            generate_embedding("   ", mock_embeddings)

    def test_embedding_failure_error(self):
        """Test embedding generation failure raises RuntimeError."""
        mock_embeddings = Mock(spec=OpenAIEmbeddings)
        mock_embeddings.embed_query.side_effect = Exception("API error")

        with pytest.raises(RuntimeError, match="Failed to generate embedding"):
            generate_embedding("test", mock_embeddings)
