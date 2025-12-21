"""
RAG (Retrieval-Augmented Generation) API routes.

Endpoints for:
- Querying the RAG knowledge base
- Adding documents and directories
- Managing namespaces
- Retrieving RAG results and statistics
- Listing namespaces and documents with pagination
"""

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agentlab.core.llm_interface import LangChainLLM
from agentlab.core.rag_service import RAGServiceImpl
from agentlab.models.config_models import (
    NamespaceListResponse,
    NamespaceInfo,
    DocumentListResponse,
    DocumentInfo,
)

router = APIRouter()

# Global instances (in production, use proper dependency injection)
_llm_instance: LangChainLLM | None = None
_rag_instance: RAGServiceImpl | None = None


def get_llm() -> LangChainLLM:
    """
    Get or create the LLM instance.

    Returns:
        LangChainLLM instance.

    Raises:
        HTTPException: If LLM initialization fails.
    """
    global _llm_instance
    if _llm_instance is None:
        try:
            import os
            temperature = float(os.getenv("LLM_DEFAULT_TEMPERATURE", "0.7"))
            max_tokens = int(os.getenv("LLM_DEFAULT_MAX_TOKENS", "1000"))
            
            _llm_instance = LangChainLLM(
                temperature=temperature,
                max_tokens=max_tokens
            )
        except ValueError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to initialize LLM: {str(e)}"
            )
    return _llm_instance


def get_rag_service() -> RAGServiceImpl | None:
    """
    Get or create the RAG service instance.

    Returns None if RAG is disabled or initialization fails.

    Returns:
        RAGServiceImpl instance or None.
    """
    global _rag_instance
    if _rag_instance is None:
        try:
            import os
            from agentlab.config.rag_config import RAGConfig
            
            if not os.getenv("ENABLE_RAG", "true").lower() == "true":
                print("⚠️  RAG is disabled via ENABLE_RAG=false")
                return None
            
            try:
                config = RAGConfig.from_env()
                llm = get_llm()
                _rag_instance = RAGServiceImpl(llm=llm, config=config)
            except ValueError as e:
                print(f"⚠️  RAG service unavailable: {e}")
                return None
        except Exception as e:
            print(f"⚠️  RAG service initialization failed: {e}")
            return None
    return _rag_instance


class RAGQueryRequest(BaseModel):
    """Request model for RAG query endpoint."""

    query: str = Field(..., min_length=1, description="Query to search knowledge base")
    top_k: int = Field(5, ge=1, le=20, description="Number of documents to retrieve")
    namespace: str | None = Field(None, description="Optional namespace to search")


class RAGQueryResponse(BaseModel):
    """Response model for RAG query."""

    success: bool
    response: str
    sources: list[dict]
    error_message: str | None = None


class RAGAddDocumentsRequest(BaseModel):
    """Request model for adding documents to RAG."""

    documents: list[str] = Field(
        ..., min_length=1, description="List of document texts or file paths"
    )
    namespace: str | None = Field(
        None, description="Optional namespace for organization"
    )
    chunk_size: int = Field(
        1000, ge=100, le=4000, description="Maximum characters per chunk"
    )
    chunk_overlap: int = Field(
        200, ge=0, le=1000, description="Overlapping characters between chunks"
    )


class RAGAddDocumentsResponse(BaseModel):
    """Response model for document addition."""

    success: bool
    message: str
    documents_added: int


class RAGAddDirectoryRequest(BaseModel):
    """Request model for adding directory of documents."""

    directory: str = Field(..., description="Path to directory containing documents")
    namespace: str | None = Field(
        None, description="Optional namespace for organization"
    )
    recursive: bool = Field(True, description="Search subdirectories recursively")
    chunk_size: int = Field(
        1000, ge=100, le=4000, description="Maximum characters per chunk"
    )
    chunk_overlap: int = Field(
        200, ge=0, le=1000, description="Overlapping characters between chunks"
    )


class RAGDeleteNamespaceResponse(BaseModel):
    """Response model for namespace deletion."""

    success: bool
    namespace: str
    message: str


