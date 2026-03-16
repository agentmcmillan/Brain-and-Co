#!/bin/bash
# Brain-and-Co: Install agents, hooks, rules, and skills into ~/.claude/
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
for agent in "$REPO_DIR"/.claude/agents/*.md; do
  name=$(basename "$agent")
  cp "$agent" "$CLAUDE_DIR/agents/$name"
  echo "  + agents/$name"
done

# --- Rules ---
echo ""
echo "Installing rules..."
mkdir -p "$CLAUDE_DIR/rules"
for rule in "$REPO_DIR"/.claude/rules/*.md; do
  name=$(basename "$rule")
  cp "$rule" "$CLAUDE_DIR/rules/$name"
  echo "  + rules/$name"
done

# --- Hooks ---
echo ""
echo "Installing hooks..."
HOOKS_DIR="$CLAUDE_DIR/hooks/brain-wave"
mkdir -p "$HOOKS_DIR"
for hook in "$REPO_DIR"/integrations/hooks/*.js; do
  [ -f "$hook" ] || continue
  name=$(basename "$hook")
  cp "$hook" "$HOOKS_DIR/$name"
  chmod +x "$HOOKS_DIR/$name"
  echo "  + hooks/brain-wave/$name"
done

# --- Skills ---
echo ""
echo "Installing skills..."
for skill_dir in "$REPO_DIR"/skills/*/; do
  skill_name=$(basename "$skill_dir")

  # Check for nested skill groups (e.g., hardware/, gsd/)
  if ls "$skill_dir"*/SKILL.md &>/dev/null 2>&1; then
    echo "  Installing $skill_name skill group..."
    for sub_skill_dir in "$skill_dir"*/; do
      sub_name=$(basename "$sub_skill_dir")
      mkdir -p "$CLAUDE_DIR/skills/$skill_name/$sub_name"
      cp -r "$sub_skill_dir"* "$CLAUDE_DIR/skills/$skill_name/$sub_name/"
      echo "    + skills/$skill_name/$sub_name/"
    done
  elif [ -f "$skill_dir/SKILL.md" ]; then
    mkdir -p "$CLAUDE_DIR/skills/$skill_name"
    cp -r "$skill_dir"* "$CLAUDE_DIR/skills/$skill_name/"
    echo "  + skills/$skill_name/"
  else
    mkdir -p "$CLAUDE_DIR/skills/$skill_name"
    cp -r "$skill_dir"* "$CLAUDE_DIR/skills/$skill_name/"
    echo "  + skills/$skill_name/ (reference)"
  fi
done

# --- Summary ---
AGENT_COUNT=$(ls -1 "$REPO_DIR"/.claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
RULE_COUNT=$(ls -1 "$REPO_DIR"/.claude/rules/*.md 2>/dev/null | wc -l | tr -d ' ')
HOOK_COUNT=$(ls -1 "$REPO_DIR"/integrations/hooks/*.js 2>/dev/null | wc -l | tr -d ' ')
SKILL_COUNT=$(find "$REPO_DIR/skills" -name 'SKILL.md' 2>/dev/null | wc -l | tr -d ' ')

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Installed: $AGENT_COUNT agents, $RULE_COUNT rules, $HOOK_COUNT hooks, $SKILL_COUNT skills"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code"
echo "  2. Run: use brain-wave-init agent"
echo ""
echo "To enable auto-sync hooks, merge integrations/hooks/settings-hooks.json"
echo "into ~/.claude/settings.json"
echo ""
echo "For infrastructure deployment: ./deploy/deploy.sh"
