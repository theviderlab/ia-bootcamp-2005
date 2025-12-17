"""
Long-term memory processor implementation.

Provides semantic, episodic, profile, and procedural memory extraction
using hybrid storage (MySQL + Pinecone).
"""

import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta
from typing import Any

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pinecone import Pinecone

from agentlab.config.memory_config import MemoryConfig
from agentlab.database.crud import get_chat_history
from agentlab.models import ChatMessage


class LongTermMemoryProcessor:
    """
    Long-term memory processor with hybrid storage.
    
    Extracts and stores semantic facts, user profiles, episodic summaries,
    and procedural patterns from conversations.
    """

    def __init__(self, config: MemoryConfig | None = None):
        """
        Initialize long-term memory processor.

        Args:
            config: Memory configuration. If None, loads from environment.

        Raises:
            ValueError: If configuration is invalid.
        """
        self.config = config or MemoryConfig.from_env()

        # Initialize embeddings for semantic memory
        if self.config.semantic_storage in ("pinecone", "hybrid"):
            if not self.config.openai_api_key:
                raise ValueError("OpenAI API key required for embeddings")

            self.embeddings = OpenAIEmbeddings(
                model=self.config.embedding_model,
                openai_api_key=self.config.openai_api_key,
            )

            # Initialize Pinecone
            if not self.config.pinecone_api_key:
                raise ValueError("Pinecone API key required")

            self.pc = Pinecone(api_key=self.config.pinecone_api_key)
            self.index = self.pc.Index(self.config.pinecone_index_name or "")
        else:
            self.embeddings = None
            self.pc = None
            self.index = None

        # Initialize LLM for extraction
        if self.config.openai_api_key:
            self.llm = ChatOpenAI(
                model=self.config.summary_model,
                openai_api_key=self.config.openai_api_key,
            )
        else:
            self.llm = None

    def extract_semantic_facts(
        self, session_id: str, messages: list[ChatMessage]
    ) -> list[str]:
        """
        Extract semantic facts from conversation.

        Uses LLM to identify key facts, statements, and information
        shared during the conversation.

        Args:
            session_id: Session identifier.
            messages: List of chat messages.

        Returns:
            List of extracted semantic facts.
        """
        if not self.llm:
            return []

        # Build conversation text
        conversation = "\n".join(
            [f"{msg.role}: {msg.content}" for msg in messages[-20:]]
        )

        prompt = f"""Extract key facts and information from this conversation.
            Focus on factual statements, preferences, and important details.
            Return as a JSON array of strings.

            Conversation:
            {conversation}

            Facts (JSON array):"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, "content") else ""
            
            # Try to parse JSON
            if content.strip().startswith("["):
                facts = json.loads(content)
                return facts if isinstance(facts, list) else []
        except Exception:
            pass

        return []

    def get_user_profile(self, session_id: str) -> dict[str, Any]:
        """
        Get aggregated user profile from conversation history.

        Extracts user preferences, characteristics, and patterns.

        Args:
            session_id: Session identifier.

        Returns:
            Dictionary with profile attributes.
        """
        messages_data = get_chat_history(session_id, limit=100)

        if not messages_data:
            return {}

        # Convert to ChatMessage objects
        messages = [
            ChatMessage(
                role=row["role"],
                content=row["content"],
                timestamp=row["created_at"],
                metadata=row.get("metadata"),
            )
            for row in messages_data
        ]

        profile = {
            "session_id": session_id,
            "total_messages": len(messages),
            "user_messages": sum(1 for m in messages if m.role == "user"),
            "first_interaction": messages[0].timestamp if messages else None,
            "last_interaction": messages[-1].timestamp if messages else None,
        }

        # Extract topics using keyword frequency (simple approach)
        user_messages = [m.content for m in messages if m.role == "user"]
        words = " ".join(user_messages).lower().split()
        
        # Filter common words and get top keywords
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on"}
        keywords = [w for w in words if len(w) > 3 and w not in common_words]
        
        if keywords:
            word_counts = Counter(keywords)
            profile["top_topics"] = [
                {"word": word, "count": count}
                for word, count in word_counts.most_common(10)
            ]

        return profile

    def get_episodic_summary(self, session_id: str) -> str | None:
        """
        Get temporal summary of conversation episodes.

        Creates a chronological summary of conversation topics and events.

        Args:
            session_id: Session identifier.

        Returns:
            Episodic summary text or None if no history.
        """
        if not self.llm:
            return None

        messages_data = get_chat_history(session_id, limit=50)
        if not messages_data:
            return None

        # Build conversation text
        conversation = "\n".join(
            [
                f"{row['created_at'].strftime('%H:%M')} - "
                f"{row['role']}: {row['content']}"
                for row in messages_data[-20:]
            ]
        )

        prompt = f"""Create a brief chronological summary of this conversation.
Focus on main topics discussed and how the conversation evolved.
Keep it concise (2-3 sentences).

Conversation:
{conversation}

Summary:"""

        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, "content") else None
        except Exception:
            return None

    def get_procedural_patterns(self, session_id: str) -> list[str]:
        """
        Identify procedural patterns from user interactions.

        Detects common workflows, question patterns, and interaction styles.

        Args:
            session_id: Session identifier.

        Returns:
            List of identified patterns.
        """
        messages_data = get_chat_history(session_id, limit=100)
        if not messages_data:
            return []

        patterns = []

        # Detect question patterns
        user_messages = [
            row["content"] for row in messages_data if row["role"] == "user"
        ]
        
        question_count = sum(1 for msg in user_messages if "?" in msg)
        if question_count > len(user_messages) * 0.5:
            patterns.append("frequently_asks_questions")

        # Detect greeting patterns
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon"]
        if any(
            any(greeting in msg.lower() for greeting in greetings)
            for msg in user_messages[:5]
        ):
            patterns.append("uses_greetings")

        # Detect code-related interactions
        if any("```" in msg or "code" in msg.lower() for msg in user_messages):
            patterns.append("discusses_code")

        return patterns

    def store_semantic_embedding(
        self, session_id: str, text: str, metadata: dict[str, Any]
    ) -> None:
        """
        Store semantic embedding in vector database.

        Args:
            session_id: Session identifier.
            text: Text to embed and store.
            metadata: Additional metadata.

        Raises:
            RuntimeError: If storage fails.
        """
        if self.config.semantic_storage == "mysql":
            # Store in MySQL (not implemented yet)
            return

        if not self.embeddings or not self.index:
            return

        # Generate embedding
        embedding = self.embeddings.embed_query(text)

        # Generate stable ID
        doc_id = hashlib.sha256(
            f"{session_id}:{text}".encode()
        ).hexdigest()[:16]

        # Prepare metadata
        meta = {
            "session_id": session_id,
            "text": text,
            "timestamp": datetime.now().isoformat(),
            **metadata,
        }

        # Store in Pinecone
        try:
            self.index.upsert(
                vectors=[(doc_id, embedding, meta)],
                namespace=self.config.pinecone_namespace,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to store embedding: {e}") from e

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
        if not self.embeddings or not self.index:
            return []

        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)

        # Build filter
        filter_dict = {"session_id": session_id} if session_id else None

        # Search Pinecone
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=self.config.pinecone_namespace,
                filter=filter_dict,
            )

            # Format results
            matches = []
            for match in results.get("matches", []):
                matches.append(
                    {
                        "id": match["id"],
                        "score": match["score"],
                        "text": match["metadata"].get("text", ""),
                        "session_id": match["metadata"].get("session_id"),
                        "metadata": match["metadata"],
                    }
                )

            return matches
        except Exception:
            return []
