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
