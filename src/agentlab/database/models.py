"""
Database table models and schema definitions.

Defines the structure for:
- KnowledgeBase: Stores documents and embeddings for RAG
- ChatHistory: Stores conversation history
- MPCInstances: Tracks MPC server instances
"""

from dataclasses import dataclass
from datetime import datetime


# SQL Schema Definitions (to be executed during database setup)

CREATE_KNOWLEDGE_BASE_TABLE = """
CREATE TABLE IF NOT EXISTS knowledge_base (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doc_id VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    embedding JSON,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_doc_id (doc_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

CREATE_CHAT_HISTORY_TABLE = """
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
"""

CREATE_MPC_INSTANCES_TABLE = """
CREATE TABLE IF NOT EXISTS mpc_instances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    instance_id VARCHAR(255) UNIQUE NOT NULL,
    status ENUM('running', 'stopped', 'error') NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_instance_id (instance_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

CREATE_SESSION_CONFIGS_TABLE = """
CREATE TABLE IF NOT EXISTS session_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    memory_config JSON NOT NULL,
    rag_config JSON NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

ALL_TABLES = [
    CREATE_KNOWLEDGE_BASE_TABLE,
    CREATE_CHAT_HISTORY_TABLE,
    CREATE_MPC_INSTANCES_TABLE,
    CREATE_SESSION_CONFIGS_TABLE,
]


@dataclass
class KnowledgeBaseRow:
    """Represents a row in the knowledge_base table."""

    id: int
    doc_id: str
    content: str
    embedding: list[float] | None
    metadata: dict
    created_at: datetime
    updated_at: datetime


@dataclass
class ChatHistoryRow:
    """Represents a row in the chat_history table."""

    id: int
    session_id: str
    role: str
    content: str
    metadata: dict | None
    created_at: datetime


@dataclass
class MPCInstanceRow:
    """Represents a row in the mpc_instances table."""

    id: int
    instance_id: str
    status: str
    host: str
    port: int
    metadata: dict | None
    created_at: datetime
    updated_at: datetime


@dataclass
class SessionConfigRow:
    """Represents a row in the session_configs table."""

    id: int
    session_id: str
    memory_config: dict
    rag_config: dict
    metadata: dict | None
    created_at: datetime
    updated_at: datetime
