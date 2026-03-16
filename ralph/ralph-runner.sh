#!/bin/bash
# Ralph Runner - CI/Automation wrapper for Claude Code Ralph execution
# Usage: ./ralph-runner.sh [options]
#
# Options:
#   --max-stories N    Maximum stories to execute (default: unlimited)
#   --timeout M        Timeout per story in minutes (default: 10)
#   --dry-run          Show what would be executed without running
#   --status           Show current prd.json status and exit
#   --help             Show this help message

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRD_FILE="$SCRIPT_DIR/prd.json"
PROGRESS_FILE="$SCRIPT_DIR/progress.txt"

# Default options
MAX_STORIES=0  # 0 = unlimited
TIMEOUT_MINUTES=10
DRY_RUN=false
STATUS_ONLY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --max-stories)
      MAX_STORIES="$2"
      shift 2
      ;;
    --timeout)
      TIMEOUT_MINUTES="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --status)
      STATUS_ONLY=true
      shift
      ;;
    --help)
      head -20 "$0" | tail -15
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Check for prd.json
if [ ! -f "$PRD_FILE" ]; then
  echo "Error: No prd.json found in $SCRIPT_DIR"
  echo "Create one using /bart or /prd skills, or copy prd.json.example"
  exit 1
fi

# Parse prd.json
PROJECT=$(jq -r '.project' "$PRD_FILE")
BRANCH=$(jq -r '.branchName' "$PRD_FILE")
TOTAL_STORIES=$(jq '.userStories | length' "$PRD_FILE")
COMPLETE_STORIES=$(jq '[.userStories[] | select(.passes == true)] | length' "$PRD_FILE")
PENDING_STORIES=$((TOTAL_STORIES - COMPLETE_STORIES))

# Status output
echo "═══════════════════════════════════════════════════════"
echo "  Ralph Runner - McRalph v2"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Project:     $PROJECT"
echo "Branch:      $BRANCH"
echo "Stories:     $COMPLETE_STORIES/$TOTAL_STORIES complete"
echo "Pending:     $PENDING_STORIES"
echo ""

if [ "$STATUS_ONLY" = true ]; then
  echo "Pending stories:"
  jq -r '.userStories[] | select(.passes == false) | "  - \(.id): \(.title)"' "$PRD_FILE"
  exit 0
fi

if [ "$PENDING_STORIES" -eq 0 ]; then
  echo "All stories already complete!"
  exit 0
fi

if [ "$DRY_RUN" = true ]; then
  echo "Dry run - would execute:"
  jq -r '.userStories[] | select(.passes == false) | "  - \(.id): \(.title)"' "$PRD_FILE"
  exit 0
fi

# Execute Ralph via Claude Code
echo "Starting Ralph execution..."
echo ""

# Build the prompt for Claude Code
RALPH_PROMPT="Execute the Ralph workflow:

1. Read prd.json at $PRD_FILE
2. Read progress.txt at $PROGRESS_FILE for codebase patterns
3. Ensure you're on branch: $BRANCH
4. For each story with passes: false (in priority order):
   a. Use the Task tool to spawn a sub-agent with the ralph-worker prompt
   b. Fill in the story details from prd.json
   c. Wait for the sub-agent to complete
   d. Parse the <ralph-result> output
   e. Update prd.json with passes: true on success
   f. Append progress to progress.txt
5. After all stories complete, output: <promise>COMPLETE</promise>

Important:
- Use subagent_type: 'general-purpose' for Task tool
- Each sub-agent gets a fresh context window
- Stop and report if any story fails
- Maximum stories to execute: $MAX_STORIES (0 = all)
"

# Run Claude Code with the ralph skill
# The skill is expected to be installed in ~/.claude/skills/ or in the project's skills/ directory
OUTPUT=$(echo "$RALPH_PROMPT" | claude --dangerously-skip-permissions 2>&1 | tee /dev/stderr) || true

# Check for completion signal
if echo "$OUTPUT" | grep -q "<promise>COMPLETE</promise>"; then
  echo ""
  echo "═══════════════════════════════════════════════════════"
  echo "  Ralph completed all stories!"
  echo "═══════════════════════════════════════════════════════"
  echo ""
  echo "Branch $BRANCH is ready for review."
  exit 0
fi

# Check current status
NEW_COMPLETE=$(jq '[.userStories[] | select(.passes == true)] | length' "$PRD_FILE")
if [ "$NEW_COMPLETE" -gt "$COMPLETE_STORIES" ]; then
  echo ""
  echo "Progress: $NEW_COMPLETE/$TOTAL_STORIES stories complete"
  echo "Run again to continue execution."
  exit 0
fi

echo ""
echo "Ralph did not complete all stories."
echo "Check $PROGRESS_FILE for details."
exit 1
