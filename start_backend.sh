#!/bin/bash

# LexiQ Backend Starter Script

echo "🚀 Starting LexiQ Backend..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Install backend requirements if needed
if ! pip show fastapi > /dev/null 2>&1; then
    echo "📦 Installing backend dependencies..."
    pip install -r backend/requirements.txt
fi

# Start the FastAPI server
echo "🌐 Starting API server at http://localhost:8000"
cd backend
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

