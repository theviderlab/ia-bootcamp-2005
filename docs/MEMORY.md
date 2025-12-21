# Memory Module Guide

## Overview

The Agent Lab memory module provides a comprehensive conversation memory system with both **short-term** and **long-term** memory capabilities. Built on **LangGraph** and **LangChain** with hybrid storage (MySQL + Pinecone), it supports multiple memory types:

- **Short-term Memory**: Recent conversation buffer using LangGraph state management
- **Semantic Memory**: Facts and knowledge extracted from conversations (hybrid storage)
- **Episodic Memory**: Temporal summaries of conversation episodes
- **Profile Memory**: Aggregated user characteristics and preferences
- **Procedural Memory**: Identified interaction patterns and workflows

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    IntegratedMemoryService                          │
│  (Unified interface combining short-term and long-term memory)      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────┐  ┌───────────────────────────────┐ │
│  │  ShortTermMemoryService    │  │  LongTermMemoryProcessor      │ │
│  │                            │  │                               │ │
│  │  - Buffer Memory           │  │  - Semantic Extraction        │ │
│  │  - Window Memory           │  │  - Profile Building           │ │
│  │  - Summary Memory          │  │  - Episodic Summarization     │ │
│  │                            │  │  - Pattern Recognition        │ │
│  │  Backend: MySQL + SQLite   │  │  Backend: MySQL + Pinecone    │ │
│  └────────────────────────────┘  └───────────────────────────────┘ │
│                                                                      │
│  Storage Layer:                                                      │
│  - MySQL (chat_history table) - Structured conversation data        │
│  - SQLite (checkpoints) - Session state persistence                 │
│  - Pinecone (optional) - Semantic embeddings for fast similarity    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **IntegratedMemoryService**: Unified interface combining short-term and long-term memory.
2. **ShortTermMemoryService**: Manages conversation state using LangGraph.
   - **Buffer**: Full history in memory.
   - **Window**: Sliding window of messages.
   - **Summary**: LLM-generated summaries of older context.
   - **Storage**: MySQL for source of truth, SQLite for state checkpoints.
3. **LongTermMemoryProcessor**: Background processor for extracting insights.
   - **Semantic**: Fact extraction and vector storage.
   - **Profile**: User attribute aggregation.
   - **Episodic**: Chronological summarization.
   - **Procedural**: Pattern detection.
   - **Storage**: MySQL for structured data, Pinecone for embeddings.

## Key Design Decisions

1. **Hybrid Storage**: Configurable support for MySQL, Pinecone, or both.
   - **Rationale**: Flexibility for different deployment scales.
   - **Implementation**: `SEMANTIC_STORAGE` config (mysql/pinecone/hybrid).

2. **Protocol-Based Architecture**: Defined `MemoryService` protocols.
   - **Rationale**: Dependency Inversion Principle (SOLID) for testability.
   - **Implementation**: Duck-typed protocols in `models.py`.

3. **Integrated Service Pattern**: Composition over inheritance.
   - **Rationale**: Unified API while keeping components decoupled.
   - **Implementation**: `IntegratedMemoryService` wraps specific services.

4. **LangGraph Integration**: State machine for conversation flow.
   - **Rationale**: Robust state management and checkpointing.
   - **Implementation**: `StateGraph` with `MemorySaver`/`SqliteSaver`.

## File Structure

```
src/agentlab/
├── models.py                     # Data models and protocols
├── config/
│   └── memory_config.py         # Memory configuration
├── core/
│   └── memory_service.py        # Short-term & Integrated services
├── agents/
│   └── memory_processor.py      # Long-term memory processor
├── database/
│   └── crud.py                  # Database operations
└── api/
    └── routes/
        └── chat_routes.py       # API endpoints
```

## Dependencies

- **mysql-connector-python**: Database connectivity.
- **langgraph**: State management and checkpointing.
- **langchain**: LLM integration and utilities.
- **langchain-openai**: OpenAI model integration.
- **langchain-pinecone**: Vector database integration.
- **pinecone-client**: Vector storage client.

## Configuration

### Environment Variables

Required variables:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=agent_lab

# OpenAI (required for embeddings and summarization)
OPENAI_API_KEY=sk-...
```

Optional variables for hybrid storage:

```bash
# Pinecone Configuration (for semantic memory)
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_NAME=agent-lab-memory
PINECONE_NAMESPACE=conversation_memory

# Memory Strategy
MEMORY_TYPE=buffer              # buffer, summary, or window
SHORT_TERM_WINDOW_SIZE=10       # For window memory
MAX_TOKEN_LIMIT=2000            # Max tokens in short-term context

# Long-term Memory
ENABLE_LONG_TERM=true           # Enable long-term features
SEMANTIC_STORAGE=hybrid         # mysql, pinecone, or hybrid

