"""Task state machine with validated transitions."""

from __future__ import annotations

import enum
import time
import uuid
from dataclasses import dataclass, field


class TaskStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    PREPARING = "PREPARING"
    RUNNING = "RUNNING"
    SUSPENDED = "SUSPENDED"
    REVIEWING = "REVIEWING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    CANCELLED = "CANCELLED"


# Valid state transitions
TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.QUEUED: {TaskStatus.PREPARING, TaskStatus.CANCELLED},
    TaskStatus.PREPARING: {TaskStatus.RUNNING, TaskStatus.FAILURE},
    TaskStatus.RUNNING: {TaskStatus.REVIEWING, TaskStatus.FAILURE, TaskStatus.RETRY, TaskStatus.CANCELLED, TaskStatus.SUSPENDED},
    TaskStatus.SUSPENDED: {TaskStatus.PREPARING, TaskStatus.FAILURE, TaskStatus.CANCELLED},
    TaskStatus.REVIEWING: {TaskStatus.SUCCESS, TaskStatus.FAILURE},
    TaskStatus.FAILURE: {TaskStatus.RETRY},
    TaskStatus.RETRY: {TaskStatus.QUEUED},
    TaskStatus.SUCCESS: set(),
    TaskStatus.CANCELLED: set(),
}

TERMINAL_STATES = {TaskStatus.SUCCESS, TaskStatus.FAILURE, TaskStatus.CANCELLED}


@dataclass
class Task:
    """A unit of work to be executed by a Claude Code agent."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    prompt: str = ""
    repo_url: str = ""
    branch: str = "main"
    status: TaskStatus = TaskStatus.QUEUED
    source: str = "manual"  # "manual", "linear", "entropy"
    external_id: str = ""
    priority: int = 1  # 0 = highest
    allowed_tools: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    max_turns: int | None = None
    timeout_minutes: int | None = None
    callback_url: str = ""

    # Runtime state
    attempt: int = 0
    max_retries: int = 2
    workspace_path: str = ""
    session_id: str = ""
    claude_session_id: str = ""
    pid: int | None = None
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    pr_url: str = ""
    ci_status: str = ""
    error: str = ""
    tools_used: list[str] = field(default_factory=list)

    # Timestamps
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None

    @property
    def is_terminal(self) -> bool:
        return self.status in TERMINAL_STATES

    @property
    def elapsed_seconds(self) -> float | None:
        if self.started_at is None:
            return None
        end = self.completed_at or time.time()
        return end - self.started_at

    def transition(self, new_status: TaskStatus) -> None:
        """Transition to a new status, raising ValueError on invalid transitions."""
        valid = TRANSITIONS.get(self.status, set())
        if new_status not in valid:
            raise ValueError(
                f"Invalid transition: {self.status.value} -> {new_status.value}. "
                f"Valid: {[s.value for s in valid]}"
            )
        self.status = new_status

        if new_status == TaskStatus.RUNNING:
            self.started_at = time.time()
        elif new_status in TERMINAL_STATES:
            self.completed_at = time.time()
        elif new_status == TaskStatus.RETRY:
            self.attempt += 1

    def can_retry(self) -> bool:
        return self.attempt < self.max_retries

    def to_dict(self) -> dict:
        return {
            "task_id": self.id,
            "title": self.title,
            "status": self.status.value,
            "source": self.source,
            "external_id": self.external_id,
            "priority": self.priority,
            "depends_on": self.depends_on,
            "attempt": self.attempt,
            "repo_url": self.repo_url,
            "branch": self.branch,
            "workspace_path": self.workspace_path,
            "session_id": self.session_id,
            "claude_session_id": self.claude_session_id,
            "tokens": {"input": self.tokens_in, "output": self.tokens_out},
            "cost_usd": self.cost_usd,
            "pr_url": self.pr_url,
            "ci_status": self.ci_status,
            "tools_used": self.tools_used,
            "error": self.error,
            "elapsed_seconds": self.elapsed_seconds,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }
