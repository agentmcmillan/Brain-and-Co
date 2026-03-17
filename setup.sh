#!/bin/bash
# Brain-and-Co: Install agents, hooks, rules, and skills into ~/.claude/
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "=== Brain-and-Co Setup ==="
echo "Installing from: $REPO_DIR"
echo "Target: $CLAUDE_DIR"

# --- Check for updates ---
if [ -d "$REPO_DIR/.git" ] && command -v git &>/dev/null; then
  echo ""
  echo "Checking for updates..."
  git -C "$REPO_DIR" fetch --quiet origin 2>/dev/null || true
  LOCAL=$(git -C "$REPO_DIR" rev-parse HEAD 2>/dev/null)
  REMOTE=$(git -C "$REPO_DIR" rev-parse origin/main 2>/dev/null)
  if [ -n "$LOCAL" ] && [ -n "$REMOTE" ] && [ "$LOCAL" != "$REMOTE" ]; then
    BEHIND=$(git -C "$REPO_DIR" rev-list --count HEAD..origin/main 2>/dev/null || echo 0)
    if [ "$BEHIND" -gt 0 ]; then
      echo "  Update available: $BEHIND commit(s) behind origin/main"
      read -r -p "  Pull latest changes before installing? [Y/n] " answer
      if [ -z "$answer" ] || [[ "$answer" =~ ^[Yy] ]]; then
        git -C "$REPO_DIR" pull --ff-only origin main
        echo "  Updated to $(git -C "$REPO_DIR" rev-parse --short HEAD)"
        echo ""
        echo "  Restarting setup with updated files..."
        exec "$0" "$@"
      else
        echo "  Skipping update, installing current version."
      fi
    else
      echo "  Already up to date."
    fi
  else
    echo "  Already up to date."
  fi
fi

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

# --- gstack (headless browser + dev workflow skills) ---
echo ""
echo "Installing gstack..."
GSTACK_SRC="$REPO_DIR/gstack"
GSTACK_DST="$CLAUDE_DIR/skills/gstack"

if [ -d "$GSTACK_SRC" ]; then
  # Copy gstack source (preserving structure for build)
  mkdir -p "$GSTACK_DST"
  rsync -a --delete \
    --exclude='node_modules' \
    --exclude='browse/dist' \
    --exclude='.git' \
    --exclude='.gstack' \
    --exclude='bun.lock' \
    --exclude='*.bun-build' \
    "$GSTACK_SRC/" "$GSTACK_DST/"

  # Link gstack sub-skills (browse, qa, review, ship, etc.)
  for skill_dir in "$GSTACK_DST"/*/; do
    if [ -f "$skill_dir/SKILL.md" ]; then
      skill_name="$(basename "$skill_dir")"
      [ "$skill_name" = "node_modules" ] && continue
      target="$CLAUDE_DIR/skills/$skill_name"
      if [ -L "$target" ] || [ ! -e "$target" ]; then
        ln -snf "gstack/$skill_name" "$target"
        echo "  + skills/$skill_name -> gstack/$skill_name"
      fi
    fi
  done

  # Build browse binary if bun is available
  if command -v bun &>/dev/null; then
    echo "  Building gstack browse binary..."
    (cd "$GSTACK_DST" && ./setup 2>&1 | sed 's/^/  /')
  else
    echo "  Note: Install bun (https://bun.sh) then run: cd $GSTACK_DST && ./setup"
  fi
else
  echo "  Skipped (gstack/ not found in repo)"
fi

# --- Summary ---
AGENT_COUNT=$(ls -1 "$REPO_DIR"/.claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
RULE_COUNT=$(ls -1 "$REPO_DIR"/.claude/rules/*.md 2>/dev/null | wc -l | tr -d ' ')
HOOK_COUNT=$(ls -1 "$REPO_DIR"/integrations/hooks/*.js 2>/dev/null | wc -l | tr -d ' ')
SKILL_COUNT=$(find "$REPO_DIR/skills" -name 'SKILL.md' 2>/dev/null | wc -l | tr -d ' ')
GSTACK_SKILL_COUNT=$(find "$REPO_DIR/gstack" -maxdepth 2 -name 'SKILL.md' 2>/dev/null | wc -l | tr -d ' ')

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Installed: $AGENT_COUNT agents, $RULE_COUNT rules, $HOOK_COUNT hooks, $SKILL_COUNT + $GSTACK_SKILL_COUNT skills"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code"
echo "  2. Run: use brain-wave-init agent"
echo ""
echo "To enable auto-sync hooks, merge integrations/hooks/settings-hooks.json"
echo "into ~/.claude/settings.json"
echo ""
echo "Remote Control (optional):"
echo "  Enable interactive oversight from claude.ai/code or Claude mobile app."
echo "  - Global toggle: claude /config -> enable Remote Control"
echo "  - NAS always-on: ./deploy/deploy-remote-control.sh"
echo "  - Symphony tasks: set remote_control: true in symphony.yaml or per-task"
echo "  - Ralph runner:   ./ralph/ralph-runner.sh --rc"
echo ""
echo "For infrastructure deployment: ./deploy/deploy.sh"
