#!/bin/bash
# Brain-Wave Hooks Installation Script
#
# Installs Brain-Wave hooks to ~/.claude/hooks/ and updates settings.json

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
HOOKS_DIR="$CLAUDE_DIR/hooks/brain-wave"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"

echo "🧠 Brain-Wave Hooks Installer"
echo "=============================="

# Create hooks directory
echo "📁 Creating hooks directory..."
mkdir -p "$HOOKS_DIR"

# Copy hook scripts
echo "📋 Copying hook scripts..."
cp "$SCRIPT_DIR/auto-sync-rem.js" "$HOOKS_DIR/"
cp "$SCRIPT_DIR/auto-index-alpha.js" "$HOOKS_DIR/"
cp "$SCRIPT_DIR/session-checkpoint.js" "$HOOKS_DIR/"
cp "$SCRIPT_DIR/discovery-logger.js" "$HOOKS_DIR/"
cp "$SCRIPT_DIR/context-hint.js" "$HOOKS_DIR/"
cp "$SCRIPT_DIR/README.md" "$HOOKS_DIR/"

# Make scripts executable
chmod +x "$HOOKS_DIR"/*.js

echo "✅ Hook scripts installed to $HOOKS_DIR"

# Check if settings.json exists
if [ ! -f "$SETTINGS_FILE" ]; then
    echo "⚠️  No settings.json found at $SETTINGS_FILE"
    echo "   Please create one and add the hooks configuration manually."
    echo ""
    echo "   Example configuration:"
    cat << 'EOF'
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "node ~/.claude/hooks/brain-wave/auto-sync-rem.js"
      },
      {
        "matcher": "Write",
        "command": "node ~/.claude/hooks/brain-wave/auto-index-alpha.js"
      },
      {
        "matcher": "Task",
        "command": "node ~/.claude/hooks/brain-wave/discovery-logger.js"
      }
    ],
    "Notification": [
      {
        "matcher": "idle_prompt",
        "command": "node ~/.claude/hooks/brain-wave/session-checkpoint.js"
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Read",
        "command": "node ~/.claude/hooks/brain-wave/context-hint.js"
      }
    ]
  }
}
EOF
    exit 0
fi

# Check if hooks are already configured
if grep -q "brain-wave" "$SETTINGS_FILE" 2>/dev/null; then
    echo "⚠️  Brain-Wave hooks appear to already be configured in settings.json"
    echo "   Please review $SETTINGS_FILE manually if you want to update."
    exit 0
fi

echo ""
echo "📝 To complete installation, add this to your $SETTINGS_FILE:"
echo ""
cat << 'EOF'
Add to your "hooks" section:

"hooks": {
  "PostToolUse": [
    {
      "matcher": "Edit|Write",
      "command": "node ~/.claude/hooks/brain-wave/auto-sync-rem.js"
    },
    {
      "matcher": "Write",
      "command": "node ~/.claude/hooks/brain-wave/auto-index-alpha.js"
    },
    {
      "matcher": "Task",
      "command": "node ~/.claude/hooks/brain-wave/discovery-logger.js"
    }
  ],
  "Notification": [
    {
      "matcher": "idle_prompt",
      "command": "node ~/.claude/hooks/brain-wave/session-checkpoint.js"
    }
  ],
  "PreToolUse": [
    {
      "matcher": "Read",
      "command": "node ~/.claude/hooks/brain-wave/context-hint.js"
    }
  ]
}
EOF

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Add the hooks configuration to ~/.claude/settings.json"
echo "2. Restart Claude Code"
echo "3. The hooks will automatically maintain your Brain-Wave memory"
echo ""
echo "Environment variables (optional):"
echo "  BRAIN_WAVE_ROOT       - Project root (default: cwd)"
echo "  BRAIN_WAVE_AUTO_SYNC  - Enable/disable sync (default: true)"
echo "  BRAIN_WAVE_VERBOSE    - Verbose logging (default: false)"
