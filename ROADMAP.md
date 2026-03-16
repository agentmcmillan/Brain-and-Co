# Brain-Wave Roadmap

Features inspired by top OpenClaw skills, research papers, and community patterns.

## Research Sources

| Source | Key Concept | Applied |
|--------|-------------|---------|
| [AI Maker Substack](https://aimaker.substack.com/p/ultimate-guide-to-claude-project-memory-system-prompt) | Friction-driven memory | ✅ friction.md |
| [Gastown](https://github.com/steveyegge/gastown) | Git worktree isolation | ✅ integrations/gastown/ |
| [Beads](https://github.com/steveyegge/beads) | Hash-based task IDs | ✅ beads-tasks |
| [MemOS](https://github.com/MemTensor/MemOS) | Memory cubes & feedback | 🔜 v1.6 |
| [Awesome-AI-Memory](https://github.com/IAAR-Shanghai/Awesome-AI-Memory) | Memory taxonomy | 📚 Reference |
| [TME Paper](https://arxiv.org/html/2504.08525v3) | Task Memory Tree | 🔜 v1.7 |
| [Token Budgeting](https://www.getmaxim.ai/articles/context-engineering-for-ai-agents-production-optimization-strategies/) | Context allocation | 🔜 v1.8 |

## Skill Inspirations

| Source Skill | Feature | Status |
|--------------|---------|--------|
| cognitive-memory | Multi-store memory layers | ✅ Implemented |
| shared-memory | Cross-instance context sharing | ✅ Implemented |
| quests | Guided multi-step processes | 🔜 v1.3 |
| summarize | Content summarization | ✅ alpha summaries |
| trellis | Structured specs & workflows | 🔜 v1.5 |
| identity-manager | Agent identity persistence | ✅ agent-id.json |

---

## ✅ v1.1 - Implemented

### Friction Log System
Capture gaps between AI output and preferences.

```
rem/discoveries/friction.md
```

Pattern: What I got → What I needed → The gap → Instruction added

### Hash-Based Session IDs
Beads-style IDs prevent merge conflicts.

```
bw-a1b2c instead of 2026-02-11-session.md
```

### Memory Decay Agent
Auto-compact old sessions.

```
/memory-decay

< 7 days:  Full detail
7-30 days: Summarized
30-90d:    Minimal
90+ days:  Archived
```

### Beads-Tasks System
Dependency-aware task tracking.

```
/tasks ready    # Show unblocked tasks
/tasks add      # Create with hash ID
/tasks done     # Complete and unblock dependents
```

### Gastown Integration
Git worktree isolation for parallel agents.

```bash
./integrations/gastown/create-agent.sh agent-auth feature
cd .worktrees/agent-auth
# Agent works in isolation
```

---

## ✅ v1.2 - Implemented

### Shared Memory
Cross-instance context sharing.

```
/shared-memory export   # Create snapshot
/shared-memory import   # Merge external context
/shared-memory sync     # Sync with peers
```

Structure:
```
rem/shared/exports/     # Your snapshots
rem/shared/imports/     # From others
rem/sync/peers.json     # Peer registry
```

---

## 🔜 v1.3 - Quests System

Guided multi-step workflows.

### Proposed Quests
- `new-project`: Initialize Brain-Wave
- `feature`: Plan → Build → Test → Ship
- `refactor`: Safe refactoring workflow
- `debug`: Systematic debugging

### Quest Format
```markdown
# Quest: Build Feature

## Steps
1. [ ] /bart new
2. [ ] /bart create-prd
3. [ ] /ralph
4. [ ] /rem

Progress: 0/4
```

---

## 🔜 v1.4 - Cognitive Memory

Human-like memory characteristics (from cognitive-memory skill).

### Memory Types
| Type | Analog | Location |
|------|--------|----------|
| Working | Current focus | rem/sessions/ |
| Episodic | Past events | rem/chats/ |
| Semantic | Facts | alpha-wave/ |
| Procedural | How-to | beta-wave/_PATTERNS.md |

### Importance Scoring
Prioritize memory by:
- Touch frequency
- Dependent count
- Recency

---

## 🔜 v1.5 - Trellis Integration

Structured specs and workflow templates.

### Spec Types
- API Endpoint Spec
- Component Spec
- Migration Spec
- Test Plan Spec

---

## 🔜 v1.6 - MemOS Concepts

From [MemOS](https://github.com/MemTensor/MemOS):

### Memory Cubes
Isolated, composable knowledge bases.

```
brain-care/           # Main cube
├── projects/
│   ├── auth/         # Auth project cube
│   └── payments/     # Payments project cube
```

### Memory Feedback
Natural language refinement:
> "That discovery about JWT was wrong - we actually use sessions"

Updates memory in place.

---

## 🔜 v1.7 - Task Memory Tree

From [TME Paper](https://arxiv.org/html/2504.08525v3):

### Hierarchical Task Structure
```
Task Root
├── Subtask A (done)
│   └── Action 1, 2, 3
├── Subtask B (in progress)
│   └── Action 1, 2
└── Subtask C (blocked by B)
```

### Dynamic Prompt Synthesis
Only include active path in context (19% token savings).

### Relationship Inference
- Dependency (A blocks B)
- Replacement (B supersedes A)
- Merging (A + B → C)
- Rollback (revert to A)

---

## 🔜 v1.8 - Token Budgeting

From [context engineering research](https://www.getmaxim.ai/articles/context-engineering-for-ai-agents-production-optimization-strategies/):

### Budget Allocation
```
Tool context:     15-20%
Knowledge:        30-40%
History:          20-30%
Buffer reserve:   10-15%
```

### Dynamic Allocation
Adapt based on:
- Query complexity
- User tier
- Context freshness

### Context Lifecycle
- Load → Use → Compress → Archive
- Active management through execution

---

## 🔜 v2.0 - OpenClaw Gateway

Full OpenClaw integration for multi-channel memory.

### Multi-Channel Sessions
```
WhatsApp → Brain-Wave
Telegram → Same context
Discord  → Same context
```

### Persistent Agent Identity
```yaml
agent:
  name: "Project Assistant"
  identity: "brain-wave-main"
  memory: "./brain-wave/"
```

---

## Memory Taxonomy Reference

From [Awesome-AI-Memory](https://github.com/IAAR-Shanghai/Awesome-AI-Memory):

### Memory Dimensions
| Dimension | Spectrum |
|-----------|----------|
| Access | Working ↔ Archived |
| Structure | Structured ↔ Unstructured |
| Scope | Personal ↔ Public |
| Validity | Permanent ↔ Time-sensitive |

### Core Operations
- Write (store new)
- Retrieve (recall)
- Update (modify)
- Delete (forget)
- Compress (summarize)

---

## Contributing

Ideas welcome. Priority given to:
1. Token efficiency
2. Context persistence
3. Multi-agent coordination
4. Developer experience
