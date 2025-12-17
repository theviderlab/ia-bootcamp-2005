"""
Database setup and table management.

Provides functions to:
- Check if tables exist
- Count rows in existing tables
- Warn users about data loss
- Create or recreate database tables
"""

from typing import Protocol

import mysql.connector

from agentlab.database.config import DatabaseConfig
from agentlab.database.models import ALL_TABLES


class DatabaseConnection(Protocol):
    """Protocol for database connection objects."""

    def cursor(self) -> mysql.connector.cursor.MySQLCursor: ...
    def commit(self) -> None: ...


def check_table_exists(connection: DatabaseConnection, table_name: str) -> bool:
    """
    Check if a table exists in the database.

    Args:
        connection: Active database connection.
        table_name: Name of the table to check.

    Returns:
        True if table exists, False otherwise.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            AND table_name = %s
            """,
            (table_name,),
        )
        result = cursor.fetchone()
        return result[0] > 0 if result else False


def count_table_rows(connection: DatabaseConnection, table_name: str) -> int:
    """
    Count the number of rows in a table.

    Args:
        connection: Active database connection.
        table_name: Name of the table to count.

    Returns:
        Number of rows in the table.
    """
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        result = cursor.fetchone()
        return result[0] if result else 0


def get_existing_tables_info(connection: DatabaseConnection) -> dict[str, int]:
    """
    Get information about existing tables and their row counts.

    Args:
        connection: Active database connection.

    Returns:
        Dictionary mapping table names to row counts.
    """
    tables = ["knowledge_base", "chat_history", "mpc_instances"]
    table_info = {}

    for table in tables:
        if check_table_exists(connection, table):
            row_count = count_table_rows(connection, table)
            table_info[table] = row_count

    return table_info


def prompt_user_confirmation(message: str) -> bool:
    """
    Prompt user for confirmation with yes/no response.

    Args:
        message: Message to display to the user.

    Returns:
        True if user confirms, False otherwise.
    """
    response = input(f"\n⚠️  {message}\nContinue? (yes/no): ").strip().lower()
    return response in ("yes", "y")


def drop_table(connection: DatabaseConnection, table_name: str) -> None:
    """
    Drop a table from the database.

    Args:
        connection: Active database connection.
        table_name: Name of the table to drop.
    """
    with connection.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    connection.commit()


def create_tables(connection: DatabaseConnection) -> None:
    """
    Create all database tables defined in models.py.

    Args:
        connection: Active database connection.
    """
    with connection.cursor() as cursor:
        for table_sql in ALL_TABLES:
            cursor.execute(table_sql)
    connection.commit()


def setup_database(config: DatabaseConfig, force: bool = False) -> None:
    """
    Set up database tables with user confirmation for data loss.

    Args:
        config: Database configuration.
        force: If True, skip user confirmation prompts.

    Raises:
        RuntimeError: If user cancels setup due to data loss warning.
    """
    connection = mysql.connector.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database,
        charset=config.charset,
    )

    try:
        # Check for existing tables
        existing_tables = get_existing_tables_info(connection)

        if existing_tables and not force:
            print("\n📊 Existing tables found:")
            has_data = False
            for table, row_count in existing_tables.items():
                print(f"   - {table}: {row_count} rows")
                if row_count > 0:
                    has_data = True

            if has_data:
                warning = (
                    "Setting up the database will DROP and RECREATE all tables.\n"
                    "   ALL EXISTING DATA WILL BE LOST!"
                )
                if not prompt_user_confirmation(warning):
                    raise RuntimeError("Setup cancelled by user.")

        # Drop existing tables
        for table in ["mpc_instances", "chat_history", "knowledge_base"]:
            if table in existing_tables:
                drop_table(connection, table)
                print(f"✓ Dropped table: {table}")

        # Create tables
        create_tables(connection)
        print("\n✅ Database setup completed successfully!")
        print("   Created tables:")
        print("   - knowledge_base")
        print("   - chat_history")
        print("   - mpc_instances")

    finally:
        connection.close()
