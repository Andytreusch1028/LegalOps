#!/usr/bin/env python3
"""
Database Setup Script for Legal Ops Platform
Handles PostgreSQL database creation, schema setup, and initial data
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
from pathlib import Path

class DatabaseSetup:
    def __init__(self, host='localhost', port=5432, user='postgres', password=None, database='legalops'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password or os.getenv('POSTGRES_PASSWORD', 'password')
        self.database = database
        self.connection = None
        
    def connect(self, database=None):
        """Connect to PostgreSQL server"""
        db_name = database or 'postgres'  # Connect to default postgres db for setup
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=db_name
            )
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            print(f"✅ Connected to PostgreSQL server")
            return True
        except psycopg2.Error as e:
            print(f"❌ Failed to connect to PostgreSQL: {e}")
            return False
    
    def create_database(self):
        """Create the Legal Ops database"""
        if not self.connection:
            print("❌ No database connection")
            return False
            
        try:
            cursor = self.connection.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.database,))
            if cursor.fetchone():
                print(f"✅ Database '{self.database}' already exists")
                cursor.close()
                return True
            
            # Create database
            cursor.execute(f'CREATE DATABASE "{self.database}"')
            print(f"✅ Created database '{self.database}'")
            cursor.close()
            return True
            
        except psycopg2.Error as e:
            print(f"❌ Failed to create database: {e}")
            return False
    
    def setup_schema(self):
        """Set up the database schema"""
        if not self.connection:
            print("❌ No database connection")
            return False
            
        # Read schema file
        schema_file = Path(__file__).parent / "database_schema.sql"
        if not schema_file.exists():
            print(f"❌ Schema file not found: {schema_file}")
            return False
            
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            cursor = self.connection.cursor()
            cursor.execute(schema_sql)
            cursor.close()
            print("✅ Database schema created successfully")
            return True
            
        except psycopg2.Error as e:
            print(f"❌ Failed to create schema: {e}")
            return False
    
    def verify_setup(self):
        """Verify the database setup"""
        if not self.connection:
            print("❌ No database connection")
            return False
            
        try:
            cursor = self.connection.cursor()
            
            # Check tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")
            
            # Check initial data
            cursor.execute("SELECT COUNT(*) FROM services")
            service_count = cursor.fetchone()[0]
            print(f"✅ Found {service_count} services")
            
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"✅ Found {user_count} users")
            
            cursor.close()
            return True
            
        except psycopg2.Error as e:
            print(f"❌ Failed to verify setup: {e}")
            return False
    
    def create_connection_string(self):
        """Create connection string for application use"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def setup_complete(self):
        """Run complete database setup"""
        print("🚀 Starting Legal Ops Platform Database Setup")
        print("=" * 50)
        
        # Step 1: Connect to PostgreSQL server
        if not self.connect():
            return False
        
        # Step 2: Create database
        if not self.create_database():
            return False
        
        # Step 3: Connect to new database
        self.connection.close()
        if not self.connect(self.database):
            return False
        
        # Step 4: Setup schema
        if not self.setup_schema():
            return False
        
        # Step 5: Verify setup
        if not self.verify_setup():
            return False
        
        print("=" * 50)
        print("🎉 Database setup completed successfully!")
        print(f"📊 Database: {self.database}")
        print(f"🔗 Connection: {self.create_connection_string()}")
        print("=" * 50)
        
        return True
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Legal Ops Platform Database Setup")
    parser.add_argument("--host", default="localhost", help="PostgreSQL host")
    parser.add_argument("--port", type=int, default=5432, help="PostgreSQL port")
    parser.add_argument("--user", default="postgres", help="PostgreSQL user")
    parser.add_argument("--password", help="PostgreSQL password")
    parser.add_argument("--database", default="legalops", help="Database name")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing setup")
    
    args = parser.parse_args()
    
    # Create database setup instance
    db_setup = DatabaseSetup(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database
    )
    
    try:
        if args.verify_only:
            # Just verify existing setup
            if db_setup.connect(args.database):
                db_setup.verify_setup()
        else:
            # Full setup
            db_setup.setup_complete()
    
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
    except Exception as e:
        print(f"❌ Setup failed: {e}")
    finally:
        db_setup.close()

if __name__ == "__main__":
    main()