class RAGNamespaceStatsResponse(BaseModel):
    """Response model for namespace statistics."""

    success: bool
    namespace: str
    vector_count: int
    dimension: int
    exists: bool


@router.post("/query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest):
    """
    Query the RAG system with a question.

    Retrieves relevant documents from the knowledge base and generates
    an answer using the LLM with retrieved context.

    Args:
        request: RAG query request with question and parameters.

    Returns:
        Generated answer with source documents.

    Raises:
        HTTPException: If RAG service is not available or query fails.
    """
    try:
        rag_service = get_rag_service()
        if rag_service is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize RAG service. "
                "Please ensure Pinecone and OpenAI API keys are configured."
            )
        result = rag_service.query(
            query=request.query, 
            top_k=request.top_k, 
            namespace=request.namespace
        )

        return RAGQueryResponse(
            success=result.success,
            response=result.response,
            sources=result.sources,
            error_message=result.error_message,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"RAG query failed: {str(e)}"
        )


@router.post("/documents", response_model=RAGAddDocumentsResponse)
async def add_documents(request: RAGAddDocumentsRequest):
    """
    Add documents to the RAG knowledge base.

    Documents can be plain text strings or file paths. Supported file types
    depend on registered loaders (currently: .txt, .md, .log).

    Args:
        request: Document addition request with texts or paths.

    Returns:
        Success status and number of documents added.

    Raises:
        HTTPException: If document addition fails.
    """
    try:
        rag_service = get_rag_service()

        rag_service.add_documents(
            documents=request.documents,
            namespace=request.namespace,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )

        return RAGAddDocumentsResponse(
            success=True,
            message=f"Successfully added {len(request.documents)} documents",
            documents_added=len(request.documents),
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add documents: {str(e)}"
        )


@router.post("/directory", response_model=RAGAddDocumentsResponse)
async def add_directory(request: RAGAddDirectoryRequest):
    """
    Add all documents from a directory to the RAG knowledge base.

    Recursively searches directory for supported file types and adds them
    to the knowledge base with chunking and metadata.

    Args:
        request: Directory addition request with path and parameters.

    Returns:
        Success status and number of documents added.

    Raises:
        HTTPException: If directory doesn't exist or addition fails.
    """
    try:
        rag_service = get_rag_service()

        dir_path = Path(request.directory)
        if not dir_path.exists():
            raise HTTPException(
                status_code=404, detail=f"Directory not found: {request.directory}"
            )

        if not dir_path.is_dir():
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a directory: {request.directory}",
            )

        pattern = "**/*" if request.recursive else "*"
        files = [
            f
            for f in dir_path.glob(pattern)
            if f.is_file() and rag_service.loader_registry.supports(f)
        ]

        if not files:
            return RAGAddDocumentsResponse(
                success=True,
                message=f"No supported files found in {request.directory}",
                documents_added=0,
            )

        rag_service.add_documents_from_directory(
            directory=request.directory,
            namespace=request.namespace,
            recursive=request.recursive,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )

        return RAGAddDocumentsResponse(
            success=True,
            message=f"Successfully added {len(files)} documents from directory",
            documents_added=len(files),
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add directory: {str(e)}"
        )


@router.get("/namespace/{namespace}/stats", response_model=RAGNamespaceStatsResponse)
async def get_namespace_stats(namespace: str):
    """
    Get statistics for a specific RAG namespace.

    Retrieves information about the number of vectors (document chunks) stored
    in the namespace and other metadata. Useful for monitoring and debugging.

    Args:
        namespace: The namespace to get statistics for.

    Returns:
        Namespace statistics including vector count and dimension.

    Raises:
        HTTPException: If stats retrieval fails or RAG service unavailable.
    """
    try:
        rag_service = get_rag_service()
        if rag_service is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize RAG service. "
                "Please ensure Pinecone and OpenAI API keys are configured.",
            )

        if not namespace or namespace.strip() == "":
            raise HTTPException(
                status_code=400, detail="Namespace cannot be empty"
            )

        result = rag_service.get_namespace_stats(namespace)

        return RAGNamespaceStatsResponse(
            success=result["success"],
            namespace=result["namespace"],
            vector_count=result["vector_count"],
            dimension=result["dimension"],
            exists=result["exists"],
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats for namespace '{namespace}': {str(e)}",
        )


