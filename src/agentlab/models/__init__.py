"""
Data models and Protocol definitions for Agent Lab.

This module defines abstract interfaces (Protocols) for dependency injection,
following the Dependency Inversion Principle. All implementations should depend
on these abstractions rather than concrete classes.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Protocol

# Import runtime configuration models
from agentlab.models.config_models import (
    ConfigurationStatus,
    MemoryToggles,
    RAGToggles,
    RuntimeConfig,
)


# ============================================================================
# Data Models (Dataclasses)
# ============================================================================


@dataclass
class ChatMessage:
    """Represents a chat message in a conversation."""

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime
    metadata: dict[str, Any] | None = None


@dataclass
class RAGResult:
    """Result from a RAG query operation."""

    success: bool
    response: str
    sources: list[dict[str, Any]]
    error_message: str | None = None


@dataclass
class RetrievalResult:
    """Result from document retrieval without LLM generation."""

    success: bool
    sources: list[dict[str, Any]]
    query: str
    error_message: str | None = None


@dataclass
class KnowledgeDocument:
    """A document stored in the knowledge base."""

    doc_id: str
    content: str
    embedding: list[float] | None
    metadata: dict[str, Any]
    created_at: datetime


@dataclass
class MemoryContext:
    """Context extracted from conversation memory."""

    session_id: str
    short_term_context: str
    semantic_facts: list[str]
    user_profile: dict[str, Any]
    episodic_summary: str | None = None
    procedural_patterns: list[str] | None = None
    total_messages: int = 0
    metadata: dict[str, Any] | None = None


@dataclass
class MemoryStats:
    """Statistics about memory usage."""

    session_id: str
    message_count: int
    token_count: int
    semantic_facts_count: int
    profile_attributes_count: int
    oldest_message_date: datetime | None
    newest_message_date: datetime | None


@dataclass
class ToolCall:
    """Represents a tool call made by the LLM."""

    id: str
    name: str
    args: dict[str, Any]
    timestamp: datetime | None = None


@dataclass
class ToolResult:
    """Result from executing a tool call."""

    tool_call_id: str
    tool_name: str
    result: dict[str, Any]
    success: bool
    error: str | None = None
    timestamp: datetime | None = None


@dataclass
class AgentStep:
    """Represents a single step in the agent's reasoning process."""

    step_number: int
    action: Literal["tool_call", "final_answer"]
    tool_call: ToolCall | None = None
    tool_result: ToolResult | None = None
    reasoning: str | None = None


# ============================================================================
# Protocol Definitions (Interfaces)
# ============================================================================


class LLMInterface(Protocol):
    """Protocol for interacting with Large Language Models."""

    def generate(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000
    ) -> str:
        """
        Generate text from the LLM.

        Args:
            prompt: Input prompt for the model.
            temperature: Sampling temperature (0.0 to 1.0).
            max_tokens: Maximum tokens to generate.

        Returns:
            Generated text response.
        """
        ...

    def chat(self, messages: list[ChatMessage]) -> str:
        """
        Generate a chat response from conversation history.

        Args:
            messages: List of chat messages.

        Returns:
            Generated response from the assistant.
        """
        ...


class RAGService(Protocol):
    """Protocol for Retrieval Augmented Generation services."""

    def query(self, query: str, top_k: int = 5) -> RAGResult:
        """
        Query the RAG system with a question.

        Args:
            query: User query string.
            top_k: Number of top documents to retrieve.

        Returns:
            RAG result with response and sources.
        """
        ...

    def add_documents(self, documents: list[str]) -> None:
        """
        Add documents to the knowledge base.

        Args:
            documents: List of document strings to add.
        """
        ...


class MPCClient(Protocol):
    """Protocol for Model Context Protocol clients."""

    def connect(self, host: str, port: int) -> None:
        """
        Connect to an MCP server.

        Args:
            host: Server hostname or IP address.
            port: Server port number.
        """
        ...

    def send_request(self, request_data: dict[str, Any]) -> dict[str, Any]:
        """
        Send a request to the MCP server.

        Args:
            request_data: Request payload.

        Returns:
            Response from the server.
        """
        ...

    def disconnect(self) -> None:
        """Disconnect from the MPC server."""
        ...


class MPCServer(Protocol):
    """Protocol for Model Context Protocol servers."""

    def start(self, host: str, port: int) -> None:
        """
        Start the MPC server.

        Args:
            host: Hostname to bind to.
            port: Port to listen on.
        """
        ...

    def stop(self) -> None:
        """Stop the MPC server."""
        ...

    def handle_request(self, request_data: dict[str, Any]) -> dict[str, Any]:
        """
        Handle an incoming MPC request.

        Args:
            request_data: Request payload from client.

        Returns:
            Response to send back to client.
        """
        ...


