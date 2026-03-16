"""Linear as a task source — polls for issues via GraphQL."""

from __future__ import annotations

import logging

import httpx

from symphony.config import LinearSourceConfig
from symphony.scheduler.state_machine import Task
from symphony.sources.base import TaskSource

logger = logging.getLogger(__name__)

LINEAR_API = "https://api.linear.app/graphql"

POLL_QUERY = """
query($teamKey: String!, $states: [String!]!, $labels: [String!]!) {
  issues(
    filter: {
      team: { key: { eq: $teamKey } }
      state: { name: { in: $states } }
      labels: { name: { in: $labels } }
    }
    first: 20
    orderBy: createdAt
  ) {
    nodes {
      id
      identifier
      title
      description
      url
      priority
      state { id name }
      labels { nodes { name } }
      branchName
    }
  }
}
"""

STATES_QUERY = """
query($teamKey: String!) {
  workflowStates(filter: { team: { key: { eq: $teamKey } } }) {
    nodes { id name }
  }
}
"""

UPDATE_ISSUE = """
mutation($issueId: String!, $stateId: String!) {
  issueUpdate(id: $issueId, input: { stateId: $stateId }) {
    success
  }
}
"""

CREATE_COMMENT = """
mutation($issueId: String!, $body: String!) {
  commentCreate(input: { issueId: $issueId, body: $body }) {
    success
  }
}
"""


class LinearSource(TaskSource):
    """Polls Linear for issues matching configured filters."""

    def __init__(self, config: LinearSourceConfig):
        self.config = config
        self._seen_ids: set[str] = set()
        self._state_map: dict[str, str] = {}  # state name -> state id
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": self.config.api_key,
                    "Content-Type": "application/json",
                },
                timeout=15.0,
            )
        return self._client

    async def _graphql(self, query: str, variables: dict | None = None) -> dict:
        client = await self._get_client()
        resp = await client.post(LINEAR_API, json={"query": query, "variables": variables or {}})
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            raise RuntimeError(f"Linear GraphQL errors: {data['errors']}")
        return data.get("data", {})

    async def _load_states(self) -> None:
        """Cache workflow state name -> id mapping."""
        if self._state_map:
            return
        data = await self._graphql(STATES_QUERY, {"teamKey": self.config.team_key})
        for node in data.get("workflowStates", {}).get("nodes", []):
            self._state_map[node["name"]] = node["id"]
        logger.info("Loaded %d Linear states for team %s", len(self._state_map), self.config.team_key)

    async def poll(self) -> list[Task]:
        if not self.config.enabled or not self.config.api_key:
            return []

        try:
            await self._load_states()

            data = await self._graphql(POLL_QUERY, {
                "teamKey": self.config.team_key,
                "states": self.config.claimable_states,
                "labels": self.config.label_filter,
            })

            issues = data.get("issues", {}).get("nodes", [])
            tasks: list[Task] = []

            for issue in issues:
                issue_id = issue["id"]
                if issue_id in self._seen_ids:
                    continue
                self._seen_ids.add(issue_id)

                identifier = issue.get("identifier", "")
                description = issue.get("description", "")
                title = issue.get("title", "")

                prompt = f"""## Linear Issue: {identifier} — {title}

{description}

Complete the task described above. Follow any existing project conventions."""

                task = Task(
                    title=f"{identifier}: {title}",
                    prompt=prompt,
                    source="linear",
                    external_id=issue_id,
                    priority=issue.get("priority", 1),
                    branch=issue.get("branchName") or "main",
                )
                tasks.append(task)

            if tasks:
                logger.info("Polled %d new issues from Linear", len(tasks))
            return tasks

        except Exception as e:
            logger.warning("Linear poll failed: %s", e)
            return []

    async def mark_claimed(self, task: Task) -> None:
        """Move issue to In Progress state."""
        state_id = self._state_map.get(self.config.in_progress_state)
        if not state_id:
            return
        try:
            await self._graphql(UPDATE_ISSUE, {
                "issueId": task.external_id,
                "stateId": state_id,
            })
            logger.info("Moved %s to '%s'", task.title, self.config.in_progress_state)
        except Exception as e:
            logger.warning("Failed to update Linear issue state: %s", e)

    async def mark_completed(self, task: Task) -> None:
        """Move issue to Done and post proof-of-work comment."""
        state_id = self._state_map.get(self.config.done_state)
        if state_id:
            try:
                await self._graphql(UPDATE_ISSUE, {
                    "issueId": task.external_id,
                    "stateId": state_id,
                })
            except Exception as e:
                logger.warning("Failed to move issue to Done: %s", e)

        # Post proof-of-work comment
        await self._post_proof_comment(task)

    async def mark_failed(self, task: Task) -> None:
        """Move issue to Needs Review and post error comment."""
        state_id = self._state_map.get(self.config.failed_state)
        if state_id:
            try:
                await self._graphql(UPDATE_ISSUE, {
                    "issueId": task.external_id,
                    "stateId": state_id,
                })
            except Exception as e:
                logger.warning("Failed to move issue to failed state: %s", e)

        body = f"""### Symphony Agent — Failed

**Task ID**: `{task.id}`
**Attempt**: {task.attempt + 1}
**Error**: {task.error or 'Unknown error'}
**Tokens**: {task.tokens_in + task.tokens_out:,}
**Duration**: {task.elapsed_seconds:.0f}s
"""
        try:
            await self._graphql(CREATE_COMMENT, {
                "issueId": task.external_id,
                "body": body,
            })
        except Exception as e:
            logger.warning("Failed to post failure comment: %s", e)

    async def _post_proof_comment(self, task: Task) -> None:
        """Post a proof-of-work summary as a Linear comment."""
        pr_line = f"**PR**: {task.pr_url}" if task.pr_url else "**PR**: Not created"
        ci_line = f"**CI**: {task.ci_status}" if task.ci_status else ""

        body = f"""### Symphony Agent — Completed

**Task ID**: `{task.id}`
{pr_line}
{ci_line}
**Tokens**: {task.tokens_in + task.tokens_out:,} (in: {task.tokens_in:,}, out: {task.tokens_out:,})
**Cost**: ${task.cost_usd:.4f}
**Duration**: {task.elapsed_seconds:.0f}s
**Tools Used**: {', '.join(task.tools_used) if task.tools_used else 'None'}
"""
        try:
            await self._graphql(CREATE_COMMENT, {
                "issueId": task.external_id,
                "body": body.strip(),
            })
            logger.info("Posted proof-of-work comment on %s", task.title)
        except Exception as e:
            logger.warning("Failed to post proof comment: %s", e)

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
