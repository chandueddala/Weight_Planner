#!/bin/bash
# Docker Build and Run Script for Weight Planner

set -e  # Exit on error

echo "========================================="
echo "Weight Planner - Docker Build Script"
echo "========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file from .env.docker template:"
    echo "  cp .env.docker .env"
    echo "  nano .env  # Edit with your credentials"
    exit 1
fi

# Check if required environment variables are set
echo "✓ Checking environment variables..."
source .env

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ "$AWS_ACCESS_KEY_ID" = "your-aws-access-key-id" ]; then
    echo "❌ Error: AWS_ACCESS_KEY_ID not configured in .env"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-openai-api-key-here" ]; then
    echo "❌ Error: OPENAI_API_KEY not configured in .env"
    exit 1
fi

echo "✓ Environment variables configured"
echo ""

# Build Docker image
echo "========================================="
echo "Building Docker image..."
echo "========================================="
docker build -t weight-planner:latest .

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Docker image built successfully!"
else
    echo ""
    echo "❌ Docker build failed"
    exit 1
fi

echo ""
echo "========================================="
echo "Starting container with docker-compose..."
echo "========================================="
docker-compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Container started successfully!"
    echo ""
    echo "========================================="
    echo "Application is running!"
    echo "========================================="
    echo ""
    echo "Access the app at: http://localhost:8501"
    echo ""
    echo "Useful commands:"
    echo "  View logs:    docker-compose logs -f"
    echo "  Stop:         docker-compose down"
    echo "  Restart:      docker-compose restart"
    echo "  Shell access: docker exec -it weight-planner-app bash"
    echo ""
else
    echo ""
    echo "❌ Failed to start container"
    exit 1
fi
