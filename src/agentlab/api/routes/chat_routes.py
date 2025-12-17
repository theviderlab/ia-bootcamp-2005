"""
Chat and LLM API routes.

Endpoints for:
- Generating text from LLM
- Chat conversations with message history
- RAG query and document management
- Session management
"""

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agentlab.core.llm_interface import LangChainLLM
from agentlab.core.memory_service import IntegratedMemoryService
from agentlab.core.rag_service import RAGServiceImpl
from agentlab.core.context_builder import ContextBuilder
from agentlab.models import ChatMessage

router = APIRouter()

# Global instances (in production, use proper dependency injection)
_llm_instance: LangChainLLM | None = None
_rag_instance: RAGServiceImpl | None = None
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
            # Read default temperature and max_tokens from environment
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


def get_rag_service() -> RAGServiceImpl | None:
    """
    Get or create the RAG service instance.

    Returns None if RAG is disabled or initialization fails.

    Returns:
        RAGServiceImpl instance or None.
    """
    global _rag_instance
    if _rag_instance is None:
        try:
            import os
            from agentlab.config.rag_config import RAGConfig
            
            # Check if RAG is enabled
            if not os.getenv("ENABLE_RAG", "true").lower() == "true":
                print("⚠️  RAG is disabled via ENABLE_RAG=false")
                return None
            
            # Try to initialize
            try:
                config = RAGConfig.from_env()
                llm = get_llm()
                _rag_instance = RAGServiceImpl(llm=llm, config=config)
            except ValueError as e:
                print(f"⚠️  RAG service unavailable: {e}")
                return None
        except Exception as e:
            print(f"⚠️  RAG service initialization failed: {e}")
            return None
    return _rag_instance


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
            
            # Try to initialize
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


class GenerateRequest(BaseModel):
    """Request model for text generation endpoint."""

    prompt: str = Field(..., min_length=1, description="Input prompt for generation")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Sampling temperature")
    max_tokens: int = Field(1000, gt=0, le=4000, description="Maximum tokens to generate")


