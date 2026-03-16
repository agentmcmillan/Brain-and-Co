"""Tests for NDJSON stream parser."""

import asyncio
import json
import pytest
from symphony.agent.stream_parser import EventType, StreamEvent, parse_ndjson_stream


@pytest.mark.asyncio
async def test_parse_assistant_event():
    events: list[StreamEvent] = []

    data = json.dumps({"type": "assistant", "content": [{"type": "text", "text": "Hello"}]})
    reader = asyncio.StreamReader()
    reader.feed_data((data + "\n").encode())
    reader.feed_eof()

    await parse_ndjson_stream(reader, events.append)

    assert len(events) == 1
    assert events[0].type == EventType.ASSISTANT
    assert events[0].message == "Hello"


@pytest.mark.asyncio
async def test_parse_tool_use_event():
    events: list[StreamEvent] = []

    data = json.dumps({"type": "tool_use", "tool": {"name": "Read", "input": "/foo.py"}})
    reader = asyncio.StreamReader()
    reader.feed_data((data + "\n").encode())
    reader.feed_eof()

    await parse_ndjson_stream(reader, events.append)

    assert len(events) == 1
    assert events[0].type == EventType.TOOL_USE
    assert events[0].tool_name == "Read"
    assert events[0].tool_input == "/foo.py"


@pytest.mark.asyncio
async def test_parse_result_event():
    events: list[StreamEvent] = []

    data = json.dumps({
        "type": "result",
        "result": "Task completed",
        "session_id": "abc-123",
        "usage": {"input_tokens": 1000, "output_tokens": 500},
        "cost_usd": 0.05,
    })
    reader = asyncio.StreamReader()
    reader.feed_data((data + "\n").encode())
    reader.feed_eof()

    await parse_ndjson_stream(reader, events.append)

    assert len(events) == 1
    assert events[0].type == EventType.RESULT
    assert events[0].result_text == "Task completed"
    assert events[0].input_tokens == 1000
    assert events[0].output_tokens == 500
    assert events[0].cost_usd == 0.05


@pytest.mark.asyncio
async def test_skip_invalid_json():
    events: list[StreamEvent] = []

    reader = asyncio.StreamReader()
    reader.feed_data(b"not json\n")
    reader.feed_data(json.dumps({"type": "assistant", "content": "ok"}).encode() + b"\n")
    reader.feed_eof()

    await parse_ndjson_stream(reader, events.append)

    assert len(events) == 1
    assert events[0].type == EventType.ASSISTANT
