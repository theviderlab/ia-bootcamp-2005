"""
Chat and LLM API routes.

Endpoints for:
- Generating text from LLM
- Chat conversations with message history
- Session management
"""

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agentlab.core.llm_interface import LangChainLLM
from agentlab.models import ChatMessage

router = APIRouter()

# Global LLM instance (in production, use dependency injection)
_llm_instance: LangChainLLM | None = None


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
            _llm_instance = LangChainLLM()
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize LLM: {str(e)}"
            )
    return _llm_instance


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
    Generate chat response from conversation history.

    Args:
        request: Chat request with message history.

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
                    status_code=400,
                    detail="Each message must have 'role' and 'content' fields"
                )
            
            role = msg["role"]
            if role not in ["user", "assistant", "system"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid role: {role}. Must be 'user', 'assistant', or 'system'"
                )
            
            chat_messages.append(ChatMessage(
                role=role,
                content=msg["content"],
                timestamp=datetime.now()
            ))
        
        llm = get_llm()
        response_text = llm.chat(chat_messages)
        
        session_id = request.session_id or str(uuid4())
        
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
