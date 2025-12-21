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

def delete_all_chat_history(
    config: DatabaseConfig | None = None,
) -> int:
    """
    Delete all chat history from all sessions.

    Args:
        config: Database configuration.

    Returns:
        Number of deleted rows.

    Raises:
        RuntimeError: If database operation fails.
    """
    query = "DELETE FROM chat_history"

    with get_db_connection(config) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            conn.commit()
            return cursor.rowcount
        except MySQLError as e:
            conn.rollback()
            raise RuntimeError(f"Failed to delete all history: {e}") from e
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
    filename: str | None = None,
    namespace: str | None = None,
    chunk_count: int = 1,
    file_size: int | None = None,
    embedding: list[float] | None = None,
    metadata: dict[str, Any] | None = None,
    config: DatabaseConfig | None = None,
) -> int:
    """
    Create or update a document in the knowledge base.

    Uses INSERT ... ON DUPLICATE KEY UPDATE to handle upserts.
    If doc_id exists, updates chunk_count, file_size, and updated_at.

    Args:
        doc_id: Unique document identifier.
        content: Document text content (sample or summary).
        filename: Original filename.
        namespace: Optional namespace for organization.
        chunk_count: Number of chunks for this document.
        file_size: File size in bytes.
        embedding: Optional vector embedding (JSON).
        metadata: Optional metadata dictionary (JSON).
        config: Database configuration.

    Returns:
        ID of the created/updated document row.

    Raises:
        RuntimeError: If database operation fails.
    """
    query = """
        INSERT INTO knowledge_base 
        (doc_id, content, filename, namespace, chunk_count, file_size, embedding, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            chunk_count = VALUES(chunk_count),
            file_size = VALUES(file_size),
            updated_at = CURRENT_TIMESTAMP
    """

    embedding_json = json.dumps(embedding) if embedding else None
    metadata_json = json.dumps(metadata) if metadata else None

    with get_db_connection(config) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                query,
                (
                    doc_id,
                    content,
                    filename,
                    namespace,
                    chunk_count,
                    file_size,
                    embedding_json,
                    metadata_json,
                ),
            )
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        except MySQLError as e:
            conn.rollback()
            raise RuntimeError(f"Failed to create knowledge document: {e}") from e
        finally:
            cursor.close()

def bulk_insert_knowledge_documents(
    documents: list[dict[str, Any]],
    config: DatabaseConfig | None = None,
) -> int:
    """
    Bulk insert or update multiple documents in the knowledge base.

    Uses INSERT ... ON DUPLICATE KEY UPDATE for efficient batch upserts.
    Rolls back entire transaction if any insert fails.

    Args:
        documents: List of document dictionaries with keys:
            - doc_id (required): Unique document identifier
            - content (required): Document text content
            - filename (optional): Original filename
            - namespace (optional): Namespace for organization
            - chunk_count (optional): Number of chunks (default: 1)
            - file_size (optional): File size in bytes
            - embedding (optional): Vector embedding list
            - metadata (optional): Metadata dictionary
        config: Database configuration.

    Returns:
        Number of documents inserted/updated.

    Raises:
        ValueError: If documents list is empty or missing required fields.
        RuntimeError: If database operation fails.
    """
    if not documents:
        raise ValueError("Documents list cannot be empty")

    query = """
        INSERT INTO knowledge_base 
        (doc_id, content, filename, namespace, chunk_count, file_size, embedding, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            chunk_count = VALUES(chunk_count),
            file_size = VALUES(file_size),
            updated_at = CURRENT_TIMESTAMP
    """

    with get_db_connection(config) as conn:
        cursor = conn.cursor()
        try:
            values = []
            for doc in documents:
                if "doc_id" not in doc or "content" not in doc:
                    raise ValueError("Each document must have 'doc_id' and 'content' fields")

                embedding_json = json.dumps(doc.get("embedding")) if doc.get("embedding") else None
                metadata_json = json.dumps(doc.get("metadata")) if doc.get("metadata") else None

                values.append(
                    (
                        doc["doc_id"],
                        doc["content"],
                        doc.get("filename"),
                        doc.get("namespace"),
                        doc.get("chunk_count", 1),
                        doc.get("file_size"),
                        embedding_json,
                        metadata_json,
                    )
                )

            cursor.executemany(query, values)
            conn.commit()
            return cursor.rowcount
        except MySQLError as e:
            conn.rollback()
            raise RuntimeError(f"Failed to bulk insert knowledge documents: {e}") from e
        finally:
            cursor.close()


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


# ============================================================================
# System Reset Operations
# ============================================================================


def count_unique_sessions(
    config: DatabaseConfig | None = None,
) -> int:
    """
    Count unique session IDs in chat history.

    Args:
        config: Database configuration.

    Returns:
        Number of unique sessions.

    Raises:
        RuntimeError: If database operation fails.
    """
    query = "SELECT COUNT(DISTINCT session_id) as count FROM chat_history"

    with get_db_connection(config) as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            return result["count"] if result else 0
        except MySQLError as e:
            raise RuntimeError(f"Failed to count sessions: {e}") from e
        finally:
            cursor.close()