@router.delete("/namespace/{namespace}", response_model=RAGDeleteNamespaceResponse)
async def delete_namespace(namespace: str):
    """
    Delete all documents in a specific namespace.

    This endpoint removes all vectors and documents associated with a namespace
    in the Pinecone index. Useful for cleanup and testing.

    Args:
        namespace: The namespace to delete.

    Returns:
        Success status and deletion details.

    Raises:
        HTTPException: If namespace deletion fails or RAG service unavailable.
    """
    try:
        rag_service = get_rag_service()
        if rag_service is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize RAG service. "
                "Please ensure Pinecone and OpenAI API keys are configured.",
            )

        if not namespace or namespace.strip() == "":
            raise HTTPException(
                status_code=400, detail="Namespace cannot be empty"
            )

        result = rag_service.delete_namespace(namespace)

        return RAGDeleteNamespaceResponse(
            success=result["success"],
            namespace=result["namespace"],
            message=result["message"],
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete namespace '{namespace}': {str(e)}",
        )


@router.get("/namespaces", response_model=NamespaceListResponse)
async def list_rag_namespaces():
    """
    List all available RAG namespaces with document counts.
    
    Retrieves namespace information from both Pinecone vector store and MySQL database,
    providing comprehensive statistics including document counts, chunk counts, and
    last update timestamps.
    
    Returns:
        NamespaceListResponse with list of namespaces and their metadata.
        
    Raises:
        HTTPException: 500 if RAG service unavailable or query fails.
    """
    try:
        rag_service = get_rag_service()
        if rag_service is None:
            raise HTTPException(
                status_code=500,
                detail="RAG service not available. Ensure Pinecone is configured.",
            )
        
        namespaces_data = rag_service.list_namespaces()
        
        namespaces = [
            NamespaceInfo(
                name=ns["name"],
                document_count=ns["document_count"],
                total_chunks=ns["total_chunks"],
                last_updated=ns["last_updated"],
            )
            for ns in namespaces_data
        ]
        
        return NamespaceListResponse(namespaces=namespaces)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list namespaces: {str(e)}",
        )


@router.get("/documents", response_model=DocumentListResponse)
async def list_rag_documents(
    namespace: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    """
    List all RAG documents with metadata and optional namespace filter.
    
    Retrieves document information from the knowledge base database, including
    filenames, chunk counts, file sizes, and upload timestamps. Supports pagination
    for efficient handling of large document collections.
    
    Args:
        namespace: Optional namespace filter. Use "default" for empty namespace.
        limit: Maximum documents to return (1-1000). Default: 100.
        offset: Number of documents to skip for pagination. Default: 0.
        
    Returns:
        DocumentListResponse with paginated list of documents and metadata.
        
    Raises:
        HTTPException: 400 if limit out of range, 500 if database query fails.
    """
    try:
        rag_service = get_rag_service()
        if rag_service is None:
            raise HTTPException(
                status_code=500,
                detail="RAG service not available. Ensure database is configured.",
            )
        
        if not 1 <= limit <= 1000:
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 1000",
            )
        
        result = rag_service.list_documents(
            namespace=namespace,
            limit=limit,
            offset=offset,
        )
        
        documents = [
            DocumentInfo(
                id=doc["id"],
                filename=doc["filename"],
                namespace=doc["namespace"],
                chunk_count=doc["chunk_count"],
                uploaded_at=doc["uploaded_at"],
                file_size=doc["file_size"],
            )
            for doc in result["documents"]
        ]
        
        return DocumentListResponse(
            documents=documents,
            total_count=result["total_count"],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"],
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}",
        )