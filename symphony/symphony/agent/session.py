"""Agent session tracking — accumulates tokens, duration, and tool usage."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field


@dataclass
class AgentSession:
    """Tracks the state of a running Claude Code subprocess."""

    task_id: str
    process: asyncio.subprocess.Process
    workspace: str
    started_at: float = field(default_factory=time.time)
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    tools_used: set[str] = field(default_factory=set)
    last_event_at: float = field(default_factory=time.time)
    output_lines: list[str] = field(default_factory=list)
    result_text: str = ""
    claude_session_id: str = ""

    @property
    def pid(self) -> int | None:
        return self.process.pid

    @property
    def elapsed_seconds(self) -> float:
        return time.time() - self.started_at

    @property
    def is_alive(self) -> bool:
        return self.process.returncode is None

    def accumulate_tokens(self, input_tokens: int = 0, output_tokens: int = 0) -> None:
        self.tokens_in += input_tokens
        self.tokens_out += output_tokens
        self.last_event_at = time.time()

    def record_tool(self, tool_name: str) -> None:
        self.tools_used.add(tool_name)
        self.last_event_at = time.time()

    async def kill(self) -> None:
        """Forcefully terminate the agent process."""
        if self.is_alive:
            self.process.kill()
            await self.process.wait()