# Model Configuration
EMBEDDING_MODEL=text-embedding-ada-002
SUMMARY_MODEL=gpt-3.5-turbo

# Privacy and Retention
RETENTION_DAYS=90               # Optional: Days to keep history (omit for forever)
ENABLE_ANONYMIZATION=false      # Enable data anonymization
SENSITIVE_FIELDS=email,phone    # Comma-separated fields to anonymize

# Performance
BATCH_SIZE=100
ENABLE_CACHING=true
CACHE_TTL_SECONDS=300
```

### Memory Types

**1. Buffer Memory** (default)
- Stores entire conversation history
- Best for: Short conversations, full context needed
- Pros: Complete history, no information loss
- Cons: Token usage grows linearly

**2. Window Memory**
- Keeps only last K messages
- Best for: Long conversations, recent context focus
- Pros: Bounded memory, consistent token usage
- Cons: Loses older context

**3. Summary Memory**
- Progressively summarizes conversation
- Best for: Very long conversations, key points needed
- Pros: Constant memory size, preserves key information
- Cons: Loses details, requires LLM calls

### Storage Strategies

**1. MySQL Only** (`SEMANTIC_STORAGE=mysql`)
- All data stored in MySQL
- Pros: Simple, single database
- Cons: Slower semantic search

**2. Pinecone Only** (`SEMANTIC_STORAGE=pinecone`)
- Semantic embeddings in Pinecone
- Requires: `PINECONE_API_KEY`, `PINECONE_INDEX_NAME`
- Pros: Fast vector similarity search
- Cons: External dependency

**3. Hybrid** (`SEMANTIC_STORAGE=hybrid`) - Recommended
- Structured data in MySQL
- Embeddings in Pinecone
- Pros: Best of both worlds, fast semantic search
- Cons: Two systems to manage

## Usage Examples

### Basic Memory Operations

```python
from agentlab.core.memory_service import IntegratedMemoryService
from agentlab.models import ChatMessage
from datetime import datetime

# Initialize memory service
memory_service = IntegratedMemoryService()

# Add messages to memory
memory_service.add_message(
    session_id="user-123",
    message=ChatMessage(
        role="user",
        content="I love programming in Python",
        timestamp=datetime.now()
    )
)

memory_service.add_message(
    session_id="user-123",
    message=ChatMessage(
        role="assistant",
        content="Python is a great language for data science!",
        timestamp=datetime.now()
    )
)

# Retrieve conversation history
messages = memory_service.get_messages("user-123", limit=50)
for msg in messages:
    print(f"{msg.role}: {msg.content}")

# Get enriched context (includes long-term memory)
context = memory_service.get_context("user-123", max_tokens=2000)
print(f"Short-term context: {context.short_term_context}")
print(f"Semantic facts: {context.semantic_facts}")
print(f"User profile: {context.user_profile}")
print(f"Episodic summary: {context.episodic_summary}")
print(f"Patterns: {context.procedural_patterns}")

# Get memory statistics
stats = memory_service.get_stats("user-123")
print(f"Total messages: {stats.message_count}")
print(f"Semantic facts: {stats.semantic_facts_count}")
print(f"Profile attributes: {stats.profile_attributes_count}")

# Clear session memory
memory_service.clear_session("user-123")
```

### Semantic Search

```python
# Search across all conversations
results = memory_service.search_semantic(
    query="Python programming best practices",
    top_k=5
)

for result in results:
    print(f"Score: {result['score']:.2f}")
    print(f"Text: {result['text']}")
    print(f"Session: {result['session_id']}")

# Search within specific session
results = memory_service.search_semantic(
    query="data science tools",
    session_id="user-123",
    top_k=3
)
```

### Using REST API

**Get Memory Context**
```bash
curl -X POST "http://localhost:8000/llm/memory/context" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "max_tokens": 2000
  }'
```

**Get Conversation History**
```bash
curl "http://localhost:8000/llm/memory/history/user-123?limit=50"
```

**Get Memory Statistics**
```bash
curl "http://localhost:8000/llm/memory/stats/user-123"
```

**Search Semantic Memory**
```bash
curl -X POST "http://localhost:8000/llm/memory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python programming",
    "session_id": "user-123",
    "top_k": 5
  }'
```

**Clear Session**
```bash
curl -X DELETE "http://localhost:8000/llm/memory/user-123"
```

## Integration with RAG

The memory module integrates cleanly with the existing RAG system for enriched query responses:

```python
from agentlab.core.llm_interface import LangChainLLM
from agentlab.core.rag_service import RAGServiceImpl
from agentlab.core.memory_service import IntegratedMemoryService

# Initialize services
llm = LangChainLLM()
rag_service = RAGServiceImpl(llm=llm)
memory_service = IntegratedMemoryService(llm=llm)

# Get conversation context
context = memory_service.get_context("user-123")

