#!/bin/bash
set -e

echo "===================================="
echo "Starting AT70.05 Backend Container"
echo "===================================="

# Wait for database to be ready
echo "Waiting for database to be ready..."
until python -c "
import sys
import psycopg2
import os
try:
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT', '5432'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASS'),
        dbname=os.getenv('DATABASE_DB')
    )
    conn.close()
    print('Database is ready!')
    sys.exit(0)
except Exception as e:
    print(f'Database not ready: {e}')
    sys.exit(1)
" 2>/dev/null; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is ready!"
echo ""

# Run database migrations
echo "Running database migrations..."
for migration_file in /app/migrations/*.sql; do
    if [ -f "$migration_file" ]; then
        echo "Applying migration: $(basename $migration_file)"
        python -c "
import os
from sqlalchemy import create_engine, text

# Construct database URL
db_user = os.getenv('DATABASE_USER')
db_pass = os.getenv('DATABASE_PASS')
db_host = os.getenv('DATABASE_HOST')
db_name = os.getenv('DATABASE_DB')
db_port = os.getenv('DATABASE_PORT', '5432')

DATABASE_URL = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

# Read migration file
with open('$migration_file', 'r') as f:
    migration_sql = f.read()

# Execute migration as a single transaction
# Don't split by semicolons - SQL may contain DO blocks with internal semicolons
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    # Execute the entire migration file as one statement
    conn.execute(text(migration_sql))
    conn.commit()
    print('✓ Migration applied successfully')
"
    fi
done

echo ""
echo "Migrations complete!"
echo "===================================="
echo "Starting FastAPI application..."
echo "===================================="
echo ""

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port ${UVICORN_PORT:-8000}
