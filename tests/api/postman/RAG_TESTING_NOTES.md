# RAG Testing Notes - Postman Collection

## 📋 Overview

This document explains the approach for testing RAG endpoints with Postman, addressing common issues with file paths and fixtures.

## 🔧 Issues Fixed

### 1. **Add Multiple Documents from Fixtures** ✅

**Previous Problem:**
- Test was sending file paths like `"{{fixtures_path}}\\sample_doc_1.txt"`
- API received paths as strings but couldn't access them (client-side paths)
- Created embeddings of the path string instead of document content

**Solution:**
- Changed to send **actual document content** as text strings
- Documents are now embedded directly in the request body
- No dependency on server-side file access

**Example:**
```json
{
  "documents": [
    "Python Programming Best Practices\n\nPython is a high-level...",
    "# FastAPI Framework Overview\n\nFastAPI is a modern..."
  ],
  "namespace": "postman-test",
  "chunk_size": 800,
  "chunk_overlap": 150
}
```

### 2. **Add Directory (Initial Knowledge)** ✅

**Previous Problem:**
- Test was sending `"{{fixtures_path}}"` which points to client machine
- Server couldn't access client-side directories
- Test would fail with "Directory not found"

**Solution:**
- Changed to use **server-side directory**: `"data/initial_knowledge"`
- This directory exists in the project structure and is accessible by the backend
- Test now gracefully handles empty directories (returns 0 documents added)

**Example:**
```json
{
  "directory": "data/initial_knowledge",
  "namespace": "postman-test",
  "recursive": true,
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

## 🎯 Best Practices for RAG Testing

### When to Use Each Endpoint

| Endpoint | Use Case | Example |
|----------|----------|---------|
| `POST /llm/rag/documents` | Send text content or server-accessible file paths | Testing with fixtures, quick document addition |
| `POST /llm/rag/directory` | Bulk load from server-side directory | Initial knowledge base setup, production data loading |

### Testing with Fixtures

**❌ Don't:**
```json
{
  "documents": ["C:\\Users\\...\\fixtures\\doc.txt"]  // Client path
}
```

**✅ Do:**
```json
{
  "documents": ["Full document content here..."]  // Actual content
}
```

### Testing with Server Files

**❌ Don't:**
```json
{
  "directory": "C:\\Users\\...\\fixtures"  // Client path
}
```

**✅ Do:**
```json
{
  "directory": "data/initial_knowledge"  // Server-relative path
}
```

## 📝 API Behavior Clarification

### `/llm/rag/documents` Endpoint

The API accepts a list of `documents` which can be:

1. **Text strings** - Direct document content
   ```json
   {"documents": ["This is my document content..."]}
   ```

2. **Server-accessible file paths** - Files the backend can read
   ```json
   {"documents": ["./data/myfile.txt", "/app/data/doc.md"]}
   ```

**Logic:**
```python
for doc in documents:
    path = Path(doc)
    if path.exists():  # Check if it's a valid file
        content = load_file(path)
    else:
        content = doc  # Treat as text content
```

### `/llm/rag/directory` Endpoint

- Expects a **server-accessible directory path**
- Recursively finds all supported files (.txt, .md, .log)
- Cannot access client-side directories
- Must be a path the FastAPI server can resolve

**Supported paths:**
- Relative to server CWD: `"data/initial_knowledge"`
- Absolute server paths: `"/app/data/documents"`
- Project-relative: `"./data/examples"`

**Not supported:**
- Client-side paths from Postman environment variables
- Windows paths when server runs on Linux/Docker
- Network drives or remote file systems

## 🔄 Migration Guide

If you have existing tests using file paths:

### Before:
```json
{
  "documents": [
    "{{fixtures_path}}\\sample_doc_1.txt",
    "{{fixtures_path}}\\sample_doc_2.md"
  ]
}
```

### After (Option 1 - Recommended for Postman):
```json
{
  "documents": [
    "Full content of sample_doc_1...",
    "Full content of sample_doc_2..."
  ]
}
```

### After (Option 2 - If server has access):
```json
{
  "documents": [
    "tests/api/fixtures/sample_doc_1.txt",
    "tests/api/fixtures/sample_doc_2.md"
  ]
}
```

## 🧪 Running the Tests

### Prerequisites
1. Server running at `http://localhost:8000`
2. Valid `OPENAI_API_KEY` and `PINECONE_API_KEY` in environment
3. `data/initial_knowledge/` directory exists (can be empty)

### Execution Order
1. **Health & Connectivity** - Verify server is up
2. **LLM Basic Operations** - Test text generation
3. **Chat Operations** - Test conversation handling
4. **RAG - Setup** - Add documents (includes our fixed tests)
5. **RAG - Query Operations** - Query the knowledge base
6. **Error Scenarios** - Test error handling
7. **Cleanup** - Remove test data

### Expected Behavior

**Add Multiple Documents from Fixtures:**
- ✅ Should succeed immediately
- ✅ Adds 2 documents (Python and FastAPI content)
- ✅ No dependency on file system

**Add Directory (Initial Knowledge):**
- ✅ Should succeed even if directory is empty
- ✅ Returns `documents_added: 0` if no files found
- ✅ Returns `documents_added: N` if files exist

## 🐛 Troubleshooting

### "Directory not found" error
**Cause:** Directory path is not accessible by the server

**Solutions:**
1. Use server-relative paths: `"data/initial_knowledge"`
2. Ensure directory exists in server's file system
3. Check Docker volume mounts if using containers

### Embeddings of file paths instead of content
**Cause:** API received path as string but file doesn't exist

**Solutions:**
1. Send content directly in request body (recommended for Postman)
2. Use server-accessible paths if files exist on server

### "No documents added" but expected files
**Cause:** Files might not have supported extensions

**Supported extensions:**
- `.txt` - Plain text
- `.md` - Markdown
- `.log` - Log files

**Check:**
```python
# In rag_service.py
self.loader_registry.supports(file_path)
```

## 🎓 Key Takeaways

1. **Postman tests cannot send file paths** from client machine - use content instead
2. **Directory endpoint requires server access** - use project-relative paths
3. **Test gracefully handles missing files** - returns success with 0 documents
4. **fixtures_path variable is still useful** - for documentation and reference
5. **Separation of concerns** - Fixtures test = content, Directory test = server files

## 📚 Related Documentation

- [API Endpoints Documentation](../../docs/api_endpoints.md)
- [RAG Implementation Guide](../../docs/rag_guide.md)
- [Postman Quick Start](../QUICKSTART.md)
- [Newman CLI Guide](../NEWMAN_GUIDE.md)
