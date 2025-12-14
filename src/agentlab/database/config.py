"""
Database configuration for MySQL connection.

Handles connection credentials and database configuration settings.
Uses environment variables for sensitive data.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class DatabaseConfig:
    """Configuration for MySQL database connection."""

    host: str
    port: int
    user: str
    password: str
    database: str
    charset: str = "utf8mb4"

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """
        Create configuration from environment variables.

        Expected environment variables:
        - DB_HOST: Database host (default: localhost)
        - DB_PORT: Database port (default: 3306)
        - DB_USER: Database username
        - DB_PASSWORD: Database password
        - DB_NAME: Database name

        Returns:
            DatabaseConfig instance.

        Raises:
            ValueError: If required environment variables are missing.
        """
        required_vars = ["DB_USER", "DB_PASSWORD", "DB_NAME"]
        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")

        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", ""),
        )
