"""
Entry point for database setup module.

Enables running: python -m agentlab.database.setup
or via Makefile: make setup-db
"""

import sys

from agentlab.database.config import DatabaseConfig
from agentlab.database.setup import setup_database


def main() -> None:
    """
    Main entry point for database setup.

    Loads configuration from environment variables and sets up the database.
    Handles errors gracefully with appropriate exit codes.
    """
    try:
        print("🗄️  Database Setup")
        print("=" * 50)

        # Load configuration
        print("\n📋 Loading configuration from environment...")
        config = DatabaseConfig.from_env()
        print(f"   Host: {config.host}:{config.port}")
        print(f"   Database: {config.database}")
        print(f"   User: {config.user}")

        # Setup database
        force = "--force" in sys.argv
        setup_database(config, force=force)

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}", file=sys.stderr)
        print("\nPlease ensure these environment variables are set:")
        print("   - DB_HOST (default: localhost)")
        print("   - DB_PORT (default: 3306)")
        print("   - DB_USER")
        print("   - DB_PASSWORD")
        print("   - DB_NAME")
        sys.exit(1)

    except RuntimeError as e:
        print(f"\n⚠️  {e}", file=sys.stderr)
        sys.exit(130)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user", file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
