"""Context offloading — dual-write completion summaries to SQLite + Network MCP memento."""

from __future__ import annotations

import logging

import httpx

from symphony.config import SymphonyConfig
from symphony.persistence.store import TaskStore
from symphony.scheduler.state_machine import Task

logger = logging.getLogger(__name__)


class ContextManager:
    """Saves and retrieves task context for repo-scoped knowledge sharing."""

    def __init__(self, config: SymphonyConfig, store: TaskStore):
        self.config = config
        self.store = store
        self._memento_base = (
            f"{config.workspace.network_mcp_url}:{config.workspace.memento_port}"
        )

    async def save(self, task: Task, summary: str) -> None:
        """Dual-write context: SQLite for persistence, memento for cross-agent sharing."""
        if not summary or not task.repo_url:
            return

        # 1. Local persistence
        await self.store.save_context(task.id, task.repo_url, summary)
        logger.info("Saved context for task %s (repo=%s)", task.id, task.repo_url)

        # 2. Network MCP memento (best-effort)
        await self._remember_in_memento(task, summary)

    async def get_prior_context(self, repo_url: str, limit: int = 5) -> list[dict]:
        """Fetch recent context entries for a repo."""
        return await self.store.get_context_for_repo(repo_url, limit=limit)

    async def _remember_in_memento(self, task: Task, summary: str) -> None:
        """POST a memory to memento so other agents can recall it."""
        if not self.config.workspace.inject_network_mcp:
            return

        try:
            # Use memento's MCP endpoint to store the memory
            # The memento server accepts tool calls via its REST/SSE interface
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{self._memento_base}/memory",
                    json={
                        "content": f"[Symphony Task {task.id}] {task.title}: {summary}",
                        "metadata": {
                            "source": "symphony",
                            "task_id": task.id,
                            "repo_url": task.repo_url,
                            "type": "task_completion",
                        },
                    },
                    headers={"Authorization": f"Bearer {self.config.workspace.memento_access_key}"},
                )
                if resp.status_code < 300:
                    logger.debug("Stored context in memento for task %s", task.id)
                else:
                    logger.warning(
                        "Memento returned %d for task %s: %s",
                        resp.status_code, task.id, resp.text[:200],
                    )
        except Exception:
            # Memento is best-effort — don't fail the task
            logger.debug("Could not reach memento for task %s", task.id, exc_info=True)
