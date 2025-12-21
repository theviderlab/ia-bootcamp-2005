"""
Context builder for combining memory and RAG information.

Builds comprehensive context for LLM prompts by intelligently combining:
- Short-term conversation history
- Long-term memory (semantic, episodic, profile, procedural)
- RAG-retrieved documents

Implements smart truncation strategies to stay within token limits.
"""

from dataclasses import dataclass
from typing import Any

import tiktoken

from agentlab.models import MemoryContext, RAGResult


@dataclass
class CombinedContext:
    """
    Combined context from memory and RAG sources.
    
    Contains all context elements and metadata about what was included.
    """

    # Memory components
    short_term_history: str = ""
    semantic_facts: list[str] | None = None
    user_profile: dict[str, Any] | None = None
    episodic_summary: str = ""
    procedural_patterns: list[str] | None = None
    
    # RAG components
    rag_documents: list[dict[str, Any]] | None = None
    rag_context: str = ""
    
    # Metadata
    total_tokens_estimated: int = 0
    truncated: bool = False
    truncation_strategy: str | None = None
    warnings: list[str] | None = None


class ContextBuilder:
    """
    Builds combined context from memory and RAG sources.
    
    Implements intelligent prioritization and truncation when needed.
    """

    def __init__(self, max_tokens: int = 4000, model: str = "gpt-3.5-turbo"):
        """
        Initialize context builder.
        
        Args:
            max_tokens: Maximum tokens for combined context.
            model: Model name for tiktoken encoding (default: gpt-3.5-turbo).
        """
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model(model)

    def build_context(
        self,
        memory_context: MemoryContext | None = None,
        rag_result: RAGResult | None = None,
        prioritize: str = "balanced",  # "memory", "rag", or "balanced"
    ) -> CombinedContext:
        """
        Build combined context from memory and RAG.
        
        Args:
            memory_context: Memory context from IntegratedMemoryService.
            rag_result: RAG retrieval result.
            prioritize: Prioritization strategy when truncating.
                - "memory": Prioritize memory over RAG
                - "rag": Prioritize RAG over memory
                - "balanced": Balance both equally
        
        Returns:
            CombinedContext with all available information.
        """
        warnings = []
        
        # Extract memory components
        short_term = ""
        semantic = None
        profile = None
        episodic = ""
        procedural = None
        
        if memory_context:
            short_term = memory_context.short_term_context or ""
            semantic = memory_context.semantic_facts if memory_context.semantic_facts else None
            profile = memory_context.user_profile if memory_context.user_profile else None
            episodic = memory_context.episodic_summary or ""
            procedural = memory_context.procedural_patterns if memory_context.procedural_patterns else None
        
        # Extract RAG components
        rag_docs = None
        rag_text = ""
        
        if rag_result and rag_result.success:
            rag_docs = rag_result.sources if rag_result.sources else None
            # Build RAG context text from sources
            if rag_docs:
                rag_text = self._format_rag_sources(rag_docs)
        
        # Estimate tokens (rough: 4 chars = 1 token)
        estimated_tokens = self._estimate_tokens(
            short_term, semantic, profile, episodic, procedural, rag_text
        )
        
        truncated = False
        truncation_strategy = None
        
        # Apply truncation if needed
        if estimated_tokens > self.max_tokens:
            warnings.append(
                f"Context exceeds {self.max_tokens} tokens (estimated {estimated_tokens}). Applying truncation."
            )
            truncated = True
            truncation_strategy = prioritize
            
            # TODO: Implement smart truncation strategies
            # For now, just return everything and let LLM handle it
            warnings.append(
                "Smart truncation not yet implemented. Returning full context."
            )
        
        return CombinedContext(
            short_term_history=short_term,
            semantic_facts=semantic,
            user_profile=profile,
            episodic_summary=episodic,
            procedural_patterns=procedural,
            rag_documents=rag_docs,
            rag_context=rag_text,
            total_tokens_estimated=estimated_tokens,
            truncated=truncated,
            truncation_strategy=truncation_strategy,
            warnings=warnings if warnings else None,
        )

    def format_for_prompt(self, context: CombinedContext) -> str:
        """
        Format combined context as a string for LLM prompt.
        
        Args:
            context: Combined context to format.
        
        Returns:
            Formatted string ready for insertion into system prompt.
        """
        sections = []
        
        # Short-term history
        if context.short_term_history:
            sections.append(
                f"## Recent Conversation\n{context.short_term_history}"
            )
        
        # RAG documents
        if context.rag_context:
            sections.append(
                f"## Relevant Knowledge Base Documents\n{context.rag_context}"
            )
        
        # Semantic facts
        if context.semantic_facts:
            facts_text = "\n".join(f"- {fact}" for fact in context.semantic_facts)
            sections.append(f"## Known Facts\n{facts_text}")
        
        # User profile
        if context.user_profile:
            profile_text = "\n".join(
                f"- {key}: {value}" 
                for key, value in context.user_profile.items()
            )
            sections.append(f"## User Profile\n{profile_text}")
        
        # Episodic summary
        if context.episodic_summary:
            sections.append(
                f"## Conversation Summary\n{context.episodic_summary}"
            )
        
        # Procedural patterns
        if context.procedural_patterns:
            patterns_text = "\n".join(
                f"- {pattern}" for pattern in context.procedural_patterns
            )
            sections.append(f"## Interaction Patterns\n{patterns_text}")
        
        # Add warnings if any
        if context.warnings:
            warnings_text = "\n".join(f"⚠️ {w}" for w in context.warnings)
            sections.append(f"## Context Warnings\n{warnings_text}")
        
        return "\n\n".join(sections) if sections else ""

    def _format_rag_sources(self, sources: list[dict[str, Any]]) -> str:
        """
        Format RAG sources into readable text.
        
        Args:
            sources: List of source documents with metadata.
        
        Returns:
            Formatted string of RAG sources.
        """
        formatted = []
        for i, source in enumerate(sources, 1):
            content = source.get("page_content", "")
            metadata = source.get("metadata", {})
            doc_id = metadata.get("doc_id", f"doc_{i}")
            namespace = metadata.get("namespace", "")
            
            header = f"### Document {i}"
            if namespace:
                header += f" (namespace: {namespace})"
            header += f"\n**ID**: {doc_id}\n"
            
            formatted.append(f"{header}\n{content}")
        
        return "\n\n".join(formatted)

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken.
        
        Args:
            text: Text to count tokens for.
        
        Returns:
            Accurate token count.
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))

    def _estimate_tokens(
        self,
        short_term: str,
        semantic: list[str] | None,
        profile: dict | None,
        episodic: str,
        procedural: list[str] | None,
        rag_text: str,
    ) -> int:
        """
        Estimate total tokens in context using tiktoken.
        
        Args:
            short_term: Short-term history text.
            semantic: Semantic facts list.
            profile: User profile dict.
            episodic: Episodic summary text.
            procedural: Procedural patterns list.
            rag_text: RAG context text.
        
        Returns:
            Accurate token count using tiktoken.
        """
        total_tokens = 0
        
        total_tokens += self.count_tokens(short_term)
        total_tokens += self.count_tokens(episodic)
        total_tokens += self.count_tokens(rag_text)
        
        if semantic:
            total_tokens += sum(self.count_tokens(fact) for fact in semantic)
        
        if profile:
            profile_text = " ".join(
                f"{k}: {v}" for k, v in profile.items()
            )
            total_tokens += self.count_tokens(profile_text)
        
        if procedural:
            total_tokens += sum(self.count_tokens(pattern) for pattern in procedural)
        
        return total_tokens
