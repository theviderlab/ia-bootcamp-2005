# Data Directory

This directory contains static files and initial data for the Agent Lab application.

## Structure

```
data/
├── initial_knowledge/    # Initial documents for RAG knowledge base
│   └── sample_docs.txt
├── examples/            # Example queries and responses
└── configs/             # Configuration files
```

## Purpose

### initial_knowledge/
Store text files, PDFs, or other documents that will be loaded into the RAG knowledge base during initialization.

**Supported formats:**
- `.txt` - Plain text files
- `.md` - Markdown files
- `.pdf` - PDF documents (will require additional parsing)
- `.json` - Structured data

### examples/
Example queries and expected responses for testing and demonstration purposes.

### configs/
Configuration files for different environments (development, staging, production).

## Usage

### Adding Knowledge Base Documents

1. Place your documents in `initial_knowledge/`
2. Run the database setup script (to be implemented):
   ```bash
   make setup-db
   ```

### Loading Documents via API

Documents can also be uploaded through the API:
```python
POST /api/chat/rag/documents
{
    "documents": ["Document content here..."]
}
```

## Git Ignore

Add large files or sensitive data to `.gitignore`:
```
data/initial_knowledge/*.pdf
data/configs/production.json
```
