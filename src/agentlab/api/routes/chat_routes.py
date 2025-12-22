"""
Chat and LLM API routes.

Endpoints for:
- Generating text from LLM
- Chat conversations with message history (with optional memory, RAG, and MCP tools)
"""

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agentlab.core.llm_interface import LangChainLLM
from agentlab.core.memory_service import IntegratedMemoryService
from agentlab.core.rag_service import RAGServiceImpl
from agentlab.core.context_builder import ContextBuilder
from agentlab.database.crud import (
    get_session_config,
    get_latest_session_id,
    create_or_update_session_config,
)
from agentlab.models import ChatMessage, ToolCall, ToolResult, AgentStep

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
    """
    Request model for chat endpoint.
    
    Configuration (memory, RAG, tools) is read from session_configs table in database.
    Only generation parameters are passed in the request.
    """

    messages: list[dict[str, str]] = Field(
        ...,
        min_length=1,
        description="Chat message history with 'role' and 'content' fields"
    )
    session_id: str | None = Field(None, description="Optional session identifier")
    
    # Generation parameters
    temperature: float = Field(
        0.7, ge=0.0, le=1.0, description="Sampling temperature"
    )
    max_tokens: int = Field(
        500, gt=0, le=4000, description="Maximum tokens to generate"
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


class ToolCallInfo(BaseModel):
    """Information about a tool call made by the agent."""

    id: str = Field(..., description="Unique tool call identifier")
    name: str = Field(..., description="Tool name")
    args: dict[str, Any] = Field(..., description="Tool arguments")
    timestamp: str | None = Field(None, description="ISO timestamp of call")


class ToolResultInfo(BaseModel):
    """Result from a tool execution."""

    tool_call_id: str = Field(..., description="ID of the tool call")
    tool_name: str = Field(..., description="Name of the tool")
    success: bool = Field(..., description="Whether execution succeeded")
    result: dict[str, Any] = Field(..., description="Tool result data")
    error: str | None = Field(None, description="Error message if failed")
    timestamp: str | None = Field(None, description="ISO timestamp of result")


class AgentStepInfo(BaseModel):
    """Information about a single agent reasoning step."""

    step_number: int = Field(..., description="Step sequence number")
    action: str = Field(..., description="Action type: tool_call or final_answer")
    tool_call: ToolCallInfo | None = Field(None, description="Tool call if action=tool_call")
    tool_result: ToolResultInfo | None = Field(None, description="Tool result if action=tool_call")
    reasoning: str | None = Field(None, description="Agent reasoning text")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str
    session_id: str
    context_text: str = Field(
        default="",
        description="Complete context sent to LLM (memory + RAG + tool results)"
    )
    context_tokens: int = Field(
        default=0,
        ge=0,
        description="Accurate token count of context using tiktoken"
    )
    token_breakdown: dict[str, int] = Field(
        default_factory=dict,
        description="Token count breakdown by component (short_term, semantic, episodic, profile, procedural, rag, tools)"
    )
    max_context_tokens: int = Field(
        default=4000,
        description="Maximum context tokens allowed"
    )
    rag_sources: list[RAGSource] = Field(
        default_factory=list,
        description="RAG documents used with similarity scores"
    )
    tool_calls: list[ToolCallInfo] = Field(
        default_factory=list,
        description="Tool calls made during agent execution"
    )
    agent_steps: list[AgentStepInfo] = Field(
        default_factory=list,
        description="Agent reasoning steps with tool calls and results"
    )
    tools_used: bool = Field(
        default=False,
        description="Whether tools were enabled and used"
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
        
        # Determine session ID: use provided, then latest, then create new
        session_id = request.session_id
        if not session_id:
            try:
                session_id = get_latest_session_id()
                if session_id:
                    print(f"📝 Using latest session: {session_id}")
            except Exception as e:
                print(f"⚠️  Could not get latest session: {e}")
        
        if not session_id:
            # Create new session with default configuration
            session_id = str(uuid4())
            try:
                create_or_update_session_config(
                    session_id=session_id,
                    memory_config={
                        "enabled": False,
                        "short_term": {"enabled": False},
                        "semantic": {"enabled": False},
                        "episodic": {"enabled": False},
                        "profile": {"enabled": False},
                        "procedural": {"enabled": False}
                    },
                    rag_config={
                        "enabled": False,
                        "top_k": 5,
                        "namespaces": []
                    },
                    metadata={"created_by": "chat_api"}
                )
                print(f"✨ Created new session: {session_id}")
            except Exception as e:
                print(f"⚠️  Could not create session config: {e}")
        
        # Get services (always initialize - will check DB config to determine usage)
        llm = get_llm()
        memory_service = get_memory_service()
        rag_service = get_rag_service()
        
        # Load session configuration from database (SINGLE SOURCE OF TRUTH)
        session_config = None
        memory_config = None
        rag_config = None
        mcp_tools_config = None
        
        try:
            session_config = get_session_config(session_id)
            if session_config:
                memory_config = session_config.get("memory_config", {})
                rag_config = session_config.get("rag_config", {})
                mcp_tools_config = session_config.get("mcp_tools_config", {})
                print(f"✅ Loaded session config from DB for session: {session_id}")
                print(f"   Memory config: {memory_config}")
                print(f"   RAG config: {rag_config}")
                print(f"   MCP Tools config: {mcp_tools_config}")
        except Exception as e:
            print(f"⚠️  Could not load session config from DB: {e}")
            # Use default disabled configs
            memory_config = {}
            rag_config = {"enabled": False}
            mcp_tools_config = {"enabled": False}
        
        # Determine if memory is enabled from DB config
        memory_enabled = False
        if memory_config:
            # Memory is enabled if any type is enabled
            memory_enabled = (
                memory_config.get("enable_short_term", False) or
                memory_config.get("enable_semantic", False) or
                memory_config.get("enable_episodic", False) or
                memory_config.get("enable_profile", False) or
                memory_config.get("enable_procedural", False)
            )
        
        # Store user message in memory (if enabled)
        if memory_service and memory_enabled and chat_messages:
            last_msg = chat_messages[-1]
            if last_msg.role == "user":
                memory_service.add_message(session_id, last_msg)
                print(f"💾 Stored user message in memory")

        # Retrieve memory context (if enabled)
        memory_context = None
        if memory_service and memory_enabled:
            try:
                print(f"🧠 Retrieving memory context with config: {memory_config}")
                memory_context = memory_service.get_context(
                    session_id=session_id,
                    memory_config=memory_config
                )
            except Exception as e:
                print(f"⚠️  Memory retrieval failed: {e}")

        # Retrieve RAG context (if enabled in DB)
        rag_result = None
        print(rag_config)
        rag_enabled = rag_config.get("enable_rag", False) if rag_config else False
        
        if rag_service and rag_enabled and chat_messages:
            try:
                # Extract RAG parameters from DB config
                rag_namespaces = rag_config.get("namespaces", [])
                rag_top_k = rag_config.get("top_k", 5)
                
                print(f"🔍 Performing RAG retrieval with DB config: namespaces={rag_namespaces}, top_k={rag_top_k}")
                
                # Use last user message as query
                user_query = next(
                    (msg.content for msg in reversed(chat_messages) if msg.role == "user"),
                    ""
                )
                
                if user_query:
                    if rag_namespaces:
                        # Retrieve documents from each namespace separately and combine
                        all_sources = []
                        for namespace in rag_namespaces:
                            try:
                                namespace_sources = rag_service.retrieve_documents(
                                    user_query,
                                    top_k=rag_top_k,
                                    namespace=namespace
                                )
                                if namespace_sources:
                                    all_sources.extend(namespace_sources)
                            except Exception as ns_error:
                                print(f"⚠️  Failed to retrieve from namespace '{namespace}': {ns_error}")
                        
                        # Create RAGResult-like structure with combined sources
                        if all_sources:
                            # Sort by score and limit to top_k
                            all_sources.sort(key=lambda x: x.get("score", 0.0), reverse=True)
                            limited_sources = all_sources[:rag_top_k]
                            
                            # Create a minimal RAGResult object for compatibility
                            from agentlab.models import RAGResult
                            rag_result = RAGResult(
                                success=True,
                                response="",  # Not used in chat flow
                                sources=limited_sources,
                                error_message=None
                            )
                            print(f"✅ RAG retrieval successful: {len(rag_result.sources)} sources from {len(rag_namespaces)} namespaces")
                    else:
                        # Retrieve from all namespaces
                        try:
                            sources = rag_service.retrieve_documents(user_query, top_k=rag_top_k)
                            if sources:
                                from agentlab.models import RAGResult
                                rag_result = RAGResult(
                                    success=True,
                                    response="",  # Not used in chat flow
                                    sources=sources,
                                    error_message=None
                                )
                                print(f"✅ RAG retrieval successful: {len(rag_result.sources)} sources")
                        except Exception as retrieval_error:
                            print(f"⚠️  Document retrieval failed: {retrieval_error}")
            except Exception as e:
                print(f"⚠️  RAG retrieval failed: {e}")
        elif not rag_enabled:
            print(f"📊 RAG is disabled in session config")
        
        print(rag_result)
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
        
        # Determine if tools are enabled from DB config
        tools_enabled = mcp_tools_config.get("enabled", False) if mcp_tools_config else False
        tool_names = mcp_tools_config.get("selected_tools", None) if mcp_tools_config else None
        max_tool_iterations = mcp_tools_config.get("max_iterations", 5) if mcp_tools_config else 5
        
        # Generate response - with or without tools (based on DB config)
        if tools_enabled:
            print(f"🔧 Using tools from DB config: {tool_names}, max_iterations={max_tool_iterations}")
            # Use tool-enabled agent
            response_text, agent_steps, tool_results = await llm.chat_with_tools(
                final_messages,
                tool_names=tool_names,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                max_iterations=max_tool_iterations
            )
            
            # Convert agent steps to response format
            agent_steps_info: list[AgentStepInfo] = []
            for step in agent_steps:
                tool_call_info = None
                tool_result_info = None
                
                if step.tool_call:
                    tool_call_info = ToolCallInfo(
                        id=step.tool_call.id,
                        name=step.tool_call.name,
                        args=step.tool_call.args,
                        timestamp=step.tool_call.timestamp.isoformat() if step.tool_call.timestamp else None
                    )
                
                if step.tool_result:
                    tool_result_info = ToolResultInfo(
                        tool_call_id=step.tool_result.tool_call_id,
                        tool_name=step.tool_result.tool_name,
                        success=step.tool_result.success,
                        result=step.tool_result.result,
                        error=step.tool_result.error,
                        timestamp=step.tool_result.timestamp.isoformat() if step.tool_result.timestamp else None
                    )
                
                agent_steps_info.append(AgentStepInfo(
                    step_number=step.step_number,
                    action=step.action,
                    tool_call=tool_call_info,
                    tool_result=tool_result_info,
                    reasoning=step.reasoning
                ))
            
            # Extract tool calls for response
            tool_calls_info: list[ToolCallInfo] = []
            for step in agent_steps:
                if step.tool_call:
                    tool_calls_info.append(ToolCallInfo(
                        id=step.tool_call.id,
                        name=step.tool_call.name,
                        args=step.tool_call.args,
                        timestamp=step.tool_call.timestamp.isoformat() if step.tool_call.timestamp else None
                    ))
            
            # Store tool calls in memory with metadata
            if memory_service:
                for step in agent_steps:
                    if step.tool_call:
                        # Store tool call message
                        tool_call_msg = ChatMessage(
                            role="assistant",
                            content=f"[Tool Call: {step.tool_call.name}]",
                            timestamp=datetime.now(),
                            metadata={
                                "is_tool_call": True,
                                "tool_name": step.tool_call.name,
                                "tool_args": step.tool_call.args
                            }
                        )
                        memory_service.add_message(session_id, tool_call_msg)
                    
                    if step.tool_result:
                        # Store tool result message
                        tool_result_msg = ChatMessage(
                            role="system",
                            content=f"[Tool Result: {step.tool_result.tool_name}]",
                            timestamp=datetime.now(),
                            metadata={
                                "is_tool_call": True,
                                "tool_name": step.tool_result.tool_name,
                                "tool_result": step.tool_result.result,
                                "tool_success": step.tool_result.success
                            }
                        )
                        memory_service.add_message(session_id, tool_result_msg)
            
            # Update context with tool results if any
            if tool_results:
                combined_context_with_tools = context_builder.build_context(
                    memory_context=memory_context,
                    rag_result=rag_result,
                    tool_results=tool_results,
                    prioritize=request.context_priority
                )
                context_text_with_tools = context_builder.format_for_prompt(combined_context_with_tools)
                context_tokens = context_builder.count_tokens(context_text_with_tools)
                context_text = context_text_with_tools
        else:
            # Standard chat without tools
            print(f"💬 Generating response without tools")
            response_text = llm.chat(
                final_messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            agent_steps_info = []
            tool_calls_info = []
        
        # Store assistant response in memory (if enabled)
        if memory_service and memory_enabled:
            assistant_msg = ChatMessage(
                role="assistant",
                content=response_text,
                timestamp=datetime.now()
            )
            memory_service.add_message(session_id, assistant_msg)
            print(f"💾 Stored assistant response in memory")
        
        print(context_text)
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            context_text=context_text,
            context_tokens=context_tokens,
            token_breakdown=combined_context.token_breakdown or {},
            max_context_tokens=request.max_context_tokens,
            rag_sources=rag_sources_list,
            tool_calls=tool_calls_info,
            agent_steps=agent_steps_info,
            tools_used=tools_enabled and len(tool_calls_info) > 0
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


