"""
RAG (Retrieval Augmented Generation) service implementation.

Manages the interaction between the knowledge base, embedding generation,
document retrieval, and LLM response generation using Pinecone vector store.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from agentlab.agents.rag_processor import (
    chunk_document,
    generate_document_id,
    preprocess_text,
)
from agentlab.config.rag_config import RAGConfig
from agentlab.loaders import DocumentLoaderRegistry, TextFileLoader
from agentlab.models import LLMInterface, RAGResult


class RAGServiceImpl:
    """
    Implementation of RAG service using Pinecone and LangChain.

    This service:
    1. Embeds documents and stores them in Pinecone vector store
    2. Retrieves relevant documents based on query similarity
    3. Augments LLM prompts with retrieved context
    4. Generates responses using the LLM with namespace support

    Features:
    - Automatic Pinecone index creation and management
    - Multi-tenant support via namespaces
    - Document chunking with metadata
    - Extensible document loader system
    """

    def __init__(self, llm: LLMInterface, config: RAGConfig | None = None):
        """
        Initialize the RAG service.

        Args:
            llm: LLM implementation for generating responses.
            config: RAG configuration. If None, loads from environment.

        Raises:
            ValueError: If configuration is invalid.
            RuntimeError: If Pinecone initialization fails.
        """
        self.llm = llm
        self.config = config or RAGConfig.from_env()

        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=self.config.pinecone_api_key)

            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=self.config.openai_api_key,
                model="text-embedding-ada-002",
            )

            # Ensure index exists
            self.ensure_index_exists()

            # Initialize vector store
            self.vectorstore = PineconeVectorStore(
                index_name=self.config.index_name,
                embedding=self.embeddings,
                pinecone_api_key=self.config.pinecone_api_key,
            )

            # Initialize document loader registry
            self.loader_registry = DocumentLoaderRegistry()
            self.loader_registry.register(TextFileLoader())

        except Exception as e:
            raise RuntimeError(f"Failed to initialize RAG service: {e}") from e

    def ensure_index_exists(self) -> None:
        """
        Ensure Pinecone index exists, create if it doesn't.

        Creates a serverless index with the configured specifications.

        Raises:
            RuntimeError: If index creation fails.
        """
        try:
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]

            if self.config.index_name not in existing_indexes:
                print(f"Creating Pinecone index: {self.config.index_name}")

                self.pc.create_index(
                    name=self.config.index_name,
                    dimension=self.config.dimension,
                    metric=self.config.metric,
                    spec=ServerlessSpec(
                        cloud=self.config.cloud, region=self.config.region
                    ),
                )

                print(f"Index {self.config.index_name} created successfully")
            else:
                print(f"Using existing index: {self.config.index_name}")

        except Exception as e:
            raise RuntimeError(f"Failed to ensure index exists: {e}") from e

    def query(
        self, query: str, top_k: int = 5, namespace: str | None = None
    ) -> RAGResult:
        """
        Query the RAG system with a question.

        Args:
            query: User query string.
            top_k: Number of top documents to retrieve.
            namespace: Optional namespace for multi-tenant isolation.

        Returns:
            RAG result with response and sources.
        """
        try:
            # Preprocess query
            processed_query = preprocess_text(query)

            if not processed_query:
                return RAGResult(
                    success=False,
                    response="",
                    sources=[],
                    error_message="Query cannot be empty",
                )

            # Use configured namespace if not provided
            search_namespace = namespace or self.config.namespace

            # Retrieve similar documents with scores
            docs_with_scores = self._retrieve_similar(processed_query, top_k, search_namespace)

            if not docs_with_scores:
                # No documents found, respond without context
                response = self.llm.generate(
                    f"Answer the following question: {query}\n\n"
                    f"Note: No relevant context was found in the knowledge base.",
                    temperature=0.7,
                )
                return RAGResult(
                    success=True,
                    response=response,
                    sources=[],
                )

            # Extract documents for context building
            docs = [doc for doc, _ in docs_with_scores]

            # Build context from retrieved documents
            context = self._build_context(docs)

            # Generate augmented prompt
            augmented_prompt = self._build_augmented_prompt(query, context)

            # Generate response using LLM
            response = self.llm.generate(augmented_prompt, temperature=0.7)

            # Extract source information with scores
            sources = self._extract_sources(docs_with_scores)

            return RAGResult(
                success=True, response=response, sources=sources, error_message=None
            )

        except Exception as e:
            return RAGResult(
                success=False,
                response="",
                sources=[],
                error_message=f"Query failed: {str(e)}",
            )

    def add_documents(
        self,
        documents: list[str] | list[Path],
        namespace: str | None = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        """
        Add documents to the knowledge base.

        Args:
            documents: List of document strings or file paths.
            namespace: Optional namespace for organization.
            chunk_size: Maximum characters per chunk.
            chunk_overlap: Overlapping characters between chunks.

        Raises:
            RuntimeError: If document addition fails.
        """
        try:
            all_chunks: list[Document] = []
            use_namespace = namespace or self.config.namespace

            for doc in documents:
                # Check if it's a file path or text content
                if isinstance(doc, (str, Path)):
                    path = Path(doc)
                    if path.exists():
                        # It's a file path - load content
                        content = self.loader_registry.load(path)
                        source = path.name
                    else:
                        # It's text content
                        content = str(doc)
                        source = None
                else:
                    content = str(doc)
                    source = None

                # Chunk document
                chunks = chunk_document(
                    document=content,
                    chunk_size=chunk_size,
                    overlap=chunk_overlap,
                    source=source,
                )

                all_chunks.extend(chunks)

            if not all_chunks:
                raise ValueError("No document chunks to add")

            # Generate stable IDs for upsert behavior
            ids = [
                generate_document_id(chunk.page_content, chunk.metadata.get("source"))
                for chunk in all_chunks
            ]

            # Add to Pinecone
            if use_namespace:
                self.vectorstore.add_documents(
                    documents=all_chunks, ids=ids, namespace=use_namespace
                )
            else:
                self.vectorstore.add_documents(documents=all_chunks, ids=ids)

            print(
                f"Added {len(all_chunks)} document chunks to namespace '{use_namespace or 'default'}'"
            )

        except Exception as e:
            raise RuntimeError(f"Failed to add documents: {e}") from e

    def add_documents_from_directory(
        self,
        directory: str | Path,
        namespace: str | None = None,
        recursive: bool = True,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        """
        Add all documents from a directory to the knowledge base.

        Args:
            directory: Path to directory containing documents.
            namespace: Optional namespace for organization.
            recursive: Whether to search subdirectories.
            chunk_size: Maximum characters per chunk.
            chunk_overlap: Overlapping characters between chunks.

        Raises:
            FileNotFoundError: If directory doesn't exist.
            RuntimeError: If document addition fails.
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        # Find all supported files
        pattern = "**/*" if recursive else "*"
        files = [
            f for f in dir_path.glob(pattern) if f.is_file() and self.loader_registry.supports(f)
        ]

        if not files:
            print(f"No supported files found in {directory}")
            return

        print(f"Found {len(files)} files to process")

        # Add documents
        self.add_documents(
            documents=files,
            namespace=namespace,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def _retrieve_similar(
        self, query: str, top_k: int, namespace: str | None
    ) -> list[tuple[Document, float]]:
        """
        Retrieve similar documents from vector store with similarity scores.

        Args:
            query: Query text.
            top_k: Number of results to return.
            namespace: Optional namespace to search in.

        Returns:
            List of tuples containing (document, similarity_score).
        """
        try:
            if namespace:
                docs_with_scores = self.vectorstore.similarity_search_with_score(
                    query, k=top_k, namespace=namespace
                )
            else:
                docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=top_k)
            return docs_with_scores
        except Exception as e:
            print(f"Warning: Similarity search failed: {e}")
            return []

    def _build_context(self, documents: list[Document]) -> str:
        """
        Build context string from retrieved documents.

        Args:
            documents: List of retrieved documents.

        Returns:
            Formatted context string.
        """
        context_parts = []

        for idx, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            chunk = doc.metadata.get("chunk", "?")
            content = doc.page_content

            context_parts.append(
                f"[Document {idx} - Source: {source}, Chunk: {chunk}]\n{content}"
            )

        return "\n\n".join(context_parts)

    def _build_augmented_prompt(self, query: str, context: str) -> str:
        """
        Build augmented prompt with context.

        Args:
            query: User query.
            context: Retrieved context.

        Returns:
            Augmented prompt string.
        """
        return f"""You are a helpful AI assistant. Use the following context to answer the question accurately and concisely.

            INSTRUCTIONS:
            - Base your answer primarily on the provided context
            - If the context contains the answer, cite the source (mention "Document X")
            - If the context is insufficient, clearly state this and provide a general answer
            - Be specific and factual
            - Keep your answer clear and well-structured

            CONTEXT:
            {context}

            QUESTION: {query}

            ANSWER:"""

    def _extract_sources(self, documents_with_scores: list[tuple[Document, float]]) -> list[dict[str, Any]]:
        """
        Extract source information from documents with similarity scores.

        Args:
            documents_with_scores: List of tuples containing (document, similarity_score).

        Returns:
            List of source metadata dictionaries including similarity scores.
        """
        sources = []

        for doc, score in documents_with_scores:
            source_info = {
                "source": doc.metadata.get("source", "Unknown"),
                "chunk": doc.metadata.get("chunk", 0),
                "created_at": doc.metadata.get("created_at"),
                "score": float(score),
                "content_preview": doc.page_content[:200] + "..."
                if len(doc.page_content) > 200
                else doc.page_content,
            }
            sources.append(source_info)

        return sources

    def delete_namespace(self, namespace: str) -> dict[str, Any]:
        """
        Delete all documents in a specific namespace.

        Args:
            namespace: The namespace to delete.

        Returns:
            Dictionary with deletion status and details.

        Raises:
            RuntimeError: If deletion fails.
        """
        try:
            if not namespace:
                raise ValueError("Namespace cannot be empty")

            # Get the Pinecone index
            index = self.pc.Index(self.config.index_name)

            # Delete all vectors in the namespace
            index.delete(delete_all=True, namespace=namespace)

            return {
                "success": True,
                "namespace": namespace,
                "message": f"Namespace '{namespace}' deleted successfully",
            }

        except Exception as e:
            raise RuntimeError(f"Failed to delete namespace '{namespace}': {e}") from e
