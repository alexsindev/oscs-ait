#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done

echo "PostgreSQL is ready!"
echo "Running database migrations..."

# Run all SQL migration files in order
for migration_file in /docker-entrypoint-initdb.d/migrations/*.sql; do
    if [ -f "$migration_file" ]; then
        echo "Executing migration: $(basename $migration_file)"
        psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -f "$migration_file"
    fi
done

echo "Database migrations completed!"
