# Configuration Management Tests

This Postman collection contains comprehensive tests for all configuration management endpoints in the Agent Lab API.

## Collection Overview

**File:** `Configuration_Management_Tests.postman_collection.json`

**Total Tests:** 16 tests across 5 sections

## Test Sections

### 1. System Status (1 test)
- `GET /config/status` - Retrieves system configuration status including available services

### 2. Session Configuration (6 tests)
- Setup: Generate test session ID
- Get non-existent session config (edge case)
- Create session configuration
- Get session configuration
- Update session configuration
- Delete session configuration

### 3. Memory Configuration (3 tests)
- Update memory config - Enable all types
- Update memory config - Disable
- Update memory config - Specific types only

### 4. RAG Configuration (3 tests)
- Update RAG config - Enable with namespaces
- Update RAG config - Disable
- Update RAG config - Change top_k

### 5. Validation Errors (2 tests)
- Session config with missing session_id (422 error)
- Memory config with invalid type (400/422 error)

## Prerequisites

- Server running at `http://localhost:8000`
- Valid `OPENAI_API_KEY` in environment
- Valid `PINECONE_API_KEY` in environment (for RAG config tests)
- MySQL database running and accessible (for memory config tests)

## How to Import

### Option 1: Import into Postman Desktop/Web

1. Open Postman
2. Click "Import" button
3. Select `Configuration_Management_Tests.postman_collection.json`
4. Click "Import"

### Option 2: Add to Existing Collection

To integrate these tests into the main `Agent_Lab_API` collection:

1. Open the main collection in Postman
2. Right-click on the collection name
3. Select "Add Folder"
4. Name it "5. Configuration Management"
5. Manually copy test requests from this collection

## Environment Variables

The collection uses these variables:

- `base_url` - API base URL (default: `http://localhost:8000`)
- `test_session_id` - Auto-generated unique session ID for testing

## Running the Tests

### Run Entire Collection

```bash
newman run Configuration_Management_Tests.postman_collection.json \
  --environment your-environment.json
```

### Run Specific Folder

```bash
newman run Configuration_Management_Tests.postman_collection.json \
  --folder "2. Session Configuration"
```

### Run with Verbose Output

```bash
newman run Configuration_Management_Tests.postman_collection.json \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export config-test-report.html
```

## Test Coverage

| Endpoint | Method | Tests | Status |
|----------|--------|-------|--------|
| `/config/status` | GET | 1 | ✅ Complete |
| `/config/session/{session_id}` | GET | 2 | ✅ Complete |
| `/config/session` | POST | 2 | ✅ Complete |
| `/config/session/{session_id}` | DELETE | 1 | ✅ Complete |
| `/config/memory` | PUT | 3 | ✅ Complete |
| `/config/rag` | PUT | 3 | ✅ Complete |

**Total Endpoint Coverage:** 6/6 endpoints (100%)

## Expected Test Results

All tests should pass with a properly configured environment:

```
┌─────────────────────────┬──────────┬──────────┐
│                         │ executed │   failed │
├─────────────────────────┼──────────┼──────────┤
│              iterations │        1 │        0 │
├─────────────────────────┼──────────┼──────────┤
│                requests │       16 │        0 │
├─────────────────────────┼──────────┼──────────┤
│            test-scripts │       21 │        0 │
├─────────────────────────┼──────────┼──────────┤
│      prerequest-scripts │        1 │        0 │
├─────────────────────────┼──────────┼──────────┤
│              assertions │       48 │        0 │
└─────────────────────────┴──────────┴──────────┘
```

## Integration with Main Collection

These tests are designed to be standalone but can also be integrated into the main `Agent_Lab_API.postman_collection.json` as a new section "5. Configuration Management".

The tests are independent and can be run in any order, though running them sequentially as organized provides the most logical flow.

## Troubleshooting

### Test Failures

**"Status code is 404"** on GET session config:
- Expected for non-existent sessions in some implementations
- Check if your implementation returns 404 or 200 with defaults

**"Status code is 500"** on RAG config tests:
- Ensure `PINECONE_API_KEY` is configured
- Check that Pinecone index exists and is accessible

**"Status code is 500"** on memory config tests:
- Ensure MySQL database is running and accessible
- Check database credentials in `.env` file

### Newman Errors

**"Collection not found"**:
```bash
# Use absolute path
newman run /full/path/to/Configuration_Management_Tests.postman_collection.json
```

**"Environment variables not set"**:
```bash
# Create environment file with base_url
newman run Configuration_Management_Tests.postman_collection.json \
  --env-var "base_url=http://localhost:8000"
```

## Related Documentation

- [API Endpoints Documentation](../../../../docs/api_endpoints.md) - Section 9: Configuration Management
- [Main API Tests](./Agent_Lab_API.postman_collection.json) - Comprehensive API test suite
- [RAG Testing Notes](../RAG_TESTING_NOTES.md) - Notes on RAG testing approach

## Maintenance Notes

**Last Updated:** 2025-12-17

**Changes:**
- Initial creation with 16 tests covering all 6 configuration endpoints
- Full CRUD testing for session configuration
- Toggle testing for memory and RAG configuration
- Validation error testing

**Future Enhancements:**
- Add tests for session-specific memory/RAG toggles (with session_id parameter)
- Add tests for configuration persistence across server restarts
- Add performance tests for bulk configuration updates
- Add tests for configuration validation edge cases
