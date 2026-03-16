"""Create a pull request from completed task workspace."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from symphony.config import SymphonyConfig
from symphony.scheduler.state_machine import Task

logger = logging.getLogger(__name__)


async def create_pr(task: Task, config: SymphonyConfig) -> None:
    """Detect new commits and create a PR via gh CLI."""
    workspace = Path(task.workspace_path)
    if not workspace.exists():
        return

    # Check if there are new commits
    proc = await asyncio.create_subprocess_exec(
        "git", "log", "--oneline", "-5",
        cwd=str(workspace),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    stdout, _ = await proc.communicate()
    if proc.returncode != 0 or not stdout:
        logger.debug("No commits found in workspace for task %s", task.id)
        return

    # Check if we're on a branch (not detached HEAD)
    proc = await asyncio.create_subprocess_exec(
        "git", "branch", "--show-current",
        cwd=str(workspace),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    stdout, _ = await proc.communicate()
    branch = stdout.decode().strip() if stdout else ""

    if not branch:
        # Create a branch from current state
        branch = f"symphony/{task.id}"
        proc = await asyncio.create_subprocess_exec(
            "git", "checkout", "-b", branch,
            cwd=str(workspace),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()

    # Push the branch
    env = dict(os.environ)
    if config.agent.github_token:
        env["GH_TOKEN"] = config.agent.github_token
        env["GITHUB_TOKEN"] = config.agent.github_token

    proc = await asyncio.create_subprocess_exec(
        "git", "push", "-u", "origin", branch,
        cwd=str(workspace),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        logger.warning("git push failed for task %s: %s", task.id, stderr.decode()[:200])
        return

    # Create PR via gh CLI
    title = task.title or f"Symphony: {task.id}"
    body = f"""## Symphony Automated PR

**Task**: {task.title}
**Source**: {task.source}
**Tokens**: {task.tokens_in + task.tokens_out:,}
**Cost**: ${task.cost_usd:.4f}
**Duration**: {task.elapsed_seconds:.0f}s

---
*Created by Symphony (Brain-and-Co autonomous agent orchestrator)*
"""

    proc = await asyncio.create_subprocess_exec(
        "gh", "pr", "create",
        "--title", title[:256],
        "--body", body,
        "--head", branch,
        cwd=str(workspace),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode == 0 and stdout:
        pr_url = stdout.decode().strip()
        task.pr_url = pr_url
        logger.info("Created PR for task %s: %s", task.id, pr_url)
    else:
        logger.warning("gh pr create failed for task %s: %s", task.id, stderr.decode()[:200])
