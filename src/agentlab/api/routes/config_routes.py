"""
Configuration management API routes.

Endpoints for:
- Getting current configuration status
- Updating session-specific configurations
- Managing memory and RAG toggles
"""

import os
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agentlab.database.crud import (
    create_or_update_session_config,
    delete_session_config,
    get_session_config,
)
from agentlab.models.config_models import (
    ConfigurationStatus,
    MemoryToggles,
    RAGToggles,
    RuntimeConfig,
)

router = APIRouter()


class UpdateConfigRequest(BaseModel):
    """Request to update session configuration."""

    session_id: str = Field(..., description="Session ID")
    memory: MemoryToggles | None = Field(
        None, description="Memory toggles to update"
    )
    rag: RAGToggles | None = Field(None, description="RAG toggles to update")


class ConfigResponse(BaseModel):
    """Response with configuration."""

    config: RuntimeConfig
    message: str = "Configuration retrieved successfully"


@router.get("/status", response_model=ConfigurationStatus)
async def get_configuration_status():
    """
    Get current system configuration status.

    Returns:
        Configuration status with availability of services and warnings.
    """
    try:
        from agentlab.api.routes.chat_routes import (
            get_llm,
            get_memory_service,
            get_rag_service,
        )
        
        warnings = []
        dependencies = {}
        
        # Check LLM availability
        try:
            llm = get_llm()
            dependencies["llm"] = True
        except Exception as e:
            warnings.append(f"LLM unavailable: {e}")
            dependencies["llm"] = False
        
        # Check Memory availability
        memory_available = False
        try:
            memory_service = get_memory_service()
            memory_available = memory_service is not None
            dependencies["memory"] = memory_available
            
            if not memory_available:
                warnings.append(
                    "Memory service unavailable. Check database configuration."
                )
        except Exception as e:
            warnings.append(f"Memory service error: {e}")
            dependencies["memory"] = False
        
        # Check RAG availability
        rag_available = False
        try:
            rag_service = get_rag_service()
            rag_available = rag_service is not None
            dependencies["rag"] = rag_available
            
            if not rag_available:
                warnings.append(
                    "RAG service unavailable. Check Pinecone configuration or ENABLE_RAG setting."
                )
        except Exception as e:
            warnings.append(f"RAG service error: {e}")
            dependencies["rag"] = False
        
        # Check environment variables
        if not os.getenv("OPENAI_API_KEY"):
            warnings.append("OPENAI_API_KEY not set")
            dependencies["openai"] = False
        else:
            dependencies["openai"] = True
        
        if not os.getenv("PINECONE_API_KEY"):
            dependencies["pinecone"] = False
        else:
            dependencies["pinecone"] = True
        
        # Build default configuration
        default_config = RuntimeConfig(
            session_id="default",
            memory=MemoryToggles(),
            rag=RAGToggles(),
        )
        
        return ConfigurationStatus(
            memory_available=memory_available,
            rag_available=rag_available,
            current_config=default_config,
            warnings=warnings if warnings else None,
            dependencies=dependencies,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get configuration: {e}"
        )


@router.get("/session/{session_id}", response_model=ConfigResponse)
async def get_session_configuration(session_id: str):
    """
    Get configuration for a specific session.

    Args:
        session_id: Session identifier.

    Returns:
        Session configuration or default if not found.
    """
    try:
        config_data = get_session_config(session_id)
        
        if config_data:
            # Parse stored configuration
            runtime_config = RuntimeConfig(
                session_id=session_id,
                memory=MemoryToggles(**config_data["memory_config"]),
                rag=RAGToggles(**config_data["rag_config"]),
                metadata=config_data.get("metadata"),
            )
            message = "Configuration retrieved successfully"
        else:
            # Return default configuration
            runtime_config = RuntimeConfig(
                session_id=session_id,
                memory=MemoryToggles(),
                rag=RAGToggles(),
            )
            message = "No stored configuration found, returning defaults"
        
        return ConfigResponse(config=runtime_config, message=message)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve session configuration: {e}",
        )


@router.post("/session", response_model=ConfigResponse)
async def update_session_configuration(request: UpdateConfigRequest):
    """
    Update configuration for a specific session.

    Args:
        request: Configuration update request.

    Returns:
        Updated configuration.
    """
    try:
        # Get existing configuration or create default
        existing = get_session_config(request.session_id)
        
        if existing:
            memory_config = existing["memory_config"]
            rag_config = existing["rag_config"]
            metadata = existing.get("metadata")
        else:
            memory_config = MemoryToggles().model_dump()
            rag_config = RAGToggles().model_dump()
            metadata = None
        
        # Update with provided values
        if request.memory:
            memory_config.update(request.memory.model_dump())
        
        if request.rag:
            rag_config.update(request.rag.model_dump())
        
        # Save to database
        create_or_update_session_config(
            session_id=request.session_id,
            memory_config=memory_config,
            rag_config=rag_config,
            metadata=metadata,
        )
        
        # Return updated configuration
        runtime_config = RuntimeConfig(
            session_id=request.session_id,
            memory=MemoryToggles(**memory_config),
            rag=RAGToggles(**rag_config),
            metadata=metadata,
        )
        
        return ConfigResponse(
            config=runtime_config,
            message="Configuration updated successfully",
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update session configuration: {e}",
        )


@router.delete("/session/{session_id}")
async def delete_session_configuration(session_id: str):
    """
    Delete configuration for a specific session.

    Args:
        session_id: Session identifier.

    Returns:
        Success message.
    """
    try:
        deleted = delete_session_config(session_id)
        
        if deleted:
            return {"message": f"Configuration for session {session_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No configuration found for session {session_id}",
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session configuration: {e}",
        )


@router.put("/memory", response_model=ConfigResponse)
async def update_memory_configuration(
    session_id: str, memory: MemoryToggles
):
    """
    Update only memory configuration for a session.

    Args:
        session_id: Session identifier.
        memory: Memory toggles.

    Returns:
        Updated configuration.
    """
    return await update_session_configuration(
        UpdateConfigRequest(session_id=session_id, memory=memory)
    )


@router.put("/rag", response_model=ConfigResponse)
async def update_rag_configuration(session_id: str, rag: RAGToggles):
    """
    Update only RAG configuration for a session.

    Args:
        session_id: Session identifier.
        rag: RAG toggles.

    Returns:
        Updated configuration.
    """
    return await update_session_configuration(
        UpdateConfigRequest(session_id=session_id, rag=rag)
    )
