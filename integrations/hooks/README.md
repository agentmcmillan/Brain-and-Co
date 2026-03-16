# Brain-Wave Hooks Integration

Automated hooks that keep the Brain-Wave memory system synchronized with your work.

## Overview

These hooks extend [claude-code-hooks](https://github.com/karanb192/claude-code-hooks) to automatically maintain Brain-Wave memory state:

| Hook | Type | Trigger | Purpose |
|------|------|---------|---------|
| `auto-sync-rem.js` | PostToolUse | Edit, Write | Updates REM changelog and session state |
| `auto-index-alpha.js` | PostToolUse | Write | Updates Alpha-Wave INDEX when files created |
| `session-checkpoint.js` | Notification | idle_prompt | Saves session state before timeout |
| `discovery-logger.js` | PostToolUse | Task | Logs agent discoveries to REM |
| `context-hint.js` | PreToolUse | Read | Suggests related files from Beta-Wave |

## Installation

1. Copy hooks to `~/.claude/hooks/brain-wave/`
2. Add configuration to `~/.claude/settings.json`
3. Restart Claude Code

## Configuration

Add to your `~/.claude/settings.json`:

```json
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
```

## How It Works

### Auto-Sync REM (PostToolUse)
After every Edit/Write, automatically:
- Appends change to `rem/CHANGELOG.md`
- Updates `rem/LAST-RUN.md` with current timestamp
- Tracks file modification patterns

### Auto-Index Alpha (PostToolUse)
When new files are created:
- Adds entry to `alpha-wave/INDEX.md`
- Updates `alpha-wave/TOPICS.md` if topic detected
- Queues file for summary generation

### Session Checkpoint (Notification)
When Claude goes idle:
- Saves current working state to `rem/sessions/`
- Creates restoration checkpoint
- Logs elapsed time and files touched

### Discovery Logger (PostToolUse)
After agent tasks complete:
- Extracts patterns and insights
- Logs to `rem/discoveries/`
- Updates decision records if applicable

### Context Hint (PreToolUse)
Before reading a file:
- Checks Beta-Wave connections
- Suggests related files
- Provides inline context

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `BRAIN_WAVE_ROOT` | `./` | Project root with Brain-Wave dirs |
| `BRAIN_WAVE_AUTO_SYNC` | `true` | Enable/disable auto-sync |
| `BRAIN_WAVE_VERBOSE` | `false` | Detailed logging |

## Testing

```bash
# Run tests
npm test

# Test individual hook
echo '{"tool":"Edit","file":"/path/to/file.md"}' | node auto-sync-rem.js
```

## Limitations

- Hooks run synchronously; keep them fast (<100ms)
- Large projects may need throttling
- Context hints limited to 5 suggestions

---

## Shell-Based Alternatives

For simpler setups without Node.js, use these bash scripts:

### Pre-Session (Startup Message)
```bash
#!/bin/bash
# brain-wave-pre-session.sh
if [ -f "rem/restoration/PROTOCOL.md" ]; then
  echo "[brain-wave] Memory ready - 'use rem agent' to sync"
fi
```

### Post-Edit (Change Tracking)
```bash
#!/bin/bash
# brain-wave-post-edit.sh
FILE_PATH="$1"
[ -z "$FILE_PATH" ] && exit 0
[[ "$FILE_PATH" == *alpha-wave* ]] && exit 0
[[ "$FILE_PATH" == *beta-wave* ]] && exit 0
[[ "$FILE_PATH" == *rem* ]] && exit 0
[ -d "rem" ] && echo "$FILE_PATH" >> .brain-wave-pending
```

### Session-End (Auto Capture)
```bash
#!/bin/bash
# brain-wave-session-end.sh
[ ! -d "rem/sessions" ] && exit 0
[ ! -f ".brain-wave-pending" ] && exit 0
TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)
cat > "rem/sessions/auto-$TIMESTAMP.md" << EOF
# Auto-Captured: $TIMESTAMP
## Files
$(cat .brain-wave-pending | sort -u | sed 's/^/- /')
EOF
rm -f .brain-wave-pending
```

---

## OpenClaw/ClawHub Compatibility

These hooks follow the [Agent Skill Convention](https://docs.openclaw.ai/tools/skills) for portability across AI coding assistants.
