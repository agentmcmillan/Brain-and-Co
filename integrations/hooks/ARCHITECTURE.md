# Brain-Wave + Hooks Integration Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Code Session                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  PreToolUse │───▶│   Claude    │───▶│ PostToolUse │         │
│  │    Hooks    │    │   Action    │    │    Hooks    │         │
│  └──────┬──────┘    └─────────────┘    └──────┬──────┘         │
│         │                                      │                │
│         ▼                                      ▼                │
│  ┌─────────────┐                       ┌─────────────┐         │
│  │context-hint │                       │auto-sync-rem│         │
│  │(suggest)    │                       │auto-index   │         │
│  └─────────────┘                       │discovery-log│         │
│                                        └──────┬──────┘         │
│                                               │                │
│  ┌─────────────────────────────────────────┐ │                │
│  │           Notification Hooks            │◀┘                │
│  │  ┌─────────────────────────────────┐   │                   │
│  │  │ session-checkpoint (idle_prompt) │   │                   │
│  │  └─────────────────────────────────┘   │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Brain-Wave Memory System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │   Alpha-Wave   │  │   Beta-Wave    │  │      REM       │    │
│  │   (Indexer)    │  │   (Mapper)     │  │   (Monitor)    │    │
│  ├────────────────┤  ├────────────────┤  ├────────────────┤    │
│  │ INDEX.md       │  │ _MAP.md        │  │ CHANGELOG.md   │    │
│  │ TOPICS.md      │  │ _CONNECTIONS.md│  │ LAST-RUN.md    │    │
│  │ summaries/     │  │ _PATTERNS.md   │  │ sessions/      │    │
│  │                │  │ _DECISIONS.md  │  │ discoveries/   │    │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘    │
│          │                   │                   │              │
│          └───────────────────┴───────────────────┘              │
│                              │                                  │
│                              ▼                                  │
│                    ┌──────────────────┐                        │
│                    │  .claude/rules/  │                        │
│                    │  (Auto-loaded)   │                        │
│                    └──────────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Hook Flow Diagram

### File Edit/Write Flow

```
User requests file change
        │
        ▼
┌───────────────────┐
│ Claude edits file │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐     ┌─────────────────────────┐
│ PostToolUse fires │────▶│ auto-sync-rem.js        │
└───────────────────┘     │ - Append to CHANGELOG   │
                          │ - Update LAST-RUN.md    │
                          └─────────────────────────┘
          │
          ▼ (if Write)
┌───────────────────┐     ┌─────────────────────────┐
│ PostToolUse fires │────▶│ auto-index-alpha.js     │
└───────────────────┘     │ - Add to INDEX.md       │
                          │ - Update TOPICS.md      │
                          └─────────────────────────┘
```

### File Read Flow

```
User requests file read
        │
        ▼
┌───────────────────┐     ┌─────────────────────────┐
│ PreToolUse fires  │────▶│ context-hint.js         │
└───────────────────┘     │ - Check Beta-Wave       │
                          │ - Find related files    │
                          │ - Output hints (stderr) │
                          └─────────────────────────┘
          │
          ▼
┌───────────────────┐
│ Claude reads file │
└───────────────────┘
```

### Agent Task Flow

```
User requests agent task
        │
        ▼
┌───────────────────┐
│ Agent executes    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐     ┌─────────────────────────┐
│ PostToolUse fires │────▶│ discovery-logger.js     │
└───────────────────┘     │ - Extract insights      │
                          │ - Categorize discovery  │
                          │ - Log to discoveries/   │
                          │ - Update daily log      │
                          └─────────────────────────┘
```

### Idle Session Flow

```
Claude becomes idle
        │
        ▼
┌───────────────────┐     ┌─────────────────────────┐
│ Notification      │────▶│ session-checkpoint.js   │
│ (idle_prompt)     │     │ - Get recent changes    │
└───────────────────┘     │ - Create checkpoint     │
                          │ - Save to sessions/     │
                          └─────────────────────────┘
```

## Data Flow

### What Gets Tracked

| Event | Hook | Data Stored | Location |
|-------|------|-------------|----------|
| File edited | auto-sync-rem | Timestamp, file path | rem/CHANGELOG.md |
| File created | auto-index-alpha | File path, topics | alpha-wave/INDEX.md |
| Agent task | discovery-logger | Insights, category | rem/discoveries/ |
| Session idle | session-checkpoint | Full session state | rem/sessions/ |
| File read | context-hint | (suggestions only) | stderr (not stored) |

### Memory Persistence

```
Session 1                    Session 2                    Session 3
    │                            │                            │
    ▼                            ▼                            ▼
┌─────────┐                 ┌─────────┐                 ┌─────────┐
│ Work    │                 │ Work    │                 │ Work    │
└────┬────┘                 └────┬────┘                 └────┬────┘
     │                           │                           │
     ▼                           ▼                           ▼
┌─────────┐                 ┌─────────┐                 ┌─────────┐
│ Hooks   │                 │ Hooks   │                 │ Hooks   │
│ Capture │                 │ Capture │                 │ Capture │
└────┬────┘                 └────┬────┘                 └────┬────┘
     │                           │                           │
     └──────────────┬────────────┴───────────────────────────┘
                    │
                    ▼
          ┌─────────────────┐
          │  Brain-Wave     │
          │  Memory Files   │
          │  (Persistent)   │
          └─────────────────┘
                    │
                    ▼
          ┌─────────────────┐
          │  Git Repository │
          │  (Versioned)    │
          └─────────────────┘
```

## Benefits

### Before Hooks

1. Manual REM sync required
2. INDEX gets stale
3. Discoveries lost between sessions
4. No automatic checkpoints
5. Context hints require manual lookup

### After Hooks

1. **Automatic sync** - Changes tracked in real-time
2. **Fresh INDEX** - New files indexed immediately
3. **Captured discoveries** - Agent insights preserved
4. **Auto-checkpoints** - Session state saved on idle
5. **Proactive hints** - Related files suggested automatically

## Performance Considerations

- Hooks execute synchronously
- Target: <100ms per hook
- Skip Brain-Wave internal files (prevent loops)
- Skip node_modules and hidden files
- Cache connections file for context hints

## Security

- Hooks only read/write to Brain-Wave directories
- No external network calls
- No credential access
- Fail-safe: errors don't block Claude actions

## Future Enhancements

1. **WebSocket live sync** - Real-time dashboard
2. **Cross-project memory** - Shared learnings
3. **Pattern detection** - Auto-document code patterns
4. **Conflict resolution** - Handle concurrent edits
5. **Compression** - Archive old sessions
