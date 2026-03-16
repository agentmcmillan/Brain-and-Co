# ClawHub Publishing Workflow

Guide for publishing Brain-Wave skills to the ClawHub registry.

## Prerequisites

1. ClawHub account at https://clawhub.ai
2. OpenClaw CLI installed: `npm install -g openclaw`
3. Authenticated: `clawhub login`

## Skill Structure

Each skill needs:
```
skills/[skill-name]/
├── SKILL.md          # Required: Skill definition
├── README.md         # Optional: Extended docs
└── examples/         # Optional: Usage examples
```

## SKILL.md Format

```yaml
---
name: skill-name
description: Short description (under 100 chars)
version: 1.0.0
author: your-username
homepage: https://github.com/...
user-invocable: true
tags:
  - memory
  - productivity
metadata:
  requires:
    bins: ["git"]
    env: ["OPTIONAL_VAR"]
    config: ["path/to/required/file"]
  os:
    - darwin
    - linux
    - windows
---

# Skill instructions go here...
```

## Publishing Steps

### 1. Validate Locally

```bash
# Test skill loads correctly
clawhub validate skills/brain-wave-init/

# Check for common issues
clawhub lint skills/
```

### 2. Test in OpenClaw

```bash
# Install locally first
clawhub install ./skills/brain-wave-init --local

# Test the skill works
openclaw> /brain-wave-init
```

### 3. Publish to Registry

```bash
# Publish single skill
clawhub publish skills/brain-wave-init/

# Publish all skills
for skill in skills/*/; do
  clawhub publish "$skill"
done
```

### 4. Verify Publication

```bash
# Check skill is live
clawhub info brain-wave-init

# View on web
open https://clawhub.ai/skills/brain-wave-init
```

## Version Management

### Semantic Versioning
- **Patch** (1.0.1): Bug fixes, typos
- **Minor** (1.1.0): New features, backwards compatible
- **Major** (2.0.0): Breaking changes

### Updating Published Skills

```bash
# Bump version in SKILL.md first
clawhub publish skills/brain-wave-init/ --update
```

## Security Checklist

Before publishing, verify:

- [ ] No hardcoded secrets or API keys
- [ ] No credential harvesting
- [ ] No unauthorized network requests
- [ ] No destructive file operations
- [ ] Clear permission requirements in metadata
- [ ] Honest description of functionality

## VirusTotal Integration

After publishing, your skill will be scanned:
```bash
# Check scan status
clawhub security brain-wave-init
```

Wait for clean scan before promoting.

## Collection Registration

To register all Brain-Wave skills as a collection:

```bash
clawhub collection create brain-wave \
  --name "Brain-Wave Memory System" \
  --description "Persistent AI context across sessions" \
  --skills brain-wave-init,alpha-wave,beta-wave,rem,bart-enhanced,ralph-enhanced,gsd-orchestrator,mcralph-orchestrator,planning-enhanced
```

## Promotion

### Awesome OpenClaw List

Submit PR to https://github.com/VoltAgent/awesome-openclaw-skills:

```markdown
### Memory & Context

- [brain-wave](https://clawhub.ai/skills/brain-wave-init) - Persistent AI memory system with indexing, mapping, and session tracking
```

### Social Sharing

```
Just published Brain-Wave to @ClawHub! 🧠

Persistent AI memory system:
- Alpha-Wave: Index your codebase
- Beta-Wave: Map architecture
- REM: Track sessions

https://clawhub.ai/skills/brain-wave-init

#OpenClaw #ClawHub #AIAgents
```

## Maintenance

### Monitor Usage

```bash
# View download stats
clawhub stats brain-wave-init

# Check for issues reported
clawhub issues brain-wave-init
```

### Respond to Security Reports

If vulnerability reported:
1. Acknowledge within 24 hours
2. Patch and publish fix
3. Notify affected users
4. Update changelog

## Unpublishing

If needed (use sparingly):

```bash
clawhub unpublish brain-wave-init@1.0.0
```

Note: Cannot unpublish if other skills depend on it.
