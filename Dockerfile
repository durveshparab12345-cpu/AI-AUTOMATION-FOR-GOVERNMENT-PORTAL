# Ultra-minimal Docker image - avoids all Python build issues
FROM python:3.10-slim

WORKDIR /app

# System dependencies (minimal, no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy backend code
COPY backend/ .

# Install ONLY packages with guaranteed pre-built wheels for Python 3.10
# Using older pydantic versions that have wheels
RUN pip install --no-cache-dir --only-binary :all: \
    'fastapi==0.100.0' \
    'uvicorn[standard]==0.23.2' \
    'pydantic==2.0.3' \
    'sqlalchemy==2.0.20' \
    'asyncpg==0.27.0' \
    'alembic==1.12.0' \
    'cryptography==41.0.3' \
    'bcrypt==4.0.1' \
    'python-jose[cryptography]==3.3.0' \
    'passlib[bcrypt]==1.7.4' \
    'python-multipart==0.0.6' \
    'httpx==0.24.1' \
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

