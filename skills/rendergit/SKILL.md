---
name: rendergit
description: Flatten a repository into HTML or LLM-ready text using rendergit
version: 1.0.0
author: agentmcmillan
homepage: https://github.com/karpathy/rendergit
user-invocable: true
tags:
  - rendering
  - llm
  - codebase
  - documentation
metadata:
  requires:
    bins:
      - uv
      - git
    config: []
  os:
    - darwin
    - linux
---

# Rendergit: Flatten a Repo for LLM Consumption

Generate a single-page view of a repository using [Karpathy's rendergit](https://github.com/karpathy/rendergit). Produces a syntax-highlighted HTML page for humans and a CXML text dump for LLMs.

## What It Does

- Checks if `rendergit` is installed; installs it via `uv` if missing
- Runs `rendergit` against the current repository (or a specified repo URL)
- Produces two output modes:
  - **HTML view** -- syntax-highlighted code, sidebar navigation, markdown rendering
  - **CXML/LLM text view** -- raw text format for pasting into Claude, ChatGPT, or other LLMs
- Outputs to `.rendergit/` by default (or a custom path)
- Can feed directly into Alpha-Wave indexing for Brain-Wave integration

## Usage

```
/rendergit                          # Render current repo to .rendergit/
/rendergit --llm-view               # Output just the CXML text to stdout
/rendergit --output build/docs      # Custom output directory
/rendergit https://github.com/user/repo  # Render a remote repo
```

## Arguments

| Flag | Default | Description |
|------|---------|-------------|
| `--output <path>` | `.rendergit/` | Directory to write output files |
| `--llm-view` | off | Output only the CXML text (no HTML), useful for piping to agents |
| `--open` | off | Open the HTML output in the default browser after rendering |

## Installation Check

On first run, the skill verifies that `rendergit` is available:

```bash
# Check if rendergit is installed
which rendergit

# If not found, install via uv
uv tool install git+https://github.com/karpathy/rendergit
```

If `uv` is not installed, the skill will display instructions:
```
rendergit requires uv for installation.
Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
Then retry: /rendergit
```

## Output Structure

```
.rendergit/
├── index.html          # Full HTML view with sidebar nav + syntax highlighting
└── cxml.txt            # Raw CXML text for LLM consumption
```

### HTML View

The HTML page includes:
- Sidebar with directory tree navigation
- Syntax highlighting via Pygments
- Markdown rendering for `.md` files
- Responsive layout (mobile-friendly)
- Full-page browser search (Ctrl+F across the entire codebase)
- Intelligent filtering (skips binaries, large generated files)

### CXML/LLM Text View

The CXML output is a plain-text representation of the entire codebase, structured for LLM consumption. Each file is delimited with clear markers showing the file path and contents. This format is designed for:
- Pasting into LLM chat interfaces
- Piping to agent tools for analysis
- Feeding into Alpha-Wave for indexing

## Alpha-Wave Integration

After rendering, the CXML output can be fed into Alpha-Wave for indexing:

```
/rendergit --llm-view > .rendergit/cxml.txt
/alpha-wave
```

This is especially useful when:
- Working with a new or unfamiliar codebase
- You want Alpha-Wave to index a remote repo without cloning it fully
- Building a Brain-Wave memory system for a third-party project

The rendered CXML gives Alpha-Wave a complete snapshot of the codebase in a single file, making indexing faster and more comprehensive.

## Example

```
/rendergit

=== Rendergit ===

Checking installation...
  rendergit found at /Users/conor/.local/bin/rendergit

Rendering current repository...
  Repository: Brain-and-Co
  Files scanned: 142
  Files included: 118 (skipped 24 binary/generated)

Output:
  HTML view:  .rendergit/index.html
  CXML view:  .rendergit/cxml.txt

Open in browser? Use: open .rendergit/index.html
```

### LLM View Example

```
/rendergit --llm-view

=== Rendergit (LLM View) ===

Rendering current repository to CXML...

--- Output (128,432 tokens estimated) ---

<document>
<source>src/gateway/index.ts</source>
<content>
import { FastMCP } from 'fastmcp';
...
</content>
</document>

<document>
<source>memento/src/server.ts</source>
<content>
...
</content>
</document>

...
```

## When to Use

- Sharing a full codebase with an LLM for analysis
- Generating a browsable HTML snapshot for documentation
- Preparing a repo for Alpha-Wave indexing
- Reviewing an unfamiliar repo in a single page
- Creating a portable, offline view of a repository

## Related Skills

- `alpha-wave` -- Index the codebase (can consume rendergit CXML output)
- `beta-wave` -- Map architecture and dependencies
- `brain-wave-init` -- Full memory system setup
