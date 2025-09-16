#!/bin/bash

# Exam Seat Planning System - Quick Run Script
# This script activates the virtual environment and starts the Django server

echo "🚀 Starting Exam Seat Planning System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./setup.sh first to set up the project."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Navigate to Django project directory
cd seatplanning

# Start the development server
echo "🌐 Starting Django development server..."
echo "📍 Server will be available at: http://127.0.0.1:8000/"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python manage.py runserver