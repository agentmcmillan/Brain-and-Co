#!/bin/bash
# Deploy Brain-and-Co to NAS
set -e

NAS_HOST="CONTAINER_HOST_IP"
NAS_USER="claude"
DEPLOY_DIR="~/brain-and-co"

echo "=== Brain-and-Co Deployment ==="
echo "Target: ${NAS_USER}@${NAS_HOST}:${DEPLOY_DIR}"

# Create deploy tarball (exclude secrets, certs, git, local-only dirs)
echo "Creating deployment archive..."
tar czf /tmp/brain-and-co-deploy.tar.gz \
    --exclude='.git' \
    --exclude='.env' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.DS_Store' \
    --exclude='caddy/client-certs/*.key' \
    --exclude='caddy/client-certs/*.p12' \
    --exclude='caddy/client-certs/*.csr' \
    --exclude='caddy/client-certs/ca.key' \
    --exclude='caddy/client-certs/ca.srl' \
    --exclude='brain-wave' \
    --exclude='skills' \
    --exclude='rem' \
    --exclude='alpha-wave' \
    --exclude='beta-wave' \
    -C "$(dirname "$0")/.." .

# Copy to NAS
echo "Copying to NAS..."
ssh "${NAS_USER}@${NAS_HOST}" "mkdir -p ${DEPLOY_DIR}"
scp /tmp/brain-and-co-deploy.tar.gz "${NAS_USER}@${NAS_HOST}:${DEPLOY_DIR}/deploy.tar.gz"

# Extract and deploy
echo "Extracting and deploying..."
ssh "${NAS_USER}@${NAS_HOST}" << 'REMOTE'
cd ~/brain-and-co
# Atomic extraction: unpack to temp dir, then overlay (prevents partial state on failure)
TMPDIR=$(mktemp -d ./deploy-XXXXXX)
trap 'rm -rf "$TMPDIR"' EXIT
tar xzf deploy.tar.gz -C "$TMPDIR"
rm deploy.tar.gz
cp -a "$TMPDIR"/. .
rm -rf "$TMPDIR"
trap - EXIT

# Ensure .env exists with required vars
if [ ! -f .env ]; then
    cp .env.example .env
    echo "WARNING: Created .env from template — edit with real values before starting"
    echo "Required: POSTGRES_PASSWORD, MEMENTO_ACCESS_KEY, GITHUB_PERSONAL_ACCESS_TOKEN"
    exit 1
fi

# Verify required env vars are set (parse safely without shell execution)
while IFS='=' read -r key val; do
  [[ "$key" =~ ^#|^$ ]] && continue
  export "$key=$val"
done < .env
if [ -z "$POSTGRES_PASSWORD" ] || [ -z "$MEMENTO_ACCESS_KEY" ]; then
    echo "ERROR: POSTGRES_PASSWORD and MEMENTO_ACCESS_KEY must be set in .env"
    exit 1
fi

if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ] || [ "$GITHUB_PERSONAL_ACCESS_TOKEN" = "ghp_your_token_here" ]; then
    echo "WARNING: GITHUB_PERSONAL_ACCESS_TOKEN not set — github-mcp will not work"
fi

# Build and start
docker compose down 2>/dev/null || true
docker compose build
docker compose up -d

echo ""
echo "=== Waiting for gateway to become healthy ==="
for i in $(seq 1 30); do
  STATUS=$(curl -sf --max-time 10 http://localhost:9000/health 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null || echo "")
  if [ "$STATUS" = "ok" ] || [ "$STATUS" = "degraded" ]; then
    echo "Gateway ready (${STATUS}) after $((i*4))s"
    break
  fi
  sleep 4
done

echo ""
echo "=== Service Status ==="
docker compose ps

echo ""
echo "=== Health Checks ==="
echo -n "Memento MCP: "
curl -sf --max-time 10 http://localhost:56332/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null || echo "not ready yet"

echo -n "FastMCP Tools: "
python3 -c "import socket; s=socket.create_connection(('localhost',8091),2); s.close(); print('up')" 2>/dev/null || echo "not ready yet"

echo -n "MCP Gateway: "
curl -sf --max-time 10 http://localhost:9000/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{d.get(\"status\",\"unknown\")} ({d.get(\"connected\",0)}/{d.get(\"total_backends\",0)} backends)')" 2>/dev/null || echo "not ready yet"

echo ""
echo "=== Deployment Complete ==="
echo "Memento MCP:   http://CONTAINER_HOST_IP:56332/mcp"
echo "FastMCP Tools: http://CONTAINER_HOST_IP:8091/mcp"
echo "MCP Gateway:   http://CONTAINER_HOST_IP:9000/mcp"
echo "CF Tunnel:     https://YOUR_DOMAIN/gateway/mcp"
REMOTE

# Cleanup
rm -f /tmp/brain-and-co-deploy.tar.gz
echo "Done!"
