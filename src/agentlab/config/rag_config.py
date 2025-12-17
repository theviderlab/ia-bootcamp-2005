"""
RAG configuration module.

Manages configuration for Pinecone vector store and embeddings.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RAGConfig:
    """
    Configuration for RAG system using Pinecone.

    Attributes:
        pinecone_api_key: API key for Pinecone service.
        index_name: Name of the Pinecone index to use.
        cloud: Cloud provider (e.g., 'aws', 'gcp', 'azure').
        region: Cloud region for the index.
        openai_api_key: API key for OpenAI embeddings.
        enable_rag: Enable or disable RAG functionality.
        dimension: Vector dimension (default 1536 for text-embedding-ada-002).
        metric: Distance metric for similarity (default 'cosine').
        namespace: Default namespace for document organization (optional).
    """

    pinecone_api_key: str
    index_name: str
    cloud: str
    region: str
    openai_api_key: str
    enable_rag: bool = True
    dimension: int = 1536
    metric: str = "cosine"
    namespace: str | None = None

    @classmethod
    def from_env(cls) -> "RAGConfig":
        """
        Create configuration from environment variables.

        Required environment variables:
            - PINECONE_API_KEY: Pinecone API key
            - PINECONE_INDEX_NAME: Name of the Pinecone index
            - PINECONE_CLOUD: Cloud provider (aws, gcp, azure)
            - PINECONE_REGION: Cloud region
            - OPENAI_API_KEY: OpenAI API key

        Optional environment variables:
            - ENABLE_RAG: Enable RAG functionality (default: true)
            - PINECONE_DIMENSION: Vector dimension (default: 1536)
            - PINECONE_METRIC: Distance metric (default: cosine)
            - PINECONE_NAMESPACE: Default namespace (default: None)

        Returns:
            RAGConfig instance with values from environment.

        Raises:
            ValueError: If required environment variables are missing.
        """
        required_vars = [
            "PINECONE_API_KEY",
            "PINECONE_INDEX_NAME",
            "PINECONE_CLOUD",
            "PINECONE_REGION",
            "OPENAI_API_KEY",
        ]

        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Please set these in your .env file or environment."
            )

        return cls(
            pinecone_api_key=os.getenv("PINECONE_API_KEY", ""),
            index_name=os.getenv("PINECONE_INDEX_NAME", ""),
            cloud=os.getenv("PINECONE_CLOUD", ""),
            region=os.getenv("PINECONE_REGION", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            enable_rag=os.getenv("ENABLE_RAG", "true").lower() == "true",
            dimension=int(os.getenv("PINECONE_DIMENSION", "1536")),
            metric=os.getenv("PINECONE_METRIC", "cosine"),
            namespace=os.getenv("PINECONE_NAMESPACE"),
        )
