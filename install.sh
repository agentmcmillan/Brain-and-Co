#!/bin/bash
# Brain-and-Co: One-line installer for Claude Code
# Usage: curl -fsSL https://raw.githubusercontent.com/agentmcmillan/Brain-and-Co/main/install.sh | bash
set -e

INSTALL_DIR="${BRAIN_AND_CO_DIR:-$HOME/Brain-and-Co}"
CLAUDE_DIR="$HOME/.claude"
REPO_URL="https://github.com/agentmcmillan/Brain-and-Co.git"

echo "=== Brain-and-Co Installer ==="
echo ""

# --- Clone or update ---
if [ -d "$INSTALL_DIR/.git" ]; then
  echo "Updating existing installation at $INSTALL_DIR..."
  cd "$INSTALL_DIR" && git pull --quiet
else
  echo "Cloning Brain-and-Co to $INSTALL_DIR..."
  git clone --quiet "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# --- Agents ---
echo ""
echo "Installing 15 agents..."
mkdir -p "$CLAUDE_DIR/agents"
cp .claude/agents/*.md "$CLAUDE_DIR/agents/"

# --- Rules ---
echo "Installing 6 rules..."
mkdir -p "$CLAUDE_DIR/rules"
cp .claude/rules/*.md "$CLAUDE_DIR/rules/"

# --- Hooks ---
echo "Installing hooks..."
HOOKS_DIR="$CLAUDE_DIR/hooks/brain-wave"
mkdir -p "$HOOKS_DIR"
for hook in integrations/hooks/*.js; do
  [ -f "$hook" ] || continue
  cp "$hook" "$HOOKS_DIR/"
  chmod +x "$HOOKS_DIR/$(basename "$hook")"
done

# --- Skills ---
echo "Installing 36 skills..."
for skill_dir in skills/*/; do
  skill_name=$(basename "$skill_dir")

  if ls "$skill_dir"*/SKILL.md &>/dev/null 2>&1; then
    for sub_skill_dir in "$skill_dir"*/; do
      sub_name=$(basename "$sub_skill_dir")
      mkdir -p "$CLAUDE_DIR/skills/$skill_name/$sub_name"
      cp -r "$sub_skill_dir"* "$CLAUDE_DIR/skills/$skill_name/$sub_name/"
    done
  elif [ -f "$skill_dir/SKILL.md" ]; then
    mkdir -p "$CLAUDE_DIR/skills/$skill_name"
    cp -r "$skill_dir"* "$CLAUDE_DIR/skills/$skill_name/"
  else
    mkdir -p "$CLAUDE_DIR/skills/$skill_name"
    cp -r "$skill_dir"* "$CLAUDE_DIR/skills/$skill_name/"
  fi
done

# --- Done ---
echo ""
echo "=== Installation Complete ==="
echo ""
echo "Installed to: $CLAUDE_DIR"
echo "  - 15 agents (memory, execution, quality)"
echo "  - 6 auto-loaded context rules"
echo "  - 36 skills (Brain-Wave, Ralph, GSD, hardware, review)"
echo "  - 6 auto-sync hooks"
echo ""
echo "Source repo: $INSTALL_DIR"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code"
echo "  2. In any project, run: use brain-wave-init agent"
echo ""
echo "To enable auto-sync hooks, merge the hook config into your settings:"
echo "  cat $INSTALL_DIR/integrations/hooks/settings-hooks.json"
echo ""
echo "For MCP infrastructure (Memento, Gateway, etc.):"
echo "  cd $INSTALL_DIR && cp .env.example .env && docker-compose up -d"
