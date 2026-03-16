"""Priority queue with concurrency slot management."""

from __future__ import annotations

import heapq
import logging
from typing import Iterator

from symphony.scheduler.state_machine import Task, TaskStatus

logger = logging.getLogger(__name__)


class TaskQueue:
    """Thread-safe priority queue with concurrency tracking."""

    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self._pending: list[tuple[int, float, Task]] = []  # (priority, created_at, task)
        self._running: dict[str, Task] = {}  # task_id -> task
        self._completed: dict[str, Task] = {}  # task_id -> task
        self._all: dict[str, Task] = {}  # task_id -> task (all tasks ever seen)

    @property
    def slots_available(self) -> int:
        return max(0, self.max_concurrent - len(self._running))

    @property
    def has_pending(self) -> bool:
        return len(self._pending) > 0

    @property
    def running_count(self) -> int:
        return len(self._running)

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    def enqueue(self, task: Task) -> bool:
        """Add a task to the queue. Returns False if duplicate."""
        if task.id in self._all:
            return False
        self._all[task.id] = task
        heapq.heappush(self._pending, (task.priority, task.created_at, task))
        logger.info("Enqueued task %s: %s (priority=%d)", task.id, task.title, task.priority)
        return True

    def enqueue_existing(self, task: Task) -> None:
        """Re-add a known task (e.g. after SUSPENDED → QUEUED). Skips duplicate check."""
        self._all[task.id] = task
        heapq.heappush(self._pending, (task.priority, task.created_at, task))
        logger.info("Re-enqueued existing task %s (status=%s)", task.id, task.status.value)

    def re_enqueue(self, task: Task) -> None:
        """Re-add a task after retry."""
        task.transition(TaskStatus.QUEUED)
        heapq.heappush(self._pending, (task.priority, task.created_at, task))
        logger.info("Re-enqueued task %s (attempt %d)", task.id, task.attempt)

    def next(self) -> Task | None:
        """Pop the highest-priority pending task, or None if queue is empty.

        Skips tasks with unmet dependencies (all depends_on must be SUCCESS).
        """
        deferred: list[tuple[int, float, Task]] = []
        result = None

        while self._pending:
            entry = heapq.heappop(self._pending)
            _, _, task = entry
            if task.status != TaskStatus.QUEUED:
                continue
            if self._deps_met(task):
                result = task
                break
            # Put it back later — deps not met yet
            deferred.append(entry)

        for entry in deferred:
            heapq.heappush(self._pending, entry)

        return result

    def _deps_met(self, task: Task) -> bool:
        """Check if all depends_on tasks have reached SUCCESS."""
        if not task.depends_on:
            return True
        for dep_id in task.depends_on:
            dep = self._all.get(dep_id)
            if not dep or dep.status != TaskStatus.SUCCESS:
                return False
        return True

    def mark_running(self, task: Task) -> None:
        """Move task to running state."""
        self._running[task.id] = task

    def mark_completed(self, task: Task) -> None:
        """Move task from running to completed."""
        self._running.pop(task.id, None)
        self._completed[task.id] = task

    def get_task(self, task_id: str) -> Task | None:
        return self._all.get(task_id)

    def get_running_tasks(self) -> list[Task]:
        return list(self._running.values())

    def all_tasks(self) -> list[Task]:
        return list(self._all.values())

    def iter_by_status(self, status: TaskStatus) -> Iterator[Task]:
        for task in self._all.values():
            if task.status == status:
                yield task
