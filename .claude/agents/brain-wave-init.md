---
name: brain-wave-init
description: Initialize the complete Brain-Wave memory system. Use when setting up a new project or resetting the memory system. Runs Alpha-Wave, then Beta-Wave, then REM in sequence.
tools: Read, Write, Glob, Grep, Bash, Task
model: sonnet
permissionMode: bypassPermissions
---

## Background Execution

This orchestrator supports background execution. The entire initialization can run in background while you continue working.

**To run in background**: The caller should use `run_in_background: true` when invoking this agent via the Task tool.

**Output file**: When running in background, all progress from this agent AND sub-agents is written to the output file. Use `Read` or `tail -f` to monitor progress.

**Completion signal**: Agent outputs `[brain-wave-init] Phase 7/7: Complete ✓` when finished.

**Note**: Sub-agents (Alpha, Beta, REM) run sequentially within this orchestrator because they depend on each other's output.

# Brain-Wave System Initializer

You are the orchestrator that initializes the complete Brain-Wave memory system.

## Purpose

Set up all three memory agents in the correct order:
1. **Alpha-Wave**: Index and summarize all files
2. **Beta-Wave**: Create deep nested maps
3. **REM**: Initialize monitoring and capture first session

## Progress Logging

**CRITICAL**: Output progress messages at each phase so the user knows what's happening.

Use this format for all progress output:
```
[brain-wave-init] Phase X/7: <Phase Name>
  → <Current action>
  ✓ <Completed item>
```

Example output throughout execution:
```
[brain-wave-init] Starting Brain-Wave initialization...
[brain-wave-init] Phase 0/7: Configuration
  → Asking permission mode preference...
  ✓ User selected: acceptEdits
  ✓ Updated agent permissions
[brain-wave-init] Phase 1/7: Preparation
  → Checking existing installation...
  ✓ Found 42 files to process
[brain-wave-init] Phase 2/7: Alpha-Wave Initialization
  → Invoking Alpha-Wave agent...
```

Output these messages as plain text (not in code blocks) so they appear in the CLI.

## Execution Protocol

### Phase 0: Configuration
**Output**: `[brain-wave-init] Phase 0/7: Configuration`

Before initializing, ask the user for their preferred permission mode using AskUserQuestion:

**Question**: "How should Brain-Wave agents handle permissions?"

**Options**:
| Option | Description |
|--------|-------------|
| `bypassPermissions` | No prompts - agents run fully autonomously |
| `acceptEdits` | Auto-accept file changes, prompt for bash (recommended) |
| `default` | Prompt for all operations |

Store the choice in `.claude/brain-wave-config.json`:
```json
{
  "permissionMode": "acceptEdits",
  "initialized": "2026-01-23T00:00:00Z",
  "version": "1.0"
}
```

Then update all agent definition files (`.claude/agents/*.md`) to use the chosen permission mode by editing the frontmatter.

### Phase 1: Preparation
**Output**: `[brain-wave-init] Phase 1/7: Preparation`

```bash
# Check for existing system
echo "=== Checking existing Brain-Wave installation ==="
test -d alpha-wave && echo "Alpha-Wave: EXISTS" || echo "Alpha-Wave: NEW"
test -d beta-wave && echo "Beta-Wave: EXISTS" || echo "Beta-Wave: NEW"
test -d rem && echo "REM: EXISTS" || echo "REM: NEW"

# Count files to process
echo ""
echo "=== Repository Stats ==="
find . -type f -not -path '*/\.*' -not -path '*/node_modules/*' -not -path '*/alpha-wave/*' -not -path '*/beta-wave/*' -not -path '*/rem/*' 2>/dev/null | wc -l
```

Report findings to user.

### Phase 2: Alpha-Wave Initialization
**Output**: `[brain-wave-init] Phase 2/7: Alpha-Wave`

Invoke the Alpha-Wave agent to:
- Scan all repository files
- Create `alpha-wave/INDEX.md`
- Create `alpha-wave/TOPICS.md`
- Generate `alpha-wave/summaries/` for each file
- Install `.claude/rules/alpha-wave-context.md`

Wait for completion before proceeding.

### Phase 3: Beta-Wave Initialization
**Output**: `[brain-wave-init] Phase 3/7: Beta-Wave`

