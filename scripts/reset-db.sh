#!/bin/bash

set -e

echo "Stopping Docker containers..."
docker compose down

echo "Removing SurrealDB volume..."
VOLUME_NAME=$(docker volume ls | grep -i surreal | awk '{print $2}' | head -1)

if [ -z "$VOLUME_NAME" ]; then
    echo "No SurrealDB volume found. Trying default name..."
    docker volume rm cinebrain_surreal_data 2>/dev/null || echo "Volume not found, may already be removed"
else
    echo "Found volume: $VOLUME_NAME"
    docker volume rm "$VOLUME_NAME" 2>/dev/null || echo "Volume may already be removed"
fi

echo "Starting services..."
docker compose up -d

echo "Waiting for SurrealDB to be ready..."
sleep 5

echo ""
echo "✅ Database reset complete!"
echo "The database is now empty and fixtures will be loaded automatically on first startup."
echo ""
echo "To manually reload fixtures:"
echo "  curl -X POST http://localhost:8001/api/fixtures/load"

