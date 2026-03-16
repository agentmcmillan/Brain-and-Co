#!/bin/bash
# Create a new Brain-Wave agent worktree
# Usage: ./create-agent.sh <agent-name> [role]

set -e

AGENT_NAME="${1:?Usage: $0 <agent-name> [role]}"
ROLE="${2:-general}"
WORKTREE_DIR=".worktrees/$AGENT_NAME"
BRANCH_NAME="brain-wave/$AGENT_NAME"

echo "=== Creating Brain-Wave Agent: $AGENT_NAME ==="

# Check if worktree already exists
if [ -d "$WORKTREE_DIR" ]; then
  echo "Error: Worktree already exists at $WORKTREE_DIR"
  exit 1
fi

# Create worktree with new branch
echo "Creating worktree at $WORKTREE_DIR..."
git worktree add "$WORKTREE_DIR" -b "$BRANCH_NAME"

# Create agent identity file
echo "Creating agent identity..."
mkdir -p "$WORKTREE_DIR/rem"
cat > "$WORKTREE_DIR/rem/agent-id.json" << EOF
{
  "id": "$AGENT_NAME",
  "worktree": "$WORKTREE_DIR",
  "branch": "$BRANCH_NAME",
  "role": "$ROLE",
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "parent": "main"
}
EOF

# Create agent-specific session directory
mkdir -p "$WORKTREE_DIR/rem/sessions"
mkdir -p "$WORKTREE_DIR/rem/discoveries"

# Create initial session
cat > "$WORKTREE_DIR/rem/sessions/init.md" << EOF
# Agent Session: $AGENT_NAME
> Created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
> Role: $ROLE
> Branch: $BRANCH_NAME

## Purpose
[Describe what this agent is working on]

## Status
Initialized and ready.

## Notes
- Parent: main
- Worktree: $WORKTREE_DIR
EOF

echo ""
echo "=== Agent Created ==="
echo "Worktree: $WORKTREE_DIR"
echo "Branch: $BRANCH_NAME"
echo "Role: $ROLE"
echo ""
echo "To work as this agent:"
echo "  cd $WORKTREE_DIR"
echo ""
echo "To merge back to main:"
echo "  git checkout main"
echo "  git merge $BRANCH_NAME --no-ff"
echo ""
echo "To remove agent:"
echo "  git worktree remove $WORKTREE_DIR"
echo "  git branch -d $BRANCH_NAME"
