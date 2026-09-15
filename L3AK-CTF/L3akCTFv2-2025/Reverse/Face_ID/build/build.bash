#!/bin/bash

docker-compose build

docker-compose up -d

echo "Docker Compose build complete. Service is running in the background."