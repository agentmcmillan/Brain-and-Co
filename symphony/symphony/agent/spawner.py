"""Spawn and manage Claude Code CLI subprocesses."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from symphony.agent.session import AgentSession
from symphony.agent.stream_parser import EventType, StreamEvent, parse_ndjson_stream
from symphony.config import SymphonyConfig
from symphony.scheduler.state_machine import Task

logger = logging.getLogger(__name__)


class AgentSpawner:
    def __init__(self, config: SymphonyConfig):
        self.config = config

    async def spawn(
        self,
        task: Task,
        workspace: Path,
        on_event: asyncio.coroutines | None = None,
    ) -> AgentSession:
        """Launch a Claude Code subprocess for a task.

        Returns an AgentSession with the running process.
        The caller should await session.process.wait() to detect completion.
        """
        cmd = self._build_command(task)
        env = self._build_env()

        logger.info(
            "Spawning agent for task %s in %s (max_turns=%s)",
            task.id,
            workspace,
            task.max_turns or self.config.agent.turns_per_heartbeat,
        )

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(workspace),
            env=env,
        )

        session = AgentSession(
            task_id=task.id,
            process=proc,
            workspace=str(workspace),
        )
        task.pid = proc.pid
        task.session_id = f"symphony-{task.id}"

        # Start NDJSON stream parser as a background task
        if proc.stdout:

            async def _handle_event(event: StreamEvent) -> None:
                self._update_session(session, event)
                if on_event:
                    await on_event(event)

            asyncio.create_task(
                parse_ndjson_stream(proc.stdout, _handle_event),
                name=f"stream-{task.id}",
            )

        return session

    def _build_command(self, task: Task) -> list[str]:
        cmd = [self.config.agent.claude_path]

        # Resume existing session or start new one
        if task.claude_session_id:
            cmd.extend(["--resume", task.claude_session_id])
        else:
            cmd.extend(["-p", task.prompt])

        cmd.extend([
            "--output-format", "stream-json",
            "--dangerously-skip-permissions",
            "--verbose",
        ])

        allowed = task.allowed_tools or self.config.agent.default_allowed_tools
        if allowed:
            cmd.extend(["--allowedTools", ",".join(allowed)])

        max_turns = task.max_turns or self.config.agent.turns_per_heartbeat
        cmd.extend(["--max-turns", str(max_turns)])

        if self.config.agent.model:
            cmd.extend(["--model", self.config.agent.model])

        return cmd

    def _build_env(self) -> dict[str, str]:
        env = dict(os.environ)
        # Only set API key if configured — Claude Code can also use OAuth session
        if self.config.agent.anthropic_api_key:
            env["ANTHROPIC_API_KEY"] = self.config.agent.anthropic_api_key
        env["TERM"] = "dumb"
        if self.config.agent.github_token:
            env["GITHUB_TOKEN"] = self.config.agent.github_token
            env["GH_TOKEN"] = self.config.agent.github_token
        return env

    def _update_session(self, session: AgentSession, event: StreamEvent) -> None:
        """Update session state from a stream event."""
        if event.type == EventType.TOOL_USE and event.tool_name:
            session.record_tool(event.tool_name)

        if event.input_tokens or event.output_tokens:
            session.accumulate_tokens(event.input_tokens, event.output_tokens)

        if event.cost_usd:
            session.cost_usd = event.cost_usd

        if event.type == EventType.RESULT:
            session.result_text = event.result_text

        if event.type == EventType.ASSISTANT:
            session.output_lines.append(event.message)

        # Capture claude session ID for heartbeat resumption
        if event.session_id and not session.claude_session_id:
            session.claude_session_id = event.session_id
