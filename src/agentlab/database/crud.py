"""
CRUD (Create, Read, Update, Delete) operations for database tables.

Provides functions to interact with the MySQL database for:
- Knowledge base documents
- Chat history
- MPC instances
"""

import json
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator

import mysql.connector
from mysql.connector import Error as MySQLError

from agentlab.database.config import DatabaseConfig
from agentlab.database.models import ALL_TABLES


@contextmanager
def get_db_connection(
    config: DatabaseConfig | None = None,
) -> Generator[mysql.connector.MySQLConnection, None, None]:
    """
    Context manager for database connections.

    Args:
        config: Database configuration. If None, loads from environment.

    Yields:
        MySQL connection object.

    Raises:
        RuntimeError: If connection fails.
    """
    if config is None:
        config = DatabaseConfig.from_env()

    connection = None
    try:
        connection = mysql.connector.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            database=config.database,
            charset=config.charset,
        )
        yield connection
    except MySQLError as e:
        raise RuntimeError(f"Database connection failed: {e}") from e
    finally:
        if connection and connection.is_connected():
            connection.close()


def initialize_database(config: DatabaseConfig | None = None) -> None:
    """
    Initialize database by creating all tables defined in models.py.

    Args:
        config: Database configuration. If None, loads from environment.

    Raises:
        RuntimeError: If table creation fails.
    """
    with get_db_connection(config) as connection:
        cursor = connection.cursor()
        try:
            for table_sql in ALL_TABLES:
                cursor.execute(table_sql)
            connection.commit()
        except MySQLError as e:
            connection.rollback()
            raise RuntimeError(f"Failed to initialize database: {e}") from e
        finally:
            cursor.close()


def create_chat_message(
    session_id: str,
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None,
    config: DatabaseConfig | None = None,
) -> int:
    """
    Store a chat message in the history.

    Args:
        session_id: Chat session identifier.
        role: Message role (user/assistant/system).
        content: Message content.
        metadata: Optional metadata.
        config: Database configuration.

    Returns:
        ID of the created message row.

    Raises:
        ValueError: If role is invalid.
        RuntimeError: If database operation fails.
    """
    valid_roles = ("user", "assistant", "system")
    if role not in valid_roles:
        raise ValueError(f"Invalid role: {role}. Must be one of {valid_roles}")

    query = """
        INSERT INTO chat_history (session_id, role, content, metadata)
        VALUES (%s, %s, %s, %s)
    """

    metadata_json = json.dumps(metadata) if metadata else None

    with get_db_connection(config) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, (session_id, role, content, metadata_json))
            conn.commit()
            return cursor.lastrowid
        except MySQLError as e:
            conn.rollback()
            raise RuntimeError(f"Failed to create message: {e}") from e
        finally:
            cursor.close()


def get_chat_history(
    session_id: str,
    limit: int = 50,
    config: DatabaseConfig | None = None,
) -> list[dict[str, Any]]:
    """
    Retrieve chat history for a session.

    Args:
        session_id: Chat session identifier.
        limit: Maximum number of messages to retrieve.
        config: Database configuration.

    Returns:
        List of chat messages ordered by timestamp (oldest first).

    Raises:
        RuntimeError: If database operation fails.
    """
    query = """
        SELECT id, session_id, role, content, metadata, created_at
        FROM chat_history
        WHERE session_id = %s
        ORDER BY created_at ASC
        LIMIT %s
    """

    with get_db_connection(config) as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, (session_id, limit))
            results = cursor.fetchall()

            # Parse JSON metadata
            for row in results:
                if row["metadata"]:
                    row["metadata"] = json.loads(row["metadata"])

            return results
        except MySQLError as e:
            raise RuntimeError(f"Failed to retrieve history: {e}") from e
        finally:
            cursor.close()


def delete_chat_history(
    session_id: str, config: DatabaseConfig | None = None
) -> int:
    """
    Delete all chat history for a session.

    Args:
        session_id: Chat session identifier.
        config: Database configuration.

    Returns:
        Number of deleted rows.

    Raises:
        RuntimeError: If database operation fails.
    """
    query = "DELETE FROM chat_history WHERE session_id = %s"

    with get_db_connection(config) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, (session_id,))
            conn.commit()
            return cursor.rowcount
        except MySQLError as e:
            conn.rollback()
            raise RuntimeError(f"Failed to delete history: {e}") from e
        finally:
            cursor.close()


def get_chat_stats(
    session_id: str, config: DatabaseConfig | None = None
) -> dict[str, Any]:
    """
    Get statistics for a chat session.

    Args:
        session_id: Chat session identifier.
        config: Database configuration.

    Returns:
        Dictionary with statistics (count, oldest, newest timestamps).

    Raises:
        RuntimeError: If database operation fails.
    """
    query = """
        SELECT 
            COUNT(*) as message_count,
            MIN(created_at) as oldest_message,
            MAX(created_at) as newest_message
        FROM chat_history
        WHERE session_id = %s
    """

    with get_db_connection(config) as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, (session_id,))
            result = cursor.fetchone()
            return result or {
                "message_count": 0,
                "oldest_message": None,
                "newest_message": None,
            }
        except MySQLError as e:
            raise RuntimeError(f"Failed to get stats: {e}") from e
        finally:
            cursor.close()


