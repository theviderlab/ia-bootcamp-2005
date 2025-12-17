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
