# McRalph Agent Instructions

## Overview

McRalph is an autonomous AI agent system with two main agents:

- **Bart** - Planning agent (ideation → research → requirements → prd.json)
- **Ralph** - Execution agent (reads prd.json → spawns workers → completes stories)

Each uses sub-agents with fresh context windows to prevent context degradation.

## Commands

```bash
# Planning with Bart
/bart new              # Start new feature planning
/bart research         # Research codebase
/bart requirements     # Define user stories
/bart create-prd       # Generate prd.json

# Execution with Ralph
/ralph                 # Execute prd.json stories
/ralph status          # Show progress
/ralph retry US-XXX    # Retry a failed story

# CI/Automation
./ralph-runner.sh      # Run Ralph non-interactively
./ralph-runner.sh --status    # Show status
./ralph-runner.sh --dry-run   # Preview execution
```

## Key Files

| File | Purpose |
|------|---------|
| `skills/ralph-master/SKILL.md` | Ralph orchestrator skill |
| `skills/bart/SKILL.md` | Bart planning skill |
| `prompts/ralph-worker.md` | Sub-agent prompt for story execution |
| `prompts/bart-researcher.md` | Sub-agent prompt for codebase research |
| `ralph-runner.sh` | CI wrapper script |
| `ralph.sh` | Legacy Amp-based script (deprecated) |
| `prd.json.example` | Example PRD format |
| `flowchart/` | Interactive visualization |

## Architecture

```
User → /bart → Planning artifacts → prd.json
User → /ralph → Spawns workers → Stories complete
```

### Bart Flow
1. `/bart new` - Gather requirements through questions
2. `/bart research` - Spawn Explore agent to investigate codebase
3. `/bart requirements` - Spawn Plan agent to define stories
4. `/bart create-prd` - Generate prd.json

### Ralph Flow
1. Read prd.json for stories
2. For each story with `passes: false`:
   - Spawn general-purpose sub-agent with ralph-worker prompt
   - Sub-agent implements story, runs checks, commits
   - Parse `<ralph-result>` from sub-agent
   - Update prd.json with `passes: true`
   - Append learnings to progress.txt
3. Output `<promise>COMPLETE</promise>` when all done

## Patterns

### Sub-Agent Spawning
Use Task tool with:
- `subagent_type: "general-purpose"` for Ralph workers
- `subagent_type: "Explore"` for Bart research
- `subagent_type: "Plan"` for Bart requirements

### State Files
- `prd.json` - Story status (`passes: true/false`)
- `progress.txt` - Learnings (append-only)
- `.planning/STATE.md` - Bart cross-session memory
- `.planning/RESEARCH.md` - Codebase investigation

### Result Format
Ralph workers output:
```json
<ralph-result>
{
  "status": "success",
  "storyId": "US-001",
  "filesChanged": ["file.ts"],
  "commitHash": "abc123",
  "learnings": ["Pattern discovered"],
  "error": null
}
</ralph-result>
```

### Story Sizing
Each story must fit in one context window:
- Right: "Add priority field to database"
- Wrong: "Build the entire authentication system"

### Completion Signal
When all stories pass:
```
<promise>COMPLETE</promise>
```

## Legacy Support

The original `ralph.sh` uses Amp CLI and is deprecated. Use:
- `/ralph` for interactive execution
- `./ralph-runner.sh` for CI/automation

## Testing

Create a minimal test PRD:
```json
{
  "project": "Test",
  "branchName": "ralph/test",
  "userStories": [
    {
      "id": "US-001",
      "title": "Create test file",
      "acceptanceCriteria": ["Create test.txt with 'hello'"],
      "priority": 1,
      "passes": false
    }
  ]
}
```

Then run `/ralph` and verify the file is created.
