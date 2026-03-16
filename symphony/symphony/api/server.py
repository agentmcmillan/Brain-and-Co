"""Lightweight HTTP API for task submission and status."""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

if TYPE_CHECKING:
    from symphony.scheduler.dispatcher import Dispatcher

_dispatcher: Dispatcher | None = None
_api_token: str = ""
_start_time: float = time.time()


def _auth(request: Request) -> bool:
    """Check bearer token authentication."""
    if not _api_token:
        return True
    auth = request.headers.get("authorization", "")
    return auth == f"Bearer {_api_token}"


async def health(request: Request) -> JSONResponse:
    assert _dispatcher is not None
    return JSONResponse({
        "status": "ok",
        "active_agents": _dispatcher.queue.running_count,
        "queued": _dispatcher.queue.pending_count,
        "uptime_seconds": int(time.time() - _start_time),
    })


async def submit_task(request: Request) -> JSONResponse:
    if not _auth(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    assert _dispatcher is not None
    body = await request.json()

    from symphony.scheduler.state_machine import Task

    task = Task(
        title=body.get("title", "Untitled"),
        prompt=body.get("prompt", ""),
        repo_url=body.get("repo_url", ""),
        branch=body.get("branch", "main"),
        source=body.get("source", "api"),
        external_id=body.get("external_id", ""),
        priority=body.get("priority", 1),
        depends_on=body.get("depends_on", []),
        allowed_tools=body.get("allowed_tools", []),
        max_turns=body.get("max_turns"),
        timeout_minutes=body.get("timeout_minutes"),
        callback_url=body.get("callback_url", ""),
    )

    accepted = await _dispatcher.submit_task(task)
    if not accepted:
        return JSONResponse({"error": "duplicate task"}, status_code=409)

    return JSONResponse({"task_id": task.id, "status": task.status.value}, status_code=201)


async def list_tasks(request: Request) -> JSONResponse:
    if not _auth(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    assert _dispatcher is not None
    status_filter = request.query_params.get("status")

    tasks = _dispatcher.queue.all_tasks()
    if status_filter:
        tasks = [t for t in tasks if t.status.value == status_filter.upper()]

    limit = int(request.query_params.get("limit", "50"))
    all_sorted = sorted(tasks, key=lambda t: t.created_at, reverse=True)
    paged = all_sorted[:limit]

    return JSONResponse({"tasks": [t.to_dict() for t in paged], "total": len(all_sorted)})


async def get_task(request: Request) -> JSONResponse:
    if not _auth(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    assert _dispatcher is not None
    task_id = request.path_params["task_id"]
    task = _dispatcher.queue.get_task(task_id)
    if not task:
        return JSONResponse({"error": "not found"}, status_code=404)
    return JSONResponse(task.to_dict())


async def submit_chain(request: Request) -> JSONResponse:
    """Submit an ordered chain of tasks where each depends on the previous."""
    if not _auth(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    assert _dispatcher is not None
    body = await request.json()
    tasks_data = body if isinstance(body, list) else body.get("tasks", [])

    if not tasks_data:
        return JSONResponse({"error": "empty chain"}, status_code=400)

    from symphony.scheduler.state_machine import Task

    created = []
    prev_id: str | None = None

    for item in tasks_data:
        deps = item.get("depends_on", [])
        if prev_id and prev_id not in deps:
            deps.append(prev_id)

        task = Task(
            title=item.get("title", "Untitled"),
            prompt=item.get("prompt", ""),
            repo_url=item.get("repo_url", ""),
            branch=item.get("branch", "main"),
            source=item.get("source", "api"),
            priority=item.get("priority", 1),
            depends_on=deps,
            allowed_tools=item.get("allowed_tools", []),
            max_turns=item.get("max_turns"),
            timeout_minutes=item.get("timeout_minutes"),
        )

        accepted = await _dispatcher.submit_task(task)
        if accepted:
            created.append({"task_id": task.id, "title": task.title, "depends_on": task.depends_on})
        prev_id = task.id

    return JSONResponse({"chain": created, "total": len(created)}, status_code=201)


async def cancel_task(request: Request) -> JSONResponse:
    if not _auth(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    assert _dispatcher is not None
    task_id = request.path_params["task_id"]
    ok = await _dispatcher.cancel_task(task_id)
    if not ok:
        return JSONResponse({"error": "task not cancellable"}, status_code=400)

    task = _dispatcher.queue.get_task(task_id)
    return JSONResponse({"task_id": task_id, "status": task.status.value if task else "CANCELLED"})


def create_app(dispatcher: Dispatcher, api_token: str = "") -> Starlette:
    global _dispatcher, _api_token, _start_time
    _dispatcher = dispatcher
    _api_token = api_token
    _start_time = time.time()

    routes = [
        Route("/health", health, methods=["GET"]),
        Route("/tasks", submit_task, methods=["POST"]),
        Route("/tasks", list_tasks, methods=["GET"]),
        Route("/tasks/chain", submit_chain, methods=["POST"]),
        Route("/tasks/{task_id}", get_task, methods=["GET"]),
        Route("/tasks/{task_id}/cancel", cancel_task, methods=["POST"]),
    ]

    return Starlette(routes=routes)