# ============================================================================
# Original stub functions (kept for backwards compatibility)
# ============================================================================


def create_knowledge_document(
    doc_id: str,
    content: str,
    embedding: list[float] | None = None,
    metadata: dict[str, Any] | None = None,
) -> int:
    """
    Create a new document in the knowledge base.

    Args:
        doc_id: Unique document identifier.
        content: Document text content.
        embedding: Optional vector embedding.
        metadata: Optional metadata dictionary.

    Returns:
        ID of the created document row.

    Raises:
        ValueError: If doc_id already exists.
    """
    # Implementation will be added in future iterations
    raise NotImplementedError("CRUD operations to be implemented")


def get_knowledge_documents(top_k: int = 10) -> list[dict[str, Any]]:
    """
    Retrieve knowledge base documents.

    Args:
        top_k: Maximum number of documents to retrieve.

    Returns:
        List of document dictionaries.
    """
    raise NotImplementedError("CRUD operations to be implemented")

def create_mpc_instance(
    instance_id: str,
    status: str,
    host: str,
    port: int,
    metadata: dict[str, Any] | None = None,
) -> int:
    """
    Register a new MPC instance.

    Args:
        instance_id: Unique instance identifier.
        status: Instance status (running/stopped/error).
        host: Server host address.
        port: Server port number.
        metadata: Optional metadata.

    Returns:
        ID of the created instance row.
    """
    raise NotImplementedError("CRUD operations to be implemented")


def update_mpc_instance_status(instance_id: str, status: str) -> None:
    """
    Update the status of an MPC instance.

    Args:
        instance_id: Instance identifier.
        status: New status value.
    """
    raise NotImplementedError("CRUD operations to be implemented")


def get_mpc_instances() -> list[dict[str, Any]]:
    """
    Retrieve all MPC instances.

    Returns:
        List of MPC instance dictionaries.
    """
    raise NotImplementedError("CRUD operations to be implemented")


# ============================================================================
# Session Configuration CRUD Operations
# ============================================================================


def create_or_update_session_config(
    session_id: str,
    memory_config: dict[str, Any],
    rag_config: dict[str, Any],
    metadata: dict[str, Any] | None = None,
    config: DatabaseConfig | None = None,
) -> None:
    """
    Create or update session configuration.

    Args:
        session_id: Session identifier.
        memory_config: Memory configuration dictionary.
        rag_config: RAG configuration dictionary.
        metadata: Optional metadata.
        config: Database configuration.

    Raises:
        RuntimeError: If operation fails.
    """
    with get_db_connection(config) as connection:
        cursor = connection.cursor()
        try:
            sql = """
                INSERT INTO session_configs 
                (session_id, memory_config, rag_config, metadata)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    memory_config = VALUES(memory_config),
                    rag_config = VALUES(rag_config),
                    metadata = VALUES(metadata),
                    updated_at = CURRENT_TIMESTAMP
            """
            cursor.execute(
                sql,
                (
                    session_id,
                    json.dumps(memory_config),
                    json.dumps(rag_config),
                    json.dumps(metadata) if metadata else None,
                ),
            )
            connection.commit()
        except MySQLError as e:
            connection.rollback()
            raise RuntimeError(
                f"Failed to save session config: {e}"
            ) from e
        finally:
            cursor.close()


def get_session_config(
    session_id: str, config: DatabaseConfig | None = None
) -> dict[str, Any] | None:
    """
    Retrieve session configuration.

    Args:
        session_id: Session identifier.
        config: Database configuration.

    Returns:
        Configuration dictionary or None if not found.
    """
    with get_db_connection(config) as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            sql = """
                SELECT session_id, memory_config, rag_config, 
                       metadata, created_at, updated_at
                FROM session_configs
                WHERE session_id = %s
            """
            cursor.execute(sql, (session_id,))
            result = cursor.fetchone()
            
            if result:
                # Parse JSON fields
                result["memory_config"] = json.loads(
                    result["memory_config"]
                )
                result["rag_config"] = json.loads(result["rag_config"])
                if result["metadata"]:
                    result["metadata"] = json.loads(result["metadata"])
            
            return result
        except MySQLError as e:
            raise RuntimeError(
                f"Failed to retrieve session config: {e}"
            ) from e
        finally:
            cursor.close()


def delete_session_config(
    session_id: str, config: DatabaseConfig | None = None
) -> bool:
    """
    Delete session configuration.

    Args:
        session_id: Session identifier.
        config: Database configuration.

    Returns:
        True if deleted, False if not found.

    Raises:
        RuntimeError: If deletion fails.
    """
    with get_db_connection(config) as connection:
        cursor = connection.cursor()
        try:
            sql = "DELETE FROM session_configs WHERE session_id = %s"
            cursor.execute(sql, (session_id,))
            connection.commit()
            return cursor.rowcount > 0
        except MySQLError as e:
            connection.rollback()
            raise RuntimeError(
                f"Failed to delete session config: {e}"
            ) from e
        finally:
            cursor.close()
