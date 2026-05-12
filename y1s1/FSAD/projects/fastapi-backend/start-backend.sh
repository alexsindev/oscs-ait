#!/bin/bash
# Start Backend Development Server

echo "Starting AT70.05 Backend..."
echo ""

# Check if database is running
if ! docker ps | grep -q "at7005-backend-db"; then
    echo "Starting PostgreSQL database..."
    docker-compose -f docker-compose-db.yml up -d
    echo "Database started"
    sleep 2
else
    echo "Database already running"
fi

# Activate virtual environment
source .venv/bin/activate

# Run migrations
echo ""
echo "Running database migrations..."
for migration_file in migrations/*.sql; do
    if [ -f "$migration_file" ]; then
        echo "Applying migration: $(basename $migration_file)"
        python -c "
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Get database URL
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    db_user = os.getenv('DATABASE_USER')
    db_pass = os.getenv('DATABASE_PASS')
    db_host = os.getenv('DATABASE_HOST', 'localhost')
    db_name = os.getenv('DATABASE_DB')
    db_port = os.getenv('DATABASE_PORT', '5432')
    DATABASE_URL = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

# Read and execute migration
with open('$migration_file', 'r') as f:
    migration_sql = f.read()

# Execute entire migration file as one statement (handles DO blocks)
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text(migration_sql))
    conn.commit()
print('✓ Migration applied successfully')
" || echo "⚠ Migration already applied or failed"
    fi
done

echo ""
echo "Migrations complete!"
echo ""

# Start FastAPI server
echo "Starting FastAPI server..."
fastapi dev app/main.py
