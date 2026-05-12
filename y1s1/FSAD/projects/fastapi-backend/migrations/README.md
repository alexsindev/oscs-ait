# Database Migrations

This directory contains SQL migration files that are automatically applied when the application starts.

## How Migrations Work

### Docker Deployment
When running with Docker (`docker-compose up`), the `docker-entrypoint.sh` script:
1. Waits for the PostgreSQL database to be ready
2. Automatically runs all `.sql` files in this directory in alphabetical order
3. Starts the FastAPI application

### Local Development
When running locally (`./start-backend.sh`), the startup script:
1. Ensures the database is running
2. Automatically runs all `.sql` files in this directory
3. Starts the FastAPI development server

## Creating a New Migration

1. Create a new SQL file with a numbered prefix: `XX_description.sql`
   - Example: `03_add_new_field.sql`
   - Use sequential numbering to ensure proper ordering

2. Write idempotent SQL using `IF NOT EXISTS` clauses:
   ```sql
   -- Add new column
   ALTER TABLE table_name
   ADD COLUMN IF NOT EXISTS new_column VARCHAR(255);
   
   -- Create index
   CREATE INDEX IF NOT EXISTS idx_name ON table_name(column);
   ```

3. The migration will be automatically applied on next startup

## Existing Migrations

- `01_create_admin_user.sql` - Creates initial admin user
- `02_add_created_at_to_users.sql` - Adds created_at timestamp to users table

## Best Practices

1. **Always use idempotent operations** - Use `IF NOT EXISTS`, `IF EXISTS`, etc.
2. **Test locally first** - Run `./start-backend.sh` to test migrations before deploying
3. **Keep migrations simple** - One logical change per file
4. **Never modify existing migrations** - Create a new migration to fix issues
5. **Use descriptive names** - Make it clear what the migration does

## Manual Migration (Emergency)

If you need to run migrations manually:

```bash
# Using the Python script
python run_migration.py

# Or connect directly to PostgreSQL
psql -h localhost -U your_user -d your_db -f migrations/XX_migration.sql
```

## Troubleshooting

- **Migration fails**: Check PostgreSQL logs and ensure SQL syntax is correct
- **Already applied**: Migrations use `IF NOT EXISTS` so they're safe to re-run
- **Database not ready**: The entrypoint script waits for the database, but you may need to increase the timeout in docker-compose healthcheck
