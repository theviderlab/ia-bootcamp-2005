"""
Unit tests for CRUD delete operations.

Tests delete_chat_history and delete_all_chat_history functions.
"""

from unittest.mock import MagicMock, patch

import pytest

from agentlab.database.crud import (
    count_unique_sessions,
    delete_all_chat_history,
    delete_all_knowledge_base,
    delete_all_session_configs,
    delete_chat_history,
    get_table_counts,
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


class TestDeleteChatHistory:
    """Test suite for delete_chat_history function."""

    def test_delete_chat_history_success(self, mock_db_connection):
        """Test successful deletion of chat history for a session."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 15

        result = delete_chat_history("test-session-123")

        # Verify correct SQL was executed
        mock_cursor.execute.assert_called_once()
        sql_call = mock_cursor.execute.call_args[0]
        assert "DELETE FROM chat_history" in sql_call[0]
        assert "WHERE session_id = %s" in sql_call[0]
        assert sql_call[1] == ("test-session-123",)

        # Verify transaction was committed
        mock_conn.commit.assert_called_once()

        # Verify correct rowcount returned
        assert result == 15

    def test_delete_chat_history_no_rows(self, mock_db_connection):
        """Test deletion when no rows exist."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 0

        result = delete_chat_history("nonexistent-session")

        assert result == 0
        mock_conn.commit.assert_called_once()

    def test_delete_chat_history_database_error(self, mock_db_connection):
        """Test handling of database errors."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection

        # Mock database error
        from mysql.connector import Error as MySQLError

        mock_cursor.execute.side_effect = MySQLError("Connection lost")

        # Should raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            delete_chat_history("test-session")

        assert "Failed to delete history" in str(exc_info.value)

        # Verify rollback was called
        mock_conn.rollback.assert_called_once()


class TestDeleteAllChatHistory:
    """Test suite for delete_all_chat_history function."""

    def test_delete_all_chat_history_success(self, mock_db_connection):
        """Test successful deletion of all chat history."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 42

        result = delete_all_chat_history()

        # Verify correct SQL was executed
        mock_cursor.execute.assert_called_once()
        sql_call = mock_cursor.execute.call_args[0]
        assert sql_call[0] == "DELETE FROM chat_history"
        # No parameters for deleting all
        assert len(sql_call) == 1

        # Verify transaction was committed
        mock_conn.commit.assert_called_once()

        # Verify correct rowcount returned
        assert result == 42

    def test_delete_all_chat_history_empty_table(self, mock_db_connection):
        """Test deletion when table is already empty."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 0

        result = delete_all_chat_history()

        assert result == 0
        mock_conn.commit.assert_called_once()

    def test_delete_all_chat_history_large_count(self, mock_db_connection):
        """Test deletion with large number of rows."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 10000

        result = delete_all_chat_history()

        assert result == 10000
        mock_conn.commit.assert_called_once()

    def test_delete_all_chat_history_database_error(
        self, mock_db_connection
    ):
        """Test handling of database errors."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection

        # Mock database error
        from mysql.connector import Error as MySQLError

        mock_cursor.execute.side_effect = MySQLError("Table locked")

        # Should raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            delete_all_chat_history()

        assert "Failed to delete all history" in str(exc_info.value)

        # Verify rollback was called
        mock_conn.rollback.assert_called_once()

    def test_delete_all_with_custom_config(self, mock_db_connection):
        """Test deletion with custom database config."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 5

        from agentlab.database.config import DatabaseConfig

        custom_config = DatabaseConfig(
            host="custom-host",
            port=3307,
            user="custom-user",
            password="custom-pass",
            database="custom-db",
        )

        result = delete_all_chat_history(config=custom_config)

        assert result == 5
        # Verify custom config was passed to connection
        mock_ctx.assert_called()


class TestCountUniqueSessions:
    """Test suite for count_unique_sessions function."""

    def test_count_unique_sessions_success(self, mock_db_connection):
        """Test successful count of unique sessions."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = {"count": 15}

        result = count_unique_sessions()

        # Verify correct SQL was executed
        mock_cursor.execute.assert_called_once()
        sql_call = mock_cursor.execute.call_args[0][0]
        assert "COUNT(DISTINCT session_id)" in sql_call
        assert "FROM chat_history" in sql_call

        assert result == 15

    def test_count_unique_sessions_zero(self, mock_db_connection):
        """Test count when no sessions exist."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = {"count": 0}

        result = count_unique_sessions()

        assert result == 0

    def test_count_unique_sessions_null_result(self, mock_db_connection):
        """Test count when query returns None."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None

        result = count_unique_sessions()

        assert result == 0

    def test_count_unique_sessions_database_error(self, mock_db_connection):
        """Test handling of database errors."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection

        from mysql.connector import Error as MySQLError

        mock_cursor.execute.side_effect = MySQLError("Connection failed")

        with pytest.raises(RuntimeError) as exc_info:
            count_unique_sessions()

        assert "Failed to count sessions" in str(exc_info.value)


class TestDeleteAllSessionConfigs:
    """Test suite for delete_all_session_configs function."""

    def test_delete_all_session_configs_success(self, mock_db_connection):
        """Test successful deletion of all session configs."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 8

        result = delete_all_session_configs()

        # Verify correct SQL was executed
        mock_cursor.execute.assert_called_once()
        sql_call = mock_cursor.execute.call_args[0][0]
        assert sql_call == "DELETE FROM session_configs"

        # Verify transaction was committed
        mock_conn.commit.assert_called_once()

        assert result == 8

    def test_delete_all_session_configs_empty(self, mock_db_connection):
        """Test deletion when no configs exist."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 0

        result = delete_all_session_configs()

        assert result == 0
        mock_conn.commit.assert_called_once()

    def test_delete_all_session_configs_database_error(self, mock_db_connection):
        """Test handling of database errors."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection

        from mysql.connector import Error as MySQLError

        mock_cursor.execute.side_effect = MySQLError("Table locked")

        with pytest.raises(RuntimeError) as exc_info:
            delete_all_session_configs()

        assert "Failed to delete session configs" in str(exc_info.value)
        mock_conn.rollback.assert_called_once()


class TestDeleteAllKnowledgeBase:
    """Test suite for delete_all_knowledge_base function."""

    def test_delete_all_knowledge_base_success(self, mock_db_connection):
        """Test successful deletion of all knowledge base documents."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 25

        result = delete_all_knowledge_base()

        # Verify correct SQL was executed
        mock_cursor.execute.assert_called_once()
        sql_call = mock_cursor.execute.call_args[0][0]
        assert sql_call == "DELETE FROM knowledge_base"

        # Verify transaction was committed
        mock_conn.commit.assert_called_once()

        assert result == 25

    def test_delete_all_knowledge_base_empty(self, mock_db_connection):
        """Test deletion when no documents exist."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 0

        result = delete_all_knowledge_base()

        assert result == 0
        mock_conn.commit.assert_called_once()

    def test_delete_all_knowledge_base_database_error(self, mock_db_connection):
        """Test handling of database errors."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection

        from mysql.connector import Error as MySQLError

        mock_cursor.execute.side_effect = MySQLError("Disk full")

        with pytest.raises(RuntimeError) as exc_info:
            delete_all_knowledge_base()

        assert "Failed to delete knowledge base" in str(exc_info.value)
        mock_conn.rollback.assert_called_once()


class TestGetTableCounts:
    """Test suite for get_table_counts function."""

    def test_get_table_counts_success(self, mock_db_connection):
        """Test successful retrieval of table counts."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection

        # Mock different counts for each query
        def mock_execute(query):
            if "chat_history" in query:
                mock_cursor.fetchone.return_value = {"count": 100}
            elif "session_configs" in query:
                mock_cursor.fetchone.return_value = {"count": 10}
            elif "knowledge_base" in query:
                mock_cursor.fetchone.return_value = {"count": 50}
            elif "mpc_instances" in query:
                mock_cursor.fetchone.return_value = {"count": 5}

        mock_cursor.execute.side_effect = mock_execute

        result = get_table_counts()

        assert result["chat_history"] == 100
        assert result["session_configs"] == 10
        assert result["knowledge_base"] == 50
        assert result["mpc_instances"] == 5

    def test_get_table_counts_all_zero(self, mock_db_connection):
        """Test when all tables are empty."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = {"count": 0}

        result = get_table_counts()

        assert result["chat_history"] == 0
        assert result["session_configs"] == 0
        assert result["knowledge_base"] == 0
        assert result["mpc_instances"] == 0

    def test_get_table_counts_table_missing(self, mock_db_connection):
        """Test when a table doesn't exist."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection

        from mysql.connector import Error as MySQLError

        def mock_execute(query):
            if "mpc_instances" in query:
                raise MySQLError("Table doesn't exist")
            else:
                mock_cursor.fetchone.return_value = {"count": 10}

        mock_cursor.execute.side_effect = mock_execute

        result = get_table_counts()

        # Tables that exist should have counts
        assert result["chat_history"] == 10
        # Missing table should be 0
        assert result["mpc_instances"] == 0

    def test_get_table_counts_null_result(self, mock_db_connection):
        """Test when query returns None."""
        mock_ctx, mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None

        result = get_table_counts()

        # All should be 0 when result is None
        assert result["chat_history"] == 0
        assert result["session_configs"] == 0
        assert result["knowledge_base"] == 0
        assert result["mpc_instances"] == 0