class GenerateResponse(BaseModel):
    """Response model for text generation."""

    text: str
    prompt: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    messages: list[dict[str, str]] = Field(
        ...,
        min_length=1,
        description="Chat message history with 'role' and 'content' fields"
    )
    session_id: str | None = Field(None, description="Optional session identifier")
    temperature: float = Field(
        0.7, ge=0.0, le=1.0, description="Sampling temperature"
    )
    max_tokens: int = Field(
        500, gt=0, le=4000, description="Maximum tokens to generate"
    )
    
    # Runtime configuration toggles
    use_memory: bool = Field(
        True, description="Enable memory context retrieval"
    )
    use_rag: bool = Field(
        False, description="Enable RAG document retrieval"
    )
    
    # Memory configuration
    memory_types: list[str] | None = Field(
        None,
        description="Specific memory types to use: semantic, episodic, profile, procedural",
    )
    
    # RAG configuration
    rag_namespaces: list[str] | None = Field(
        None,
        description="Specific Pinecone namespaces to query (empty = all)",
    )
    rag_top_k: int = Field(
        5, ge=1, le=20, description="Number of RAG documents to retrieve"
    )
    
    # Context configuration
    max_context_tokens: int = Field(
        4000, ge=100, le=8000, description="Max tokens for combined context"
    )
    context_priority: str = Field(
        "balanced",
        description="Context priority: 'memory', 'rag', or 'balanced'",
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str
    session_id: str


@router.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """
    Generate text from a prompt using the LLM.

    Args:
        request: Generation request with prompt and parameters.

    Returns:
        Generated text response.

    Raises:
        HTTPException: If generation fails or prompt is invalid.
    """
    try:
        llm = get_llm()
        response_text = llm.generate(
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return GenerateResponse(
            text=response_text,
            prompt=request.prompt
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Generate chat response with optional memory and RAG augmentation.

    Features:
    - Integrates conversation memory (short-term and long-term)
    - RAG document retrieval with namespace control
    - Dynamic feature toggling per request
    - Intelligent context combination and prioritization

    Args:
        request: Chat request with message history and configuration.

    Returns:
        Chat response with generated text and session ID.

    Raises:
        HTTPException: If chat generation fails or messages are invalid.
    """
    try:
        # Validate and convert messages
        chat_messages = []
        for msg in request.messages:
            if "role" not in msg or "content" not in msg:
                raise HTTPException(
                    status_code=422,
                    detail="Each message must have 'role' and 'content' fields"
                )
            
            role = msg["role"]
            if role not in ["user", "assistant", "system"]:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid role: {role}. Must be 'user', 'assistant', or 'system'"
                )
            
            chat_messages.append(ChatMessage(
                role=role,
                content=msg["content"],
                timestamp=datetime.now()
            ))
        
        # Generate or use provided session ID
        session_id = request.session_id or str(uuid4())
        
        # Get services
        llm = get_llm()
        memory_service = get_memory_service() if request.use_memory else None
        rag_service = get_rag_service() if request.use_rag else None
        
        # Store user message in memory
        if memory_service and chat_messages:
            last_msg = chat_messages[-1]
            if last_msg.role == "user":
                memory_service.add_message(session_id, last_msg)
        
        # Retrieve memory context
        memory_context = None
        if memory_service:
            try:
                memory_context = memory_service.get_context(session_id)
            except Exception as e:
                # Log warning but continue without memory
                print(f"⚠️  Memory retrieval failed: {e}")
        
        # Retrieve RAG context
        rag_result = None
        if rag_service and chat_messages:
            try:
                # Use last user message as query
                user_query = next(
                    (msg.content for msg in reversed(chat_messages) if msg.role == "user"),
                    ""
                )
                if user_query:
                    # Query with optional namespace filtering
                    if request.rag_namespaces:
                        # Query each namespace separately and combine results
                        all_sources = []
                        for namespace in request.rag_namespaces:
                            ns_result = rag_service.query(
                                user_query,
                                top_k=request.rag_top_k,
                                namespace=namespace
                            )
                            if ns_result.success and ns_result.sources:
                                all_sources.extend(ns_result.sources)
                        
                        # Create combined result
                        if all_sources:
                            rag_result = rag_service.query(user_query, top_k=0)  # Empty query
                            rag_result.sources = all_sources[:request.rag_top_k]  # Limit total
                    else:
                        # Query all namespaces
                        rag_result = rag_service.query(
                            user_query,
                            top_k=request.rag_top_k
                        )
            except Exception as e:
                # Log warning but continue without RAG
                print(f"⚠️  RAG retrieval failed: {e}")
        
        # Build combined context
        context_builder = ContextBuilder(max_tokens=request.max_context_tokens)
        combined_context = context_builder.build_context(
            memory_context=memory_context,
            rag_result=rag_result,
            prioritize=request.context_priority
        )
        
        # Format context for prompt
        context_text = context_builder.format_for_prompt(combined_context)
        
        # Add context to messages if available
        final_messages = chat_messages.copy()
        if context_text:
            # Insert context as system message at the beginning
            system_msg = ChatMessage(
                role="system",
                content=f"Use the following context to inform your response:\n\n{context_text}",
                timestamp=datetime.now()
            )
            final_messages.insert(0, system_msg)
        
        # Generate response
        response_text = llm.chat(
            final_messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Store assistant response in memory
        if memory_service:
            assistant_msg = ChatMessage(
                role="assistant",
                content=response_text,
                timestamp=datetime.now()
            )
            memory_service.add_message(session_id, assistant_msg)
        
        return ChatResponse(
            response=response_text,
            session_id=session_id
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RAG Endpoints
# ============================================================================


class RAGQueryRequest(BaseModel):
    """Request model for RAG query endpoint."""

    query: str = Field(..., min_length=1, description="Query to search knowledge base")
    top_k: int = Field(5, ge=1, le=20, description="Number of documents to retrieve")
    namespace: str | None = Field(None, description="Optional namespace to search")


class RAGQueryResponse(BaseModel):
    """Response model for RAG query."""

    success: bool
    response: str
    sources: list[dict]
    error_message: str | None = None


class RAGAddDocumentsRequest(BaseModel):
    """Request model for adding documents to RAG."""

    documents: list[str] = Field(
        ..., min_length=1, description="List of document texts or file paths"
    )
    namespace: str | None = Field(
        None, description="Optional namespace for organization"
    )
    chunk_size: int = Field(
        1000, ge=100, le=4000, description="Maximum characters per chunk"
    )
    chunk_overlap: int = Field(
        200, ge=0, le=1000, description="Overlapping characters between chunks"
    )


class RAGAddDocumentsResponse(BaseModel):
    """Response model for document addition."""

    success: bool
    message: str
    documents_added: int


class RAGAddDirectoryRequest(BaseModel):
    """Request model for adding directory of documents."""

    directory: str = Field(..., description="Path to directory containing documents")
    namespace: str | None = Field(
        None, description="Optional namespace for organization"
    )
    recursive: bool = Field(True, description="Search subdirectories recursively")
    chunk_size: int = Field(
        1000, ge=100, le=4000, description="Maximum characters per chunk"
    )
    chunk_overlap: int = Field(
        200, ge=0, le=1000, description="Overlapping characters between chunks"
    )


@router.post("/rag/query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest):
    """
    Query the RAG system with a question.

    Retrieves relevant documents from the knowledge base and generates
    an answer using the LLM with retrieved context.

    Args:
        request: RAG query request with question and parameters.

    Returns:
        Generated answer with source documents.

    Raises:
        HTTPException: If RAG service is not available or query fails.
    """
    try:
        rag_service = get_rag_service()
        if rag_service is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize RAG service. "
                "Please ensure Pinecone and OpenAI API keys are configured."
            )
        result = rag_service.query(
            query=request.query, top_k=request.top_k, namespace=request.namespace
        )

        return RAGQueryResponse(
            success=result.success,
            response=result.response,
            sources=result.sources,
            error_message=result.error_message,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"RAG query failed: {str(e)}"
        )


@router.post("/rag/documents", response_model=RAGAddDocumentsResponse)
async def add_documents(request: RAGAddDocumentsRequest):
    """
    Add documents to the RAG knowledge base.

    Documents can be plain text strings or file paths. Supported file types
    depend on registered loaders (currently: .txt, .md, .log).

    Args:
        request: Document addition request with texts or paths.

    Returns:
        Success status and number of documents added.

    Raises:
        HTTPException: If document addition fails.
    """
    try:
        rag_service = get_rag_service()

        # Add documents
        rag_service.add_documents(
            documents=request.documents,
            namespace=request.namespace,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )

        return RAGAddDocumentsResponse(
            success=True,
            message=f"Successfully added {len(request.documents)} documents",
            documents_added=len(request.documents),
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add documents: {str(e)}"
        )


@router.post("/rag/directory", response_model=RAGAddDocumentsResponse)
async def add_directory(request: RAGAddDirectoryRequest):
    """
    Add all documents from a directory to the RAG knowledge base.

    Recursively searches directory for supported file types and adds them
    to the knowledge base with chunking and metadata.

    Args:
        request: Directory addition request with path and parameters.

    Returns:
        Success status and number of documents added.

    Raises:
        HTTPException: If directory doesn't exist or addition fails.
    """
    try:
        rag_service = get_rag_service()

        # Validate directory exists
        dir_path = Path(request.directory)
        if not dir_path.exists():
            raise HTTPException(
                status_code=404, detail=f"Directory not found: {request.directory}"
            )

        if not dir_path.is_dir():
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a directory: {request.directory}",
            )

        # Count files before processing
        pattern = "**/*" if request.recursive else "*"
        files = [
            f
            for f in dir_path.glob(pattern)
            if f.is_file() and rag_service.loader_registry.supports(f)
        ]

        if not files:
            return RAGAddDocumentsResponse(
                success=True,
                message=f"No supported files found in {request.directory}",
                documents_added=0,
            )

        # Add documents from directory
        rag_service.add_documents_from_directory(
            directory=request.directory,
            namespace=request.namespace,
            recursive=request.recursive,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )

        return RAGAddDocumentsResponse(
            success=True,
            message=f"Successfully added {len(files)} documents from directory",
            documents_added=len(files),
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add directory: {str(e)}"
        )


class RAGDeleteNamespaceResponse(BaseModel):
    """Response model for namespace deletion."""

    success: bool
    namespace: str
    message: str


@router.delete("/rag/namespace/{namespace}", response_model=RAGDeleteNamespaceResponse)
async def delete_namespace(namespace: str):
    """
    Delete all documents in a specific namespace.

    This endpoint removes all vectors and documents associated with a namespace
    in the Pinecone index. Useful for cleanup and testing.

    Args:
        namespace: The namespace to delete.

    Returns:
        Success status and deletion details.

    Raises:
        HTTPException: If namespace deletion fails or RAG service unavailable.
    """
    try:
        rag_service = get_rag_service()
        if rag_service is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize RAG service. "
                "Please ensure Pinecone and OpenAI API keys are configured.",
            )

        if not namespace or namespace.strip() == "":
            raise HTTPException(
                status_code=400, detail="Namespace cannot be empty"
            )

        # Delete the namespace
        result = rag_service.delete_namespace(namespace)

        return RAGDeleteNamespaceResponse(
            success=result["success"],
            namespace=result["namespace"],
            message=result["message"],
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete namespace '{namespace}': {str(e)}",
        )


# ============================================================================
# Memory Management Endpoints
# ============================================================================


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


@router.post("/memory/context", response_model=MemoryContextResponse)
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
            session_id=request.session_id, max_tokens=request.max_tokens
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


@router.get("/memory/history/{session_id}", response_model=MemoryHistoryResponse)
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

        # Convert to dict format
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


@router.delete("/memory/{session_id}")
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


@router.get("/memory/stats/{session_id}", response_model=MemoryStatsResponse)
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


@router.post("/memory/search", response_model=MemorySearchResponse)
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

