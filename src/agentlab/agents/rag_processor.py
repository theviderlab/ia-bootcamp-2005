"""
RAG processor - Low-level functions for RAG operations.

Handles:
- Text embedding generation
- Vector similarity search
- Document chunking and preprocessing
"""

import hashlib
import numpy as np
from datetime import datetime
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def generate_embedding(
    text: str, embeddings: OpenAIEmbeddings
) -> list[float]:
    """
    Generate vector embedding for text using OpenAI embeddings.

    Args:
        text: Text to embed.
        embeddings: Configured OpenAI embeddings instance.

    Returns:
        Vector embedding as list of floats.

    Raises:
        ValueError: If text is empty.
        RuntimeError: If embedding generation fails.
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    try:
        embedding = embeddings.embed_query(text)
        return embedding
    except Exception as e:
        raise RuntimeError(f"Failed to generate embedding: {e}") from e


def chunk_document(
    document: str,
    chunk_size: int = 1000,
    overlap: int = 200,
    source: str | None = None,
) -> list[Document]:
    """
    Split document into overlapping chunks with metadata.

    Args:
        document: Full document text.
        chunk_size: Maximum characters per chunk.
        overlap: Number of overlapping characters between chunks.
        source: Source filename or identifier for metadata.

    Returns:
        List of LangChain Document objects with metadata.

    Raises:
        ValueError: If chunk_size or overlap are invalid.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and less than chunk_size")

    # Use RecursiveCharacterTextSplitter for intelligent chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    # Split text into chunks
    texts = text_splitter.split_text(document)

    # Create Document objects with metadata
    documents = []
    created_at = datetime.now().isoformat()

    for idx, text in enumerate(texts):
        metadata = {
            "chunk": idx,
            "created_at": created_at,
            "total_chunks": len(texts),
        }

        if source:
            metadata["source"] = source

        doc = Document(page_content=text, metadata=metadata)
        documents.append(doc)

    return documents


def calculate_similarity(
    query_embedding: list[float], doc_embedding: list[float]
) -> float:
    """
    Calculate cosine similarity between two embeddings.

    Args:
        query_embedding: Query vector.
        doc_embedding: Document vector.

    Returns:
        Similarity score (0 to 1).

    Raises:
        ValueError: If vectors have different dimensions or are empty.
    """
    if not query_embedding or not doc_embedding:
        raise ValueError("Embeddings cannot be empty")

    if len(query_embedding) != len(doc_embedding):
        raise ValueError(
            f"Embedding dimensions must match: {len(query_embedding)} != {len(doc_embedding)}"
        )

    # Convert to numpy arrays
    query_vec = np.array(query_embedding)
    doc_vec = np.array(doc_embedding)

    # Calculate cosine similarity
    dot_product = np.dot(query_vec, doc_vec)
    query_norm = np.linalg.norm(query_vec)
    doc_norm = np.linalg.norm(doc_vec)

    if query_norm == 0 or doc_norm == 0:
        return 0.0

    similarity = dot_product / (query_norm * doc_norm)

    # Normalize to 0-1 range (cosine similarity is -1 to 1)
    return float((similarity + 1) / 2)


def preprocess_text(text: str) -> str:
    """
    Preprocess text before embedding.

    Args:
        text: Raw text.

    Returns:
        Preprocessed text.
    """
    # Basic preprocessing: strip whitespace, normalize spaces
    text = " ".join(text.split())
    return text.strip()


def generate_document_id(content: str, source: str | None = None) -> str:
    """
    Generate a stable document ID from content and source.

    Uses SHA-256 hash to create reproducible IDs for upsert behavior.

    Args:
        content: Document content.
        source: Source filename or identifier.

    Returns:
        Hexadecimal document ID.
    """
    # Combine source and content for ID generation
    id_string = f"{source or 'unknown'}:{content[:200]}"
    return hashlib.sha256(id_string.encode()).hexdigest()


def load_text_file(file_path: str | Path) -> str:
    """
    Load text file content.

    Args:
        file_path: Path to text file.

    Returns:
        File content as string.

    Raises:
        FileNotFoundError: If file doesn't exist.
        RuntimeError: If file cannot be read.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        raise RuntimeError(f"Failed to read file {file_path}: {e}") from e
