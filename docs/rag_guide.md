# RAG System Guide

Complete guide to using the **Retrieval Augmented Generation (RAG)** system in Agent Lab, powered by Pinecone and LangChain.

## Overview

The RAG system enhances LLM responses by retrieving relevant information from a knowledge base before generating answers. This allows the LLM to:

- Answer questions based on your custom documents
- Provide factual information from your knowledge base
- Cite sources for transparency
- Handle domain-specific queries with accuracy

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      RAG Query Flow                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. User Query                                              │
│      ↓                                                      │
│  2. Text Preprocessing → Embedding Generation               │
│      ↓                                                      │
│  3. Pinecone Vector Search (Similarity)                     │
│      ↓                                                      │
│  4. Retrieve Top-K Documents                                │
│      ↓                                                      │
│  5. Build Augmented Prompt (Query + Context)                │
│      ↓                                                      │
│  6. LLM Generation                                          │
│      ↓                                                      │
│  7. Response + Sources                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Setup

### 1. Install Dependencies

```bash
# Add Pinecone and LangChain packages
uv add pinecone langchain-pinecone langchain-text-splitters

# Or sync existing dependencies
uv sync
```

### 2. Configure Environment Variables

Create or update your `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-...                    # OpenAI API key for embeddings
PINECONE_API_KEY=pcsk_...                # Pinecone API key
PINECONE_INDEX_NAME=agent-lab-index      # Name for your Pinecone index
PINECONE_CLOUD=aws                       # Cloud provider (aws, gcp, azure)
PINECONE_REGION=us-east-1                # Region for serverless index

# Optional
PINECONE_DIMENSION=1536                  # Vector dimension (default: 1536)
PINECONE_METRIC=cosine                   # Distance metric (default: cosine)
PINECONE_NAMESPACE=default               # Default namespace (optional)
```

### 3. Get API Keys

**Pinecone:**
1. Sign up at [pinecone.io](https://www.pinecone.io/)
2. Create a new project
3. Get your API key from the dashboard
4. Note your cloud provider and region

**OpenAI:**
1. Sign up at [platform.openai.com](https://platform.openai.com/)
2. Generate an API key in Settings → API Keys

## Usage

### Python API

#### Basic RAG Query

```python
from agentlab.core.llm_interface import LangChainLLM
from agentlab.core.rag_service import RAGServiceImpl
from agentlab.config.rag_config import RAGConfig

# Initialize LLM and RAG service
llm = LangChainLLM()
rag_service = RAGServiceImpl(llm=llm)

# Query the knowledge base
result = rag_service.query(
    query="What is Agent Lab?",
    top_k=5  # Retrieve top 5 relevant documents
)

if result.success:
    print(f"Answer: {result.response}")
    print(f"\nSources ({len(result.sources)}):")
    for source in result.sources:
        print(f"  - {source['source']} (chunk {source['chunk']})")
else:
    print(f"Error: {result.error_message}")
```

#### Add Documents

**From Text:**
```python
documents = [
    "Agent Lab is a learning platform for LLMs and RAG systems.",
    "It uses Pinecone for vector storage and LangChain for embeddings.",
]

rag_service.add_documents(documents)
```

**From Files:**
```python
from pathlib import Path

# Single file
rag_service.add_documents(
    documents=[Path("data/initial_knowledge/sample_docs.txt")]
)

# Multiple files
files = [
    Path("docs/guide1.txt"),
    Path("docs/guide2.md"),
]
rag_service.add_documents(documents=files)
```

**From Directory:**
```python
rag_service.add_documents_from_directory(
    directory="data/initial_knowledge",
    recursive=True,  # Search subdirectories
    chunk_size=1000,
    chunk_overlap=200
)
```

#### Multi-Tenant Support with Namespaces

Use namespaces to isolate documents for different users, projects, or use cases:

```python
# Add documents to a namespace
rag_service.add_documents(
    documents=["Project A documentation..."],
    namespace="project-a"
)

# Query within a specific namespace
result = rag_service.query(
    query="What is the API endpoint?",
    namespace="project-a"
)
```

#### Custom Configuration

```python
from agentlab.config.rag_config import RAGConfig

# Create custom config
config = RAGConfig(
    pinecone_api_key="your-key",
    index_name="custom-index",
    cloud="aws",
    region="us-west-2",
    openai_api_key="your-key",
    dimension=1536,
    metric="cosine",
    namespace="production"
)

# Initialize with custom config
rag_service = RAGServiceImpl(llm=llm, config=config)
```

### REST API

#### Start the API Server

```bash
# Using Make
make api

# Or directly with uvicorn
uv run uvicorn agentlab.api.main:app --reload

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

#### Query RAG System

```bash
curl -X POST "http://localhost:8000/llm/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Agent Lab?",
    "top_k": 5,
    "namespace": null
  }'
```

Response:
```json
{
  "success": true,
  "response": "Agent Lab is a modern Python learning platform...",
  "sources": [
    {
      "source": "sample_docs.txt",
      "chunk": 0,
      "created_at": "2025-12-14T10:30:00",
      "content_preview": "Agent Lab is designed for..."
    }
  ],
  "error_message": null
}
```

#### Add Documents

```bash
curl -X POST "http://localhost:8000/llm/rag/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "New documentation content here...",
      "data/initial_knowledge/sample_docs.txt"
    ],
    "namespace": "my-project",
    "chunk_size": 1000,
    "chunk_overlap": 200
  }'
