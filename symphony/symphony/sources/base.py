"""Abstract base class for task sources."""

from __future__ import annotations

from abc import ABC, abstractmethod

from symphony.scheduler.state_machine import Task


class TaskSource(ABC):
    """Interface for polling external systems for tasks."""

    @abstractmethod
    async def poll(self) -> list[Task]:
        """Poll for new tasks. Returns tasks not yet seen."""
        ...

    @abstractmethod
    async def mark_claimed(self, task: Task) -> None:
        """Notify the source that a task has been claimed."""
        ...

    @abstractmethod
    async def mark_completed(self, task: Task) -> None:
        """Notify the source that a task has completed."""
        ...

    @abstractmethod
    async def mark_failed(self, task: Task) -> None:
        """Notify the source that a task has failed."""
        ...
