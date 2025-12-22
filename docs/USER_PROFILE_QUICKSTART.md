# User Profile Memory System

## Quick Start

### 1. Initialize Database

```python
from agentlab.database.crud import initialize_database
initialize_database()  # Creates user_profiles table
```

### 2. Extract Profile from Conversation

```python
from agentlab.agents.memory_processor import LongTermMemoryProcessor
from agentlab.config.memory_config import MemoryConfig

# Initialize processor
config = MemoryConfig.from_env()
processor = LongTermMemoryProcessor(config=config)

# Extract and store profile from a session
profile = processor.extract_and_store_profile(
    session_id="user-session-123",
    incremental=True  # Only process new messages
)

print(profile)
# {
#   "user_name": "Maria",
#   "age": 28,
#   "occupation": "Data Scientist",
#   "interests": ["Machine Learning", "NLP"],
#   ...
# }
```

### 3. Retrieve Stored Profile

```python
from agentlab.database.crud import get_user_profile

profile_row = get_user_profile()
print(profile_row['profile_data'])
```

### 4. Use Profile in Memory Context

The profile is automatically loaded when building memory context:

```python
from agentlab.core.memory_service import IntegratedMemoryService

service = IntegratedMemoryService()
context = service.get_context(
    session_id="user-session-123",
    memory_config={"enable_profile": True}
)

print(context.user_profile)
```

## API Endpoints

### Get Current Profile
```bash
GET /api/memory/profile
```

Response:
```json
{
  "profile_data": {
    "user_name": "Maria",
    "age": 28,
    "occupation": "Data Scientist",
    "interests": ["ML", "NLP"],
    "expertise_areas": ["Python", "PyTorch"]
  },
  "version": 2,
  "last_updated": "2025-12-22T10:30:00",
  "created_at": "2025-12-22T08:00:00"
}
```

### Extract Profile from Session
```bash
POST /api/memory/profile/extract
Content-Type: application/json

{
  "session_id": "user-session-123",
  "incremental": true
}
```

Response:
```json
{
  "profile_data": {...},
  "status": "updated"
}
```

### Delete Profile
```bash
DELETE /api/memory/profile
```

## Profile Schema

Default schema is in `data/configs/profile_schema.json`:

```json
{
  "user_name": "string",
  "age": "integer",
  "interests": ["string"],
  "home": "string",
  "occupation": "string",
  "expertise_areas": ["string"],
  "goals": ["string"],
  "conversation_preferences": ["string"],
  "technical_context": {
    "programming_languages": ["string"],
    "tools": ["string"],
    "operating_system": "string"
  },
  "learning_style": "string"
}
```

**Note:** LLM can add additional fields beyond the base schema.

## How It Works

1. **Conversation Happens** - User chats in any session
2. **Extraction Triggered** - API call or automatic trigger
3. **LLM Analysis** - ChatGPT analyzes conversation using schema
4. **JSON Generation** - LLM returns structured profile data
5. **Merge & Store** - New data merged with existing profile
6. **Version Increment** - Profile version increases
7. **Context Integration** - Profile loaded automatically in future chats

## Features

- ✅ **LLM-Powered Extraction** - Smart profile building vs. keyword counting
- ✅ **Global Profile** - Single profile across all sessions
- ✅ **Extensible Schema** - LLM adds relevant fields dynamically
- ✅ **Patch Mode** - Merges new data without losing existing info
- ✅ **Incremental Updates** - Process only new messages
- ✅ **Version Tracking** - Know when profile was last updated
- ✅ **API Access** - Easy integration with frontend
- ✅ **Persistent Storage** - MySQL database backend

## Example Usage

Run the demo:

```bash
cd src/agentlab/examples
python profile_extraction_demo.py
```

This will:
1. Create example conversation
2. Extract profile with LLM
3. Store in database
4. Add new messages
5. Update profile incrementally
6. Show before/after comparison

## Configuration

### Environment Variables

```bash
OPENAI_API_KEY=sk-...              # Required for LLM extraction
ENABLE_PROFILE_MEMORY=true         # Enable/disable feature (default: true)
OPENAI_SUMMARY_MODEL=gpt-4o-mini  # Model for extraction (default: gpt-4o-mini)
```

### Per-Session Configuration

Profile can be disabled per-session via memory_config:

```python
context = service.get_context(
    session_id="session-123",
    memory_config={
        "enable_profile": False  # Disable profile for this request
    }
)
```

## Testing

Run unit tests:

```bash
make test-unit
# or
uv run pytest tests/unit/test_user_profile.py -v
```

Tests cover:
- Schema loading
- LLM extraction
- Patch mode merging
- JSON parsing
- Error handling
- Database operations

## Troubleshooting

### Profile Not Extracting

**Problem:** Profile returns empty dict

**Solutions:**
1. Check `OPENAI_API_KEY` is set
2. Verify `ENABLE_PROFILE_MEMORY=true`
3. Ensure conversation has actual messages
4. Check LLM model is accessible

### Profile Missing Fields

**Problem:** Expected fields not in profile

**Solutions:**
1. LLM only extracts mentioned information
2. User must mention data in conversation
3. Try more explicit conversation
4. Check schema instructions

### Version Not Incrementing

**Problem:** Version stays at 1

**Solutions:**
1. Ensure `create_or_update_user_profile()` is called
2. Check database connection
3. Verify update query executes successfully

## Architecture

```
┌─────────────────┐
│  Conversation   │
│   (any session) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ LongTermMemoryProcessor     │
│ - extract_and_store_profile()│
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ LLM (ChatGPT)               │
│ - Analyze conversation      │
│ - Extract structured data   │
│ - Follow schema             │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Database (MySQL)            │
│ user_profiles table         │
│ - Single row                │
│ - JSON storage              │
│ - Version tracking          │
└─────────────────────────────┘
```

## Best Practices

1. **Extract Periodically** - Call `/profile/extract` every N messages
2. **Use Incremental Mode** - Set `incremental=true` for efficiency
3. **Validate Important Fields** - Check critical fields exist
4. **Monitor Token Usage** - LLM extraction costs tokens
5. **Keep Schema Updated** - Review and refine schema regularly
6. **Respect Privacy** - Be careful with PII
7. **Test Thoroughly** - Verify extraction quality with real conversations

## See Also

- [Full Implementation Details](USER_PROFILE_IMPLEMENTATION.md)
- [Memory System Documentation](MEMORY.md)
- [API Documentation](API.md)
