---
name: predict
description: Run predictive simulations via MiroFish swarm intelligence. Submits seed material and a question, monitors simulation progress, and returns the generated report. Supports post-simulation agent interviews.
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/666ghj/MiroFish
user-invocable: true
tags:
  - prediction
  - simulation
  - swarm-intelligence
  - mirofish
metadata:
  requires:
    bins:
      - curl
    env:
      - MIROFISH_URL (optional, defaults to http://${CONTAINER_HOST_IP}:5001)
  os:
    - darwin
    - linux
---

# Predict: MiroFish Swarm Simulations

Run predictive simulations using MiroFish swarm intelligence — thousands of AI agents on simulated social platforms predicting outcomes from seed material.

## Usage

```
/predict "What happens if we open-source this project?"
/predict --seed news-article.txt "How will this policy affect adoption?"
/predict --seed https://example.com/article "What is the public reaction?"
/predict --status <sim_id>
/predict --interview <sim_id> <agent_name> "Why did you react that way?"
```

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `MIROFISH_URL` | `http://${CONTAINER_HOST_IP}:5001` | MiroFish API endpoint |

## Process

### Step 1: Gather Seed Material

Determine the seed input based on what the user provides:

**No `--seed` flag (default):** Use current repository context as seed.
1. Call Memento `recall` with the repo name and recent topics to gather cross-session context
2. Read `alpha-wave/INDEX.md` for project structure (if available)
3. Read the last 3 entries from `git log --oneline`
4. Combine into a seed text block (max 4000 chars)

**`--seed <file_path>`:** Read the file contents as seed text.

**`--seed <url>`:** Fetch the URL content and use the body text as seed.

**Multiple seeds:** Concatenate all seed material separated by `---`.

### Step 2: Submit Simulation

POST to MiroFish API to create a new simulation:

```bash
MIROFISH_URL="${MIROFISH_URL:-http://${CONTAINER_HOST_IP}:5001}"

curl -s -X POST "$MIROFISH_URL/api/simulations" \
  -H "Content-Type: application/json" \
  -d '{
    "seed_text": "<gathered seed material>",
    "prediction_requirement": "<the user question>"
  }'
```

**Expected response:**
```json
{
  "simulation_id": "sim-abc123",
  "status": "queued",
  "estimated_duration_minutes": 15
}
```

Save the `simulation_id` and report it to the user:

```
Simulation created: sim-abc123
Estimated duration: ~15 minutes
Status: queued

Use `/predict --status sim-abc123` to check progress.
```

### Step 3: Monitor Progress

Poll for completion. For short estimates (under 5 minutes), poll inline. For longer simulations, suggest Symphony monitoring or manual status checks.

**Inline polling (short simulations):**

```bash
curl -s "$MIROFISH_URL/api/simulations/$SIM_ID"
```

**Expected response:**
```json
{
  "simulation_id": "sim-abc123",
  "status": "running",
  "progress_pct": 42,
  "agents_active": 1200,
  "elapsed_minutes": 6
}
```

Poll every 30 seconds. Status values: `queued`, `running`, `completed`, `failed`.

**Long-running simulations (over 5 minutes):**

If Symphony is available, register a monitoring task:

```bash
curl -s -X POST "http://${CONTAINER_HOST_IP}:9100/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SYMPHONY_API_TOKEN" \
  -d '{
    "title": "Monitor MiroFish simulation '$SIM_ID'",
    "prompt": "Poll '$MIROFISH_URL/api/simulations/$SIM_ID' every 60s until status=completed, then fetch the report from '$MIROFISH_URL/api/simulations/$SIM_ID/report' and send results via Signal.",
    "type": "monitor"
  }'
```

Otherwise, instruct the user to check manually with `/predict --status <sim_id>`.

### Step 4: Fetch Report

When status is `completed`:

```bash
curl -s "$MIROFISH_URL/api/simulations/$SIM_ID/report"
```

**Expected response:**
```json
{
  "simulation_id": "sim-abc123",
  "report": {
    "summary": "...",
    "consensus_prediction": "...",
    "confidence_score": 0.78,
    "key_factors": ["...", "..."],
    "dissenting_views": ["...", "..."],
    "agent_clusters": [
      {"name": "optimists", "size": 450, "position": "..."},
      {"name": "skeptics", "size": 320, "position": "..."}
    ],
    "timeline": "..."
  }
}
```

Display the report to the user in a readable format:

```
=== MiroFish Prediction Report ===

Simulation: sim-abc123
Confidence: 78%

## Consensus
[consensus_prediction text]

## Key Factors
1. [factor 1]
2. [factor 2]

## Agent Clusters
- Optimists (450 agents): [position]
- Skeptics (320 agents): [position]

## Dissenting Views
- [view 1]
- [view 2]

## Timeline
[timeline text]
```

### Step 5: Persist to Memory

After displaying the report:

1. Write a summary to `rem/discoveries/prediction-[date].md`:

```markdown
# Prediction: [question]
Date: [YYYY-MM-DD]
Simulation: [sim_id]
Confidence: [score]%

## Summary
[consensus_prediction]

## Key Factors
[factors list]
```

2. Sync to Memento for cross-agent recall:

```
remember(
  topic="prediction",
  type="fact",
  content="MiroFish sim [sim_id]: [question] -> [one-line consensus] (confidence: [score]%)",
  importance=0.7,
  scope="permanent"
)
```

### Step 6: Interview (Optional)

When `--interview` is provided:

```bash
curl -s -X POST "$MIROFISH_URL/api/simulations/$SIM_ID/interview" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "<agent_name>",
    "question": "<user question>"
  }'
```

**Expected response:**
```json
{
  "agent_name": "agent-47",
  "cluster": "skeptics",
  "response": "...",
  "reasoning": "...",
  "confidence": 0.65
}
```

Display as:

```
=== Agent Interview ===

Agent: agent-47 (cluster: skeptics)
Confidence: 65%

Response:
[response text]

Reasoning:
[reasoning text]
```

The user can interview multiple agents in sequence.

## Status Check

When `--status <sim_id>` is provided:

```bash
curl -s "$MIROFISH_URL/api/simulations/$SIM_ID"
```

Display:

```
Simulation: sim-abc123
Status: running
Progress: 42%
Active agents: 1,200
Elapsed: 6 minutes
```

If status is `completed`, automatically fetch and display the report (Step 4).
If status is `failed`, display the error message from the response.

## Rules

- ALWAYS validate that `MIROFISH_URL` is reachable before submitting a simulation
- If MiroFish is unreachable, suggest checking that the service is running on the container host
- NEVER fabricate simulation results — only display actual API responses
- Keep seed text under 4000 characters; truncate with a note if longer
- For repo-context seeds, exclude binary files, lock files, and node_modules references
- Memento sync is best-effort — do not fail the prediction if Memento is unreachable
- If the simulation fails, display the error and suggest re-running with different seed material

## Related Skills

- `bart-enhanced` — Use prediction results to inform feature planning
- `forge` — Capture prediction insights as learnings
- `brain-wave-init` — Provides repo context for seed material
- `rem` — Stores prediction discoveries
