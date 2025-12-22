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
from agentlab.database.crud import bulk_insert_knowledge_documents
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

    def retrieve_documents(
        self, query: str, top_k: int = 5, namespace: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant documents without LLM generation.

        This method performs only vector similarity search and returns
        document metadata with scores. No LLM calls are made.

        Args:
            query: User query string.
            top_k: Number of top documents to retrieve.
            namespace: Optional namespace for multi-tenant isolation.

        Returns:
            List of source dictionaries with metadata and similarity scores.
            Returns empty list if no documents found or query is invalid.

        Raises:
            RuntimeError: If document retrieval fails.
        """
        try:
            # Preprocess query
            processed_query = preprocess_text(query)

            if not processed_query:
                print("Warning: Empty query after preprocessing")
                return []

            # Use configured namespace if not provided
            search_namespace = namespace or self.config.namespace

            # Retrieve similar documents with scores
            docs_with_scores = self._retrieve_similar(processed_query, top_k, search_namespace)

            if not docs_with_scores:
                return []

            # Extract source information with scores
            sources = self._extract_sources(docs_with_scores)

            return sources

        except Exception as e:
            raise RuntimeError(f"Document retrieval failed: {str(e)}") from e

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
            # Use retrieve_documents for document retrieval
            sources = self.retrieve_documents(query, top_k, namespace)

            if not sources:
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

            # Reconstruct documents from sources for context building
            from langchain_core.documents import Document
            docs = [
                Document(
                    page_content=src["content_preview"].replace("...", ""),
                    metadata={
                        "source": src["source"],
                        "chunk": src["chunk"],
                        "created_at": src["created_at"],
                    }
                )
                for src in sources
            ]
            print(docs)

            # Build context from retrieved documents
            context = self._build_context(docs)

            # Generate augmented prompt
            augmented_prompt = self._build_augmented_prompt(query, context)

            # Generate response using LLM
            response = self.llm.generate(augmented_prompt, temperature=0.7)

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
            document_metadata: dict[str, dict[str, Any]] = {}  # Track metadata per doc_id

            for idx, doc in enumerate(documents):
                # Check if it's a file path or text content
                file_size = None
                source = None
                
                if isinstance(doc, (str, Path)):
                    path = Path(doc)
                    if path.exists():
                        # It's a file path - load content
                        content = self.loader_registry.load(path)
                        source = path.name
                        file_size = path.stat().st_size
                    else:
                        # It's text content - generate a source name
                        content = str(doc)
                        source = f"text_upload_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        file_size = len(content.encode('utf-8'))
                else:
                    # It's text content - generate a source name
                    content = str(doc)
                    source = f"text_upload_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    file_size = len(content.encode('utf-8'))

                # Chunk document
                chunks = chunk_document(
                    document=content,
                    chunk_size=chunk_size,
                    overlap=chunk_overlap,
                    source=source,
                )

                # Track metadata for MySQL insert (now always has source)
                if chunks:
                    doc_id = generate_document_id(chunks[0].page_content, source)
                    if doc_id not in document_metadata:
                        # Determine upload type
                        is_file = isinstance(doc, (str, Path)) and Path(doc).exists()
                        upload_type = "file" if is_file else "text"
                        
                        document_metadata[doc_id] = {
                            "doc_id": doc_id,
                            "content": chunks[0].page_content[:500],  # Store first 500 chars as sample
                            "filename": source,
                            "namespace": use_namespace,
                            "chunk_count": 0,
                            "file_size": file_size,
                            "metadata": {
                                "source": source, 
                                "chunk_size": chunk_size, 
                                "chunk_overlap": chunk_overlap,
                                "upload_type": upload_type,
                            },
                        }
                    document_metadata[doc_id]["chunk_count"] += len(chunks)

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

            print(f"✅ Added {len(all_chunks)} chunks to Pinecone namespace '{use_namespace or 'default'}'")

            # Add to MySQL knowledge_base table (fail entire operation if this fails)
            if document_metadata:
                try:
                    mysql_documents = list(document_metadata.values())
                    rows_affected = bulk_insert_knowledge_documents(mysql_documents)
                    print(
                        f"✅ Stored {rows_affected} document(s) metadata in MySQL knowledge_base table"
                    )
                except Exception as mysql_error:
                    # Critical: fail the entire operation if MySQL write fails
                    raise RuntimeError(
                        f"Failed to store document metadata in MySQL: {mysql_error}. "
                        f"Pinecone vectors added but metadata not persisted."
                    ) from mysql_error
            else:
                print("⚠️  Warning: No document metadata to store in MySQL")

            print(
                f"✅ Successfully added {len(document_metadata)} document(s) to namespace '{use_namespace or 'default'}'"
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
            List of tuples containing (document, similarity_score) sorted by score descending.
        """
        try:
            if namespace:
                docs_with_scores = self.vectorstore.similarity_search_with_score(
                    query, k=top_k, namespace=namespace
                )
            else:
                docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=top_k)
            
            # Sort by score in descending order (higher score = more similar)
            # Pinecone may return results in unpredictable order depending on the metric
            docs_with_scores.sort(key=lambda x: x[1], reverse=True)
            
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

    def get_namespace_stats(self, namespace: str) -> dict[str, Any]:
        """
        Get statistics for a specific namespace.

        Args:
            namespace: The namespace to get stats for.

        Returns:
            Dictionary with namespace statistics including vector count and dimension.

        Raises:
            RuntimeError: If stats retrieval fails.
        """
        try:
            if not namespace:
                raise ValueError("Namespace cannot be empty")

            # Get the Pinecone index
            index = self.pc.Index(self.config.index_name)

            # Get index statistics
            stats = index.describe_index_stats()

            # Extract namespace-specific stats
            namespace_stats = stats.get("namespaces", {}).get(namespace, {})
            
            if not namespace_stats:
                # Namespace exists but is empty or doesn't exist yet
                return {
                    "success": True,
                    "namespace": namespace,
                    "vector_count": 0,
                    "dimension": self.config.dimension,
                    "exists": False,
                }

            return {
                "success": True,
                "namespace": namespace,
                "vector_count": namespace_stats.get("vector_count", 0),
                "dimension": stats.get("dimension", self.config.dimension),
                "exists": True,
            }

        except Exception as e:
            raise RuntimeError(f"Failed to get stats for namespace '{namespace}': {e}") from e

    def list_namespaces(self) -> list[dict[str, Any]]:
        """
        List all available namespaces with document counts and metadata.

        Combines data from Pinecone index statistics and MySQL database
        to provide comprehensive namespace information.

        Returns:
            List of dictionaries with namespace information:
            - name: Namespace name ("default" for empty namespace)
            - document_count: Number of unique documents
            - total_chunks: Total number of vector chunks
            - last_updated: ISO timestamp of most recent update

        Raises:
            RuntimeError: If listing fails.
        """
        try:
            # Get Pinecone namespace stats
            index = self.pc.Index(self.config.index_name)
            stats = index.describe_index_stats()
            pinecone_namespaces = stats.get("namespaces", {})

            # Get database document counts
            from agentlab.database.crud import get_namespace_document_counts

            db_namespaces = get_namespace_document_counts()
            db_lookup = {ns["namespace"]: ns for ns in db_namespaces}

            # Merge Pinecone and database data
            namespaces = []
            seen_namespaces = set()

            # Process Pinecone namespaces
            for ns_name, ns_data in pinecone_namespaces.items():
                # Map empty string to "default" for display
                display_name = "default" if ns_name == "" else ns_name
                seen_namespaces.add(ns_name)

                db_data = db_lookup.get(ns_name, {})
                
                namespaces.append({
                    "name": display_name,
                    "document_count": db_data.get("document_count", 0),
                    "total_chunks": ns_data.get("vector_count", 0),
                    "last_updated": db_data.get("last_updated").isoformat() 
                        if db_data.get("last_updated") else datetime.now().isoformat(),
                })

            # Add any database-only namespaces (shouldn't happen in normal operation)
            for ns_data in db_namespaces:
                ns_name = ns_data["namespace"]
                if ns_name not in seen_namespaces:
                    display_name = "default" if ns_name == "" else ns_name
                    namespaces.append({
                        "name": display_name,
                        "document_count": ns_data.get("document_count", 0),
                        "total_chunks": ns_data.get("total_chunks", 0),
                        "last_updated": ns_data.get("last_updated").isoformat()
                            if ns_data.get("last_updated") else datetime.now().isoformat(),
                    })

            # Sort by last_updated descending
            namespaces.sort(key=lambda x: x["last_updated"], reverse=True)

            return namespaces

        except Exception as e:
            raise RuntimeError(f"Failed to list namespaces: {e}") from e

    def list_documents(
        self, 
        namespace: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        List documents in the knowledge base with optional namespace filter.

        Args:
            namespace: Optional namespace to filter by. Use "default" for empty namespace.
            limit: Maximum number of documents to return (1-1000).
            offset: Number of documents to skip for pagination.

        Returns:
            Dictionary containing:
            - documents: List of document metadata
            - total_count: Total documents matching filter
            - limit: Applied limit
            - offset: Applied offset
            - has_more: Boolean indicating if more documents exist

        Raises:
            RuntimeError: If listing fails.
            ValueError: If limit is out of range.
        """
        try:
            from agentlab.database.crud import query_knowledge_base_documents

            # Map "default" display name back to empty string for query
            query_namespace = "" if namespace == "default" else namespace

            result = query_knowledge_base_documents(
                namespace=query_namespace,
                limit=limit,
                offset=offset,
            )

            # Process documents to format timestamps and map empty namespace to "default"
            documents = []
            for doc in result["documents"]:
                # Map empty namespace to "default" for display
                ns = doc.get("namespace", "")
                display_namespace = "default" if ns == "" else ns

                documents.append({
                    "id": doc["id"],
                    "filename": doc["filename"],
                    "namespace": display_namespace,
                    "chunk_count": doc.get("chunk_count", 0),
                    "file_size": doc.get("file_size", 0),
                    "uploaded_at": doc["uploaded_at"].isoformat() 
                        if doc.get("uploaded_at") else datetime.now().isoformat(),
                })

            has_more = (offset + limit) < result["total_count"]

            return {
                "documents": documents,
                "total_count": result["total_count"],
                "limit": limit,
                "offset": offset,
                "has_more": has_more,
            }

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to list documents: {e}") from e
