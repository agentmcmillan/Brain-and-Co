# gstack Integration

[gstack](https://github.com/garrytan/gstack) is a unified AI engineering workflow system by Garry Tan. It provides 8 skills for Claude Code covering the full development lifecycle.

## Install

```bash
git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup
```

Requires [Bun](https://bun.sh) runtime.

## Skills Provided

| Skill | Command | Purpose |
|-------|---------|---------|
| Plan (CEO) | `/plan-ceo-review` | Founder mode: rethink the problem, find the 10-star product |
| Plan (Eng) | `/plan-eng-review` | Tech lead mode: architecture, data flow, edge cases, tests |
| Review | `/review` | Pre-landing code review: SQL safety, LLM trust, structural issues |
| Ship | `/ship` | Release workflow: sync main, tests, review, PR |
| Browse | `/browse` or `$B` | Headless browser: navigate, click, screenshot, verify |
| QA | `/qa` | Systematic QA testing: diff-aware, full, quick, or regression |
| Cookies | `/setup-browser-cookies` | Import cookies from real browser for authenticated testing |
| Retro | `/retro` | Engineering retrospective with per-person feedback |

## How It Works

gstack runs a persistent headless Chromium daemon:
- First command starts the daemon (~3s startup)
- Subsequent commands are HTTP POSTs (~100ms latency)
- State persists: cookies, tabs, localStorage, login sessions
- Auto-shuts down after 30 minutes idle

## Integration with Brain-and-Co

gstack skills are referenced in:
- `.claude/rules/unified-workflow.md` — Workflow coordination rules
- `skills/integration/unified-workflow.md` — Quality gate flow

When both gstack and Brain-and-Co are installed:
- `/review` = gstack pre-landing PR review
- `/code-review` = Brain-Wave adversarial reviewer agent
- Both are valid — use `/review` for PR-focused work, `/code-review` for broader analysis

## Auto-Upgrade

gstack checks for updates daily. When an upgrade is available:
```
/gstack-upgrade
```
