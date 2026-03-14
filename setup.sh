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

# --- Skills (top-level) ---
echo ""
echo "Installing skills..."
for skill_dir in "$REPO_DIR"/skills/*/; do
  skill_name=$(basename "$skill_dir")
  # Skip directories that contain subdirectories (nested skill groups like hardware/)
  if ls "$skill_dir"*/SKILL.md &>/dev/null; then
    # Nested skill group (e.g., skills/hardware/bom-review/SKILL.md)
    echo "  Installing $skill_name skill group..."
    for sub_skill_dir in "$skill_dir"*/; do
      sub_name=$(basename "$sub_skill_dir")
      mkdir -p "$CLAUDE_DIR/skills/$skill_name/$sub_name"
      cp -r "$sub_skill_dir"* "$CLAUDE_DIR/skills/$skill_name/$sub_name/"
      echo "    + skills/$skill_name/$sub_name/"
    done
  else
    # Flat skill (e.g., skills/code-review/SKILL.md)
    mkdir -p "$CLAUDE_DIR/skills/$skill_name"
    cp -r "$skill_dir"* "$CLAUDE_DIR/skills/$skill_name/"
    echo "  + skills/$skill_name/"
  fi
done

echo ""
echo "=== Setup Complete ==="
echo "Restart Claude Code to load new agents, hooks, rules, and skills."
