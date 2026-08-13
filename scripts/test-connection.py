#!/usr/bin/env python3
"""Simple database connection test."""

import psycopg2
import sys

try:
    print("Attempting connection to PostgreSQL...")
    print("Host: 127.0.0.1")
    print("Port: 5432")
    print("Database: agentbench")
    print("User: postgres")
    print()

    conn = psycopg2.connect(
        host="127.0.0.1", port=5432, database="agentbench", user="postgres", password="postgres"
    )

    print("✓ Connection successful!")

    cursor = conn.cursor()
    cursor.execute("SELECT version()")
    version = cursor.fetchone()[0]
    print(f"PostgreSQL version: {version}")

    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
    table_count = cursor.fetchone()[0]
    print(f"Tables in database: {table_count}")

    conn.close()
    sys.exit(0)

except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)
