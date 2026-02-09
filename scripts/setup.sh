#!/bin/bash

# Network Monitor Setup Script

set -e

echo "🚀 Setting up Distributed Network Monitor..."

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/prometheus
mkdir -p data/grafana
mkdir -p data/redis
mkdir -p logs

# Set permissions
echo "🔧 Setting permissions..."
chmod -R 755 data/
chmod -R 755 logs/

# Copy environment file
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Build and start services
echo "🏗️  Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Print access information
echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Services are running:"
echo "   Load Balancer API:    http://localhost:5000"
echo "   Dashboard:           http://localhost:3000"
echo "   Grafana:             http://localhost:3001 (admin/admin)"
echo "   Prometheus:          http://localhost:9090"
echo ""
echo "🔄 To stop services: docker-compose down"
echo "📝 To view logs: docker-compose logs -f"
echo "🔧 To rebuild: docker-compose up -d --build"
echo ""

# Test the setup
echo "🧪 Testing setup..."
curl -f http://localhost:5000/ || echo "⚠️  Load balancer not ready yet"
curl -f http://localhost:5001/health || echo "⚠️  Server 1 not ready yet"
curl -f http://localhost:5002/health || echo "⚠️  Server 2 not ready yet"
curl -f http://localhost:5003/health || echo "⚠️  Server 3 not ready yet"

echo ""
echo "🎉 Setup complete! Enjoy monitoring your network!"