# Combine with RAG for enriched query
query = f"""
Context from conversation:
{context.short_term_context}

User profile: {context.user_profile}

Question: {user_question}
"""

# Query RAG with enriched context
rag_result = rag_service.query(query, top_k=5)
print(rag_result.response)
```

## Memory Types Explained

### 1. Short-Term Memory

Managed by `ShortTermMemoryService`, uses **LangGraph** for state management:

- **Buffer**: Full conversation history (uses `MemorySaver`).
- **Window**: Sliding window of last K messages (uses `SqliteSaver`).
- **Summary**: Progressive summarization (uses `SqliteSaver`).

Backend: MySQL `chat_history` table (persistence) + SQLite (checkpoints).

### 2. Semantic Memory

Facts and knowledge extracted from conversations:

```python
# Automatically extracted facts
context.semantic_facts
# Example: ["User prefers Python", "Interested in data science"]

# Search semantic memory
results = memory_service.search_semantic("machine learning")
```

Backend: Hybrid (MySQL + Pinecone embeddings)

### 3. Episodic Memory

Temporal summaries of conversation flow:

```python
context.episodic_summary
# Example: "User started with Python basics, moved to data science tools, 
# then discussed deployment strategies."
```

Generated by LLM, stored in context object

### 4. Profile Memory

Aggregated user characteristics:

```python
context.user_profile
# Example: {
#   "session_id": "user-123",
#   "total_messages": 45,
#   "first_interaction": "2024-01-01T10:00:00",
#   "top_topics": [
#     {"word": "python", "count": 12},
#     {"word": "data", "count": 8}
#   ]
# }
```

Extracted from message statistics and patterns

### 5. Procedural Memory

Interaction patterns and workflows:

```python
context.procedural_patterns
# Example: ["frequently_asks_questions", "discusses_code", "uses_greetings"]
```

Detected from message analysis

## Database Schema

### chat_history Table

```sql
CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/llm/memory/context` | POST | Get enriched memory context |
| `/llm/memory/history/{session_id}` | GET | Get conversation history |
| `/llm/memory/stats/{session_id}` | GET | Get memory statistics |
| `/llm/memory/search` | POST | Search semantic memory |
| `/llm/memory/{session_id}` | DELETE | Clear session memory |

## Performance Considerations

### Token Management

- Set appropriate `MAX_TOKEN_LIMIT` based on model context window
- Use `window` or `summary` memory for long conversations
- Monitor token usage via stats endpoint

### Caching

Enable caching for frequently accessed sessions:

```bash
ENABLE_CACHING=true
CACHE_TTL_SECONDS=300  # 5 minutes
```

### Batch Operations

Process multiple messages efficiently:

```bash
BATCH_SIZE=100  # Batch size for bulk operations
```

## Privacy and Security

### Data Retention

Set retention policy to automatically clean old data:

```bash
RETENTION_DAYS=90  # Keep only last 90 days
```

Implement cleanup job:

```python
# TODO: Add cleanup script
# Delete messages older than retention period
```

### Anonymization

Enable sensitive field anonymization:

```bash
ENABLE_ANONYMIZATION=true
SENSITIVE_FIELDS=email,phone,ssn
```

Note: Anonymization feature is configurable but implementation pending.

## Troubleshooting

### Database Connection Issues

```bash
# Test database connection
mysql -h localhost -u your_user -p your_database

# Check environment variables
echo $DB_HOST $DB_USER $DB_NAME
```

### Pinecone Setup

```bash
# Verify Pinecone credentials
export PINECONE_API_KEY="your-key"

# Test index exists
# See Pinecone dashboard or use Python API
```

### Memory Not Persisting

1. Check database connection in logs
2. Verify `chat_history` table exists
3. Ensure session IDs are consistent

### High Token Usage

1. Switch from `buffer` to `window` memory
2. Reduce `SHORT_TERM_WINDOW_SIZE`
3. Use `summary` memory for compression

## Testing

Run memory module tests:

```bash
# All memory tests
uv run pytest tests/unit/test_memory*.py -v

# Specific test file
uv run pytest tests/unit/test_memory_service.py -v

# With coverage
uv run pytest tests/unit/test_memory*.py --cov=src/agentlab
```

## Future Enhancements

- [ ] Automatic retention policy enforcement
- [ ] Sensitive data anonymization implementation
- [ ] Multi-user profile aggregation
- [ ] Conversation topic clustering
- [ ] Export/import conversation archives
- [ ] Real-time memory updates via WebSockets
- [ ] Cross-session knowledge transfer

## References

- [LangChain Memory Documentation](https://python.langchain.com/docs/modules/memory/)
- [Pinecone Vector Database](https://docs.pinecone.io/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [Project AGENTS.md](../AGENTS.md) - Coding guidelines
