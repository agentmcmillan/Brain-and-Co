"""Parse NDJSON stream from Claude Code --output-format stream-json."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    ASSISTANT = "assistant"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    SYSTEM = "system"
    RESULT = "result"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class StreamEvent:
    """A parsed event from Claude Code's NDJSON output."""

    type: EventType
    raw: dict[str, Any]

    @property
    def message(self) -> str:
        """Extract human-readable message from the event."""
        if self.type == EventType.ASSISTANT:
            content = self.raw.get("content", "")
            if isinstance(content, list):
                return " ".join(
                    block.get("text", "") for block in content if block.get("type") == "text"
                )
            return str(content)
        if self.type == EventType.TOOL_USE:
            name = self.raw.get("tool", {}).get("name", "unknown")
            return f"Tool: {name}"
        if self.type == EventType.RESULT:
            return self.raw.get("result", "")
        return self.raw.get("message", str(self.raw))

    @property
    def tool_name(self) -> str | None:
        if self.type == EventType.TOOL_USE:
            return self.raw.get("tool", {}).get("name")
        return None

    @property
    def tool_input(self) -> str | None:
        if self.type == EventType.TOOL_USE:
            inp = self.raw.get("tool", {}).get("input", "")
            return str(inp)[:200]
        return None

    @property
    def input_tokens(self) -> int:
        usage = self.raw.get("usage", {})
        return usage.get("input_tokens", 0)

    @property
    def output_tokens(self) -> int:
        usage = self.raw.get("usage", {})
        return usage.get("output_tokens", 0)

    @property
    def cost_usd(self) -> float:
        return self.raw.get("cost_usd", 0.0)

    @property
    def session_id(self) -> str:
        return self.raw.get("session_id", "")

    @property
    def result_text(self) -> str:
        return self.raw.get("result", "")


EventCallback = Callable[[StreamEvent], Awaitable[None]]


def _classify_event(data: dict[str, Any]) -> EventType:
    """Classify a raw JSON event into an EventType."""
    etype = data.get("type", "")
    if etype == "assistant":
        return EventType.ASSISTANT
    if etype == "tool_use":
        return EventType.TOOL_USE
    if etype == "tool_result":
        return EventType.TOOL_RESULT
    if etype == "system":
        return EventType.SYSTEM
    if etype == "result":
        return EventType.RESULT
    if etype == "error":
        return EventType.ERROR
    return EventType.UNKNOWN


async def parse_ndjson_stream(
    stream: asyncio.StreamReader,
    on_event: EventCallback,
) -> None:
    """Read NDJSON lines from a stream and dispatch parsed events."""
    while True:
        line = await stream.readline()
        if not line:
            break

        text = line.decode("utf-8", errors="replace").strip()
        if not text:
            continue

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            logger.debug("Non-JSON line from claude: %s", text[:200])
            continue

        event_type = _classify_event(data)
        event = StreamEvent(type=event_type, raw=data)

        try:
            await on_event(event)
        except Exception:
            logger.exception("Error in event callback for %s", event_type)
