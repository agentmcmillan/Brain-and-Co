"""HTTP client for reporting events and status to Entropy Reader."""

from __future__ import annotations

import logging
import uuid

import httpx

from symphony.agent.stream_parser import EventType, StreamEvent
from symphony.config import SymphonyConfig
from symphony.scheduler.state_machine import Task

logger = logging.getLogger(__name__)


class EntropyClient:
    """Forwards events to Entropy Reader's ClaudeCodeWebhookController."""

    def __init__(self, config: SymphonyConfig):
        self.config = config
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.reporting.entropy_base_url,
                headers={"Authorization": f"Bearer {self.config.reporting.entropy_bearer_token}"},
                timeout=10.0,
            )
        return self._client

    async def report_event(self, task: Task, event: StreamEvent) -> None:
        """Forward a stream event to Entropy Reader's webhook endpoint."""
        if not self.config.reporting.entropy_bearer_token:
            return

        # Map event type to ClaudeCodeEvent format
        event_type = "text"
        if event.type == EventType.TOOL_USE:
            event_type = "tool_use"
        elif event.type == EventType.RESULT:
            event_type = "stop"

        payload = {
            "sessionId": task.session_id or str(uuid.uuid4()),
            "type": event_type,
            "message": event.message[:200] if event.message else None,
            "toolName": event.tool_name,
            "toolInput": event.tool_input,
        }

        try:
            client = await self._get_client()
            resp = await client.post("/api/v1/claude-code/events", json=payload)
            if resp.status_code not in (200, 204):
                logger.warning("Entropy event report got %d", resp.status_code)
        except httpx.HTTPError as e:
            logger.debug("Failed to report event to Entropy Reader: %s", e)

    async def report_completion(self, task: Task) -> None:
        """Report task completion/failure with proof-of-work."""
        if not self.config.reporting.entropy_bearer_token:
            return

        payload = {
            "taskId": task.id,
            "externalId": task.external_id,
            "status": task.status.value,
            "proof": {
                "pr_url": task.pr_url,
                "tokens_used": task.tokens_in + task.tokens_out,
                "cost_usd": task.cost_usd,
                "ci_status": task.ci_status,
                "duration_seconds": task.elapsed_seconds,
                "tools_used": task.tools_used,
                "error": task.error,
            },
        }

        try:
            client = await self._get_client()
            # This will eventually hit a SymphonyController callback endpoint
            await client.post("/api/v1/symphony/callback", json=payload)
        except httpx.HTTPError as e:
            logger.debug("Failed to report completion to Entropy Reader: %s", e)

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
