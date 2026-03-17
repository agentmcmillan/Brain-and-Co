#!/bin/bash
# Deploy Claude Code Remote Control as a systemd user service on container host
set -e

NAS_HOST="CONTAINER_HOST_IP"
NAS_USER="claude"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/claude-remote-control.service"

echo "=== Claude Code Remote Control Deployment ==="
echo "Target: ${NAS_USER}@${NAS_HOST}"

# 1. Verify prerequisites on container host
echo ""
echo "Checking prerequisites..."
ssh "${NAS_USER}@${NAS_HOST}" << 'CHECK'
set -e
echo -n "  Claude CLI: "
claude --version 2>&1 | head -1
echo -n "  Workspace: "
if [ -d ~/brain-and-co ]; then
    echo "~/brain-and-co exists"
else
    echo "ERROR: ~/brain-and-co not found. Run deploy.sh first."
    exit 1
fi
echo -n "  Git repo: "
if [ -d ~/brain-and-co/.git ]; then
    echo "yes (worktree spawn ready)"
else
    echo "WARNING: ~/brain-and-co is not a git repo. Initializing..."
    cd ~/brain-and-co
    git init
    git add -A
    git commit -m "Initial deploy" --allow-empty
    echo "  Git repo initialized"
fi
CHECK

# 2. Enable linger (allows user services to run after logout)
echo ""
echo "Enabling linger for user ${NAS_USER}..."
ssh "${NAS_USER}@${NAS_HOST}" << 'LINGER'
LINGER_STATUS=$(loginctl show-user claude -p Linger --value 2>/dev/null || echo "no")
if [ "$LINGER_STATUS" = "no" ]; then
    echo "  Requesting linger enable (requires sudo)..."
    sudo loginctl enable-linger claude
    echo "  Linger enabled"
else
    echo "  Linger already enabled"
fi
LINGER

# 3. Install systemd user service
echo ""
echo "Installing systemd user service..."
scp "$SERVICE_FILE" "${NAS_USER}@${NAS_HOST}:/tmp/claude-remote-control.service"
ssh "${NAS_USER}@${NAS_HOST}" << 'INSTALL'
mkdir -p ~/.config/systemd/user
mv /tmp/claude-remote-control.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable claude-remote-control.service
echo "  Service installed and enabled"
INSTALL

# 4. Start (or restart) the service
echo ""
echo "Starting service..."
ssh "${NAS_USER}@${NAS_HOST}" << 'START'
systemctl --user restart claude-remote-control.service
sleep 3
STATUS=$(systemctl --user is-active claude-remote-control.service 2>/dev/null || echo "unknown")
echo "  Service status: $STATUS"
if [ "$STATUS" = "active" ]; then
    echo ""
    echo "  Remote Control is running!"
    echo ""
    echo "  Connect from:"
    echo "    - https://claude.ai/code (look for 'Brain-and-Co')"
    echo "    - Claude mobile app (iOS/Android)"
else
    echo ""
    echo "  WARNING: Service not active. Check logs:"
    echo "    ssh claude@CONTAINER_HOST_IP journalctl --user -u claude-remote-control -f"
fi
START

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Management commands (run on container host):"
echo "  systemctl --user status claude-remote-control"
echo "  systemctl --user restart claude-remote-control"
echo "  journalctl --user -u claude-remote-control -f"
