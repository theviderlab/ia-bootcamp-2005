# RAG System Guide

Complete guide to using the **Retrieval Augmented Generation (RAG)** system in Agent Lab, powered by Pinecone and LangChain.

## Quick Start

Get up and running with the RAG system in 5 minutes.

### 1. Install Dependencies

```bash
# Add required packages
uv add pinecone langchain-pinecone langchain-text-splitters

# Sync all dependencies
uv sync
```

### 2. Set Up Environment

Create `.env` file with your API keys:

```bash
# Required
OPENAI_API_KEY=sk-...                    # OpenAI API key for embeddings
PINECONE_API_KEY=pcsk_...                # Pinecone API key
PINECONE_INDEX_NAME=agent-lab-index      # Name for your Pinecone index
PINECONE_CLOUD=aws                       # Cloud provider (aws, gcp, azure)
PINECONE_REGION=us-east-1                # Region for serverless index
```

### 3. Run the Example

```bash
uv run python -m agentlab.examples.rag_example
```

This will initialize the RAG service, create the Pinecone index (if needed), add sample documents, and run example queries.

### 4. Try the API

Start the server:

```bash
make api
# or
uv run uvicorn agentlab.api.main:app --reload
```

Then use the API to add documents and query:

```bash
# Add documents from a directory
curl -X POST "http://localhost:8000/llm/rag/directory" \
  -H "Content-Type: application/json" \
  -d '{ "directory": "data/initial_knowledge", "recursive": true }'

# Query the knowledge base
curl -X POST "http://localhost:8000/llm/rag/query" \
  -H "Content-Type: application/json" \
  -d '{ "query": "What is Agent Lab?", "top_k": 5 }'
```

---

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

### Data Storage Architecture

The system uses a dual-storage approach for optimal performance:

| Storage | Purpose | Data Stored |
|---------|---------|-------------|
| **Pinecone** | Vector search | Document embeddings, chunk content, basic metadata |
| **MySQL** | Metadata & management | Document details, filenames, sizes, timestamps, namespace stats |

**Integration Points:**
- When adding documents: Store vectors in Pinecone + metadata in MySQL
- When querying: Search Pinecone for relevant chunks, optionally enrich with MySQL metadata
- When listing: Combine Pinecone namespace stats with MySQL document metadata

**Namespace Mapping:**
- Empty namespace (`""`) in database is displayed as `"default"` in API responses
- API accepts `"default"` and converts to `""` for database queries

## Implementation Details

The RAG system is built with a clean separation of concerns:

### Core Components

- **`src/agentlab/core/rag_service.py`**: The main `RAGServiceImpl` class. It handles:
    - Pinecone index initialization and management.
    - Embedding generation using `LangChain` and `OpenAI`.
    - Document retrieval and context building.
    - LLM response generation with augmented prompts.
- **`src/agentlab/agents/rag_processor.py`**: Low-level helper functions for:
    - `chunk_document`: Splitting text into overlapping chunks.
    - `generate_document_id`: Creating stable IDs for deduplication.
    - `preprocess_text`: Cleaning text before processing.
- **`src/agentlab/config/rag_config.py`**: Configuration management using Pydantic/Dataclasses to load settings from environment variables.

### Document Loading

- **`src/agentlab/loaders/`**: Extensible loader system.
    - `registry.py`: Manages supported file types.
    - `text_loader.py`: Handles `.txt`, `.md`, `.log` files.

### Key Features

1.  **Automatic Index Management**: The `ensure_index_exists()` method checks for the Pinecone index and creates it with the correct settings (Serverless, Cosine metric) if missing.
2.  **Namespace Isolation**: Supports multi-tenancy by allowing documents to be stored and queried within specific Pinecone namespaces.
3.  **Smart Chunking**: Uses `RecursiveCharacterTextSplitter` to respect sentence and paragraph boundaries.
4.  **Deduplication**: Generates deterministic IDs based on content hash to prevent duplicate entries when re-indexing.

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

### 4. Verify Installation

You can verify that the packages are installed and the system is working by running the unit tests:

```bash
# Check installed packages
uv pip list | grep -E "pinecone|langchain"

# Run unit tests
uv run pytest tests/unit/test_rag_processor.py -v
```

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

#### List Namespaces

Retrieve all available namespaces with document statistics:

```bash
curl -X GET "http://localhost:8000/llm/rag/namespaces"
```

Response:
```json
{
  "namespaces": [
    {
      "namespace": "default",
      "document_count": 15,
      "vector_count": 234,
      "last_updated": "2025-12-21T10:30:00"
    },
    {
      "namespace": "project-a",
      "document_count": 8,
      "vector_count": 156,
      "last_updated": "2025-12-20T15:45:00"
    }
  ]
}
```

#### List Documents

Retrieve documents with pagination and optional namespace filtering:

```bash
# List all documents (paginated)
curl -X GET "http://localhost:8000/llm/rag/documents?limit=100&offset=0"

# Filter by namespace
curl -X GET "http://localhost:8000/llm/rag/documents?namespace=project-a&limit=50"
```

