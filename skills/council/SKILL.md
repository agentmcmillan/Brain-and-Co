---
name: council
description: "Multi-LLM consensus for high-stakes decisions. Sends the same prompt to multiple AI models in parallel (gemini-cli, grok-cli, codex-cli, cursor-cli), collects independent responses, and synthesizes a Chairman verdict highlighting agreements, disagreements, and the recommended approach. Inspired by Karpathy's llm-council. Modes: consensus, review, debate."
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/karpathy/llm-council
user-invocable: true
tags:
  - consensus
  - multi-model
  - review
  - decision-making
  - council
metadata:
  requires:
    bins:
      - git
  os:
    - darwin
    - linux
---

# Council: Multi-LLM Consensus

Inspired by [Karpathy's llm-council](https://github.com/karpathy/llm-council). Send the same prompt to multiple AI models running in parallel, collect independent responses, and synthesize a Chairman verdict.

## What It Does

- Launches 3-4 AI subagents in parallel (gemini-cli, grok-cli, codex-cli, cursor-cli)
- Each model evaluates the same prompt independently with no cross-contamination
- Collects all responses and produces a Chairman synthesis
- Highlights agreements, disagreements, and the recommended approach
- Three modes: `consensus`, `review`, `debate`

## Usage

```
/council "What's the best approach to implement caching?"
/council review
/council debate "Should we use microservices or a monolith?"
```

## Trigger

User runs `/council` followed by an optional mode and prompt.

## Process

### Step 1: Parse Input

Determine mode and prompt from the user's input:

| Input | Mode | Prompt |
|-------|------|--------|
| `/council "prompt"` | `consensus` (default) | The quoted text |
| `/council consensus "prompt"` | `consensus` | The quoted text |
| `/council review` | `review` | Auto-generated from current git diff |
| `/council review "focus area"` | `review` | Git diff + focus area context |
| `/council debate "prompt"` | `debate` | The quoted text |

If no prompt is provided and mode is not `review`, ask the user:

```
What question or decision should the Council evaluate?
```

### Step 2: Prepare the Prompt

**For `consensus` mode:**

Wrap the user's prompt with council instructions:

```
You are one member of an AI council evaluating a question independently.
Give your honest, thorough analysis. Do not hedge or give non-answers.
Be specific and opinionated. Support your position with reasoning.

QUESTION:
{user_prompt}

Provide:
1. Your recommended approach (be specific)
2. Key tradeoffs you considered
3. Risks or concerns with your recommendation
4. Confidence level (LOW / MEDIUM / HIGH) and why
```

**For `review` mode:**

First, gather the diff:

```bash
git diff HEAD
```

If the diff is empty, try `git diff HEAD~1` instead. If still empty, report that there are no changes to review.

Wrap with review instructions:

```
You are one member of an AI code review council. Review this diff independently.
Be adversarial. Find real issues, not style nitpicks. Focus on correctness, security, and maintainability.
{focus_area_context}

DIFF:
{git_diff}

Provide:
1. CRITICAL issues (bugs, security, data loss risks)
2. IMPORTANT issues (logic errors, missing edge cases, performance)
3. SUGGESTIONS (improvements, better patterns)
4. Overall verdict: SHIP / SHIP WITH CHANGES / BLOCK
5. Confidence level (LOW / MEDIUM / HIGH)
```

**For `debate` mode:**

Wrap with debate instructions:

```
You are one member of an AI debate council. Take a clear position on this question.
Do NOT try to be balanced. Pick a side and argue it forcefully with evidence and reasoning.
It is fine to disagree with other models — that is the point.

QUESTION:
{user_prompt}

Provide:
1. Your position (stated clearly in one sentence)
2. Your strongest 3 arguments FOR this position
3. The strongest counterargument and why it is wrong
4. What would change your mind
```

### Step 3: Launch Subagents in Parallel

Use the Task tool to launch 3-4 subagents simultaneously. Each subagent runs independently with the prepared prompt.

**Subagent configuration:**

| Subagent | subagent_type | Notes |
|----------|---------------|-------|
| Gemini | `gemini-cli` | Google's model |
| Grok | `grok-cli` | xAI's model |
| Codex | `codex-cli` | OpenAI's model |
| Cursor | `cursor-cli` | Optional 4th voice (include for high-stakes decisions) |

Launch all subagents in a single message using multiple Task tool calls. Each call should:
- Use a descriptive `description` like "Council Member: Gemini evaluating caching strategy"
- Pass the full prepared prompt
- NOT share any other model's response

**Important:** If a subagent type is unavailable or fails to respond, proceed with the responses you have. The council works with a minimum of 2 responses.

### Step 4: Collect Responses

Wait for all subagents to complete. Record each response with the model name.

If a subagent times out or errors, note it:
```
[Gemini]: responded
[Grok]: responded
[Codex]: timed out — proceeding with 2/3 responses
```

### Step 5: Chairman Synthesis

The primary Claude session acts as Chairman. Analyze all collected responses and produce the synthesis.

**For `consensus` mode:**

```markdown
## Council Verdict

**Question:** {original_prompt}
**Council Size:** {N} models responded

### Consensus Points (All Models Agree)
- {point 1}
- {point 2}

### Majority View ({N}/{total})
- {point where most but not all agree}

### Disagreements
| Topic | Model A | Model B | Model C |
|-------|---------|---------|---------|
| {area} | {position} | {position} | {position} |

### Chairman's Recommendation
{Synthesized best answer drawing from all responses. Not a compromise — pick the strongest reasoning regardless of which model produced it.}

**Confidence:** {LOW / MEDIUM / HIGH}
**Rationale:** {Why this confidence level — did models agree or diverge?}

### Individual Responses

<details>
<summary>Gemini</summary>
{full response}
</details>

<details>
<summary>Grok</summary>
{full response}
</details>

<details>
<summary>Codex</summary>
{full response}
</details>
```

**For `review` mode:**

```markdown
## Council Code Review

**Diff:** {file count} files changed
**Council Size:** {N} models responded

### Critical Issues (flagged by any model)
- [{severity}] {issue} — flagged by: {model(s)}

### Issue Agreement Matrix
| Issue | Gemini | Grok | Codex | Consensus |
|-------|--------|------|-------|-----------|
| {issue} | {Y/N} | {Y/N} | {Y/N} | {N}/{total} |

### Verdicts
| Model | Verdict | Confidence |
|-------|---------|------------|
| Gemini | {verdict} | {confidence} |
| Grok | {verdict} | {confidence} |
| Codex | {verdict} | {confidence} |

### Chairman's Verdict
**{SHIP / SHIP WITH CHANGES / BLOCK}**

{Reasoning. Issues flagged by multiple models are weighted higher. A single BLOCK from any model requires explicit Chairman override with justification.}

### Individual Reviews

<details>
<summary>Gemini</summary>
{full review}
</details>

<details>
<summary>Grok</summary>
{full review}
</details>

<details>
<summary>Codex</summary>
{full review}
</details>
```

**For `debate` mode:**

```markdown
## Council Debate

**Question:** {original_prompt}
**Council Size:** {N} models responded

### Position Map
| Model | Position | Confidence |
|-------|----------|------------|
| Gemini | {position} | {confidence} |
| Grok | {position} | {confidence} |
| Codex | {position} | {confidence} |

### Strongest Arguments (Across All Positions)

**For {Position A}:**
1. {strongest argument from any model supporting this}
2. {next strongest}

**For {Position B}:**
1. {strongest argument from any model supporting this}
2. {next strongest}

### Key Tension Points
- {Where the fundamental disagreement lies and why it is hard to resolve}

### Chairman's Analysis
{Do NOT pick a winner. Instead, clarify what the real decision factors are, what information would resolve the debate, and what the tradeoffs are. The user decides — the Chairman illuminates.}

### Individual Arguments

<details>
<summary>Gemini</summary>
{full argument}
</details>

<details>
<summary>Grok</summary>
{full argument}
</details>

<details>
<summary>Codex</summary>
{full argument}
</details>
```

## Rules

- ALWAYS launch subagents in parallel — sequential execution defeats the purpose of independent evaluation
- NEVER share one model's response with another model — independence is the entire value proposition
- ALWAYS include the individual responses in collapsed `<details>` blocks so the user can audit the synthesis
- If fewer than 2 models respond, report the failure and present the single response without synthesis
- For `review` mode, if the git diff is empty, tell the user and do not invoke the council
- For `debate` mode, do NOT pick a winner in the Chairman's analysis — the point is to surface the tradeoffs, not to decide
- For `consensus` mode, DO pick a recommendation — the point is to synthesize the best answer
- Weight issues/points flagged by multiple models higher than those flagged by only one
- If all models agree, say so clearly — unanimous consensus is valuable signal
- If all models disagree, say so clearly — that signals the question may not have a single right answer
- Keep the Chairman synthesis concise (under 500 words) — the individual responses provide the depth

## When to Use

- Architecture decisions with significant long-term impact
- Code review for high-risk changes (security, data, payments)
- Technical debates where the team is split
- Evaluating approaches when you want diverse perspectives
- Any decision where being wrong is expensive

## Related Skills

- `/code-review` — Single-model adversarial review (faster, less thorough)
- `/review` — gstack pre-landing PR review
- `/premortem` — Failure analysis for features (complementary to council debate)
