"""Lifecycle hooks for task completion — PR creation, CI checking, notifications."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from symphony.config import SymphonyConfig
from symphony.scheduler.state_machine import Task

logger = logging.getLogger(__name__)


async def run_after_completion_hooks(task: Task, config: SymphonyConfig) -> None:
    """Run all configured post-completion hooks."""
    if not task.workspace_path:
        return

    workspace = Path(task.workspace_path)
    if not workspace.exists():
        return

    if config.hooks.auto_create_pr:
        from symphony.hooks.pr_creator import create_pr
        await create_pr(task, config)

    if config.hooks.check_ci and task.pr_url:
        from symphony.hooks.ci_checker import check_ci
        await check_ci(task, config)