def delete_all_session_configs(
    config: DatabaseConfig | None = None,
) -> int:
    """
    Delete all session configurations.

    Args:
        config: Database configuration.

    Returns:
        Number of deleted rows.

    Raises:
        RuntimeError: If database operation fails.
    """
    query = "DELETE FROM session_configs"

    with get_db_connection(config) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            conn.commit()
            return cursor.rowcount
        except MySQLError as e:
            conn.rollback()
            raise RuntimeError(f"Failed to delete session configs: {e}") from e
        finally:
            cursor.close()

def delete_all_knowledge_base(
    config: DatabaseConfig | None = None,
) -> int:
    """
    Delete all documents from knowledge base.

    Args:
        config: Database configuration.

    Returns:
        Number of deleted rows.

    Raises:
        RuntimeError: If database operation fails.
    """
    query = "DELETE FROM knowledge_base"

    with get_db_connection(config) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            conn.commit()
            return cursor.rowcount
        except MySQLError as e:
            conn.rollback()
            raise RuntimeError(f"Failed to delete knowledge base: {e}") from e
        finally:
            cursor.close()

def get_namespace_document_counts(
    config: DatabaseConfig | None = None,
) -> list[dict[str, Any]]:
    """
    Get document counts and metadata grouped by namespace.

    Args:
        config: Database configuration.

    Returns:
        List of dictionaries with namespace statistics:
        - namespace: Namespace name (empty string for default)
        - document_count: Number of unique documents
        - total_chunks: Total number of chunks across all documents
        - last_updated: Most recent update timestamp

    Raises:
        RuntimeError: If database operation fails.
    """
    query = """
        SELECT 
            COALESCE(namespace, '') as namespace,
            COUNT(DISTINCT filename) as document_count,
            SUM(chunk_count) as total_chunks,
            MAX(updated_at) as last_updated
        FROM knowledge_base
        GROUP BY namespace
        ORDER BY last_updated DESC
    """

    with get_db_connection(config) as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            return results if results else []
        except MySQLError as e:
            raise RuntimeError(f"Failed to get namespace counts: {e}") from e
        finally:
            cursor.close()

def query_knowledge_base_documents(
    namespace: str | None = None,
    limit: int = 100,
    offset: int = 0,
    config: DatabaseConfig | None = None,
) -> dict[str, Any]:
    """
    Query documents from knowledge base with optional namespace filter and pagination.

    Args:
        namespace: Optional namespace to filter by (None = all namespaces).
        limit: Maximum number of documents to return (1-1000).
        offset: Number of documents to skip for pagination.
        config: Database configuration.

    Returns:
        Dictionary containing:
        - documents: List of document metadata dictionaries
        - total_count: Total number of documents matching filter
        - limit: Applied limit
        - offset: Applied offset

    Raises:
        RuntimeError: If database operation fails.
        ValueError: If limit is out of range.
    """
    if not 1 <= limit <= 1000:
        raise ValueError("Limit must be between 1 and 1000")

    # Build query with optional namespace filter
    where_clause = "WHERE namespace = %s" if namespace is not None else ""
    
    # Query for documents with aggregated chunk counts
    query = f"""
        SELECT 
            doc_id as id,
            filename,
            COALESCE(namespace, '') as namespace,
            SUM(chunk_count) as chunk_count,
            MAX(file_size) as file_size,
            MIN(created_at) as uploaded_at
        FROM knowledge_base
        {where_clause}
        GROUP BY doc_id, filename, namespace
        ORDER BY uploaded_at DESC
        LIMIT %s OFFSET %s
    """
    
    # Count query for total
    count_query = f"""
        SELECT COUNT(DISTINCT doc_id) as total
        FROM knowledge_base
        {where_clause}
    """

    with get_db_connection(config) as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # Get total count
            if namespace is not None:
                cursor.execute(count_query, (namespace,))
            else:
                cursor.execute(count_query)
            count_result = cursor.fetchone()
            total_count = count_result["total"] if count_result else 0

            # Get documents
            if namespace is not None:
                cursor.execute(query, (namespace, limit, offset))
            else:
                cursor.execute(query, (limit, offset))
            documents = cursor.fetchall()

            return {
                "documents": documents if documents else [],
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
            }
        except MySQLError as e:
            raise RuntimeError(f"Failed to query knowledge base documents: {e}") from e
        finally:
            cursor.close()

def get_table_counts(
    config: DatabaseConfig | None = None,
) -> dict[str, int]:
    """
    Get row counts for all major tables.

    Args:
        config: Database configuration.

    Returns:
        Dictionary with table names as keys and row counts as values.

    Raises:
        RuntimeError: If database operation fails.
    """
    tables = {
        "chat_history": "SELECT COUNT(*) as count FROM chat_history",
        "session_configs": "SELECT COUNT(*) as count FROM session_configs",
        "knowledge_base": "SELECT COUNT(*) as count FROM knowledge_base",
        "mpc_instances": "SELECT COUNT(*) as count FROM mpc_instances",
    }

    counts = {}
    with get_db_connection(config) as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            for table_name, query in tables.items():
                try:
                    cursor.execute(query)
                    result = cursor.fetchone()
                    counts[table_name] = result["count"] if result else 0
                except MySQLError:
                    # If table doesn't exist or query fails, set to 0
                    counts[table_name] = 0
            return counts
        except MySQLError as e:
            raise RuntimeError(f"Failed to get table counts: {e}") from e
        finally:
            cursor.close()
