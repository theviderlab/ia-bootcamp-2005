"""
Memory service implementation.

Provides conversation memory management using LangGraph with state persistence
and MySQL backend for conversation history storage.
"""

from datetime import datetime
from typing import Any, Annotated

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

from agentlab.agents.memory_processor import LongTermMemoryProcessor
from agentlab.config.memory_config import MemoryConfig
from agentlab.database.crud import (
    create_chat_message,
    delete_chat_history,
    get_chat_history,
    get_chat_stats,
)
from agentlab.models import ChatMessage, MemoryContext, MemoryStats


class ConversationState(dict):
    """State schema for LangGraph conversation management."""
    
    messages: Annotated[list[BaseMessage], add_messages]
    session_id: str
    summary: str | None


class IntegratedMemoryService:
    """
    Integrated memory service combining short-term and long-term memory.
    
    Implements the MemoryService protocol with full support for
    semantic, episodic, profile, and procedural memory.
    """

    def __init__(
        self,
        config: MemoryConfig | None = None,
        llm: BaseChatModel | None = None,
    ):
        """
        Initialize integrated memory service.

        Args:
            config: Memory configuration. If None, loads from environment.
            llm: Language model. If None, creates default ChatOpenAI.
        """
        self.config = config or MemoryConfig.from_env()
        
        # Initialize short-term memory
        self.short_term = ShortTermMemoryService(config=self.config, llm=llm)
        
        # Initialize long-term memory if enabled
        if self.config.enable_long_term:
            self.long_term = LongTermMemoryProcessor(config=self.config)
        else:
            self.long_term = None

    def add_message(self, session_id: str, message: ChatMessage) -> None:
        """
        Add a message to conversation memory.

        Args:
            session_id: Unique session identifier.
            message: Chat message to store.
        """
        self.short_term.add_message(session_id, message)

    def get_messages(
        self, session_id: str, limit: int = 50
    ) -> list[ChatMessage]:
        """
        Retrieve conversation history for a session.

        Args:
            session_id: Session identifier.
            limit: Maximum number of messages to retrieve.

        Returns:
            List of chat messages ordered by timestamp.
        """
        return self.short_term.get_messages(session_id, limit)

    def get_context(
        self, session_id: str, max_tokens: int | None = None
    ) -> MemoryContext:
        """
        Get enriched context from conversation memory.

        Combines short-term buffer with long-term semantic facts,
        user profile, episodic summary, and procedural patterns.

        Args:
            session_id: Session identifier.
            max_tokens: Maximum tokens to include.

        Returns:
            Complete memory context with all memory types.
        """
        # Get base context from short-term
        context = self.short_term.get_context(session_id, max_tokens)
        
        # Enrich with long-term memory if enabled
        if self.long_term:
            messages = self.get_messages(session_id)
            
            # Extract semantic facts
            context.semantic_facts = self.long_term.extract_semantic_facts(
                session_id, messages
            )
            
            # Get user profile
            context.user_profile = self.long_term.get_user_profile(session_id)
            
            # Get episodic summary
            context.episodic_summary = self.long_term.get_episodic_summary(
                session_id
            )
            
            # Get procedural patterns
            context.procedural_patterns = (
                self.long_term.get_procedural_patterns(session_id)
            )

        return context

    def clear_session(self, session_id: str) -> None:
        """
        Clear all memory for a session.

        Args:
            session_id: Session identifier to clear.
        """
        self.short_term.clear_session(session_id)

    def get_stats(self, session_id: str) -> MemoryStats:
        """
        Get memory statistics for a session.

        Args:
            session_id: Session identifier.

        Returns:
            Memory usage statistics with long-term counts.
        """
        stats = self.short_term.get_stats(session_id)
        
        # Enrich with long-term stats if enabled
        if self.long_term:
            messages = self.get_messages(session_id)
            semantic_facts = self.long_term.extract_semantic_facts(
                session_id, messages
            )
            profile = self.long_term.get_user_profile(session_id)
            
            stats.semantic_facts_count = len(semantic_facts)
            stats.profile_attributes_count = len(profile)
        
        return stats

    def search_semantic(
        self,
        query: str,
        session_id: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Search semantic memory for relevant facts.

        Args:
            query: Search query text.
            session_id: Optional session filter.
            top_k: Number of results to return.

        Returns:
            List of matching facts with metadata and scores.
        """
        if not self.long_term:
            return []
        
        return self.long_term.search_semantic(query, session_id, top_k)


class ShortTermMemoryService:
    """
    Short-term conversation memory service.
    
    Uses LangGraph for state management with MySQL persistence for
    conversation history and checkpointing for session state.
    """

    def __init__(
        self,
        config: MemoryConfig | None = None,
        llm: BaseChatModel | None = None,
    ):
        """
        Initialize short-term memory service.

        Args:
            config: Memory configuration. If None, loads from environment.
            llm: Language model for summary generation. Required for
                summary memory type.

        Raises:
            ValueError: If configuration is invalid or LLM is missing
                for summary memory.
        """
        self.config = config or MemoryConfig.from_env()

        # Initialize LLM for summaries if needed
        if self.config.memory_type == "summary":
            if llm is None:
                if not self.config.openai_api_key:
                    raise ValueError(
                        "OpenAI API key required for summary memory"
                    )
                llm = ChatOpenAI(
                    model=self.config.summary_model,
                    openai_api_key=self.config.openai_api_key,
                )
            self.llm = llm
        else:
            self.llm = llm

        # Configure checkpointer based on memory type
        self.checkpointer = self._create_checkpointer()
        
        # Build conversation graph
        self.graph = self._build_graph()

    def _create_checkpointer(self) -> MemorySaver | SqliteSaver:
        """
        Create appropriate checkpointer for memory persistence.

        Returns:
            MemorySaver for in-memory or SqliteSaver for persistent checkpoints.
        """
        if self.config.memory_type == "buffer":
            # In-memory checkpointer for simple buffer
            return MemorySaver()
        else:
            # Persistent checkpointer with SQLite for window and summary
            db_path = f"{self.config.db_name}_checkpoints.db"
            return SqliteSaver.from_conn_string(db_path)
    
    def _build_graph(self) -> StateGraph:
        """
        Build LangGraph for conversation state management.

        Returns:
            Compiled StateGraph with checkpointing.
        """
        workflow = StateGraph(ConversationState)
        
        def process_message(state: dict) -> dict:
            """
            Process and store messages with windowing and summarization.

            Args:
                state: Current conversation state.

            Returns:
                Updated state dict.
            """
            # Get last message
            messages = state.get("messages", [])
            if not messages:
                return state
            
            last_msg = messages[-1]
            
            # Store in MySQL (source of truth)
            create_chat_message(
                session_id=state["session_id"],
                role="user" if isinstance(last_msg, HumanMessage) else "assistant",
                content=last_msg.content,
            )
            
            # Apply windowing if configured
            if self.config.memory_type == "window":
                windowed_messages = messages[-self.config.short_term_window_size:]
                return {"messages": windowed_messages}
            
            # Apply summarization if configured
            if self.config.memory_type == "summary" and len(messages) > 10:
                summary = self._summarize_messages(messages)
                return {
                    "messages": messages,
                    "summary": summary
                }
            
            return {"messages": messages}
        
        # Add node to workflow
        workflow.add_node("process", process_message)
        workflow.add_edge(START, "process")
        workflow.add_edge("process", END)
        
        # Compile with checkpointing
        return workflow.compile(checkpointer=self.checkpointer)
    
    def _summarize_messages(self, messages: list[BaseMessage]) -> str:
        """
        Generate summary of messages using LLM.

        Args:
            messages: List of conversation messages.

        Returns:
            Summary text.
        """
        if not self.llm:
            return ""
        
        prompt = "Summarize the following conversation concisely:\n\n"
        for msg in messages:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            prompt += f"{role}: {msg.content}\n"
        
        response = self.llm.invoke(prompt)
        return response.content

    def add_message(self, session_id: str, message: ChatMessage) -> None:
        """
        Add a message to conversation memory.

        Args:
            session_id: Unique session identifier.
            message: Chat message to store.

        Raises:
            RuntimeError: If storage fails.
        """
        # Convert to LangChain message
        if message.role == "user":
            lc_message = HumanMessage(content=message.content)
        elif message.role == "assistant":
            lc_message = AIMessage(content=message.content)
        else:
            # Skip system messages in conversation state
            return
        
        # Invoke graph with checkpointing
        config = {"configurable": {"thread_id": session_id}}
        
        self.graph.invoke(
            {"messages": [lc_message], "session_id": session_id},
            config=config
        )

    def get_messages(
        self, session_id: str, limit: int = 50
    ) -> list[ChatMessage]:
        """
        Retrieve conversation history for a session.

        Args:
            session_id: Session identifier.
            limit: Maximum number of messages to retrieve.

        Returns:
            List of chat messages ordered by timestamp.
        """
        # Retrieve from MySQL (source of truth)
        rows = get_chat_history(session_id, limit)

        # Convert to ChatMessage objects
        messages = []
        for row in rows:
            messages.append(
                ChatMessage(
                    role=row["role"],
                    content=row["content"],
                    timestamp=row["created_at"],
                    metadata=row.get("metadata"),
                )
            )

        return messages

    def get_context(
        self, session_id: str, max_tokens: int | None = None
    ) -> MemoryContext:
        """
        Get enriched context from conversation memory.

        Args:
            session_id: Session identifier.
            max_tokens: Maximum tokens to include. Uses config default if None.

        Returns:
            Memory context with short-term buffer.
        """
        if max_tokens is None:
            max_tokens = self.config.max_token_limit

        # Get state from checkpointer
        config = {"configurable": {"thread_id": session_id}}
        
        try:
            state = self.checkpointer.get(config)
            
            # Format messages from state
            if state and "messages" in state.values:
                messages = state.values["messages"]
                history_text = self._format_messages(messages)
                summary = state.values.get("summary")
            else:
                # Fallback to database
                messages = self.get_messages(session_id)
                history_text = "\n".join(
                    f"{msg.role}: {msg.content}" for msg in messages
                )
                summary = None
        except Exception:
            # Fallback to database if checkpointer fails
            messages = self.get_messages(session_id)
            history_text = "\n".join(
                f"{msg.role}: {msg.content}" for msg in messages
            )
            summary = None

        # Get stats
        stats = get_chat_stats(session_id)

        # Build context (long-term features filled by LongTermMemoryProcessor)
        context = MemoryContext(
            session_id=session_id,
            short_term_context=history_text,
            semantic_facts=[],  # Filled by long-term processor
            user_profile={},  # Filled by long-term processor
            episodic_summary=summary,
            procedural_patterns=None,
            total_messages=stats["message_count"],
            metadata={"memory_type": self.config.memory_type},
        )

        return context

    def clear_session(self, session_id: str) -> None:
        """
        Clear all memory for a session.

        Args:
            session_id: Session identifier to clear.
        """
        # Clear from MySQL database
        delete_chat_history(session_id)
        
        # Clear checkpoint state
        config = {"configurable": {"thread_id": session_id}}
        try:
            # Try to delete from checkpointer
            if hasattr(self.checkpointer, 'delete'):
                self.checkpointer.delete(config)
        except Exception:
            # Ignore errors if checkpoint doesn't exist
            pass

    def get_stats(self, session_id: str) -> MemoryStats:
        """
        Get memory statistics for a session.

        Args:
            session_id: Session identifier.

        Returns:
            Memory usage statistics.
        """
        stats = get_chat_stats(session_id)

        return MemoryStats(
            session_id=session_id,
            message_count=stats["message_count"],
            token_count=0,  # TODO: Calculate actual token count
            semantic_facts_count=0,  # Filled by long-term processor
            profile_attributes_count=0,  # Filled by long-term processor
            oldest_message_date=stats["oldest_message"],
            newest_message_date=stats["newest_message"],
        )

    def _format_messages(self, messages: list[BaseMessage]) -> str:
        """
        Format LangChain messages as text.

        Args:
            messages: List of LangChain messages.

        Returns:
            Formatted conversation string.
        """
        formatted = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            formatted.append(f"{role}: {msg.content}")
        return "\n".join(formatted)
