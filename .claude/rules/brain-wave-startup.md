---
paths:
  - "**/*"
---

# Brain-Wave Startup Verification

**IMPORTANT**: On every session start, verify the Brain-Wave memory system is properly installed.

## Startup Check Protocol

When a session begins, silently check for these critical files:

### Required Files Checklist
```
Alpha-Wave:
  - alpha-wave/INDEX.md
  - alpha-wave/TOPICS.md

Beta-Wave:
  - beta-wave/_MAP.md
  - beta-wave/_CONNECTIONS.md

REM:
  - rem/restoration/PROTOCOL.md
  - rem/sessions/ (directory with at least one file)

Agents:
  - .claude/agents/alpha-wave.md
  - .claude/agents/beta-wave.md
  - .claude/agents/rem.md
  - .claude/agents/brain-wave-init.md
```

## Verification Logic

### If ALL files present:
Continue normally - system is ready.

### If AGENTS missing (.claude/agents/*.md):
Display this message:

```
[brain-wave] Warning: Agent definitions missing

The Brain-Wave agent files are not installed. To fix this:

Option 1 - Download from GitHub:
  git clone https://github.com/agentmcmillan/Claude-Brain-Care.git /tmp/brain-care
  cp -r /tmp/brain-care/.claude/agents/* .claude/agents/
  rm -rf /tmp/brain-care

Option 2 - If this IS the brain-care repo:
  The agent files should already exist. Check your git status.

Would you like me to help set this up?
```

### If MEMORY FOLDERS missing (alpha-wave/, beta-wave/, rem/):
Display this message:

```
[brain-wave] Memory system not initialized

The Brain-Wave memory folders are missing. This is normal for:
  - Fresh clone of the repository
  - New project setup

To initialize the memory system, run:
  use brain-wave-init agent

This will:
  1. Index all files (Alpha-Wave)
  2. Create architecture maps (Beta-Wave)
  3. Set up session tracking (REM)

Would you like me to initialize the Brain-Wave system now?
```

### If PARTIAL installation (some files missing):
Display this message:

```
[brain-wave] Incomplete installation detected

Missing components:
  [ ] alpha-wave/INDEX.md
  [x] beta-wave/_MAP.md
  [ ] rem/restoration/PROTOCOL.md

(x = present, empty = missing)

To repair, run:
  use brain-wave-init agent

Or run individual agents:
  use alpha-wave agent   (if alpha-wave missing)
  use beta-wave agent    (if beta-wave missing)
  use rem agent          (if rem missing)

Would you like me to repair the Brain-Wave system?
```

## Auto-Repair Option

If the user confirms they want to initialize or repair:
1. Run `use brain-wave-init agent` in background
2. This will handle all setup/repair automatically
3. User can continue working while initialization runs

## Background Execution

**IMPORTANT**: Always run Brain-Wave agents in background to allow the user to keep working.

When invoking agents via the Task tool, use:
```
run_in_background: true
```

This allows the user to continue prompting while agents work. Progress can be monitored via:
- The output file returned by the Task tool
- `tail -f <output_file>` to watch live progress
- Agents output `[agent-name] Phase X/X: Complete ✓` when finished

## GitHub Repository Reference

Brain-Wave Memory System repository:
- GitHub: https://github.com/agentmcmillan/Claude-Brain-Care

To get the latest agent definitions:
```bash
# Clone just the agents folder
curl -L https://github.com/agentmcmillan/Claude-Brain-Care/archive/main.zip -o /tmp/brain-care.zip
unzip /tmp/brain-care.zip -d /tmp/
cp -r /tmp/Claude-Brain-Care-main/.claude/agents/* .claude/agents/
rm -rf /tmp/brain-care.zip /tmp/Claude-Brain-Care-main
```

## Silent Mode

If all checks pass, do NOT output any startup messages - just proceed normally.
Only alert the user if something needs attention.
