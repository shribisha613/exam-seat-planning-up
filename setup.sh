#!/bin/bash

# Exam Seat Planning System - Easy Setup Script
# This script sets up the virtual environment and installs all dependencies

echo "🎯 Setting up Exam Seat Planning System..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Navigate to Django project directory
cd seatplanning

# Check if migrations need to be applied
echo "🗄️  Checking database migrations..."
python manage.py showmigrations

# Apply any pending migrations
echo "⚡ Applying migrations..."
python manage.py migrate

echo "✅ Setup complete!"
echo ""
echo "🚀 To run the server:"
echo "   1. source venv/bin/activate"
echo "   2. cd seatplanning" 
echo "   3. python manage.py runserver"
echo ""
echo "🌐 Then visit: http://127.0.0.1:8000/"
echo "🔧 Admin panel: http://127.0.0.1:8000/admin/"