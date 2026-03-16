"""Poll GitHub Actions CI status for a PR."""

from __future__ import annotations

import asyncio
import logging
import os
import re

from symphony.config import SymphonyConfig
from symphony.scheduler.state_machine import Task

logger = logging.getLogger(__name__)

# Max time to wait for CI (5 minutes)
CI_TIMEOUT_SECONDS = 300
CI_POLL_INTERVAL = 15


async def check_ci(task: Task, config: SymphonyConfig) -> None:
    """Poll CI status for a task's PR until completion or timeout."""
    if not task.pr_url:
        return

    env = dict(os.environ)
    if config.agent.github_token:
        env["GH_TOKEN"] = config.agent.github_token

    # Extract PR number from URL
    match = re.search(r"/pull/(\d+)", task.pr_url)
    if not match:
        return

    elapsed = 0.0
    while elapsed < CI_TIMEOUT_SECONDS:
        proc = await asyncio.create_subprocess_exec(
            "gh", "pr", "checks", match.group(1),
            "--json", "name,state,conclusion",
            cwd=task.workspace_path or ".",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            env=env,
        )
        stdout, _ = await proc.communicate()

        if proc.returncode != 0 or not stdout:
            # No checks configured or gh failed
            task.ci_status = "no_checks"
            return

        import json
        try:
            checks = json.loads(stdout.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            task.ci_status = "unknown"
            return

        if not checks:
            task.ci_status = "no_checks"
            return

        # Check if all are complete
        all_complete = all(c.get("state") == "COMPLETED" for c in checks)
        if all_complete:
            all_passed = all(c.get("conclusion") == "SUCCESS" for c in checks)
            task.ci_status = "passed" if all_passed else "failed"
            logger.info("CI for task %s: %s", task.id, task.ci_status)
            return

        await asyncio.sleep(CI_POLL_INTERVAL)
        elapsed += CI_POLL_INTERVAL

    task.ci_status = "timeout"
    logger.warning("CI timed out for task %s after %ds", task.id, CI_TIMEOUT_SECONDS)