class DatabaseConnection(Protocol):
    """Protocol for database operations."""

    def connect(self) -> None:
        """Establish database connection."""
        ...

    def disconnect(self) -> None:
        """Close database connection."""
        ...

    def execute_query(self, query: str, params: tuple = ()) -> list[dict]:
        """
        Execute a SQL query.

        Args:
            query: SQL query string.
            params: Query parameters.

        Returns:
            List of result rows as dictionaries.
        """
        ...


class DocumentLoader(Protocol):
    """Protocol for loading documents from various file formats."""

    def load(self, file_path: str | Path) -> str:
        """
        Load document content from a file.

        Args:
            file_path: Path to the document file.

        Returns:
            Document content as text string.

        Raises:
            FileNotFoundError: If file doesn't exist.
            RuntimeError: If file cannot be loaded or parsed.
        """
        ...

    def supports(self, file_path: str | Path) -> bool:
        """
        Check if this loader supports the given file type.

        Args:
            file_path: Path to check.

        Returns:
            True if this loader can handle the file type.
        """
        ...


class MemoryService(Protocol):
    """Protocol for conversation memory management."""

    def add_message(
        self, session_id: str, message: ChatMessage
    ) -> None:
        """
        Add a message to conversation memory.

        Args:
            session_id: Unique session identifier.
            message: Chat message to store.
        """
        ...

    def get_messages(
        self, session_id: str, limit: int = 50
    ) -> list[ChatMessage]:
        """
        Retrieve conversation history for a session.

        Args:
            session_id: Session identifier.
            limit: Maximum number of messages to retrieve.

        Returns:
            List of chat messages ordered by timestamp.
        """
        ...

    def get_context(
        self, session_id: str, max_tokens: int = 2000
    ) -> MemoryContext:
        """
        Get enriched context from conversation memory.

        Args:
            session_id: Session identifier.
            max_tokens: Maximum tokens to include in context.

        Returns:
            Memory context with short-term and long-term information.
        """
        ...

    def clear_session(self, session_id: str) -> None:
        """
        Clear all memory for a session.

        Args:
            session_id: Session identifier to clear.
        """
        ...

    def get_stats(self, session_id: str) -> MemoryStats:
        """
        Get memory statistics for a session.

        Args:
            session_id: Session identifier.

        Returns:
            Memory usage statistics.
        """
        ...


class ShortTermMemory(Protocol):
    """Protocol for short-term conversation memory."""

    def add(self, session_id: str, message: ChatMessage) -> None:
        """Add message to short-term memory."""
        ...

    def get_buffer(self, session_id: str) -> str:
        """Get formatted conversation buffer."""
        ...

    def get_window(
        self, session_id: str, k: int = 10
    ) -> list[ChatMessage]:
        """Get last k messages from session."""
        ...


class LongTermMemory(Protocol):
    """Protocol for long-term memory with semantic storage."""

    def extract_semantic_facts(
        self, session_id: str, messages: list[ChatMessage]
    ) -> list[str]:
        """Extract semantic facts from conversation."""
        ...

    def get_user_profile(self, session_id: str) -> dict[str, Any]:
        """Get aggregated user profile from conversation history."""
        ...

    def get_episodic_summary(self, session_id: str) -> str | None:
        """Get temporal summary of conversation episodes."""
        ...

    def get_procedural_patterns(
        self, session_id: str
    ) -> list[str]:
        """Identify procedural patterns from user interactions."""
        ...

    def store_semantic_embedding(
        self, session_id: str, text: str, metadata: dict[str, Any]
    ) -> None:
        """Store semantic embedding in vector database."""
        ...

    def search_semantic(
        self, query: str, session_id: str | None = None, top_k: int = 5
    ) -> list[dict[str, Any]]:
        """Search semantic memory for relevant facts."""
        ...


# Export all public symbols
__all__ = [
    # Configuration models
    "ConfigurationStatus",
    "MemoryToggles",
    "RAGToggles",
    "RuntimeConfig",
    # Data models
    "ChatMessage",
    "RAGResult",
    "RetrievalResult",
    "KnowledgeDocument",
    "MemoryContext",
    "MemoryStats",
    "ToolCall",
    "ToolResult",
    "AgentStep",
    # Protocol definitions
    "LLMInterface",
    "RAGService",
    "MPCClient",
    "MPCServer",
    "DatabaseConnection",
    "DocumentLoader",
    "MemoryService",
    "ShortTermMemory",
    "LongTermMemory",
]
