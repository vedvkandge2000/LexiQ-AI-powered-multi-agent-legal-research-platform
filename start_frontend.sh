#!/bin/bash

# LexiQ Frontend Starter Script

echo "🚀 Starting LexiQ Frontend..."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting development server at http://localhost:5173"
npm run dev

