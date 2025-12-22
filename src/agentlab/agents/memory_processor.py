"""
Long-term memory processor implementation.

Provides semantic, episodic, profile, and procedural memory extraction
using hybrid storage (MySQL + Pinecone).
"""

import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pinecone import Pinecone

from agentlab.config.memory_config import MemoryConfig
from agentlab.database.crud import (
    get_chat_history,
    get_user_profile as db_get_user_profile,
    create_or_update_user_profile as db_create_or_update_user_profile,
)
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
        
        # Load profile schema
        self.profile_schema = self._load_profile_schema()
    
    def _load_profile_schema(self) -> dict[str, Any]:
        """
        Load profile schema from configuration file.

        Returns:
            Profile schema dictionary.
        """
        schema_path = Path(__file__).parent.parent.parent / "data" / "configs" / "profile_schema.json"
        
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Return minimal schema if file not found
            return {
                "name": "User Profile",
                "description": "Basic user profile",
                "parameters": {"type": "object", "properties": {}}
            }

    def _build_search_query_from_messages(
        self, messages: list[ChatMessage], max_messages: int = 3
    ) -> str:
        """
        Build search query from recent conversation messages.
        
        Prioritizes user messages to capture current intent.
        
        Args:
            messages: List of conversation messages.
            max_messages: Maximum number of messages to include (default: 3).
        
        Returns:
            Query string for semantic search.
        """
        if not messages:
            return ""
        
        # Take last max_messages, prioritizing user messages
        recent_messages = messages[-max_messages * 2:]  # Get more to filter
        
        # Prioritize user messages
        user_messages = [msg for msg in recent_messages if msg.role == "user"]
        
        # If we have enough user messages, use only those
        if len(user_messages) >= max_messages:
            query_messages = user_messages[-max_messages:]
        else:
            # Use all user messages + some assistant messages
            query_messages = recent_messages[-max_messages:]
        
        # Build query text
        query_parts = [msg.content for msg in query_messages]
        query = " ".join(query_parts)
        
        # Truncate if too long (max ~500 chars for embedding)
        if len(query) > 500:
            query = query[:500]
        
        return query
    
    def search_relevant_conversations(
        self, messages: list[ChatMessage], top_k: int | None = None
    ) -> list[str]:
        """
        Search for relevant past conversations using semantic similarity.
        
        Uses RAG-like approach to find similar conversations from vector database.
        Returns conversation texts as simple strings for compatibility with
        MemoryContext.semantic_facts format.
        
        Args:
            messages: Current conversation messages to build search query.
            top_k: Number of results to return. Uses config default if None.
        
        Returns:
            List of relevant conversation texts from past sessions.
        """
        if not self.embeddings or not self.index:
            return []
        
        if not messages:
            return []
        
        # Build search query from recent messages
        query = self._build_search_query_from_messages(messages)
        
        if not query:
            return []
        
        # Use config default if top_k not specified
        if top_k is None:
            top_k = self.config.semantic_search_top_k
        
        # Search semantic memory (no session_id filter to search all past conversations)
        results = self.search_semantic(
            query=query,
            session_id=None,  # Search across all sessions
            top_k=top_k
        )
        
        # Extract text field and format as list[str]
        conversation_texts = []
        for result in results:
            text = result.get("text", "")
            if text:
                # Optionally include score in format for debugging
                score = result.get("score", 0.0)
                # For now, just return the text without score
                conversation_texts.append(text)
        
        return conversation_texts
    
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

    def get_user_profile(self, session_id: str | None = None) -> dict[str, Any]:
        """
        Get or extract user profile from conversation history.

        Loads existing profile from database and optionally updates it
        with new information from recent messages.

        Args:
            session_id: Session identifier (used to get recent messages for updates).

        Returns:
            Dictionary with profile attributes.
        """
        # Load existing profile from database
        stored_profile = db_get_user_profile()
        
        if stored_profile:
            # Return existing profile data
            return stored_profile["profile_data"]
        
        # No profile exists - return empty dict
        # Profile will be created when extract_and_store_profile is called
        return {}

    def extract_profile_from_messages(
        self, messages: list[ChatMessage], existing_profile: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Extract user profile from messages using LLM.

        Args:
            messages: List of chat messages to analyze.
            existing_profile: Existing profile to update (patch mode).

        Returns:
            Extracted profile dictionary.
        """
        if not self.llm:
            return existing_profile or {}
        
        # Build conversation text (last 50 messages to keep token count manageable)
        conversation = "\n".join(
            [f"{msg.role}: {msg.content}" for msg in messages[-50:]]
        )
        
        # Build prompt with schema
        schema_desc = self.profile_schema.get("description", "")
        schema_props = json.dumps(
            self.profile_schema.get("parameters", {}).get("properties", {}),
            indent=2
        )
        instructions = self.profile_schema.get("instructions", "")
        
        existing_context = ""
        if existing_profile:
            existing_context = f"\n\nEXISTING PROFILE (update/patch this):\n{json.dumps(existing_profile, indent=2)}"
        
        prompt = f"""Extract user profile information from this conversation.

{schema_desc}

SCHEMA:
{schema_props}

INSTRUCTIONS:
{instructions}

You can add additional relevant fields beyond the base schema if you discover important information about the user.
{existing_context}

CONVERSATION:
{conversation}

Return ONLY a valid JSON object with the profile data. Do not include any explanation or markdown formatting:"""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, "content") else ""
            
            # Clean up response - remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]  # Remove ```json
            elif content.startswith("```"):
                content = content[3:]  # Remove ```
            if content.endswith("```"):
                content = content[:-3]  # Remove trailing ```
            content = content.strip()
            
            # Parse JSON
            if content:
                profile = json.loads(content)
                
                # Merge with existing profile if in patch mode
                if existing_profile:
                    merged = existing_profile.copy()
                    merged.update(profile)
                    return merged
                
                return profile if isinstance(profile, dict) else {}
        except Exception as e:
            # If extraction fails, return existing profile or empty dict
            print(f"Profile extraction error: {e}")
            return existing_profile or {}
        
        return existing_profile or {}
    
    def extract_and_store_profile(
        self, session_id: str, incremental: bool = True
    ) -> dict[str, Any]:
        """
        Extract profile from conversation and store in database.

        Args:
            session_id: Session identifier to get messages from.
            incremental: If True, only process new messages since last update.

        Returns:
            Updated profile dictionary.
        """
        # Load existing profile
        stored_profile = db_get_user_profile()
        existing_profile = stored_profile["profile_data"] if stored_profile else None
        last_message_id = stored_profile["last_updated_message_id"] if stored_profile else None
        
        # Get messages
        if incremental and last_message_id:
            # TODO: Implement fetching only new messages after last_message_id
            # For now, get recent messages
            messages_data = get_chat_history(session_id, limit=50)
        else:
            # Full extraction
            messages_data = get_chat_history(session_id, limit=100)
        
        if not messages_data:
            return existing_profile or {}
        
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
        
        # Extract profile using LLM
        new_profile = self.extract_profile_from_messages(messages, existing_profile)
        
        # Store in database
        if new_profile:
            last_msg_id = messages_data[-1]["id"] if messages_data else None
            db_create_or_update_user_profile(new_profile, last_msg_id)
        
        return new_profile
    
    def extract_and_store_semantic(
        self, session_id: str, limit: int = 100
    ) -> dict[str, Any]:
        """
        Extract semantic embeddings from conversation and store in vector database.

        Creates embeddings directly from chat history without LLM extraction.
        Stores conversation with timestamps in metadata.

        Args:
            session_id: Session identifier to get messages from.
            limit: Maximum number of messages to process.

        Returns:
            Dictionary with extraction status and count.

        Raises:
            ValueError: If semantic storage is not configured.
        """
        if self.config.semantic_storage == "mysql":
            raise ValueError("Semantic storage requires Pinecone configuration")
        
        if not self.embeddings or not self.index:
            raise ValueError("Embeddings and vector store not initialized")
        
        # Get messages from database
        messages_data = get_chat_history(session_id, limit=limit)
        
        if not messages_data:
            return {"status": "no_messages", "count": 0}
        
        # Build conversation text with timestamps
        conversation_parts = []
        for row in messages_data:
            timestamp = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            role = row["role"]
            content = row["content"]
            conversation_parts.append(f"[{timestamp}] {role}: {content}")
        
        conversation_text = "\n".join(conversation_parts)
        
        # Get timestamp range for metadata
        first_timestamp = messages_data[0]["created_at"]
        last_timestamp = messages_data[-1]["created_at"]
        
        # Prepare metadata
        metadata = {
            "session_id": session_id,
            "message_count": len(messages_data),
            "first_timestamp": first_timestamp.isoformat(),
            "last_timestamp": last_timestamp.isoformat(),
            "extracted_at": datetime.now().isoformat(),
        }
        
        # Store in vector database
        self.store_semantic_embedding(
            session_id=session_id,
            text=conversation_text,
            metadata=metadata
        )
        
        return {
            "status": "success",
            "count": 1,
            "message_count": len(messages_data),
            "timestamp_range": {
                "start": first_timestamp.isoformat(),
                "end": last_timestamp.isoformat()
            }
        }
    
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
