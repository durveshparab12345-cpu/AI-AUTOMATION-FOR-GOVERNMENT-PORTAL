# Ultra-minimal Docker image - avoids all Python build issues
FROM python:3.11-slim

WORKDIR /app

# System dependencies (minimal, no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip

# Copy backend code
COPY backend/ .

# Install all dependencies in ONE layer with workarounds for pydantic-core
RUN pip install --no-cache-dir \
    --prefer-binary \
    'fastapi==0.104.1' \
    'uvicorn[standard]==0.24.0' \
    'pydantic==2.4.2' \
    'pydantic-settings==2.0.3' \
    'sqlalchemy==2.0.23' \
    'asyncpg==0.28.0' \
    'alembic==1.12.1' \
    'python-jose[cryptography]==3.3.0' \
    'passlib[bcrypt]==1.7.4' \
    'python-multipart==0.0.6' \
    'cryptography==41.0.7' \
    'bcrypt==4.1.1' \
    'httpx==0.25.2' \
    'requests==2.31.0' \
    'python-dotenv==1.0.0' \
    'python-json-logger==2.0.7' \
    'python-dateutil==2.8.2' \
    'pytz==2024.1'

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
