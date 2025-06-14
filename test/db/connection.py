"""
Simple test for database connection
Run with: uv run python test_connection.py
"""

import os
import sys

from src.db.connection import DatabaseConnection


def main():
    """Test database connection"""
    print("🔌 Testing database connection...")
    
    # Debug: Show what environment variables are loaded
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🐛 Debug - Environment variables:")
    print(f"   MYSQL_HOST: '{os.getenv('MYSQL_HOST')}'")
    print(f"   MYSQL_PORT: '{os.getenv('MYSQL_PORT')}'")
    print(f"   MYSQL_USER: '{os.getenv('MYSQL_USER')}'")
    print(f"   MYSQL_PASSWORD: '{os.getenv('MYSQL_PASSWORD')}'")
    
    try:
        # Create connection
        db = DatabaseConnection()
        print(f"📋 Config: {db.user}@{db.host}:{db.port}/{db.database}")
        
        # Test connection
        connection = db.connect()
        print("✅ Connection successful!")
        
        # Test simple query
        result = db.execute_query("SELECT 1 as test, DATABASE() as current_db")
        print(f"🔍 Test query result: {result[0]}")
        
        # Test database and tables
        tables = db.execute_query("SHOW TABLES")
        if tables:
            print(f"📊 Found {len(tables)} tables:")
            for table in tables:
                table_name = list(table.values())[0]
                print(f"  - {table_name}")
        else:
            print("📊 No tables found")
        
        # Close connection
        db.close()
        print("🚪 Connection closed")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Make sure:")
        print("  1. Docker containers are running: docker-compose up -d")
        print("  2. .env file has correct values")
        print("  3. MySQL is ready (wait a few seconds after starting)")


if __name__ == "__main__":
    main()