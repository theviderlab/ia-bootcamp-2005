"""
Unit tests for session management routes.

Tests the /session/reset endpoint functionality.
"""

import uuid
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from agentlab.api.routes import session_routes


class TestResetSession:
    """Test suite for reset_session endpoint."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock SessionResetRequest."""
        mock = Mock()
        mock.current_session_id = "test-session-123"
        return mock

    @pytest.mark.asyncio
    async def test_reset_session_success(self, mock_request):
        """Test successful session reset."""
        with patch("agentlab.api.routes.session_routes.crud") as mock_crud:
            # Mock successful deletion
            mock_crud.delete_all_chat_history.return_value = 15

            # Call endpoint
            response = await session_routes.reset_session(mock_request)

            # Verify response
            assert response.success is True
            assert response.new_session_id is not None
            assert "15 messages" in response.message

            # Verify new session ID is valid UUID
            try:
                uuid.UUID(response.new_session_id)
            except ValueError:
                pytest.fail("new_session_id is not a valid UUID")

            # Verify crud function was called
            mock_crud.delete_all_chat_history.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_session_with_zero_messages(self, mock_request):
        """Test session reset when no messages exist."""
        with patch("agentlab.api.routes.session_routes.crud") as mock_crud:
            # Mock deletion with no messages
            mock_crud.delete_all_chat_history.return_value = 0

            response = await session_routes.reset_session(mock_request)

            assert response.success is True
            assert "0 messages" in response.message

    @pytest.mark.asyncio
    async def test_reset_session_database_error(self, mock_request):
        """Test session reset with database error."""
        with patch("agentlab.api.routes.session_routes.crud") as mock_crud:
            # Mock RuntimeError from crud
            mock_crud.delete_all_chat_history.side_effect = RuntimeError(
                "Database connection failed"
            )

            # Should raise HTTPException with 500
            with pytest.raises(HTTPException) as exc_info:
                await session_routes.reset_session(mock_request)

            assert exc_info.value.status_code == 500
            assert "Failed to reset session" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_reset_session_unexpected_error(self, mock_request):
        """Test session reset with unexpected error."""
        with patch("agentlab.api.routes.session_routes.crud") as mock_crud:
            # Mock unexpected exception
            mock_crud.delete_all_chat_history.side_effect = Exception(
                "Unexpected error"
            )

            with pytest.raises(HTTPException) as exc_info:
                await session_routes.reset_session(mock_request)

            assert exc_info.value.status_code == 500
            assert "Failed to reset session" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_reset_generates_unique_session_ids(self, mock_request):
        """Test that each reset generates a unique session ID."""
        with patch("agentlab.api.routes.session_routes.crud") as mock_crud:
            mock_crud.delete_all_chat_history.return_value = 5

            # Call reset multiple times
            response1 = await session_routes.reset_session(mock_request)
            response2 = await session_routes.reset_session(mock_request)
            response3 = await session_routes.reset_session(mock_request)

            # Verify all session IDs are unique
            session_ids = {
                response1.new_session_id,
                response2.new_session_id,
                response3.new_session_id,
            }
            assert len(session_ids) == 3

    @pytest.mark.asyncio
    async def test_reset_session_message_format(self, mock_request):
        """Test that success message has correct format."""
        with patch("agentlab.api.routes.session_routes.crud") as mock_crud:
            mock_crud.delete_all_chat_history.return_value = 42

            response = await session_routes.reset_session(mock_request)

            # Verify message format
            assert "Session reset successfully" in response.message
            assert "42 messages" in response.message
            assert response.message.endswith(".")
