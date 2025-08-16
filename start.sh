#!/bin/bash

# AI Travel Guide - Quick Start Script
echo "🚀 Starting AI Travel Guide Application..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before running the application"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "🐳 Starting with Docker Compose..."
docker compose up -d

echo "✅ Application started successfully!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 To stop: docker compose down"
echo "📊 To view logs: docker compose logs -f"
