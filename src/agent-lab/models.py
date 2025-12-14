"""
Data models and Protocol definitions for Agent Lab.

This module defines abstract interfaces (Protocols) for dependency injection,
following the Dependency Inversion Principle. All implementations should depend
on these abstractions rather than concrete classes.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Protocol


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
class MPCInstanceInfo:
    """Information about an MPC server instance."""

    instance_id: str
    status: Literal["running", "stopped", "error"]
    host: str
    port: int
    created_at: datetime
    metadata: dict[str, Any] | None = None


@dataclass
class KnowledgeDocument:
    """A document stored in the knowledge base."""

    doc_id: str
    content: str
    embedding: list[float] | None
    metadata: dict[str, Any]
    created_at: datetime


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
        """Disconnect from the MCP server."""
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
