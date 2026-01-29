"""
Setup Script for SOR Dashboard
Creates the necessary database tables
"""
import pymysql
from src.config import config

def setup_database():
    """Create dashboard tables in the database"""
    print("=" * 60)
    print("MindWorx SOR Dashboard Setup")
    print("=" * 60)

    try:
        # Connect to database
        print(f"\n📊 Connecting to database: {config.DB_NAME}...")
        conn = pymysql.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            port=config.DB_PORT
        )

        cursor = conn.cursor()

        # Read SQL file
        print("📄 Reading SQL schema...")
        with open('database_schema.sql', 'r') as f:
            sql_commands = f.read()

        # Execute SQL commands
        print("🔨 Creating tables...")

        # Split by semicolon and execute each statement
        for statement in sql_commands.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"  ✅ Executed: {statement[:50]}...")
                except Exception as e:
                    print(f"  ⚠️  Warning: {e}")

        conn.commit()
        print("\n✅ Database setup completed successfully!")
        print("\nCreated tables:")
        print("  - sor_requests")
        print("  - sor_audit_log")
        print("  - sor_settings")

        # Verify tables
        cursor.execute("SHOW TABLES LIKE 'sor_%'")
        tables = cursor.fetchall()
        print(f"\n📋 Found {len(tables)} SOR tables in database")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("Setup Complete! You can now run the dashboard.")
        print("Run: python run_dashboard.py")
        print("=" * 60)

    except FileNotFoundError:
        print("\n❌ Error: database_schema.sql not found")
        print("Make sure you're running this from the project root directory")
    except pymysql.Error as e:
        print(f"\n❌ Database error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    setup_database()
