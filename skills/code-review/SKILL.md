---
name: code-review
description: Trigger adversarial code review on current changes. Runs the reviewer agent to find issues, rate severity, and produce a ship/block verdict.
---

# Code Review (Brain-Wave)

Trigger the reviewer agent for adversarial code review. Use `/code-review` (the gstack `/review` skill handles PR-focused pre-landing reviews).

## Trigger

User runs `/code-review` to review current uncommitted or recent changes.

## Process

1. Delegate to the `reviewer` agent
2. The agent will run `git diff`, check against patterns, and produce a review
3. Review is written to `rem/discoveries/`

## Usage

```
/code-review           (reviews current uncommitted changes)
/code-review HEAD~3    (reviews last 3 commits)
```
