"""Entropy Reader as a task source — polls for pending tasks submitted from iOS."""

from __future__ import annotations

import logging

import httpx

from symphony.config import EntropySourceConfig
from symphony.scheduler.state_machine import Task
from symphony.sources.base import TaskSource

logger = logging.getLogger(__name__)


class EntropySource(TaskSource):
    """Polls Entropy Reader's Symphony endpoint for pending tasks."""

    def __init__(self, config: EntropySourceConfig):
        self.config = config
        self._seen_ids: set[str] = set()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers={"Authorization": f"Bearer {self.config.bearer_token}"},
                timeout=10.0,
            )
        return self._client

    async def poll(self) -> list[Task]:
        if not self.config.enabled or not self.config.bearer_token:
            return []

        try:
            client = await self._get_client()
            resp = await client.get("/api/v1/symphony/tasks", params={"status": "pending"})
            if resp.status_code != 200:
                logger.debug("Entropy poll returned %d", resp.status_code)
                return []

            data = resp.json().get("data", [])
            tasks: list[Task] = []

            for item in data:
                ext_id = item.get("id", "")
                if ext_id in self._seen_ids:
                    continue
                self._seen_ids.add(ext_id)

                task = Task(
                    title=item.get("title", "Untitled"),
                    prompt=item.get("prompt", ""),
                    repo_url=item.get("repo_url", item.get("repoUrl", "")),
                    branch=item.get("branch", "main"),
                    source="entropy",
                    external_id=ext_id,
                    priority=item.get("priority", 1),
                    allowed_tools=item.get("allowed_tools", item.get("allowedTools", [])),
                    max_turns=item.get("max_turns", item.get("maxTurns")),
                    timeout_minutes=item.get("timeout_minutes", item.get("timeoutMinutes")),
                )
                tasks.append(task)

            if tasks:
                logger.info("Polled %d new tasks from Entropy Reader", len(tasks))
            return tasks

        except httpx.HTTPError as e:
            logger.debug("Entropy poll failed: %s", e)
            return []

    async def mark_claimed(self, task: Task) -> None:
        try:
            client = await self._get_client()
            await client.post(f"/api/v1/symphony/tasks/{task.external_id}/claim", json={
                "symphonyTaskId": task.id,
            })
        except httpx.HTTPError:
            pass

    async def mark_completed(self, task: Task) -> None:
        # Handled by EntropyClient.report_completion
        pass

    async def mark_failed(self, task: Task) -> None:
        # Handled by EntropyClient.report_completion
        pass

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
