"""
Runtime configuration models for dynamic feature toggling.

Allows users to enable/disable memory types and RAG functionality
per session or per request.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MemoryToggles(BaseModel):
    """
    Configuration for individual memory types.
    
    Allows granular control over which memory features are active.
    """

    enable_short_term: bool = Field(
        True, description="Enable conversation buffer/history"
    )
    enable_semantic: bool = Field(
        True, description="Enable semantic facts extraction"
    )
    enable_episodic: bool = Field(
        True, description="Enable episodic summaries"
    )
    enable_profile: bool = Field(
        True, description="Enable user profile building"
    )
    enable_procedural: bool = Field(
        True, description="Enable procedural pattern detection"
    )

class RAGToggles(BaseModel):
    """
    Configuration for RAG functionality.
    
    Supports granular namespace control for document-level toggling.
    """

    enable_rag: bool = Field(
        False, description="Enable RAG retrieval augmentation"
    )
    namespaces: list[str] = Field(
        default_factory=list,
        description="List of Pinecone namespaces to query (empty = all)",
    )
    top_k: int = Field(
        5, ge=1, le=20, description="Number of documents to retrieve"
    )

class RuntimeConfig(BaseModel):
    """
    Complete runtime configuration for a chat session.
    
    Can be stored per session_id in database or passed per request.
    """

    session_id: str = Field(..., description="Session identifier")
    memory: MemoryToggles = Field(
        default_factory=MemoryToggles,
        description="Memory configuration",
    )
    rag: RAGToggles = Field(
        default_factory=RAGToggles,
        description="RAG configuration",
    )
    metadata: dict | None = Field(
        None, description="Additional configuration metadata"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "memory": {
                    "enable_short_term": True,
                    "enable_semantic": True,
                    "enable_episodic": False,
                    "enable_profile": True,
                    "enable_procedural": False,
                },
                "rag": {
                    "enable_rag": True,
                    "namespaces": ["product_docs", "user_manual"],
                    "top_k": 5,
                },
            }
        }
    )

class ConfigurationStatus(BaseModel):
    """
    Current configuration status including dependency validation.
    
    Used by GET /config/status endpoint to show what features are available.
    """

    memory_available: bool = Field(
        ..., description="Memory service initialized and ready"
    )
    rag_available: bool = Field(
        ..., description="RAG service initialized and ready"
    )
    current_config: RuntimeConfig = Field(
        ..., description="Active configuration"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Configuration warnings (e.g., missing API keys)",
    )
    dependencies: dict[str, bool] = Field(
        default_factory=dict,
        description="Status of external dependencies (DB, Pinecone, etc.)",
    )


# Session Management Models

class SessionResetRequest(BaseModel):
    """Request model for session reset."""

    current_session_id: str = Field(
        ..., min_length=1, description="Current session ID to reset"
    )

class SessionResetResponse(BaseModel):
    """Response model for session reset."""

    success: bool = Field(..., description="Whether reset was successful")
    new_session_id: str = Field(..., description="New session ID")
    message: str = Field(..., description="Success message")

class SystemResetRequest(BaseModel):
    """Request model for system reset (nuclear option)."""

    confirmation: str = Field(
        ..., description="Must be exactly 'DELETE' to confirm"
    )

class DeletionCounts(BaseModel):
    """Counts of deleted items during system reset."""

    sessions: int = Field(..., description="Number of unique sessions deleted")
    memory_entries: int = Field(..., description="Chat history entries deleted")
    rag_documents: int = Field(..., description="RAG documents deleted")
    vector_count: int = Field(..., description="Vectors deleted from Pinecone")

class SystemResetResponse(BaseModel):
    """Response model for system reset."""

    success: bool = Field(..., description="Whether reset was successful")
    message: str = Field(..., description="Success message")
    deleted: DeletionCounts = Field(..., description="Deletion counts")


# RAG Listing Models

class NamespaceInfo(BaseModel):
    """Information about a RAG namespace."""

    name: str = Field(..., description="Namespace name")
    document_count: int = Field(..., description="Number of documents")
    total_chunks: int = Field(..., description="Total number of chunks/vectors")
    last_updated: str | None = Field(
        None, description="Last update timestamp"
    )

class NamespaceListResponse(BaseModel):
    """Response model for listing namespaces."""

    namespaces: list[NamespaceInfo] = Field(
        ..., description="List of available namespaces"
    )

class DocumentInfo(BaseModel):
    """Information about a RAG document."""

    id: str = Field(..., description="Document ID")
    filename: str = Field(..., description="Original filename")
    namespace: str = Field(..., description="Document namespace")
    chunk_count: int = Field(..., description="Number of chunks")
    uploaded_at: str = Field(..., description="Upload timestamp")
    file_size: int | None = Field(None, description="File size in bytes")

class DocumentListResponse(BaseModel):
    """Response model for listing documents."""

    documents: list[DocumentInfo] = Field(
        ..., description="List of documents"
    )
    total_count: int = Field(
        default=0, description="Total number of documents matching filter"
    )
    limit: int = Field(
        default=100, description="Maximum documents returned"
    )
    offset: int = Field(
        default=0, description="Number of documents skipped"
    )
    has_more: bool = Field(
        default=False, description="Whether more documents exist beyond this page"
    )


# RAG Query Results Models

class RAGChunk(BaseModel):
    """A single RAG chunk with score and metadata."""

    id: str = Field(..., description="Chunk ID")
    content: str = Field(..., description="Chunk content")
    score: float = Field(..., description="Similarity score")
    metadata: dict = Field(
        default_factory=dict, description="Chunk metadata"
    )

class RAGQueryResult(BaseModel):
    """Result of a RAG query with chunks and metadata."""

    query: str = Field(..., description="Original query text")
    timestamp: str = Field(..., description="Query timestamp")
    chunks: list[RAGChunk] = Field(..., description="Retrieved chunks")
    namespace: str | None = Field(None, description="Namespace filter used")
    top_k: int = Field(..., description="Number of chunks requested")

class LastRAGResultsResponse(BaseModel):
    """Response model for last RAG query results."""

    session_id: str = Field(..., description="Session ID")
    results: RAGQueryResult | None = Field(
        None, description="Last query results (null if no query yet)"
    )


# Context Window Models

class ContextComponent(BaseModel):
    """A component of the context window."""

    content: str = Field(..., description="Component content")
    tokens: int = Field(..., description="Token count")

class ConversationMessage(BaseModel):
    """A message in conversation history."""

    role: str = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    tokens: int = Field(..., description="Token count")

class ContextWindowResponse(BaseModel):
    """Response model for context window visualization."""

    session_id: str = Field(..., description="Session ID")
    total_tokens: int = Field(..., description="Total tokens used")
    max_tokens: int = Field(..., description="Maximum tokens allowed")
    components: dict[str, ContextComponent | list[ConversationMessage]] = Field(
        ..., description="Context components breakdown"
    )
