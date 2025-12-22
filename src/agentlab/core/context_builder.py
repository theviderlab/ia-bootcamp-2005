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

from agentlab.models import MemoryContext, RAGResult, ToolResult


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
    
    # Tool results
    tool_results: list[ToolResult] | None = None
    
    # Metadata
    total_tokens_estimated: int = 0
    token_breakdown: dict[str, int] | None = None
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
        tool_results: list[ToolResult] | None = None,
        prioritize: str = "balanced",  # "memory", "rag", or "balanced"
    ) -> CombinedContext:
        """
        Build combined context from memory, RAG, and tool results.
        
        Args:
            memory_context: Memory context from IntegratedMemoryService.
            rag_result: RAG retrieval result.
            tool_results: List of tool execution results from MCP tools.
            prioritize: Prioritization strategy when truncating.
                - "memory": Prioritize memory over RAG
                - "rag": Prioritize RAG over memory
                - "balanced": Balance both equally
        
        Returns:
            CombinedContext with all available information.
        """
        warnings = []
        
        # Extract memory components (only non-empty values)
        short_term = ""
        semantic = None
        profile = None
        episodic = ""
        procedural = None
        
        if memory_context:
            # Only include if non-empty (respects disabled features)
            short_term = memory_context.short_term_context or ""
            
            # Only include semantic facts if present and not empty
            if memory_context.semantic_facts and len(memory_context.semantic_facts) > 0:
                semantic = memory_context.semantic_facts
            
            # Only include profile if present and not empty
            if memory_context.user_profile and len(memory_context.user_profile) > 0:
                profile = memory_context.user_profile
            
            # Only include episodic summary if present and not empty
            episodic = memory_context.episodic_summary or ""
            
            # Only include procedural patterns if present and not empty
            if memory_context.procedural_patterns and len(memory_context.procedural_patterns) > 0:
                procedural = memory_context.procedural_patterns
        
        # Extract RAG components
        rag_docs = None
        rag_text = ""
        
        if rag_result and rag_result.success:
            rag_docs = rag_result.sources if rag_result.sources else None
            # Build RAG context text from sources
            if rag_docs:
                rag_text = self._format_rag_sources(rag_docs)
        
        # Estimate tokens with breakdown
        tool_results_text = ""
        if tool_results:
            tool_results_text = self._format_tool_results(tool_results)
        
        estimated_tokens, token_breakdown = self._estimate_tokens(
            short_term, semantic, profile, episodic, procedural, rag_text, tool_results_text
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
            tool_results=tool_results,
            total_tokens_estimated=estimated_tokens,
            token_breakdown=token_breakdown,
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
        
        # Tool results
        if context.tool_results:
            tool_text = self._format_tool_results(context.tool_results)
            sections.append(f"## Tool Execution Results\n{tool_text}")
        
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

    def _format_tool_results(self, tool_results: list[ToolResult]) -> str:
        """
        Format tool execution results into readable text.
        
        Args:
            tool_results: List of ToolResult objects from MCP tool executions.
        
        Returns:
            Formatted string of tool results with status, output, and errors.
        """
        if not tool_results:
            return ""
        
        formatted = []
        for i, result in enumerate(tool_results, 1):
            status = "✅ Success" if result.success else "❌ Failed"
            timestamp = result.timestamp.strftime("%H:%M:%S") if result.timestamp else "N/A"
            
            header = f"### Tool {i}: `{result.tool_name}` ({status})"
            header += f"\n**Time**: {timestamp}"
            header += f"\n**Call ID**: {result.tool_call_id}"
            
            if result.error:
                formatted.append(f"{header}\n**Error**: {result.error}")
            else:
                # Format result dict as readable text
                result_text = ""
                if isinstance(result.result, dict):
                    for key, value in result.result.items():
                        result_text += f"\n- **{key}**: {value}"
                else:
                    result_text = f"\n{result.result}"
                
                formatted.append(f"{header}\n**Result**:{result_text}")
        
        return "\n\n".join(formatted)

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
        tool_results_text: str = "",
    ) -> tuple[int, dict[str, int]]:
        """
        Estimate total tokens in context using tiktoken with breakdown.
        
        Args:
            short_term: Short-term history text.
            semantic: Semantic facts list.
            profile: User profile dict.
            episodic: Episodic summary text.
            procedural: Procedural patterns list.
            rag_text: RAG context text.
            tool_results_text: Formatted tool results text.
        
        Returns:
            Tuple of (total_tokens, breakdown_dict) with accurate counts.
        """
        breakdown = {
            "short_term": self.count_tokens(short_term),
            "episodic": self.count_tokens(episodic),
            "rag": self.count_tokens(rag_text),
            "tools": self.count_tokens(tool_results_text),
            "semantic": 0,
            "profile": 0,
            "procedural": 0,
        }
        
        if semantic:
            breakdown["semantic"] = sum(self.count_tokens(fact) for fact in semantic)
        
        if profile:
            profile_text = " ".join(
                f"{k}: {v}" for k, v in profile.items()
            )
            breakdown["profile"] = self.count_tokens(profile_text)
        
        if procedural:
            breakdown["procedural"] = sum(self.count_tokens(pattern) for pattern in procedural)
        
        total_tokens = sum(breakdown.values())
        
        return total_tokens, breakdown