Response:
```json
{
  "documents": [
    {
      "doc_id": "abc123...",
      "filename": "sample_docs.txt",
      "namespace": "default",
      "total_chunks": 5,
      "total_size": 4567,
      "created_at": "2025-12-21T10:30:00"
    }
  ],
  "total_count": 150,
  "limit": 100,
  "offset": 0,
  "has_more": true
}
```

**Query Parameters:**
- `namespace` (optional): Filter by namespace (use "default" for default namespace)
- `limit` (optional): Number of documents per page (1-1000, default: 100)
- `offset` (optional): Starting position (default: 0)

---

## Namespace Strategy for Playground/Testing

For small projects (3-10 documents), using **1 namespace per document** is perfectly valid and recommended:

### Pattern: 1 Namespace = 1 Document

```python
# ✅ Recommended for playground (<10 documents)
documents = [
    ("data/docs/fastapi_intro.md", "doc-fastapi-intro"),
    ("data/docs/python_guide.md", "doc-python-guide"),
    ("data/docs/testing_best.md", "doc-testing-best"),
]

for file_path, namespace in documents:
    rag_service.add_documents(
        documents=[Path(file_path)],
        namespace=namespace  # Unique namespace per document
    )
```

**Advantages for small projects:**
- ✅ Perfect granular selection (each document is a namespace)
- ✅ Easy to manage in UI (each toggle = one document)
- ✅ No complexity overhead for 3-4 documents
- ✅ Clear and clean organization
- ✅ Simple implementation in frontend

**When to use this pattern:**
- Learning/playground projects
- Less than 10 documents
- Testing and development
- Rapid prototyping
- Individual file-level control needed

**When NOT to use this pattern:**
- Production with hundreds of documents
- Multiple projects sharing same index
- Need to group documents by category
- Scaling beyond 50+ documents

### Complete Example for Playground

```python
# Playground initialization script
from pathlib import Path
from agentlab.core.rag_service import RAGServiceImpl
from agentlab.core.llm_interface import LangChainLLM

# Setup
llm = LangChainLLM()
rag_service = RAGServiceImpl(llm=llm)

# Playground documents (1 namespace per document)
playground_docs = {
    "fastapi-intro": "data/docs/fastapi_intro.md",
    "python-guide": "data/docs/python_guide.md",
    "testing-tips": "data/docs/testing_best_practices.md",
}

# Load each document in its own namespace
for namespace, filepath in playground_docs.items():
    print(f"Loading {filepath} into namespace '{namespace}'...")
    rag_service.add_documents(
        documents=[Path(filepath)],
        namespace=namespace
    )

print(f"✅ {len(playground_docs)} documents loaded in separate namespaces")
```

### API Usage for Playground

```bash
# Load individual document in its namespace
curl -X POST "http://localhost:8000/llm/rag/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": ["data/docs/fastapi_intro.md"],
    "namespace": "fastapi-intro"
  }'

# Chat with specific documents selected
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Explain FastAPI"}],
    "use_rag": true,
    "rag_namespaces": ["fastapi-intro", "python-guide"],
    "rag_top_k": 5
  }'
```

**UI Implementation:**
- Each document appears as a separate checkbox in the RAG sidebar
- Selecting/deselecting a document = adding/removing its namespace
- Multiple documents can be selected simultaneously
- Chat endpoint receives array of selected namespaces

### Comparison: Playground vs Production

| Aspect | Playground (1 doc = 1 NS) | Production (Grouped NS) |
|--------|---------------------------|-------------------------|
| **Documents** | 3-10 | 100+ |
| **Namespaces** | One per document | Category-based |
| **UI Control** | Per-file checkboxes | Category toggles |
| **Scalability** | Limited to ~50 docs | Unlimited |
| **Management** | Very simple | Requires planning |
| **Use Case** | Learning, testing | Production systems |

**Example Production Strategy (for comparison):**
```python
# ❌ NOT for your playground (requires many documents)
namespaces = {
    "product-docs": ["intro.md", "api.md", "guide.md", ...],  # 50 docs
    "legal": ["tos.md", "privacy.md", ...],                   # 20 docs
    "support": ["faq.md", "troubleshooting.md", ...]          # 30 docs
}
```

---

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

### 6. Document Management

- **List before querying**: Use GET /rag/namespaces to see available namespaces
- **Pagination**: When listing documents, use reasonable limit values (50-100)
- **Namespace filtering**: Filter documents by namespace to reduce response size
- **Monitor statistics**: Check document_count and vector_count to track growth

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

### Issue: Dependency Conflicts or Import Errors

If you encounter version conflicts or import errors:

```bash
# Update the lockfile
uv lock --upgrade

# Sync dependencies
uv sync
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
- `GET /llm/rag/namespaces` - List all namespaces with statistics
- `GET /llm/rag/documents` - List documents with pagination

See interactive docs at http://localhost:8000/docs when API is running.
