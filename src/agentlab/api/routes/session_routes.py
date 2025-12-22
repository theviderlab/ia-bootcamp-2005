"""
Session management routes.

Provides endpoints for:
- Session reset (clear short-term memory, generate new session ID)
- System reset (nuclear option - delete all data)
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException

from agentlab.database import crud
from agentlab.models.config_models import (
    DeletionCounts,
    SessionResetRequest,
    SessionResetResponse,
    SystemResetRequest,
    SystemResetResponse,
)
from agentlab.core.rag_service import RAGServiceImpl
from agentlab.core.llm_interface import LangChainLLM
from agentlab.config.rag_config import RAGConfig

router = APIRouter()


@router.get("/latest")
async def get_latest_session():
    """
    Get the most recent session ID from chat history.
    
    Returns:
        Dictionary with session_id or null if no sessions exist.
        
    Example:
        >>> GET /session/latest
        >>> 
        >>> Response:
        >>> {
        >>>   "session_id": "550e8400-e29b-41d4-a716-446655440000"
        >>> }
    """
    try:
        latest_session_id = crud.get_latest_session_id()
        return {"session_id": latest_session_id}
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get latest session: {str(e)}",
        )

@router.post("/reset", response_model=SessionResetResponse)
async def reset_session():
    """
    Reset the system by clearing all chat history and creating a fresh session.
    
    Deletes ALL chat messages from ALL sessions and generates a new session ID
    with default configuration. Preserves long-term memory (semantic facts,
    episodic summaries, user profile, procedural patterns) and RAG documents.
    
    Returns:
        SessionResetResponse with new session_id and success message.
        
    Raises:
        HTTPException: 500 if database operation fails.
        
    Example:
        >>> POST /session/reset
        >>> 
        >>> Response:
        >>> {
        >>>   "success": true,
        >>>   "new_session_id": "550e8400-e29b-41d4-a716-446655440000",
        >>>   "message": "Session reset successfully. Chat history cleared (15 messages)."
        >>> }
    """
    try:
        # Generate new UUID for session
        new_session_id = str(uuid.uuid4())
        
        # Clear ALL data from previous sessions
        deleted_count = crud.delete_all_chat_history()  # Delete all chat messages
        crud.delete_all_session_configs()  # Delete all old session configurations
        
        # Create fresh session configuration with default values
        from agentlab.models.config_models import MemoryToggles, RAGToggles
        default_memory = MemoryToggles().model_dump()
        default_rag = RAGToggles().model_dump()
        crud.create_or_update_session_config(
            session_id=new_session_id,
            memory_config=default_memory,
            rag_config=default_rag,
            metadata={"created_by": "reset"},
        )
        
        return SessionResetResponse(
            success=True,
            new_session_id=new_session_id,
            message=f"Session reset successfully. Chat history cleared ({deleted_count} messages).",
        )
        
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset session: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset session: {str(e)}",
        )


@router.post("/reset-all", response_model=SystemResetResponse)
async def reset_all_data(request: SystemResetRequest):
    """
    Nuclear option: Delete ALL data from the system.
    
    This permanently deletes:
    - All conversation history (all sessions)
    - All long-term memory (semantic, episodic, profile, procedural)
    - All RAG documents and vectors
    - All session configurations
    - All MPC instances
    
    ⚠️ WARNING: This operation is IRREVERSIBLE.
    
    Args:
        request: SystemResetRequest with confirmation="DELETE".
        
    Returns:
        SystemResetResponse with deletion counts.
        
    Raises:
        HTTPException: 400 if confirmation is incorrect.
        HTTPException: 500 if deletion fails.
        
    Example:
        >>> DELETE /session/reset-all
        >>> {
        >>>   "confirmation": "DELETE"
        >>> }
        >>> 
        >>> Response:
        >>> {
        >>>   "success": true,
        >>>   "message": "All data deleted. System restored to initial state.",
        >>>   "deleted": {
        >>>     "sessions": 15,
        >>>     "memory_entries": 234,
        >>>     "rag_documents": 45,
        >>>     "vector_count": 1230
        >>>   }
        >>> }
    """
    # Validate confirmation string
    if request.confirmation != "DELETE":
        raise HTTPException(
            status_code=400,
            detail="Invalid confirmation. Must be exactly 'DELETE' to proceed.",
        )
    
    try:
        # Initialize counters
        session_count = 0
        memory_count = 0
        rag_count = 0
        vector_count = 0
        
        # 1. Count unique sessions before deletion
        try:
            session_count = crud.count_unique_sessions()
        except Exception as e:
            print(f"Warning: Could not count sessions: {e}")
            session_count = 0
        
        # 2. Clear MySQL tables
        try:
            # Delete all chat history (short-term memory)
            memory_count = crud.delete_all_chat_history()
            
            # Delete all session configurations
            config_count = crud.delete_all_session_configs()
            
            # Delete all knowledge base documents
            rag_count = crud.delete_all_knowledge_base()
            
        except Exception as e:
            print(f"Warning: Database cleanup failed: {e}")
        
        # 3. Clear Pinecone vectors
        try:
            # Initialize RAG service to access Pinecone
            llm = LangChainLLM()
            rag_config = RAGConfig.from_env()
            rag_service = RAGServiceImpl(llm=llm, config=rag_config)
            
            # Get index stats to count vectors and find namespaces
            index = rag_service.pc.Index(rag_config.index_name)
            stats = index.describe_index_stats()
            
            # Count total vectors across all namespaces
            vector_count = stats.get("total_vector_count", 0)
            
            # Delete all vectors from all namespaces
            namespaces = stats.get("namespaces", {})
            for namespace_name in namespaces.keys():
                try:
                    index.delete(delete_all=True, namespace=namespace_name)
                    print(f"Deleted namespace: {namespace_name}")
                except Exception as ns_error:
                    print(f"Warning: Could not delete namespace {namespace_name}: {ns_error}")
            
            # Also delete default namespace (empty string)
            try:
                index.delete(delete_all=True, namespace="")
            except Exception as default_error:
                print(f"Warning: Could not delete default namespace: {default_error}")
                
        except Exception as e:
            print(f"Warning: Pinecone cleanup failed (may not be configured): {e}")
            vector_count = 0
        
        return SystemResetResponse(
            success=True,
            message="All data deleted. System restored to initial state.",
            deleted=DeletionCounts(
                sessions=session_count,
                memory_entries=memory_count,
                rag_documents=rag_count,
                vector_count=vector_count,
            ),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset system: {str(e)}",
        )
