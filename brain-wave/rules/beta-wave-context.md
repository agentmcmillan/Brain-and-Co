---
paths:
  - "**/*"
---

# Beta-Wave Deep Context

This project has deep knowledge maps available.

## Architecture Understanding
- @beta-wave/_MAP.md - Full system overview with diagrams
- @beta-wave/_CONNECTIONS.md - How modules connect and depend on each other
- @beta-wave/_PATTERNS.md - Code patterns and conventions used
- @beta-wave/_DECISIONS.md - Why things are the way they are

## When Working In a Directory
Check for `beta-wave/[directory]/_MAP.md` for deep context about that area.

## Key Insights

### Three-Agent Pipeline
Agents execute in strict order: Alpha-Wave (index) -> Beta-Wave (map) -> REM (monitor). Each builds on the previous.

### Filesystem Persistence
All state stored as markdown files in dedicated folders. Survives context resets and is git-trackable.

### Memory Hooks
`.claude/rules/` files auto-load on session start, providing immediate context.

---
*Last mapped: 2026-01-23*
*Run `use beta-wave agent` to refresh*
