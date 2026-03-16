"""Collect proof-of-work from completed tasks."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from symphony.scheduler.state_machine import Task

logger = logging.getLogger(__name__)


async def collect_proof(task: Task) -> dict:
    """Gather proof-of-work evidence from a completed task's workspace."""
    proof: dict = {
        "task_id": task.id,
        "tokens_in": task.tokens_in,
        "tokens_out": task.tokens_out,
        "cost_usd": task.cost_usd,
        "tools_used": task.tools_used,
        "duration_seconds": task.elapsed_seconds,
    }

    workspace = Path(task.workspace_path)
    if not workspace.exists():
        return proof

    # Collect git diff stats
    try:
        proc = await asyncio.create_subprocess_exec(
            "git", "diff", "--stat", "HEAD~1",
            cwd=str(workspace),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await proc.communicate()
        if proc.returncode == 0 and stdout:
            proof["diff_stats"] = stdout.decode().strip()
    except Exception:
        pass

    # Count new commits
    try:
        proc = await asyncio.create_subprocess_exec(
            "git", "rev-list", "--count", "HEAD",
            cwd=str(workspace),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await proc.communicate()
        if proc.returncode == 0 and stdout:
            proof["commit_count"] = int(stdout.decode().strip())
    except Exception:
        pass

    return proof
