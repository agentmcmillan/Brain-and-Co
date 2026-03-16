# Sub-Agents vs Agent Teams: When to Use Each

Brain-Wave supports both patterns. Choose based on your task.

## Quick Comparison

| Aspect | Sub-Agents | Agent Teams |
|--------|------------|-------------|
| **Context** | Returns results to caller | Fully independent |
| **Communication** | Report to main only | Message each other |
| **Coordination** | Main agent manages | Self-coordinate via task list |
| **Token cost** | Lower | Higher |
| **Best for** | Focused tasks | Collaborative work |

## When to Use Sub-Agents

**Single-focus tasks where only the result matters:**

```
"Use alpha-wave subagent to index src/auth/"
"Use beta-wave subagent to map the API module"
"Use rem subagent to sync current session"
```

**Parallel research (no inter-agent discussion):**

```
"Research auth, API, and database modules in parallel using separate subagents"
→ Each returns findings to main
→ Main synthesizes
```

**Cost-conscious work:**

```
Index 5 directories → 5 haiku sub-agents → Low cost
```

## When to Use Agent Teams

**Work requiring discussion:**

```
"Create a team to design the payment system:
- One on security implications
- One on performance
- One on user experience
Have them challenge each other's designs."
```

**Cross-layer coordination:**

```
"Create a team for the auth feature:
- Frontend teammate (React components)
- Backend teammate (API routes)
- Database teammate (schema + migrations)
Have them coordinate on the contract."
```

**Competing hypotheses:**

```
"Users report auth failures. Create a team:
- One investigating token expiry
- One investigating session handling
- One investigating network issues
Have them disprove each other."
```

## Brain-Wave Integration

### Sub-Agent Pattern

```
Prime Agent (McRalph)
├── Loads Brain-Wave context
├── Spawns sub-agents for focused tasks
├── Sub-agents return results
└── Prime consolidates to REM

Sub-agents:
- alpha-wave (index)
- beta-wave (map)
- rem (sync)
- bart-enhanced (plan)
- ralph-enhanced (execute)
```

### Agent Team Pattern

```
Team Lead (with Brain-Wave)
├── Creates team with shared task list
├── Teammates self-coordinate
├── Teammates message each other
└── Lead synthesizes findings

Teammates:
- Research (explores options)
- Architect (designs system)
- Implementer (writes code)
- Reviewer (validates work)
```

## Hybrid Pattern

**Use both together:**

```
Team Lead (with Brain-Wave)
├── Teammate: Feature A
│   └── Uses alpha-wave sub-agent for indexing
├── Teammate: Feature B
│   └── Uses beta-wave sub-agent for mapping
└── Teammate: Feature C
    └── Uses rem sub-agent for syncing
```

## Brain-Wave Memory Flow

### Sub-Agents
```
1. Prime loads Brain-Wave
2. Prime spawns sub-agent with context injection
3. Sub-agent works
4. Results return to Prime
5. Prime writes to rem/discoveries/
```

### Agent Teams
```
1. Lead loads Brain-Wave
2. Lead creates team with shared Brain-Wave context
3. Teammates each read Brain-Wave (via CLAUDE.md)
4. Teammates work and message each other
5. Teammates update shared task list (rem/tasks/)
6. Lead consolidates discoveries to REM
```

## Decision Tree

```
Is inter-agent discussion needed?
├── YES → Agent Teams
└── NO
    └── Is coordination complex?
        ├── YES → Agent Teams
        └── NO
            └── Are tasks independent?
                ├── YES → Parallel Sub-Agents
                └── NO → Sequential Sub-Agents
```

## Cost Estimates

| Pattern | Task | Approximate Cost |
|---------|------|------------------|
| Single sub-agent (haiku) | Index module | $ |
| 5 parallel sub-agents (haiku) | Index codebase | $$ |
| 3-person team (sonnet) | Design feature | $$$ |
| 5-person team (sonnet) | Major refactor | $$$$ |

## Recommendations

### For Brain-Wave Memory Tasks
**Use Sub-Agents** - Memory operations are focused and don't need discussion.

### For Feature Planning (Bart)
**Use Sub-Agent** - Planning returns a PRD, no discussion needed.

### For Feature Execution (Ralph)
**Use Sub-Agent** - Stories execute sequentially, results return.

### For Complex Architecture Design
**Use Agent Team** - Needs debate between security, performance, UX.

### For Major Refactors
**Use Agent Team** - Cross-module coordination, competing approaches.

### For Research & Investigation
**Use Agent Team** - Competing hypotheses, mutual challenge.
