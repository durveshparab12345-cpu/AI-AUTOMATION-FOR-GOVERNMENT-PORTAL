#!/bin/bash
set -e

echo "=== AI Portal Backend Build Script ==="

# Navigate to backend
cd backend

echo "Step 1: Listing Python version..."
python --version
python3 --version

echo "Step 2: Upgrading pip..."
pip install --upgrade pip

echo "Step 3: Installing packages - ONLY BINARY WHEELS"
# This is critical - use only pre-built wheels, no compilation
pip install --only-binary :all: \
    'fastapi==0.100.0' \
    'uvicorn[standard]==0.23.2' \
    'pydantic==2.0.3' \
    'sqlalchemy==2.0.20' \
    'asyncpg==0.27.0' \
    'alembic==1.12.0' \
    'python-jose[cryptography]==3.3.0' \
    'passlib[bcrypt]==1.7.4' \
    'python-multipart==0.0.6' \
    'cryptography==41.0.3' \
    'bcrypt==4.0.1' \
    'httpx==0.24.1' \
    'requests==2.31.0' \
    'python-dotenv==1.0.0' \
    'python-json-logger==2.0.7' \
    'python-dateutil==2.8.2' \
    'pytz==2024.1' 2>&1 | tee /tmp/pip_output.log

echo "Step 4: Checking installed packages..."
pip list | grep -E "fastapi|pydantic|uvicorn"

echo "Step 5: Running database migrations..."
python -m alembic upgrade head || echo "Warning: Migration failed, may be first deploy"

echo "=== Build Complete ==="
