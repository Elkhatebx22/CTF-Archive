#!/bin/bash

echo "Building Docker image..."
docker-compose build

echo "Starting Docker container..."
docker-compose up -d
