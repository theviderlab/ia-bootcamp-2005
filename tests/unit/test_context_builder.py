"""
Unit tests for context builder functionality.

Tests the combination of memory and RAG contexts.
"""

import pytest

from agentlab.core.context_builder import CombinedContext, ContextBuilder
from agentlab.models import MemoryContext, RAGResult


def test_context_builder_initialization():
    """Test ContextBuilder initialization with custom token limit."""
    builder = ContextBuilder(max_tokens=2000)
    assert builder.max_tokens == 2000


def test_build_context_memory_only():
    """Test building context with only memory data."""
    builder = ContextBuilder()
    
    memory_context = MemoryContext(
        session_id="test-session",
        short_term_context="User asked about Python.\nAssistant explained basics.",
        semantic_facts=["User prefers Python", "User is learning programming"],
        user_profile={"skill_level": "beginner", "language": "Python"},
        episodic_summary="Discussion about Python programming",
        procedural_patterns=["Asks for code examples"],
        total_messages=2,
    )
    
    result = builder.build_context(memory_context=memory_context)
    
    assert isinstance(result, CombinedContext)
    assert result.short_term_history == "User asked about Python.\nAssistant explained basics."
    assert len(result.semantic_facts) == 2
    assert result.user_profile["skill_level"] == "beginner"
    assert result.episodic_summary == "Discussion about Python programming"
    assert result.rag_context == ""
    assert result.rag_documents is None


def test_build_context_rag_only():
    """Test building context with only RAG data."""
    builder = ContextBuilder()
    
    rag_result = RAGResult(
        success=True,
        response="Generated response",
        sources=[
            {
                "page_content": "Python is a high-level programming language.",
                "metadata": {"doc_id": "doc1", "namespace": "tutorials"},
            },
            {
                "page_content": "FastAPI is a modern web framework.",
                "metadata": {"doc_id": "doc2", "namespace": "frameworks"},
            },
        ],
    )
    
    result = builder.build_context(rag_result=rag_result)
    
    assert isinstance(result, CombinedContext)
    assert result.short_term_history == ""
    assert result.semantic_facts is None
    assert result.user_profile is None
    assert result.rag_documents is not None
    assert len(result.rag_documents) == 2
    assert "Python is a high-level" in result.rag_context


def test_build_context_combined():
    """Test building context with both memory and RAG."""
    builder = ContextBuilder()
    
    memory_context = MemoryContext(
        session_id="test-session",
        short_term_context="User asked about FastAPI.",
        semantic_facts=["User knows Python"],
        user_profile={"framework": "FastAPI"},
        total_messages=1,
    )
    
    rag_result = RAGResult(
        success=True,
        response="Response",
        sources=[
            {
                "page_content": "FastAPI documentation excerpt.",
                "metadata": {"doc_id": "fastapi-doc"},
            }
        ],
    )
    
    result = builder.build_context(
        memory_context=memory_context,
        rag_result=rag_result,
        prioritize="balanced",
    )
    
    assert result.short_term_history == "User asked about FastAPI."
    assert len(result.semantic_facts) == 1
    assert result.rag_documents is not None
    assert "FastAPI documentation" in result.rag_context


def test_build_context_empty():
    """Test building context with no data."""
    builder = ContextBuilder()
    result = builder.build_context()
    
    assert result.short_term_history == ""
    assert result.semantic_facts is None
    assert result.user_profile is None
    assert result.rag_context == ""
    assert result.total_tokens_estimated == 0


def test_format_for_prompt():
    """Test formatting combined context for LLM prompt."""
    builder = ContextBuilder()
    
    context = CombinedContext(
        short_term_history="Recent chat",
        semantic_facts=["Fact 1", "Fact 2"],
        user_profile={"name": "John"},
        rag_context="RAG document content",
    )
    
    formatted = builder.format_for_prompt(context)
    
    assert "## Recent Conversation" in formatted
    assert "Recent chat" in formatted
    assert "## Known Facts" in formatted
    assert "Fact 1" in formatted
    assert "## User Profile" in formatted
    assert "name: John" in formatted
    assert "## Relevant Knowledge Base Documents" in formatted
    assert "RAG document content" in formatted


def test_format_for_prompt_empty():
    """Test formatting empty context."""
    builder = ContextBuilder()
    context = CombinedContext()
    formatted = builder.format_for_prompt(context)
    
    assert formatted == ""


def test_estimate_tokens():
    """Test token estimation."""
    builder = ContextBuilder()
    
    # Roughly 4 chars = 1 token
    short_term = "a" * 400  # ~100 tokens
    semantic = ["b" * 40, "c" * 40]  # ~20 tokens
    profile = {"key": "d" * 40}  # ~10 tokens
    episodic = "e" * 40  # ~10 tokens
    procedural = ["f" * 40]  # ~10 tokens
    rag_text = "g" * 400  # ~100 tokens
    
    tokens = builder._estimate_tokens(
        short_term, semantic, profile, episodic, procedural, rag_text
    )
    
    # Total should be around 250 tokens
    assert 200 <= tokens <= 300


def test_format_rag_sources():
    """Test formatting RAG sources."""
    builder = ContextBuilder()
    
    sources = [
        {
            "page_content": "Content 1",
            "metadata": {"doc_id": "doc1", "namespace": "ns1"},
        },
        {
            "page_content": "Content 2",
            "metadata": {"doc_id": "doc2"},
        },
    ]
    
    formatted = builder._format_rag_sources(sources)
    
    assert "### Document 1" in formatted
    assert "namespace: ns1" in formatted
    assert "**ID**: doc1" in formatted
    assert "Content 1" in formatted
    assert "### Document 2" in formatted
    assert "Content 2" in formatted
