# User Profile Memory - Implementation Summary

## Overview

Implemented a global user profile system that extracts and persists user information across all sessions using LLM-based analysis with a configurable, extensible schema.

## Key Design Decisions

### 1. **Single Global Profile** (Not Session-Based)
- Only ONE row in the `user_profiles` table
- Profile is shared across all sessions
- Suitable for single-user systems
- No `session_id` foreign key needed

### 2. **Schema Extensibility**
- Base schema defined in `data/configs/profile_schema.json`
- LLM can add custom fields beyond base schema
- No strict validation - allows organic growth
- Supports patch-mode updates (merge new data with existing)

### 3. **No Profile Confidence Decay**
- Profile data does not lose relevance over time
- Simple versioning with incrementing version numbers
- Tracks `last_updated_message_id` for incremental updates

## Components Modified/Created

### 1. **Profile Schema** (`data/configs/profile_schema.json`)
```json
{
  "name": "User Profile",
  "parameters": {
    "properties": {
      "user_name": "User's preferred name",
      "age": "User's age",
      "interests": "Array of interests/hobbies",
      "home": "Location description",
      "occupation": "Job/profession",
      "expertise_areas": "Areas of knowledge",
      "goals": "User's objectives",
      "conversation_preferences": "Communication style preferences",
      "technical_context": {
        "programming_languages": [],
        "tools": [],
        "operating_system": ""
      },
      "learning_style": "How user prefers to learn"
    }
  }
}
```

### 2. **Database Table** (`user_profiles`)
```sql
CREATE TABLE user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profile_data JSON NOT NULL,
    version INT DEFAULT 1,
    last_updated_message_id INT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_updated_at (updated_at)
)
```

### 3. **CRUD Operations** (`database/crud.py`)
- `get_user_profile()` - Retrieve the single profile row
- `create_or_update_user_profile()` - Upsert profile with version increment
- `delete_user_profile()` - Delete profile

### 4. **Memory Processor** (`agents/memory_processor.py`)

#### New Methods:
- `_load_profile_schema()` - Load schema from JSON file
- `extract_profile_from_messages(messages, existing_profile)` - LLM-based extraction
- `extract_and_store_profile(session_id, incremental)` - Full workflow
- `get_user_profile()` - Load from database (refactored from keyword counting)

#### LLM Prompt Strategy:
```python
prompt = f"""Extract user profile information from this conversation.

SCHEMA:
{schema_properties}

INSTRUCTIONS:
{schema_instructions}

You can add additional relevant fields beyond the base schema.

EXISTING PROFILE (update/patch this):
{existing_profile}

CONVERSATION:
{recent_messages}

Return ONLY a valid JSON object with the profile data."""
```

### 5. **Memory Service Integration** (`core/memory_service.py`)
- Updated `get_context()` to load profile from database
- Removed `session_id` parameter from `get_user_profile()` calls
- Profile is now global, not session-specific

### 6. **API Endpoints** (`api/routes/memory_routes.py`)

#### New Endpoints:
- `GET /memory/profile` - Get current profile
- `POST /memory/profile/extract` - Extract profile from session
- `DELETE /memory/profile` - Delete profile

#### Request/Response Models:
```python
class ProfileUpdateRequest:
    session_id: str
    incremental: bool = True

# Response
{
    "profile_data": {...},
    "version": 1,
    "last_updated": "2025-12-22T...",
    "created_at": "2025-12-22T..."
}
```

## Workflow

### Profile Extraction Flow:
```
1. User sends messages in any session
   ↓
2. API calls /memory/profile/extract
   ↓
3. LongTermMemoryProcessor.extract_and_store_profile()
   ↓
4. Load existing profile from database
   ↓
5. Fetch chat history (full or incremental)
   ↓
6. Call LLM with schema + existing profile + conversation
   ↓
7. Parse JSON response
   ↓
8. Merge with existing profile (patch mode)
   ↓
9. Store in database (version++)
   ↓
10. Return updated profile
```

### Profile Retrieval Flow:
```
1. Chat request needs memory context
   ↓
2. IntegratedMemoryService.get_context()
   ↓
3. LongTermMemoryProcessor.get_user_profile()
   ↓
4. Load from user_profiles table
   ↓
5. Return profile_data JSON
   ↓
6. Include in context for LLM
```

## Usage Examples

### Extract Profile from Conversation:
```bash
curl -X POST http://localhost:8000/api/memory/profile/extract \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "incremental": true
  }'
```

### Get Current Profile:
```bash
curl http://localhost:8000/api/memory/profile
```

### Delete Profile:
```bash
curl -X DELETE http://localhost:8000/api/memory/profile
```

## Testing

Created comprehensive unit tests in `tests/unit/test_user_profile.py`:
- Schema loading
- LLM extraction with mock responses
- Patch mode (merging with existing profile)
- JSON parsing with markdown code blocks
- Error handling (invalid JSON, no LLM)
- Database integration
- Full workflow testing

Run tests:
```bash
make test-unit
# or
uv run pytest tests/unit/test_user_profile.py -v
```

## Benefits

1. **Persistent Learning** - Profile builds up across all sessions
2. **LLM Intelligence** - Smart extraction vs. keyword counting
3. **Flexible Schema** - Adapts to discovered user attributes
4. **Incremental Updates** - Efficient processing of new messages only
5. **Patch Mode** - Merges new data without losing existing info
6. **Simple Architecture** - Single global profile, no session complexity
7. **API Access** - Easy integration with frontend/external systems

## Migration Notes

### To Initialize:
```python
from agentlab.database.crud import initialize_database
initialize_database()  # Creates user_profiles table
```

### Existing Systems:
- Old profile data (keyword-based) will be ignored
- First extraction creates new LLM-based profile
- No data migration needed (fresh start recommended)

## Future Enhancements (Optional)

1. **Multi-User Support** - Add `user_id` column if needed
2. **Profile History** - Track changes over time in separate table
3. **Confidence Scores** - Add confidence per field
4. **Profile Validation** - Pydantic models for type safety
5. **PII Detection** - Automatic masking of sensitive data
6. **Export/Import** - GDPR compliance features
7. **Profile Templates** - Pre-configured schemas for different use cases

## Files Changed

### Created:
- `data/configs/profile_schema.json` - Profile schema definition
- `tests/unit/test_user_profile.py` - Unit tests

### Modified:
- `src/agentlab/database/models.py` - Added user_profiles table + UserProfileRow
- `src/agentlab/database/crud.py` - Added profile CRUD operations
- `src/agentlab/agents/memory_processor.py` - Refactored profile extraction
- `src/agentlab/core/memory_service.py` - Updated profile integration
- `src/agentlab/api/routes/memory_routes.py` - Added profile endpoints

## Configuration

No environment variables needed. Profile system uses existing:
- `OPENAI_API_KEY` - For LLM extraction
- `ENABLE_PROFILE_MEMORY` - Toggle feature on/off (default: true)
- Database connection from `DatabaseConfig`

## Notes

- Profile extraction is **on-demand** via API call
- Not automatically extracted on every message (performance)
- Frontend can trigger extraction periodically or on-demand
- Profile loads automatically when building memory context
- Incremental mode processes only new messages since last update
