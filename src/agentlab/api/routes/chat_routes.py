"""
Chat and LLM API routes.

Endpoints for:
- Generating text from LLM
- Chat conversations with message history (with optional memory and RAG)
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

class RAGSource(BaseModel):
    """RAG source document with score and metadata."""

    content: str = Field(..., description="Document content")
    score: float = Field(..., description="Similarity score (0-1)")
    doc_id: str = Field(..., description="Document identifier")
    namespace: str = Field(default="", description="Pinecone namespace")
    chunk_index: int | None = Field(None, description="Chunk index in document")

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str
    session_id: str
    context_text: str = Field(
        default="",
        description="Complete context sent to LLM (memory + RAG)"
    )
    context_tokens: int = Field(
        default=0,
        ge=0,
        description="Accurate token count of context using tiktoken"
    )
    rag_sources: list[RAGSource] = Field(
        default_factory=list,
        description="RAG documents used with similarity scores"
    )


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
        
        # Count context tokens using tiktoken
        context_tokens = context_builder.count_tokens(context_text)
        
        # Extract RAG sources with scores
        rag_sources_list: list[RAGSource] = []
        if combined_context.rag_documents:
            for doc in combined_context.rag_documents:
                rag_sources_list.append(RAGSource(
                    content=doc.get("page_content", ""),
                    score=doc.get("score", 0.0),
                    doc_id=doc.get("metadata", {}).get("doc_id", ""),
                    namespace=doc.get("metadata", {}).get("namespace", ""),
                    chunk_index=doc.get("metadata", {}).get("chunk_index"),
                ))
        
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
            session_id=session_id,
            context_text=context_text,
            context_tokens=context_tokens,
            rag_sources=rag_sources_list
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


