#!/usr/bin/env python3
"""Run SQL migration to add created_at column to users table."""

import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Construct from individual components
    db_user = os.getenv("DATABASE_USER")
    db_pass = os.getenv("DATABASE_PASS")
    db_host = os.getenv("DATABASE_HOST")
    db_name = os.getenv("DATABASE_DB")

    if not all([db_user, db_pass, db_host, db_name]):
        print("Error: Database configuration not found in environment variables")
        sys.exit(1)

    DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}"

print(
    f"Using database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'unknown'}"
)

# Read the migration file
migration_file = "migrations/02_add_created_at_to_users.sql"

try:
    with open(migration_file, "r") as f:
        migration_sql = f.read()

    # Create engine and execute migration
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Split by semicolon and execute each statement
        statements = [
            s.strip()
            for s in migration_sql.split(";")
            if s.strip() and not s.strip().startswith("--")
        ]

        for statement in statements:
            if statement:
                print(f"Executing: {statement[:100]}...")
                conn.execute(text(statement))

        conn.commit()
        print("✓ Migration completed successfully!")

except FileNotFoundError:
    print(f"Error: Migration file not found: {migration_file}")
    sys.exit(1)
except Exception as e:
    print(f"Error executing migration: {e}")
    sys.exit(1)
