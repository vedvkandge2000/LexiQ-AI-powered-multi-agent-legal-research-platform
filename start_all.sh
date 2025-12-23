#!/bin/bash

# LexiQ Full Stack Starter Script

echo "🚀 Starting LexiQ Full Stack Application..."
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Start backend
echo "📡 Starting Backend API..."
./start_backend.sh &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Frontend..."
./start_frontend.sh &
FRONTEND_PID=$!

echo ""
echo "═══════════════════════════════════════════════"
echo "  🏛️  LexiQ is running!"
echo "═══════════════════════════════════════════════"
echo ""
echo "  🌐 Frontend: http://localhost:5173"
echo "  📡 Backend:  http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "═══════════════════════════════════════════════"
echo ""

# Wait for both processes
wait

