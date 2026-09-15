#!/bin/bash

# GitBad CTF Challenge Deployment Script

echo "🚀 Starting GitBad CTF Challenge deployment..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check for both docker-compose and docker compose (newer versions)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Using: $DOCKER_COMPOSE"


# Build and start the services
echo "🔨 Building and starting services..."
$DOCKER_COMPOSE down --remove-orphans 2>/dev/null || true
$DOCKER_COMPOSE up --build -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

# Check if services are running
if $DOCKER_COMPOSE ps | grep -q "Up"; then
    echo "✅ GitBad CTF Challenge is now running!"
    echo ""
    echo "🌐 Access points:"
    echo "   Main application: http://localhost"
else
    echo "❌ Failed to start services. Check the logs:"
    echo "   $DOCKER_COMPOSE logs"
    exit 1
fi
