#!/usr/bin/env bash
set -euo pipefail

NAS_HOST="claude@CONTAINER_HOST_IP"
REMOTE_DIR="~/symphony"

echo "==> Deploying Symphony to container host..."

# Create remote directory
ssh "$NAS_HOST" "mkdir -p $REMOTE_DIR"

# Sync project files (exclude .env, data, venv)
rsync -avz --delete \
    --exclude '.env' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude 'data/' \
    --exclude '.git' \
    . "$NAS_HOST:$REMOTE_DIR/"

echo "==> Building and starting containers..."
ssh "$NAS_HOST" "cd $REMOTE_DIR && docker compose up -d --build"

echo "==> Checking health..."
sleep 5
ssh "$NAS_HOST" "curl -sf http://localhost:9100/health && echo ' OK' || echo ' FAILED'"

echo "==> Done."
