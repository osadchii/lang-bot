# Multi-stage build for Greek Language Learning Bot

# Stage 1: Base image with system dependencies
FROM python:3.13-slim AS base

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Stage 2: Dependencies installation
FROM base AS dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Production image
FROM base AS production

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash botuser && \
    chown -R botuser:botuser /app

# Copy installed packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=botuser:botuser bot/ /app/bot/
COPY --chown=botuser:botuser migrations/ /app/migrations/
COPY --chown=botuser:botuser alembic.ini /app/alembic.ini
COPY --chown=botuser:botuser entrypoint.sh /app/entrypoint.sh

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER botuser

# Health check: verify bot process is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD pgrep -f "python -m bot" || exit 1

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
