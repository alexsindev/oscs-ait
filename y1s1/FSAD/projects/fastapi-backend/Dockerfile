FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && pip install --upgrade pip \
    && apt-get purge -y --auto-remove build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY pyproject.toml /app/pyproject.toml

# Install Python dependencies
RUN pip install --no-cache-dir .

# Copy application code
COPY app /app/app

# Copy migrations and entrypoint script
COPY migrations /app/migrations
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/uploads && \
    chmod +x /app/docker-entrypoint.sh && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run application using entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
