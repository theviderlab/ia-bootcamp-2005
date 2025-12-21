"""
API routes package.

Routers:
- chat_routes: LLM generation and chat endpoints
- rag_routes: RAG document management and query endpoints
- memory_routes: Memory management and search endpoints
"""

from agentlab.api.routes.chat_routes import router as chat_router
from agentlab.api.routes.rag_routes import router as rag_router
from agentlab.api.routes.memory_routes import router as memory_router

__all__ = ["chat_router", "rag_router", "memory_router"]