```

#### Add Directory

```bash
curl -X POST "http://localhost:8000/llm/rag/directory" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "data/initial_knowledge",
    "namespace": null,
    "recursive": true,
    "chunk_size": 1000,
    "chunk_overlap": 200
  }'
```

## Features

### Document Chunking

Documents are automatically split into manageable chunks with metadata:

- **Chunk Size**: Maximum characters per chunk (default: 1000)
- **Overlap**: Characters shared between consecutive chunks (default: 200)
- **Smart Splitting**: Uses `RecursiveCharacterTextSplitter` to split on:
  - Paragraph boundaries (`\n\n`)
  - Line breaks (`\n`)
  - Sentence endings (`. `)
  - Spaces
  - Characters (last resort)

### Metadata Tracking

Each chunk includes metadata:

```python
{
    "source": "document_name.txt",      # Original file name
    "chunk": 0,                         # Chunk index
    "created_at": "2025-12-14T10:30:00",  # ISO timestamp
    "total_chunks": 5                   # Total chunks from document
}
```

### Automatic Index Management

The RAG service automatically:
- Creates Pinecone index if it doesn't exist
- Configures with optimal settings (dimension=1536, metric=cosine)
- Uses serverless deployment for cost efficiency
- Checks index existence before operations

### Document Deduplication

Uses stable document IDs based on content hash:
- Same content → same ID → upsert (update existing)
- Different content → different ID → new document
- Prevents duplicate documents in the knowledge base

## Supported File Formats

### Currently Supported

- **Plain Text**: `.txt`, `.text`
- **Markdown**: `.md`, `.markdown`
- **Logs**: `.log`

### Adding New Formats

The system uses a loader registry pattern for easy extension:

#### Example: PDF Loader

```python
from pathlib import Path
from PyPDF2 import PdfReader

class PDFLoader:
    """Loader for PDF files."""
    
    SUPPORTED_EXTENSIONS = {".pdf"}
    
    def load(self, file_path: str | Path) -> str:
        """Load PDF content."""
        path = Path(file_path)
        reader = PdfReader(path)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        return text
    
    def supports(self, file_path: str | Path) -> bool:
        """Check if PDF file."""
        return Path(file_path).suffix.lower() in self.SUPPORTED_EXTENSIONS

# Register the loader
rag_service.loader_registry.register(PDFLoader())

# Now PDF files are supported
rag_service.add_documents([Path("document.pdf")])
```

## Configuration Options

### RAGConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pinecone_api_key` | str | Required | Pinecone API key |
| `index_name` | str | Required | Name of Pinecone index |
| `cloud` | str | Required | Cloud provider (aws, gcp, azure) |
| `region` | str | Required | Cloud region |
| `openai_api_key` | str | Required | OpenAI API key |
| `dimension` | int | 1536 | Vector dimension |
| `metric` | str | "cosine" | Distance metric |
| `namespace` | str | None | Default namespace |

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | str | Required | Question to ask |
| `top_k` | int | 5 | Number of documents to retrieve |
| `namespace` | str | None | Namespace to search in |

### Document Addition Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `documents` | list | Required | List of texts or file paths |
| `namespace` | str | None | Namespace for organization |
| `chunk_size` | int | 1000 | Maximum characters per chunk |
| `chunk_overlap` | int | 200 | Overlapping characters |

## Best Practices

### 1. Chunk Size Selection

- **Small chunks (500-1000 chars)**: Better for precise retrieval, specific facts
- **Large chunks (2000-3000 chars)**: Better for context, broader topics
- **Overlap**: Use 10-20% of chunk_size for continuity

### 2. Namespace Strategy

- **Per-user**: Isolate data for each user
- **Per-project**: Separate documents by project
- **Per-environment**: dev, staging, production
- **Default**: Use default namespace for shared knowledge

### 3. Query Optimization

- **Use descriptive queries**: "What are the API endpoints for chat?" vs "API?"
- **Adjust top_k**: Start with 5, increase if context is insufficient
- **Preprocess queries**: Clean up typos, expand acronyms

