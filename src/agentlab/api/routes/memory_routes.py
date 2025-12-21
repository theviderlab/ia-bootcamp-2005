"""
Memory management API routes.

Endpoints for:
- Retrieving memory context for sessions
- Managing conversation history
- Searching semantic memory
- Memory statistics and cleanup
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agentlab.core.llm_interface import LangChainLLM
from agentlab.core.memory_service import IntegratedMemoryService

router = APIRouter()

# Global instances (in production, use proper dependency injection)
_llm_instance: LangChainLLM | None = None
_memory_instance: IntegratedMemoryService | None = None


def get_llm() -> LangChainLLM:
    """
    Get or create the LLM instance.

    Returns:
        LangChainLLM instance.

    Raises:
        HTTPException: If LLM initialization fails.
    """
    global _llm_instance
    if _llm_instance is None:
        try:
            import os
            temperature = float(os.getenv("LLM_DEFAULT_TEMPERATURE", "0.7"))
            max_tokens = int(os.getenv("LLM_DEFAULT_MAX_TOKENS", "1000"))
            
            _llm_instance = LangChainLLM(
                temperature=temperature,
                max_tokens=max_tokens
            )
        except ValueError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to initialize LLM: {str(e)}"
            )
    return _llm_instance


def get_memory_service() -> IntegratedMemoryService | None:
    """
    Get or create the memory service instance.

    Returns None if memory initialization fails.

    Returns:
        IntegratedMemoryService instance or None.
    """
    global _memory_instance
    if _memory_instance is None:
        try:
            from agentlab.config.memory_config import MemoryConfig
            
            try:
                config = MemoryConfig.from_env()
                llm = get_llm()
                _memory_instance = IntegratedMemoryService(llm=llm, config=config)
            except ValueError as e:
                print(f"⚠️  Memory service unavailable: {e}")
                return None
        except Exception as e:
            print(f"⚠️  Memory service initialization failed: {e}")
            return None
    return _memory_instance


class MemoryContextRequest(BaseModel):
    """Request model for memory context retrieval."""

    session_id: str = Field(..., min_length=1, description="Session identifier")
    max_tokens: int = Field(
        2000, gt=0, le=8000, description="Maximum tokens in context"
    )


class MemoryContextResponse(BaseModel):
    """Response model for memory context."""

    session_id: str
    short_term_context: str
    semantic_facts: list[str]
    user_profile: dict
    episodic_summary: str | None
    procedural_patterns: list[str] | None
    total_messages: int


class MemoryHistoryResponse(BaseModel):
    """Response model for conversation history."""

    session_id: str
    messages: list[dict]
    total_count: int


class MemoryStatsResponse(BaseModel):
    """Response model for memory statistics."""

    session_id: str
    message_count: int
    token_count: int
    semantic_facts_count: int
    profile_attributes_count: int
    oldest_message: str | None
    newest_message: str | None


class MemorySearchRequest(BaseModel):
    """Request model for semantic memory search."""

    query: str = Field(..., min_length=1, description="Search query")
    session_id: str | None = Field(None, description="Optional session filter")
    top_k: int = Field(5, gt=0, le=20, description="Number of results")


class MemorySearchResponse(BaseModel):
    """Response model for semantic search."""

    query: str
    results: list[dict]
    total_results: int


@router.post("/context", response_model=MemoryContextResponse)
async def get_memory_context(request: MemoryContextRequest):
    """
    Get enriched memory context for a session.

    Retrieves short-term conversation buffer plus long-term memory
    including semantic facts, user profile, episodic summary, and
    procedural patterns.

    Args:
        request: Context request with session ID and token limit.

    Returns:
        Complete memory context.

    Raises:
        HTTPException: If retrieval fails.
    """
    try:
        memory_service = get_memory_service()
        context = memory_service.get_context(
            session_id=request.session_id, 
            max_tokens=request.max_tokens
        )

        return MemoryContextResponse(
            session_id=context.session_id,
            short_term_context=context.short_term_context,
            semantic_facts=context.semantic_facts,
            user_profile=context.user_profile,
            episodic_summary=context.episodic_summary,
            procedural_patterns=context.procedural_patterns,
            total_messages=context.total_messages,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get context: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=MemoryHistoryResponse)
async def get_conversation_history(session_id: str, limit: int = 50):
    """
    Get conversation history for a session.

    Args:
        session_id: Session identifier.
        limit: Maximum number of messages (default: 50).

    Returns:
        Conversation history with messages.

    Raises:
        HTTPException: If retrieval fails.
    """
    try:
        memory_service = get_memory_service()
        messages = memory_service.get_messages(session_id, limit=limit)

        message_dicts = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata,
            }
            for msg in messages
        ]

        return MemoryHistoryResponse(
            session_id=session_id,
            messages=message_dicts,
            total_count=len(message_dicts),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get history: {str(e)}"
        )


@router.delete("/{session_id}")
async def clear_conversation_memory(session_id: str):
    """
    Clear all memory for a session.

    Args:
        session_id: Session identifier to clear.

    Returns:
        Success message.

    Raises:
        HTTPException: If clearing fails.
    """
    try:
        memory_service = get_memory_service()
        memory_service.clear_session(session_id)

        return {"success": True, "message": f"Cleared memory for session {session_id}"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to clear memory: {str(e)}"
        )


@router.get("/stats/{session_id}", response_model=MemoryStatsResponse)
async def get_memory_statistics(session_id: str):
    """
    Get memory statistics for a session.

    Args:
        session_id: Session identifier.

    Returns:
        Memory usage statistics.

    Raises:
        HTTPException: If retrieval fails.
    """
    try:
        memory_service = get_memory_service()
        stats = memory_service.get_stats(session_id)

        return MemoryStatsResponse(
            session_id=stats.session_id,
            message_count=stats.message_count,
            token_count=stats.token_count,
            semantic_facts_count=stats.semantic_facts_count,
            profile_attributes_count=stats.profile_attributes_count,
            oldest_message=stats.oldest_message_date.isoformat()
            if stats.oldest_message_date
            else None,
            newest_message=stats.newest_message_date.isoformat()
            if stats.newest_message_date
            else None,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get stats: {str(e)}"
        )


@router.post("/search", response_model=MemorySearchResponse)
async def search_semantic_memory(request: MemorySearchRequest):
    """
    Search semantic memory for relevant facts.

    Uses vector similarity to find relevant information from
    conversation history.

    Args:
        request: Search request with query and filters.

    Returns:
        Matching results with scores.

    Raises:
        HTTPException: If search fails.
    """
    try:
        memory_service = get_memory_service()
        results = memory_service.search_semantic(
            query=request.query,
            session_id=request.session_id,
            top_k=request.top_k,
        )

        return MemorySearchResponse(
            query=request.query, results=results, total_results=len(results)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to search memory: {str(e)}"
        )
