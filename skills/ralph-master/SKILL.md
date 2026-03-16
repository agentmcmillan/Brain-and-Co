---
name: ralph
description: "Execute PRD user stories autonomously using sub-agents. Reads prd.json and spawns fresh context workers for each story. Use when you have a prd.json ready for execution. Triggers on: run ralph, execute prd, start ralph, run stories."
---

# Ralph Master Agent

Autonomous execution of PRD-defined user stories using sub-agents with fresh context windows.

---

## Overview

Ralph is a master orchestrator that:
1. Reads `prd.json` for user stories
2. Spawns sub-agents (ralphs) to implement each story
3. Coordinates state updates across iterations
4. Preserves context by using fresh sub-agents per story

---

## Execution Flow

### Step 1: Initialize

1. Read `prd.json` in the current directory (or McRalph directory if running from there)
2. Read `progress.txt` for codebase patterns from previous iterations
3. Verify the branch matches `branchName` in PRD - create or checkout if needed

**If no prd.json exists:**
```
No prd.json found. Create one using:
- /bart to plan a new feature (recommended)
- /prd to generate a PRD from a feature description
- Copy prd.json.example and customize it
```

### Step 2: Archive Check

If `prd.json` exists with a different `branchName` than the last run:
1. Create archive folder: `archive/YYYY-MM-DD-feature-name/`
2. Copy current `prd.json` and `progress.txt` to archive
3. Reset `progress.txt` with fresh header

### Step 3: Story Selection

Find the highest priority story where `passes: false`:
```json
{
  "id": "US-001",
  "title": "Story title",
  "passes": false,
  "priority": 1
}
```

If no incomplete stories remain, output completion signal and exit.

### Step 4: Spawn Sub-Agent

For each incomplete story, spawn a ralph worker sub-agent using the Task tool:

```
Use the Task tool with:
- subagent_type: "general-purpose"
- prompt: The ralph-worker prompt with story details filled in
- description: "Ralph: US-XXX story title"
```

The sub-agent prompt template is at `prompts/ralph-worker.md`. Fill in:
- `{{STORY_ID}}` - The story ID (e.g., US-001)
- `{{STORY_TITLE}}` - The story title
- `{{STORY_DESCRIPTION}}` - The full description
- `{{ACCEPTANCE_CRITERIA}}` - Bullet list of criteria
- `{{PROJECT_NAME}}` - From prd.json project field
- `{{BRANCH_NAME}}` - From prd.json branchName field
- `{{WORKING_DIR}}` - The working directory path
- `{{CODEBASE_PATTERNS}}` - From progress.txt Codebase Patterns section

### Step 5: Handle Result

Parse the `<ralph-result>` from sub-agent output:

**On success:**
1. Update `prd.json`: Set story's `passes: true`
2. Append to `progress.txt`:
   ```
   ## [Date/Time] - US-XXX
   - Implemented: [story title]
   - Files changed: [list from result]
   - Learnings: [from result]
   ---
   ```
3. If learnings contain patterns, add to `## Codebase Patterns` section
4. Continue to next story

**On failure:**
1. Add error to story's `notes` field in prd.json
2. Log failure to progress.txt
3. Ask user: "Story US-XXX failed: [error]. Retry, skip, or stop?"

### Step 6: Completion Check

After each story, check if ALL stories have `passes: true`.

**If all complete:**
```
<promise>COMPLETE</promise>

All user stories have been implemented:
- US-001: [title] ✓
- US-002: [title] ✓
...

Branch: [branchName]
Total stories: X
```

**If stories remain:**
Continue to next incomplete story (return to Step 3).

---

## State Files

### prd.json
```json
{
  "project": "ProjectName",
  "branchName": "ralph/feature-name",
  "description": "Feature description",
  "userStories": [
    {
      "id": "US-001",
      "title": "Story title",
      "description": "As a user...",
      "acceptanceCriteria": ["Criterion 1", "Criterion 2"],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

### progress.txt
```markdown
# Ralph Progress Log
Started: [date]
---

## Codebase Patterns
- Pattern 1 discovered
- Pattern 2 discovered

## [Date] - US-001
- Implemented: Story title
- Files: file1.ts, file2.ts
- Learnings: Pattern discovered
---
```

---

## Error Handling

1. **Sub-agent timeout:** Retry once with extended timeout
2. **Quality check failure:** Sub-agent handles internally, reports in result
3. **Git conflict:** Stop and ask user for resolution
4. **Missing dependencies:** Report in failure, suggest next steps

---

## Integration with Bart

If `/bart` was used to create the prd.json:
- Read `.planning/STATE.md` for additional context
- Honor any constraints from Bart's research phase
- Reference `.planning/REQUIREMENTS.md` if clarification needed

---

## Example Session

```
User: /ralph

Ralph: Reading prd.json...
Found 4 user stories, 0 complete.
Branch: ralph/task-priority

Starting US-001: Add priority field to database
[Spawning sub-agent...]

US-001 complete ✓
- Added priority column to tasks table
- Migration successful
- Learnings: Use IF NOT EXISTS for migrations

Starting US-002: Display priority indicator
[Spawning sub-agent...]

US-002 complete ✓
...

<promise>COMPLETE</promise>

All 4 stories implemented successfully.
Branch ralph/task-priority ready for review.
```

---

## Commands Reference

- `/ralph` - Execute prd.json stories
- `/ralph status` - Show current progress without executing
- `/ralph retry US-XXX` - Retry a specific failed story
- `/ralph skip US-XXX` - Skip a story and continue
