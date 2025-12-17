"""
Unit tests for session configuration CRUD operations.

Tests database operations for storing and retrieving session configs.
"""

import json
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from agentlab.database.crud import (
    create_or_update_session_config,
    delete_session_config,
    get_session_config,
)


@pytest.fixture
def mock_db_connection():
    """Mock database connection."""
    with patch("agentlab.database.crud.get_db_connection") as mock:
        connection = MagicMock()
        cursor = MagicMock()
        connection.cursor.return_value = cursor
        connection.__enter__.return_value = connection
        connection.__exit__.return_value = None
        mock.return_value.__enter__.return_value = connection
        yield mock, connection, cursor


def test_create_session_config(mock_db_connection):
    """Test creating a new session configuration."""
    mock_ctx, mock_conn, mock_cursor = mock_db_connection
    
    memory_config = {
        "enable_short_term": True,
        "enable_semantic": True,
        "enable_episodic": False,
    }
    rag_config = {
        "enable_rag": True,
        "namespaces": ["docs"],
        "top_k": 5,
    }
    
    create_or_update_session_config(
        session_id="test-session",
        memory_config=memory_config,
        rag_config=rag_config,
        metadata={"user": "test"},
    )
    
    # Verify SQL was executed
    mock_cursor.execute.assert_called_once()
    sql_call = mock_cursor.execute.call_args
    assert "INSERT INTO session_configs" in sql_call[0][0]
    assert "ON DUPLICATE KEY UPDATE" in sql_call[0][0]
    
    # Verify parameters
    params = sql_call[0][1]
    assert params[0] == "test-session"
    assert json.loads(params[1]) == memory_config
    assert json.loads(params[2]) == rag_config


def test_get_session_config_exists(mock_db_connection):
    """Test retrieving an existing session configuration."""
    mock_ctx, mock_conn, mock_cursor = mock_db_connection
    
    # Mock return data
    mock_cursor.fetchone.return_value = {
        "session_id": "test-session",
        "memory_config": json.dumps({"enable_semantic": True}),
        "rag_config": json.dumps({"enable_rag": False}),
        "metadata": json.dumps({"user": "test"}),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    
    result = get_session_config("test-session")
    
    assert result is not None
    assert result["session_id"] == "test-session"
    assert result["memory_config"]["enable_semantic"] is True
    assert result["rag_config"]["enable_rag"] is False
    assert result["metadata"]["user"] == "test"


def test_get_session_config_not_found(mock_db_connection):
    """Test retrieving a non-existent session configuration."""
    mock_ctx, mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None
    
    result = get_session_config("nonexistent-session")
    
    assert result is None


def test_update_session_config(mock_db_connection):
    """Test updating an existing session configuration."""
    mock_ctx, mock_conn, mock_cursor = mock_db_connection
    
    updated_memory = {"enable_semantic": False}
    updated_rag = {"enable_rag": True, "namespaces": ["new-ns"]}
    
    create_or_update_session_config(
        session_id="existing-session",
        memory_config=updated_memory,
        rag_config=updated_rag,
    )
    
    # Should use same SQL (INSERT ... ON DUPLICATE KEY UPDATE)
    mock_cursor.execute.assert_called_once()
    sql_call = mock_cursor.execute.call_args
    assert "ON DUPLICATE KEY UPDATE" in sql_call[0][0]


def test_delete_session_config_success(mock_db_connection):
    """Test deleting an existing session configuration."""
    mock_ctx, mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 1  # 1 row deleted
    
    result = delete_session_config("test-session")
    
    assert result is True
    mock_cursor.execute.assert_called_once()
    sql_call = mock_cursor.execute.call_args
    assert "DELETE FROM session_configs" in sql_call[0][0]


def test_delete_session_config_not_found(mock_db_connection):
    """Test deleting a non-existent session configuration."""
    mock_ctx, mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 0  # No rows deleted
    
    result = delete_session_config("nonexistent-session")
    
    assert result is False


def test_create_session_config_null_metadata(mock_db_connection):
    """Test creating config without metadata."""
    mock_ctx, mock_conn, mock_cursor = mock_db_connection
    
    create_or_update_session_config(
        session_id="test-session",
        memory_config={},
        rag_config={},
        metadata=None,
    )
    
    params = mock_cursor.execute.call_args[0][1]
    assert params[3] is None  # metadata parameter


def test_get_session_config_null_metadata(mock_db_connection):
    """Test retrieving config with null metadata."""
    mock_ctx, mock_conn, mock_cursor = mock_db_connection
    
    mock_cursor.fetchone.return_value = {
        "session_id": "test-session",
        "memory_config": json.dumps({}),
        "rag_config": json.dumps({}),
        "metadata": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    
    result = get_session_config("test-session")
    
    assert result["metadata"] is None
