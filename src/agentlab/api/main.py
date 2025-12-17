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
            },
            "memory": {
                "context": "/llm/memory/context",
                "history": "/llm/memory/history",
                "stats": "/llm/memory/stats",
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
            "mpc": {
                "create_instance": "/mpc/instances",
                "delete_instance": "/mpc/instances/{instance_id}",
                "get_instance": "/mpc/instances/{instance_id}",
                "list_instances": "/mpc/instances",
            },
        },
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Mount routers
from agentlab.api.routes import chat_routes, config_routes, mpc_routes

app.include_router(chat_routes.router, prefix="/llm", tags=["llm"])
app.include_router(config_routes.router, prefix="/config", tags=["config"])
app.include_router(mpc_routes.router, prefix="/mpc", tags=["mpc"])
