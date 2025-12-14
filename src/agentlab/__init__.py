"""
AgentLab - LLM, MCP & RAG Learning Platform.

This package provides a modular architecture for experimenting with:
- Large Language Models (LLMs) via LangChain
- Model Context Protocol (MCP) servers and clients (Anthropic's specification)
- Retrieval Augmented Generation (RAG) systems

The application is organized into:
- core: High-level business logic and services
- agents: Low-level implementations and processors
- api: FastAPI REST API
- database: Data persistence layer

Public API:
    Core Services:
        - LangChainLLM: LLM interface using LangChain
        - RAGService: Retrieval Augmented Generation service
        - MPCManager: Model Context Protocol manager
    
    Models:
        - ChatMessage: Chat message data structure
        - LLMInterface: Protocol for LLM implementations
        - RAGServiceProtocol: Protocol for RAG services
    
    Agents:
        - RAGProcessor: Document processing and embeddings
        - MPCClientBase: Base class for MCP clients
        - MPCServerBase: Base class for MCP servers

Example:
    >>> from agentlab import LangChainLLM, ChatMessage
    >>> from datetime import datetime
    >>> 
    >>> llm = LangChainLLM(model_name="gpt-3.5-turbo")
    >>> response = llm.generate("Explain machine learning", temperature=0.7)
    >>> print(response)
"""

__version__ = "0.1.0"

# Core services - publicly accessible API
from agentlab.core.llm_interface import LangChainLLM

# Models and protocols
from agentlab.models import ChatMessage, LLMInterface

# Public API exports
__all__ = [
    # Version
    "__version__",
    # Core services
    "LangChainLLM",
    # Models
    "ChatMessage",
    "LLMInterface",
]
