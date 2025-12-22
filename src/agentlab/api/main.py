"""
FastAPI application entry point.

Initializes the FastAPI app and mounts all routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Cargar variables de entorno ANTES de importar otros módulos
load_dotenv()

app = FastAPI(
    title="Agent Lab API",
    description="API for LLM, MCP, and RAG experimentation",
    version="0.1.0",
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Agent Lab API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "llm": {
                "generate": "/llm/generate",
                "chat": "/llm/chat",
            },
            "rag": {
                "query": "/llm/rag/query",
                "add_documents": "/llm/rag/documents",
                "add_directory": "/llm/rag/directory",
                "list_namespaces": "/llm/rag/namespaces",
                "list_documents": "/llm/rag/documents",
                "delete_namespace": "/llm/rag/namespace/{namespace}",
                "namespace_stats": "/llm/rag/namespace/{namespace}/stats",
            },
            "memory": {
                "context": "/llm/memory/context",
                "history": "/llm/memory/history/{session_id}",
                "stats": "/llm/memory/stats/{session_id}",
                "search": "/llm/memory/search",
                "clear": "/llm/memory/session/{session_id}",
            },
            "config": {
                "status": "/config/status",
                "get_session": "/config/session/{session_id}",
                "update_session": "/config/session",
                "delete_session": "/config/session/{session_id}",
                "update_memory": "/config/memory",
                "update_rag": "/config/rag",
            },
            "session": {
                "reset": "/session/reset",
                "reset_all": "/session/reset-all",
            },
            "mpc": {
                "list_tools": "/mpc/tools",
                "tool_names": "/mpc/tools/names",
                "get_tool": "/mpc/tools/{tool_name}",
            },
        },
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Mount routers
from agentlab.api.routes import (
    chat_router,
    rag_router,
    memory_router,
    config_routes,
    mpc_routes,
    session_routes,
)

app.include_router(chat_router, prefix="/llm", tags=["llm"])
app.include_router(rag_router, prefix="/llm/rag", tags=["rag"])
app.include_router(memory_router, prefix="/llm/memory", tags=["memory"])
app.include_router(config_routes.router, prefix="/config", tags=["config"])
app.include_router(mpc_routes.router, prefix="/mpc", tags=["mpc"])
app.include_router(session_routes.router, prefix="/session", tags=["session"])
