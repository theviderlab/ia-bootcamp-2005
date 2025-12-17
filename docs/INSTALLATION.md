# Installation Instructions for RAG System

## Required Steps

### 1. Install New Dependencies

The RAG implementation requires additional packages. Install them with:

```bash
# Navigate to project directory
cd c:\Users\rdiaz\Documents\GitHub\ia-bootcamp-2005

# Add Pinecone and LangChain packages
uv add pinecone
uv add langchain-pinecone
uv add langchain-text-splitters

# Sync all dependencies
uv sync
```

### 2. Verify Installation

Check that packages were installed:

```bash
uv pip list | grep -E "pinecone|langchain"
```

You should see:
- pinecone
- langchain-pinecone
- langchain-text-splitters
- langchain-openai (already installed)
- langchain-core (already installed)

### 3. Configure Environment

Update your `.env` file with Pinecone credentials:

```bash
# Add these lines to .env
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=agent-lab-index
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
```

### 4. Get Pinecone API Key

1. Go to https://www.pinecone.io/
2. Sign up for a free account
3. Create a new project
4. Get your API key from the dashboard
5. Note the cloud provider and region

### 5. Test Installation

Run the unit tests to verify everything is set up correctly:

```bash
# Run RAG processor tests (no API calls needed)
uv run pytest tests/unit/test_rag_processor.py -v
```

### 6. Test RAG System

Run the example script:

```bash
# Make sure environment variables are set
uv run python -m agentlab.examples.rag_example
```

## Dependency Versions

The following versions are recommended:

```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "pinecone>=3.0.0",
    "langchain-pinecone>=0.1.0",
    "langchain-text-splitters>=0.0.1",
]
```

These will be added automatically by `uv add`.

## Troubleshooting

### Import Errors

If you see import errors for `pinecone` or `langchain_pinecone`:

```bash
# Reinstall packages
uv pip uninstall pinecone langchain-pinecone
uv add pinecone langchain-pinecone
uv sync
```

### Version Conflicts

If you encounter version conflicts:

```bash
# Update the lockfile
uv lock --upgrade

# Sync with new lockfile
uv sync
```

### Pinecone Connection Issues

Test your Pinecone connection:

```python
from pinecone import Pinecone
import os

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
print(pc.list_indexes())
```

## Next Steps

After successful installation:

1. Read the Quick Start Guide: `docs/RAG_QUICKSTART.md`
2. Read the Full Guide: `docs/rag_guide.md`
3. Run the example: `uv run python -m agentlab.examples.rag_example`
4. Start the API: `make api`
5. Test the endpoints: http://localhost:8000/docs

## Files Changed

Summary of implementation files:

```
src/agentlab/
├── config/
│   ├── __init__.py (new)
│   └── rag_config.py (new)
├── core/
│   └── rag_service.py (updated - fully implemented)
├── agents/
│   └── rag_processor.py (updated - fully implemented)
├── loaders/
│   ├── __init__.py (new)
│   ├── text_loader.py (new)
│   └── registry.py (new)
├── api/routes/
│   └── chat_routes.py (updated - added RAG endpoints)
├── examples/
│   ├── __init__.py (new)
│   └── rag_example.py (new)
└── models.py (updated - added DocumentLoader protocol)

tests/unit/
└── test_rag_processor.py (new)

docs/
├── rag_guide.md (new)
├── RAG_QUICKSTART.md (new)
└── RAG_IMPLEMENTATION_SUMMARY.md (new)

.env.example (updated - added Pinecone vars)
README.md (updated - added RAG section)
```

## Support

If you encounter issues:

1. Check the troubleshooting sections in `docs/rag_guide.md`
2. Verify all environment variables are set
3. Ensure API keys are valid
4. Check Pinecone dashboard for index status
