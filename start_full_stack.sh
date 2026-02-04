#!/bin/bash

echo "========================================"
echo "Starting City Governance Full Stack"
echo "========================================"
echo ""
echo "This will start:"
echo "  1. Backend API (Port 8000)"
echo "  2. Frontend Dev Server (Port 5173)"
echo ""
echo "Press Ctrl+C to stop all services"
echo "========================================"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "Starting Backend..."
python start_backend.py &
BACKEND_PID=$!

sleep 3

# Start frontend
echo "Starting Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "Services Running!"
echo "========================================"
echo ""
echo "Backend:   http://localhost:8000"
echo "Frontend:  http://localhost:5173"
echo "Test Page: http://localhost:5173/#test"
echo "API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo "========================================"
echo ""

# Wait for processes
wait
