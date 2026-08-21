# Production Dockerfile for RACE (Revenue Adaptive Control Engine)
FROM python:3.12-slim

WORKDIR /app

# Set non-buffering environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HOST=0.0.0.0

# Install minimal system tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY pyproject.toml .
COPY README.md .

# Install dependencies in production mode
RUN pip install --no-cache-dir -e .

# Copy application packages and assets
COPY backend/ backend/
COPY data/ data/
COPY datasets/ datasets/
COPY docs/ docs/
COPY evaluation/ evaluation/
COPY frontend/ frontend/
COPY integrations/ integrations/

# Security: non-root execution user
RUN useradd -m -u 1000 raceuser && \
    chown -R raceuser:raceuser /app
USER raceuser

# Expose HTTP port
EXPOSE 8000

# Container health probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production entrypoint
CMD ["python", "-m", "uvicorn", "backend.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