### 4. Document Preparation

- **Clean text**: Remove formatting artifacts, headers/footers
- **Structure**: Use clear headings, paragraphs
- **Metadata**: Include source information in filenames
- **Format**: Prefer markdown for structured content

### 5. Cost Management

- **Pinecone**: Serverless indexes scale to zero when not in use
- **OpenAI**: Embeddings cost ~$0.0001 per 1K tokens
- **Batch operations**: Add multiple documents at once
- **Namespace limits**: Use namespaces to limit search scope

## Troubleshooting

### Issue: "Missing required environment variables"

**Solution**: Ensure all required variables are set in `.env`:
```bash
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_NAME=agent-lab-index
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
```

### Issue: "Failed to initialize RAG service"

**Causes:**
1. Invalid API keys
2. Network connectivity issues
3. Pinecone service unavailable

**Solution:**
```bash
# Test Pinecone connection
python -c "from pinecone import Pinecone; pc = Pinecone(api_key='your-key'); print(pc.list_indexes())"

# Test OpenAI connection
python -c "from langchain_openai import OpenAIEmbeddings; emb = OpenAIEmbeddings(); print(emb.embed_query('test'))"
```

### Issue: "No documents found" when querying

**Causes:**
1. Documents not added to correct namespace
2. Query too specific or unrelated to content
3. Index recently created (needs time to sync)

**Solution:**
```python
# Check index stats
from pinecone import Pinecone
pc = Pinecone(api_key="your-key")
index = pc.Index("agent-lab-index")
print(index.describe_index_stats())

# Try broader query or different namespace
result = rag_service.query("general topic", namespace=None)
```

### Issue: "File type not supported"

**Solution**: Register a loader for the file type (see "Adding New Formats" above) or convert to supported format:

```bash
# Convert PDF to text
pdftotext document.pdf document.txt

# Convert HTML to markdown
pandoc document.html -o document.md
```

## Examples

### Example 1: Build Documentation Q&A

```python
# Add your project docs
rag_service.add_documents_from_directory(
    directory="docs/",
    namespace="project-docs",
    recursive=True
)

# Query the docs
result = rag_service.query(
    query="How do I authenticate API requests?",
    namespace="project-docs",
    top_k=3
)

print(result.response)
```

### Example 2: Multi-User Knowledge Base

```python
# Add documents for different users
rag_service.add_documents(
    documents=["User A's private notes..."],
    namespace="user-a"
)

rag_service.add_documents(
    documents=["User B's private notes..."],
    namespace="user-b"
)

# Query isolated by user
result_a = rag_service.query("my notes", namespace="user-a")
result_b = rag_service.query("my notes", namespace="user-b")
```

### Example 3: Incremental Updates

```python
# Initial load
rag_service.add_documents_from_directory("data/v1/")

# Later: Add new documents (won't duplicate existing)
rag_service.add_documents_from_directory("data/v2/")

# Documents with same content have same IDs → upsert behavior
```

## Performance Considerations

### Embedding Generation

- **Rate**: ~1000 tokens/sec with OpenAI
- **Batch size**: Process 20-50 documents at once
- **Caching**: Embeddings are cached in Pinecone

### Vector Search

- **Latency**: <100ms for typical queries
- **Scalability**: Millions of vectors supported
- **Filtering**: Use namespaces for efficient filtering

### Recommended Limits

- **Chunk size**: 500-2000 characters
- **Documents per batch**: 50-100
- **Top-K retrieval**: 3-10 documents
- **Context length**: Keep under LLM token limits

## Next Steps

1. **Add your documents**: Start with `data/initial_knowledge/`
2. **Test queries**: Use the API or Python interface
3. **Tune parameters**: Adjust chunk_size and top_k
4. **Add file types**: Implement loaders for PDF, HTML, etc.
5. **Monitor usage**: Track Pinecone and OpenAI API usage

## Resources

- [Pinecone Documentation](https://docs.pinecone.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)

## API Reference

### RAGServiceImpl

Full API documentation: [docs/api_endpoints.md](api_endpoints.md)

Key methods:
- `query(query, top_k, namespace)` - Query knowledge base
- `add_documents(documents, namespace, chunk_size, chunk_overlap)` - Add documents
- `add_documents_from_directory(directory, namespace, recursive)` - Bulk add
- `ensure_index_exists()` - Create/verify Pinecone index

### REST Endpoints

- `POST /llm/rag/query` - Query RAG system
- `POST /llm/rag/documents` - Add documents
- `POST /llm/rag/directory` - Add directory of documents

See interactive docs at http://localhost:8000/docs when API is running.
