"""
AgentLab - LLM, MCP & RAG Learning Platform.

This package provides a modular architecture for experimenting with:
- Large Language Models (LLMs) via LangChain
- Model Context Protocol (MCP) tools for LLM function calling
- Retrieval Augmented Generation (RAG) systems

The application is organized into:
- core: High-level business logic and services
- mcp: MCP tools infrastructure (registry, base classes)
- agents: Low-level implementations and processors
- api: FastAPI REST API
- database: Data persistence layer

Public API:
    Core Services:
        - LangChainLLM: LLM interface using LangChain
        - RAGService: Retrieval Augmented Generation service
    
    MCP Tools:
        - MCPToolRegistry: Central registry for MCP tools
        - MCPToolBase: Base class for creating tools
        - get_registry: Get global tool registry instance
    
    Models:
        - ChatMessage: Chat message data structure
        - LLMInterface: Protocol for LLM implementations
        - RAGServiceProtocol: Protocol for RAG services
    
    Agents:
        - RAGProcessor: Document processing and embeddings

Example:
    >>> from agentlab import LangChainLLM, ChatMessage
    >>> from agentlab.mcp import get_registry
    >>> 
    >>> # Use LLM
    >>> llm = LangChainLLM(model_name="gpt-3.5-turbo")
    >>> response = llm.generate("Explain machine learning", temperature=0.7)
    >>> 
    >>> # Use MCP tools
    >>> registry = get_registry()
    >>> tools = registry.get_langchain_tools()
    >>> print(registry.list_tools())
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
