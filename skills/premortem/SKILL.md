---
name: premortem
description: Trigger pre-mortem failure analysis on a feature or task. Runs the premortem agent to simulate failure modes and produce a risk register with readiness gate verdict.
---

# Pre-mortem Analysis

Trigger the premortem agent for failure analysis.

## Trigger

User runs `/premortem` optionally followed by a feature/task description.

## Process

1. If no description provided, ask the user what feature or task to analyze
2. Delegate to the `premortem` agent with the task description
3. The agent will produce a risk register in `rem/discoveries/`

## Usage

```
/premortem Add payment integration with Stripe
/premortem Migrate database from SQLite to PostgreSQL
/premortem  (will prompt for description)
```
