#!/bin/bash
set -e

echo "=== AI Portal Backend Build Script ==="
echo "Step 1: Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

echo "Step 2: Installing pre-built dependencies..."
# Install in stages to avoid timeout
pip install --prefer-binary fastapi uvicorn pydantic

echo "Step 3: Installing remaining dependencies..."
pip install --prefer-binary -r requirements.txt

echo "Step 4: Running database migrations..."
python -m alembic upgrade head

echo "=== Build Complete ==="
