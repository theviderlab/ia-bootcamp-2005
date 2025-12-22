"""
Database migration script for User Profile feature.

Adds the user_profiles table to existing database.
Safe to run multiple times (uses CREATE TABLE IF NOT EXISTS).
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentlab.database.crud import initialize_database, get_table_counts


def run_migration():
    """Run the database migration."""
    
    print("\n" + "="*60)
    print(" USER PROFILE TABLE MIGRATION")
    print("="*60 + "\n")
    
    print("📊 Checking current database state...")
    
    try:
        counts = get_table_counts()
        print(f"  ✓ chat_history: {counts.get('chat_history', 0)} rows")
        print(f"  ✓ session_configs: {counts.get('session_configs', 0)} rows")
        print(f"  ✓ knowledge_base: {counts.get('knowledge_base', 0)} rows")
        print(f"  ✓ mpc_instances: {counts.get('mpc_instances', 0)} rows")
        
        has_profile_table = counts.get('user_profiles', -1) >= 0
        
        if has_profile_table:
            print(f"  ✓ user_profiles: {counts['user_profiles']} rows (already exists)")
        else:
            print(f"  ⚠ user_profiles: Not found")
        
    except Exception as e:
        print(f"  ⚠ Could not check existing tables: {e}")
        has_profile_table = False
    
    print(f"\n{'='*60}")
    print("Running database initialization...")
    print(f"{'='*60}\n")
    
    try:
        initialize_database()
        print("✓ Database tables created/verified")
        
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False
    
    print(f"\n{'='*60}")
    print("Verifying user_profiles table...")
    print(f"{'='*60}\n")
    
    try:
        counts_after = get_table_counts()
        
        if counts_after.get('user_profiles', -1) >= 0:
            print(f"✓ user_profiles table exists")
            print(f"  Current rows: {counts_after['user_profiles']}")
            
            if not has_profile_table:
                print(f"  ✨ Table successfully created!")
            else:
                print(f"  ℹ Table already existed (no changes needed)")
            
        else:
            print("❌ user_profiles table not found after migration")
            return False
            
    except Exception as e:
        print(f"❌ Failed to verify table: {e}")
        return False
    
    print(f"\n{'='*60}")
    print("Migration Summary")
    print(f"{'='*60}\n")
    
    print("✅ Migration completed successfully!")
    print("\nDatabase schema updated with:")
    print("  • user_profiles table")
    print("    - id (INT, PRIMARY KEY, AUTO_INCREMENT)")
    print("    - profile_data (JSON)")
    print("    - version (INT)")
    print("    - last_updated_message_id (INT, nullable)")
    print("    - created_at (TIMESTAMP)")
    print("    - updated_at (TIMESTAMP)")
    print("    - INDEX on updated_at")
    
    print("\n📚 Next steps:")
    print("  1. Run profile extraction: POST /api/memory/profile/extract")
    print("  2. View documentation: docs/USER_PROFILE_QUICKSTART.md")
    print("  3. Try demo: python src/agentlab/examples/profile_extraction_demo.py")
    
    return True


def rollback_migration():
    """
    Rollback migration (drop user_profiles table).
    
    WARNING: This will delete all profile data!
    """
    
    print("\n" + "="*60)
    print(" ROLLBACK USER PROFILE TABLE")
    print("="*60 + "\n")
    
    response = input("⚠️  WARNING: This will DELETE the user_profiles table and all data!\n   Continue? (yes/no): ")
    
    if response.lower() != "yes":
        print("\nRollback cancelled.")
        return
    
    try:
        from agentlab.database.crud import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS user_profiles")
            conn.commit()
            cursor.close()
        
        print("\n✓ user_profiles table dropped")
        print("\nRollback completed successfully.")
        
    except Exception as e:
        print(f"\n❌ Rollback failed: {e}")


def main():
    """Main entry point."""
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        success = run_migration()
        
        if not success:
            print("\n❌ Migration failed!")
            sys.exit(1)
        
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
