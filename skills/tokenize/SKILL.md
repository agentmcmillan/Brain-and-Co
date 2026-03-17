---
name: tokenize
description: "Token analysis and cost estimation. Count tokens in files, prompts, directories, or git diffs using tiktoken (cl100k_base). Estimate API costs across models. Show token distribution breakdown. Inspired by Karpathy's minbpe/rustbpe."
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/karpathy/minbpe
user-invocable: true
tags:
  - tokens
  - cost
  - analysis
  - tiktoken
  - optimization
metadata:
  requires:
    bins:
      - python3
      - git
    pip:
      - tiktoken
  os:
    - darwin
    - linux
---

# Tokenize: Token Analysis and Cost Estimation

Inspired by [Karpathy's minbpe](https://github.com/karpathy/minbpe) and [rustbpe](https://github.com/karpathy/rustbpe). Analyze token counts and estimate API costs for files, prompts, directories, and diffs.

## What It Does

- Counts tokens using tiktoken with the `cl100k_base` encoding (used by Claude, GPT-4, and most modern LLMs)
- Estimates API costs across multiple models and providers
- Analyzes token distribution: code vs comments vs whitespace
- Supports files, directories (recursive), git diffs, and inline text

## Usage

```
/tokenize src/                          # Analyze all files in a directory
/tokenize src/main.py                   # Analyze a single file
/tokenize --cost "my prompt text here"  # Count tokens and estimate cost for inline text
/tokenize --diff HEAD~3                 # Analyze tokens in recent git diff
/tokenize --diff                        # Analyze tokens in uncommitted changes
/tokenize --summary                     # Token summary for the whole project
```

## Trigger

User runs `/tokenize` followed by a target (file, directory, text, or diff flag).

## Process

### Step 0: Check Prerequisites

Verify tiktoken is installed:

```bash
python3 -c "import tiktoken" 2>/dev/null
```

If this fails, prompt the user:

```
tiktoken is required but not installed. Install it with:

  pip install tiktoken

Or:

  pip3 install tiktoken

Would you like me to install it now?
```

If the user confirms, run `pip3 install tiktoken` and continue. If they decline, exit gracefully.

### Step 1: Parse Input

Determine the analysis target:

| Input | Target Type | Action |
|-------|-------------|--------|
| `/tokenize path/to/file` | Single file | Analyze that file |
| `/tokenize path/to/dir/` | Directory | Recursively analyze all text files |
| `/tokenize --cost "text"` | Inline text | Count tokens, show costs |
| `/tokenize --diff` | Git diff (uncommitted) | Analyze `git diff HEAD` |
| `/tokenize --diff HEAD~N` | Git diff (commits) | Analyze `git diff HEAD~N` |
| `/tokenize --diff branch` | Git diff (branch) | Analyze `git diff branch...HEAD` |
| `/tokenize --summary` | Project summary | Analyze all tracked files |

If no argument is provided, ask:

```
What should I tokenize? Provide a file path, directory, text in quotes, or use --diff.
```

### Step 2: Gather Content

**For single files:**
Read the file content. If the file is binary, report "Binary file — skipping token analysis" and exit.

**For directories:**
Recursively find all text files, excluding:
- `.git/`, `node_modules/`, `__pycache__/`, `.venv/`, `venv/`, `dist/`, `build/`
- Binary files (images, compiled files, archives)
- Files larger than 1MB (note them as skipped)

Use this command to list candidate files:
```bash
git ls-files -- '{target_dir}' 2>/dev/null || find '{target_dir}' -type f -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/__pycache__/*'
```

Prefer `git ls-files` as it respects `.gitignore`.

**For inline text:**
Use the text directly as provided.

**For git diffs:**
```bash
git diff HEAD           # for --diff (uncommitted)
git diff HEAD~N         # for --diff HEAD~N
git diff branch...HEAD  # for --diff branch
```

If the diff is empty, report "No changes found" and exit.

**For project summary:**
```bash
git ls-files
```

### Step 3: Count Tokens

Run the token counting script. Use this Python snippet via bash:

```bash
python3 -c "
import tiktoken, sys

enc = tiktoken.get_encoding('cl100k_base')
text = sys.stdin.read()
tokens = enc.encode(text)
print(len(tokens))
" < "{file_path}"
```

For directories, count each file individually and accumulate totals.

### Step 4: Token Distribution Analysis

For files and directories (not inline text), analyze the token breakdown:

```bash
python3 -c "
import tiktoken, sys, re

enc = tiktoken.get_encoding('cl100k_base')
text = sys.stdin.read()
lines = text.split('\n')

code_lines = []
comment_lines = []
blank_lines = []

for line in lines:
    stripped = line.strip()
    if not stripped:
        blank_lines.append(line)
    elif stripped.startswith(('#', '//', '/*', '*', '<!--', '\"\"\"', \"'''\", ';', '--')):
        comment_lines.append(line)
    else:
        code_lines.append(line)

code_tokens = len(enc.encode('\n'.join(code_lines)))
comment_tokens = len(enc.encode('\n'.join(comment_lines)))
blank_tokens = len(enc.encode('\n'.join(blank_lines)))
total_tokens = len(enc.encode(text))

print(f'total:{total_tokens}')
print(f'code:{code_tokens}')
print(f'comment:{comment_tokens}')
print(f'blank:{blank_tokens}')
print(f'lines:{len(lines)}')
print(f'code_lines:{len(code_lines)}')
print(f'comment_lines:{len(comment_lines)}')
print(f'blank_lines:{len(blank_lines)}')
" < "{file_path}"
```

### Step 5: Cost Estimation

Calculate estimated costs using current model pricing:

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Claude Opus 4 | $15.00 | $75.00 |
| Claude Sonnet 4 | $3.00 | $15.00 |
| Claude Haiku 3.5 | $0.80 | $4.00 |
| GPT-4o | $2.50 | $10.00 |
| GPT-4.1 | $2.00 | $8.00 |
| Gemini 2.5 Pro | $1.25 | $10.00 |
| Gemini 2.5 Flash | $0.15 | $3.50 |

**Note:** These are approximate prices and may change. The token counts use cl100k_base which is a reasonable approximation across models (actual tokenization varies by model, but counts are typically within 10-15%).

Cost formula: `tokens / 1_000_000 * price_per_million`

Show costs for input only (the content being analyzed is input context). Mention that output costs are separate and depend on response length.

### Step 6: Present Results

**For single file:**

```markdown
## Token Analysis: {filename}

| Metric | Value |
|--------|-------|
| Total tokens | {N} |
| Lines | {N} |
| Characters | {N} |

### Distribution
| Category | Tokens | % of Total | Lines |
|----------|--------|-----------|-------|
| Code | {N} | {pct}% | {N} |
| Comments | {N} | {pct}% | {N} |
| Whitespace/Blank | {N} | {pct}% | {N} |

### Estimated Input Cost (this file as context)
| Model | Cost |
|-------|------|
| Claude Opus 4 | ${cost} |
| Claude Sonnet 4 | ${cost} |
| Claude Haiku 3.5 | ${cost} |
| GPT-4o | ${cost} |
| GPT-4.1 | ${cost} |
| Gemini 2.5 Pro | ${cost} |
| Gemini 2.5 Flash | ${cost} |
```

**For directory:**

```markdown
## Token Analysis: {directory}/

| Metric | Value |
|--------|-------|
| Total tokens | {N} |
| Files analyzed | {N} |
| Files skipped | {N} (binary/too large) |

### Top 10 Files by Token Count
| File | Tokens | % of Total |
|------|--------|-----------|
| {path} | {N} | {pct}% |
| ... | ... | ... |

### By File Type
| Extension | Files | Tokens | % of Total |
|-----------|-------|--------|-----------|
| .ts | {N} | {N} | {pct}% |
| .py | {N} | {N} | {pct}% |
| ... | ... | ... | ... |

### Distribution (Aggregate)
| Category | Tokens | % of Total |
|----------|--------|-----------|
| Code | {N} | {pct}% |
| Comments | {N} | {pct}% |
| Whitespace/Blank | {N} | {pct}% |

### Estimated Input Cost (entire directory as context)
| Model | Cost |
|-------|------|
| Claude Opus 4 | ${cost} |
| Claude Sonnet 4 | ${cost} |
| Claude Haiku 3.5 | ${cost} |
| GPT-4o | ${cost} |
| GPT-4.1 | ${cost} |
| Gemini 2.5 Pro | ${cost} |
| Gemini 2.5 Flash | ${cost} |

{If total tokens > 200000, add warning:}
**Warning:** This directory exceeds 200K tokens. Most models have context limits between 128K-1M tokens. Consider analyzing subdirectories individually.
```

**For inline text (`--cost`):**

```markdown
## Token Analysis

| Metric | Value |
|--------|-------|
| Total tokens | {N} |
| Characters | {N} |
| Words (approx) | {N} |

### Estimated Input Cost
| Model | Cost |
|-------|------|
| Claude Opus 4 | ${cost} |
| Claude Sonnet 4 | ${cost} |
| Claude Haiku 3.5 | ${cost} |
| GPT-4o | ${cost} |
| GPT-4.1 | ${cost} |
| Gemini 2.5 Pro | ${cost} |
| Gemini 2.5 Flash | ${cost} |
```

**For git diff (`--diff`):**

```markdown
## Token Analysis: git diff {ref}

| Metric | Value |
|--------|-------|
| Diff tokens | {N} |
| Files changed | {N} |
| Lines added | {N} |
| Lines removed | {N} |

### Files in Diff
| File | Tokens (in diff) | Change |
|------|-----------------|--------|
| {path} | {N} | +{add}/-{del} |
| ... | ... | ... |

### Estimated Input Cost (diff as context)
| Model | Cost |
|-------|------|
| Claude Opus 4 | ${cost} |
| Claude Sonnet 4 | ${cost} |
| Claude Haiku 3.5 | ${cost} |
| GPT-4o | ${cost} |
| GPT-4.1 | ${cost} |
| Gemini 2.5 Pro | ${cost} |
| Gemini 2.5 Flash | ${cost} |
```

## Rules

- ALWAYS check for tiktoken before attempting analysis — do not fail with a cryptic Python import error
- NEVER analyze binary files — detect and skip them
- ALWAYS use `cl100k_base` encoding — it is the standard for modern LLMs
- For directories, respect `.gitignore` by using `git ls-files` when in a git repo
- Skip files larger than 1MB and report them as skipped with their size
- Round cost estimates to 4 decimal places (or use scientific notation for very small amounts)
- If a directory has more than 500 files, show only the top 20 by token count and summarize the rest
- Token counts are approximate across models — note this in the output for cost estimates
- For `--summary` mode, warn if total project tokens exceed the context window of common models
- NEVER modify any files — this is a read-only analysis tool

## When to Use

- Before adding files to LLM context, estimate cost
- Optimize prompts by understanding token overhead
- Compare token efficiency across codebases
- Estimate costs for batch processing jobs
- Identify bloated files that dominate context windows
- Audit a directory before feeding it to an LLM-powered tool

## Related Skills

- `/code-review` — Review code changes (uses tokens as context)
- `/council` — Multi-model consensus (multiplies token costs)
- `/forge` — Capture session learnings (generates token-consuming output)
