"""
Memory module configuration.

This module provides configuration for the memory system, including
short-term and long-term memory settings with hybrid storage strategy.
"""

import os
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class MemoryConfig:
    """
    Configuration for the memory system.
    
    Supports hybrid storage strategy: MySQL for structured data
    and Pinecone for semantic embeddings.
    """

    # Database configuration
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    # Memory strategy
    memory_type: Literal["buffer", "summary", "window"] = "buffer"
    short_term_window_size: int = 10  # Last K messages for window memory
    max_token_limit: int = 2000  # Max tokens in short-term context

    # Long-term memory configuration
    enable_long_term: bool = True
    semantic_storage: Literal["mysql", "pinecone", "hybrid"] = "hybrid"
    
    # Granular memory type toggles
    enable_semantic: bool = True  # Extract semantic facts
    enable_episodic: bool = True  # Generate episodic summaries
    enable_profile: bool = True  # Build user profiles
    enable_procedural: bool = True  # Detect procedural patterns
    
    # Pinecone configuration (for semantic memory)
    pinecone_api_key: str | None = None
    pinecone_index_name: str | None = None
    pinecone_namespace: str = "conversation_memory"
    
    # OpenAI configuration (for embeddings and summarization)
    openai_api_key: str | None = None
    embedding_model: str = "text-embedding-ada-002"
    summary_model: str = "gpt-3.5-turbo"
    
    # Semantic search configuration
    semantic_search_top_k: int = 5  # Number of relevant conversations to retrieve

    # Privacy and retention settings
    retention_days: int | None = None  # None = keep forever
    enable_anonymization: bool = False
    sensitive_fields: list[str] | None = None

    # Performance settings
    batch_size: int = 100  # Batch size for bulk operations
    enable_caching: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes

    @classmethod
    def from_env(cls) -> "MemoryConfig":
        """
        Create configuration from environment variables.

        Required environment variables:
            - DB_HOST: MySQL hostname
            - DB_PORT: MySQL port
            - DB_USER: MySQL username
            - DB_PASSWORD: MySQL password
            - DB_NAME: Database name
            
        Optional environment variables:
            - MEMORY_TYPE: buffer, summary, or window (default: buffer)
            - SHORT_TERM_WINDOW_SIZE: Window size for window memory
            - MAX_TOKEN_LIMIT: Max tokens in context
            - ENABLE_LONG_TERM: Enable long-term memory (default: true)
            - SEMANTIC_STORAGE: mysql, pinecone, or hybrid (default: hybrid)
            - ENABLE_SEMANTIC_MEMORY: Enable semantic facts extraction (default: true)
            - ENABLE_EPISODIC_MEMORY: Enable episodic summaries (default: true)
            - ENABLE_PROFILE_MEMORY: Enable user profile building (default: true)
            - ENABLE_PROCEDURAL_MEMORY: Enable procedural pattern detection (default: true)
            - PINECONE_API_KEY: Pinecone API key
            - PINECONE_INDEX_NAME: Pinecone index name
            - PINECONE_NAMESPACE: Namespace for memory (default: conversation_memory)
            - OPENAI_API_KEY: OpenAI API key
            - EMBEDDING_MODEL: Embedding model name
            - SUMMARY_MODEL: Summary model name
            - SEMANTIC_SEARCH_TOP_K: Number of results for semantic search (default: 5)
            - RETENTION_DAYS: Days to keep memory (None = forever)
            - ENABLE_ANONYMIZATION: Enable data anonymization
            - BATCH_SIZE: Batch size for operations
            - ENABLE_CACHING: Enable caching
            - CACHE_TTL_SECONDS: Cache TTL in seconds

        Returns:
            MemoryConfig instance.

        Raises:
            ValueError: If required environment variables are missing.
        """
        # Required variables
        required_vars = {
            "DB_HOST": "DB_HOST",
            "DB_PORT": "DB_PORT",
            "DB_USER": "DB_USER",
            "DB_PASSWORD": "DB_PASSWORD",
            "DB_NAME": "DB_NAME",
        }
        
        missing = [
            name for name, env_var in required_vars.items()
            if not os.getenv(env_var)
        ]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        
        # Get optional semantic storage setting
        semantic_storage = os.getenv("SEMANTIC_STORAGE", "hybrid")
        
        # Validate semantic storage dependencies
        if semantic_storage in ("pinecone", "hybrid"):
            if not os.getenv("PINECONE_API_KEY"):
                raise ValueError(
                    "PINECONE_API_KEY required for pinecone/hybrid storage"
                )
            if not os.getenv("PINECONE_INDEX_NAME"):
                raise ValueError(
                    "PINECONE_INDEX_NAME required for pinecone/hybrid storage"
                )
        
        # Get retention days (None means keep forever)
        retention_str = os.getenv("RETENTION_DAYS")
        retention_days = int(retention_str) if retention_str else None
        
        # Parse sensitive fields
        sensitive_fields_str = os.getenv("SENSITIVE_FIELDS")
        sensitive_fields = (
            sensitive_fields_str.split(",") if sensitive_fields_str else None
        )
        
        return cls(
            # Database
            db_host=os.getenv("DB_HOST", ""),
            db_port=int(os.getenv("DB_PORT", "3306")),
            db_user=os.getenv("DB_USER", ""),
            db_password=os.getenv("DB_PASSWORD", ""),
            db_name=os.getenv("DB_NAME", ""),
            # Memory strategy
            memory_type=os.getenv("MEMORY_TYPE", "buffer"),  # type: ignore
            short_term_window_size=int(
                os.getenv("SHORT_TERM_WINDOW_SIZE", "10")
            ),
            max_token_limit=int(os.getenv("MAX_TOKEN_LIMIT", "2000")),
            # Long-term
            enable_long_term=os.getenv("ENABLE_LONG_TERM", "true").lower()
            == "true",
            semantic_storage=semantic_storage,  # type: ignore
            # Granular memory types
            enable_semantic=os.getenv(
                "ENABLE_SEMANTIC_MEMORY", "true"
            ).lower()
            == "true",
            enable_episodic=os.getenv(
                "ENABLE_EPISODIC_MEMORY", "true"
            ).lower()
            == "true",
            enable_profile=os.getenv(
                "ENABLE_PROFILE_MEMORY", "true"
            ).lower()
            == "true",
            enable_procedural=os.getenv(
                "ENABLE_PROCEDURAL_MEMORY", "true"
            ).lower()
            == "true",
            # Pinecone
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            pinecone_index_name=os.getenv("PINECONE_INDEX_NAME"),
            pinecone_namespace=os.getenv(
                "PINECONE_NAMESPACE", "conversation_memory"
            ),
            # OpenAI
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            embedding_model=os.getenv(
                "EMBEDDING_MODEL", "text-embedding-ada-002"
            ),
            summary_model=os.getenv("SUMMARY_MODEL", "gpt-3.5-turbo"),
            semantic_search_top_k=int(os.getenv("SEMANTIC_SEARCH_TOP_K", "5")),
            # Privacy
            retention_days=retention_days,
            enable_anonymization=os.getenv(
                "ENABLE_ANONYMIZATION", "false"
            ).lower()
            == "true",
            sensitive_fields=sensitive_fields,
            # Performance
            batch_size=int(os.getenv("BATCH_SIZE", "100")),
            enable_caching=os.getenv("ENABLE_CACHING", "true").lower()
            == "true",
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
        )