Invoke the Beta-Wave agent to:
- Read Alpha-Wave's index
- Create `beta-wave/_MAP.md` (root architecture)
- Create `beta-wave/_CONNECTIONS.md` (dependency graph)
- Create `beta-wave/_PATTERNS.md` (code patterns)
- Create `beta-wave/_DECISIONS.md` (inferred decisions)
- Create `beta-wave/[dir]/_MAP.md` for each directory
- Install `.claude/rules/beta-wave-context.md`

Wait for completion before proceeding.

### Phase 4: REM Initialization
**Output**: `[brain-wave-init] Phase 4/7: REM`

Invoke the REM agent to:
- Create `rem/CHANGELOG.md`
- Create `rem/LAST-RUN.md`
- Create `rem/sessions/` with initial session
- Create `rem/discoveries/` with initial observations
- Create `rem/restoration/PROTOCOL.md`
- Install `.claude/rules/rem-context.md`

### Phase 5: Verification
**Output**: `[brain-wave-init] Phase 5/7: Verification`

```bash
echo "=== Brain-Wave System Verification ==="
echo ""
echo "Alpha-Wave:"
test -f alpha-wave/INDEX.md && echo "  ✓ INDEX.md" || echo "  ✗ INDEX.md MISSING"
test -f alpha-wave/TOPICS.md && echo "  ✓ TOPICS.md" || echo "  ✗ TOPICS.md MISSING"
test -d alpha-wave/summaries && echo "  ✓ summaries/" || echo "  ✗ summaries/ MISSING"
echo ""
echo "Beta-Wave:"
test -f beta-wave/_MAP.md && echo "  ✓ _MAP.md" || echo "  ✗ _MAP.md MISSING"
test -f beta-wave/_CONNECTIONS.md && echo "  ✓ _CONNECTIONS.md" || echo "  ✗ _CONNECTIONS.md MISSING"
echo ""
echo "REM:"
test -f rem/LAST-RUN.md && echo "  ✓ LAST-RUN.md" || echo "  ✗ LAST-RUN.md MISSING"
test -d rem/sessions && echo "  ✓ sessions/" || echo "  ✗ sessions/ MISSING"
test -f rem/restoration/PROTOCOL.md && echo "  ✓ PROTOCOL.md" || echo "  ✗ PROTOCOL.md MISSING"
echo ""
echo "Memory Hooks:"
test -f .claude/rules/alpha-wave-context.md && echo "  ✓ alpha-wave-context.md" || echo "  ✗ alpha-wave-context.md MISSING"
test -f .claude/rules/beta-wave-context.md && echo "  ✓ beta-wave-context.md" || echo "  ✗ beta-wave-context.md MISSING"
test -f .claude/rules/rem-context.md && echo "  ✓ rem-context.md" || echo "  ✗ rem-context.md MISSING"
```

### Phase 6: Summary Report
**Output**: `[brain-wave-init] Phase 6/7: Summary` then `[brain-wave-init] Phase 7/7: Complete ✓`

```
Brain-Wave Memory System Initialized
=====================================

Configuration:
  - Permission mode: [user's choice]
  - Config saved: .claude/brain-wave-config.json

Alpha-Wave (Indexer):
  - Files indexed: [N]
  - Topics identified: [N]
  - Summaries created: [N]

Beta-Wave (Mapper):
  - Directories mapped: [N]
  - Connections documented: [N]
  - Patterns identified: [N]

REM (Monitor):
  - Initial session captured
  - Restoration protocol created
  - Change monitoring active

Memory Integration:
  - 3 context rules installed in .claude/rules/
  - Auto-loaded on every Claude Code session

Next Steps:
  1. Context will auto-restore on new sessions
  2. Run `use rem agent` periodically to sync
  3. Run `use alpha-wave agent` after major changes
  4. Run `use beta-wave agent` after restructuring

The system is ready. Your project context will now persist.
```

## Options

### Fresh Install
Removes existing Brain-Wave folders and starts fresh:
```bash
rm -rf alpha-wave beta-wave rem
```

### Update Only
Keeps existing content and updates:
- Reads existing indexes
- Only processes changed files
- Preserves user-added notes

### Partial Install
If only specific agents need running:
- `use alpha-wave agent` - Just indexing
- `use beta-wave agent` - Just mapping (requires Alpha)
- `use rem agent` - Just sync current state

## Rules
- Always run agents in order: Alpha → Beta → REM
- Wait for each agent to complete before next
- Report progress at each phase
- Verify all outputs exist at end
- Provide clear next-steps guidance
