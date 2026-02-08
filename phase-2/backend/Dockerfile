FROM python:3.12-slim

# Force Railway redeploy - 2025-12-28
# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv for faster Python package installation
RUN pip install --no-cache-dir uv

# Copy dependency files first (for better Docker layer caching)
COPY pyproject.toml ./

# Install Python dependencies
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy source code and configuration
COPY src/ ./src/
COPY alembic.ini ./

# Explicitly ensure migrations are included (critical for Railway deployment)
# The .dockerignore may exclude test files, so we verify migrations are present
RUN test -d src/db/migrations/versions || (echo "ERROR: Migration files missing!" && exit 1)

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose the port
EXPOSE 8000



# Start the application using Railway's PORT environment variable
CMD sh -c "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"
