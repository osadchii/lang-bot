#!/bin/bash
set -e

echo "Starting Greek Language Learning Bot..."

# Parse database connection details from DATABASE_URL or environment variables
if [ -n "$DATABASE_URL" ]; then
    # Extract from DATABASE_URL (format: postgresql+asyncpg://user:pass@host:port/db)
    DB_HOST=$(echo $DATABASE_URL | sed -E 's|.*@([^:]+):.*|\1|')
    DB_USER=$(echo $DATABASE_URL | sed -E 's|.*://([^:]+):.*|\1|')
    DB_NAME=$(echo $DATABASE_URL | sed -E 's|.*/([^?]+).*|\1|')
else
    # Use individual environment variables
    DB_HOST="${POSTGRES_HOST:-db}"
    DB_USER="${POSTGRES_USER:-postgres}"
    DB_NAME="${POSTGRES_DB:-langbot}"
fi

export PGPASSWORD="${POSTGRES_PASSWORD}"

echo "Waiting for PostgreSQL at ${DB_HOST}..."

# Wait for PostgreSQL to be ready (30 retries, 2s interval)
RETRIES=30
RETRY_INTERVAL=2
RETRY_COUNT=0

until pg_isready -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))

    if [ $RETRY_COUNT -ge $RETRIES ]; then
        echo "ERROR: PostgreSQL did not become ready after ${RETRIES} attempts"
        exit 1
    fi

    echo "PostgreSQL is unavailable - attempt ${RETRY_COUNT}/${RETRIES}, waiting ${RETRY_INTERVAL}s..."
    sleep $RETRY_INTERVAL
done

echo "PostgreSQL is ready!"

# Test database connection with a query
echo "Testing database connection..."
if ! psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    echo "ERROR: Failed to connect to database"
    exit 1
fi

echo "Database connection successful!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

if [ $? -ne 0 ]; then
    echo "ERROR: Database migrations failed"
    exit 1
fi

echo "Migrations completed successfully!"

# Start the bot (use exec for proper signal handling)
echo "Starting bot..."
exec python -m bot
