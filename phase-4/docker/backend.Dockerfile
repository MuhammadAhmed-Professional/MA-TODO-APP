# Multi-stage Dockerfile for FastAPI Backend with UV
# Based on existing phase-2/backend/Dockerfile but optimized for Kubernetes

# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv for faster Python package installation
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies into a virtual environment
RUN uv pip install --system --no-cache -r pyproject.toml

# Stage 2: Runner (Production)
FROM python:3.12-slim AS runner
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code and configuration
COPY src/ ./src/
COPY alembic.ini ./

# Verify migrations are present (critical for database schema)
RUN test -d src/db/migrations/versions || (echo "ERROR: Migration files missing!" && exit 1)

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Start the FastAPI application
# Using PORT environment variable for flexibility (defaults to 8000)
CMD sh -c "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"
