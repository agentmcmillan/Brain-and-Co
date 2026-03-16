"""Templates for CLAUDE.md injection into workspaces."""

from __future__ import annotations

from symphony.scheduler.state_machine import Task


def render_claude_md(task: Task, prior_context: list[dict] | None = None) -> str:
    """Generate a task-specific CLAUDE.md section."""
    lines = [
        "# Symphony Task Context",
        "",
        f"**Task ID**: {task.id}",
        f"**Title**: {task.title}",
        f"**Source**: {task.source}",
        f"**Attempt**: {task.attempt + 1}",
        "",
        "## Instructions",
        "",
        task.prompt,
        "",
        "## Guidelines",
        "",
        "- Complete the task described above.",
        "- Create a new git branch for your changes: `symphony/{task_id}`",
        "- Make atomic, well-described commits.",
        "- Run any existing tests to verify your changes don't break anything.",
        "- If tests exist and fail, fix them before finishing.",
        "- Do NOT push to remote — the orchestrator handles that.",
        "",
    ]

    if prior_context:
        lines.extend([
            "## Prior Context",
            "",
            "Previous work on this repository (most recent first):",
            "",
        ])
        for entry in prior_context:
            lines.append(f"- **Task {entry['task_id']}**: {entry['summary'][:500]}")
        lines.append("")

    return "\n".join(lines)
