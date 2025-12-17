# RAG Quick Start Guide

Get up and running with the RAG system in 5 minutes.

## 1. Install Dependencies

```bash
cd ia-bootcamp-2005

# Add required packages
uv add pinecone langchain-pinecone langchain-text-splitters

# Sync all dependencies
uv sync
```

## 2. Set Up Environment

Create `.env` file with your API keys:

```bash
# Copy template
cp .env.example .env

# Edit .env and add:
OPENAI_API_KEY=sk-your-openai-key-here
PINECONE_API_KEY=pcsk_your-pinecone-key-here
PINECONE_INDEX_NAME=agent-lab-index
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Pinecone: https://www.pinecone.io/ (free tier available)

## 3. Add Your Documents

Put text files in `data/initial_knowledge/`:

```bash
# Example: Create a sample document
echo "Agent Lab is a learning platform for AI." > data/initial_knowledge/about.txt
```

## 4. Run the Example

```bash
uv run python -m agentlab.examples.rag_example
```

This will:
- Initialize the RAG service
- Create Pinecone index (if needed)
- Add documents to the knowledge base
- Run example queries
- Demonstrate namespace isolation

## 5. Try the API

Start the server:

```bash
make api
# or
uv run uvicorn agentlab.api.main:app --reload
```

Open http://localhost:8000/docs for interactive API documentation.

**Add documents via API:**

```bash
curl -X POST "http://localhost:8000/llm/rag/directory" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "data/initial_knowledge",
    "recursive": true
  }'
```

**Query the knowledge base:**

```bash
curl -X POST "http://localhost:8000/llm/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Agent Lab?",
    "top_k": 5
  }'
```

## 6. Use in Your Code

```python
from agentlab.core.llm_interface import LangChainLLM
from agentlab.core.rag_service import RAGServiceImpl

# Initialize
llm = LangChainLLM()
rag = RAGServiceImpl(llm=llm)

# Add documents
rag.add_documents([
    "Your document content here...",
    "More content..."
])

# Or from files
rag.add_documents_from_directory("data/initial_knowledge")

# Query
result = rag.query("Your question here?", top_k=5)

if result.success:
    print(f"Answer: {result.response}")
    print(f"Sources: {len(result.sources)}")
else:
    print(f"Error: {result.error_message}")
```

## Troubleshooting

**"Missing required environment variables"**
- Check your `.env` file has all required keys
- Make sure `.env` is in project root

**"Failed to initialize RAG service"**
- Verify API keys are valid
- Check internet connection
- For Pinecone: ensure you're using correct cloud/region

**"No documents found"**
- Add documents first with `add_documents()`
- Check correct namespace is being used
- Wait a few seconds after adding documents

## Next Steps

- Read the full guide: [docs/rag_guide.md](rag_guide.md)
- Explore API docs: http://localhost:8000/docs
- Add more document types (PDF, HTML, etc.)
- Use namespaces for multi-tenant apps
- Integrate into your application

## Common Tasks

**Add documents from directory:**
```python
rag.add_documents_from_directory(
    directory="path/to/docs",
    namespace="my-project",
    recursive=True
)
```

**Query with namespace:**
```python
result = rag.query(
    query="How do I authenticate?",
    namespace="my-project",
    top_k=3
)
```

**Check sources:**
```python
for source in result.sources:
    print(f"{source['source']}: {source['content_preview']}")
```

## Resources

- Full Documentation: [docs/rag_guide.md](rag_guide.md)
- API Reference: http://localhost:8000/docs
- Pinecone Docs: https://docs.pinecone.io/
- LangChain Docs: https://python.langchain.com/

Happy RAG building! 🚀
