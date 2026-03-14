#!/bin/bash
# Brain-and-Co: Install brain-wave agents, hooks, rules, and skills into ~/.claude/
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "=== Brain-and-Co Setup ==="
echo "Installing from: $REPO_DIR"
echo "Target: $CLAUDE_DIR"

# --- Agents ---
echo ""
echo "Installing agents..."
mkdir -p "$CLAUDE_DIR/agents"
for agent in "$REPO_DIR"/brain-wave/agents/*.md; do
  name=$(basename "$agent")
  cp "$agent" "$CLAUDE_DIR/agents/$name"
  echo "  + agents/$name"
done

# --- Hooks ---
echo ""
echo "Installing hooks..."
mkdir -p "$CLAUDE_DIR/hooks"
for hook in "$REPO_DIR"/brain-wave/hooks/*.js; do
  name=$(basename "$hook")
  cp "$hook" "$CLAUDE_DIR/hooks/$name"
  echo "  + hooks/$name"
done

# --- Rules ---
echo ""
echo "Installing rules..."
mkdir -p "$CLAUDE_DIR/rules"
for rule in "$REPO_DIR"/brain-wave/rules/*.md; do
  name=$(basename "$rule")
  cp "$rule" "$CLAUDE_DIR/rules/$name"
  echo "  + rules/$name"
done

# --- Skills ---
echo ""
echo "Installing skills..."
for skill_dir in "$REPO_DIR"/skills/*/; do
  skill_name=$(basename "$skill_dir")
  mkdir -p "$CLAUDE_DIR/skills/$skill_name"
  cp -r "$skill_dir"* "$CLAUDE_DIR/skills/$skill_name/"
  echo "  + skills/$skill_name/"
done

echo ""
echo "=== Setup Complete ==="
echo "Restart Claude Code to load new agents, hooks, rules, and skills."
