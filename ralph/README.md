# McRalph

![Ralph](ralph.webp)

McRalph is an autonomous AI agent system that uses **master agents with sub-agent workers** to plan and execute software development tasks. Built for Claude Code, it spawns fresh context workers for each task to prevent context degradation.

Based on [Geoffrey Huntley's Ralph pattern](https://ghuntley.com/ralph/) and inspired by [Get Shit Done](https://github.com/glittercowboy/get-shit-done).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Commands                           │
├─────────────────────────────────────────────────────────────┤
│   /bart (planning)          │      /ralph (execution)       │
│   /bart new                 │      /ralph                   │
│   /bart research            │      /ralph status            │
│   /bart requirements        │      /ralph retry US-XXX      │
│   /bart create-prd          │                               │
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
                ▼                             ▼
┌───────────────────────────┐ ┌───────────────────────────────┐
│      Bart (Planning)       │ │       Ralph (Execution)       │
│  - Ideation & discovery    │ │  - Reads prd.json             │
│  - Codebase research       │ │  - Spawns worker sub-agents   │
│  - Requirements definition │ │  - Coordinates state updates  │
│  - Creates prd.json        │ │  - Handles failures/retries   │
└───────────────────────────┘ └───────────────┬───────────────┘
                                              │ Task tool
                                              ▼
                              ┌───────────────────────────────┐
                              │    Ralph Worker Sub-Agent     │
                              │  - Fresh context per story    │
                              │  - Implements single story    │
                              │  - Runs quality checks        │
                              │  - Commits and reports back   │
                              └───────────────────────────────┘
```

## Key Concepts

### Bart Plans, Ralph Executes

- **Bart** handles discovery: asks questions, researches codebase, defines requirements
- **Ralph** handles execution: spawns workers for each user story until all pass

### Fresh Context Per Story

Each story runs in a **fresh sub-agent context**. This prevents "context rot" where quality degrades as the context window fills up.

### State Persistence

Memory persists via files, not context:
- `prd.json` - User stories with `passes` status
- `progress.txt` - Learnings for future iterations
- `.planning/` - Bart's research and requirements docs
- Git history - All committed changes

## Quick Start

### Prerequisites

- [Claude Code CLI](https://claude.ai/code) installed
- `jq` installed (`brew install jq` on macOS)
- A git repository for your project

### Option 1: Interactive (Recommended)

Start a new feature with Bart:

```
/bart new
```

Answer the questions, then research and create requirements:

```
/bart research
/bart requirements
/bart create-prd
```

Execute with Ralph:

```
/ralph
```

### Option 2: CI/Automation

Use the runner script:

```bash
# Show status
./ralph-runner.sh --status

# Execute all pending stories
./ralph-runner.sh

# Dry run
./ralph-runner.sh --dry-run
```

### Option 3: Manual PRD

Create `prd.json` manually (see `prd.json.example`), then run:

```
/ralph
```

## Commands

### Bart (Planning)

| Command | Description |
|---------|-------------|
| `/bart new` | Start new feature planning |
| `/bart research` | Research codebase for feature |
| `/bart requirements` | Define user stories |
| `/bart create-prd` | Generate prd.json |
| `/bart status` | Show current planning state |

### Ralph (Execution)

| Command | Description |
|---------|-------------|
| `/ralph` | Execute prd.json stories |
| `/ralph status` | Show progress without executing |
| `/ralph retry US-XXX` | Retry a failed story |
| `/ralph skip US-XXX` | Skip a story and continue |

## File Structure

```
your-project/
├── prd.json              # User stories for Ralph to execute
├── progress.txt          # Learnings across iterations
├── .planning/            # Bart's planning artifacts
│   ├── PROJECT.md        # Vision and scope
│   ├── RESEARCH.md       # Codebase investigation
│   ├── REQUIREMENTS.md   # Scoped user stories
│   └── STATE.md          # Cross-session memory
└── archive/              # Previous runs (auto-archived)
```

## PRD Format

```json
{
  "project": "MyApp",
  "branchName": "ralph/feature-name",
  "description": "Feature description",
  "userStories": [
    {
      "id": "US-001",
      "title": "Add database field",
      "description": "As a developer...",
      "acceptanceCriteria": [
        "Add column to table",
        "Migration runs successfully",
        "Typecheck passes"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

## Story Sizing

Each story must complete in **one context window**. If a story is too big, the sub-agent runs out of context and produces poor code.

**Right-sized:**
- Add a database column and migration
- Add a UI component to existing page
- Update a server action with new logic

**Too big (split these):**
- "Build the entire dashboard"
- "Add authentication"
- "Refactor the API"

**Rule of thumb:** If you can't describe it in 2-3 sentences, split it.

## Flowchart

[![Ralph Flowchart](ralph-flowchart.png)](https://snarktank.github.io/ralph/)

**[View Interactive Flowchart](https://snarktank.github.io/ralph/)** - Click through to see each step with animations.

## Legacy Support

The original `ralph.sh` (which uses Amp CLI) is deprecated but still available for backwards compatibility. It will display a deprecation warning when run.

**New approach:**
- Interactive: `/ralph` in Claude Code
- CI/Automation: `./ralph-runner.sh`

## Debugging

```bash
# See story status
cat prd.json | jq '.userStories[] | {id, title, passes}'

# See learnings
cat progress.txt

# Check Bart's planning state
cat .planning/STATE.md

# Check git history
git log --oneline -10
```

## References

- [Geoffrey Huntley's Ralph pattern](https://ghuntley.com/ralph/)
- [Get Shit Done](https://github.com/glittercowboy/get-shit-done)
- [Claude Code documentation](https://claude.ai/code)
