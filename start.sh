#!/bin/bash
# Railway startup script
# This script ensures proper directory and environment setup

set -e  # Exit on error

echo "Starting City Governance System Backend..."
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Change to backend directory if not already there
if [ ! -f "main.py" ]; then
    echo "Changing to backend directory..."
    cd backend
fi

echo "Backend directory contents:"
ls -la

echo "Python version:"
python --version

echo "Installing/checking dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Starting Uvicorn server on port ${PORT:-8000}..."
exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
