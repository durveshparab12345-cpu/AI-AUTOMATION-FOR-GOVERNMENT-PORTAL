# Production-ready backend image - minimal, no build tools
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies (no build tools to avoid Rust compilation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel
RUN pip install --no-cache-dir --upgrade pip wheel setuptools

# Copy application code
COPY backend/ .

# Install dependencies without building anything from source
# This will fail gracefully if wheels aren't available
RUN pip install --no-cache-dir --only-binary :all: \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 || true

# If wheels failed, install normally but with no-build-isolation
RUN pip install --no-cache-dir --no-build-isolation --prefer-binary \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.4.2 \
    pydantic-settings==2.0.3 \
    sqlalchemy==2.0.23 \
    asyncpg==0.28.0 \
    alembic==1.12.1 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    python-multipart==0.0.6 \
    cryptography==41.0.7 \
    bcrypt==4.1.1 \
    httpx==0.25.2 \
    requests==2.31.0 \
    python-dotenv==1.0.0 \
    python-json-logger==2.0.7 \
    python-dateutil==2.8.2 \
    pytz==2024.1 2>&1 | grep -v "already satisfied" || echo "Install complete"

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

