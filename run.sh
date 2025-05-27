#!/bin/bash

# Exit on any error
set -e

echo "🔧 Starting LangGraph Game App..."

# Step 1: Activate virtual environment (optional - uncomment if using venv)
# source venv/bin/activate

# Step 2: Start FastAPI backend in background
echo "🚀 Launching FastAPI backend on http://localhost:8000..."
uvicorn app.backend.main:app --host 0.0.0.0 --port 8000 --reload &

# Store backend PID to terminate later
BACKEND_PID=$!

# Wait a bit to ensure backend is ready
sleep 2

# Step 3: Launch Streamlit frontend
echo "🌐 Opening Streamlit frontend on http://localhost:8501..."
streamlit run app/streamlit_ui.py

# Step 4: Cleanup – stop FastAPI backend when Streamlit closes
echo "🛑 Stopping backend..."
kill $BACKEND_PID
