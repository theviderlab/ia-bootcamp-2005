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
            "generate": "/llm/generate",
            "chat": "/llm/chat",
            "health": "/health",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Mount routers
from agentlab.api.routes import chat_routes

app.include_router(chat_routes.router, prefix="/llm", tags=["llm"])
