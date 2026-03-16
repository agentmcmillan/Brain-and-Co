"""SQLite persistence for tasks, heartbeat runs, and context entries."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import aiosqlite

from symphony.scheduler.state_machine import Task, TaskStatus

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT,
    prompt TEXT,
    repo_url TEXT,
    branch TEXT DEFAULT 'main',
    status TEXT DEFAULT 'QUEUED',
    source TEXT DEFAULT 'manual',
    external_id TEXT DEFAULT '',
    priority INTEGER DEFAULT 1,
    depends_on TEXT DEFAULT '[]',
    allowed_tools TEXT DEFAULT '[]',
    max_turns INTEGER,
    timeout_minutes INTEGER,
    callback_url TEXT DEFAULT '',
    attempt INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 2,
    workspace_path TEXT DEFAULT '',
    session_id TEXT DEFAULT '',
    claude_session_id TEXT DEFAULT '',
    tokens_in INTEGER DEFAULT 0,
    tokens_out INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0.0,
    pr_url TEXT DEFAULT '',
    ci_status TEXT DEFAULT '',
    error TEXT DEFAULT '',
    tools_used TEXT DEFAULT '[]',
    created_at REAL,
    started_at REAL,
    completed_at REAL
);

CREATE TABLE IF NOT EXISTS heartbeat_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT REFERENCES tasks(id),
    run_number INTEGER,
    claude_session_id TEXT DEFAULT '',
    turns_used INTEGER DEFAULT 0,
    tokens_in INTEGER DEFAULT 0,
    tokens_out INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0.0,
    exit_code INTEGER,
    started_at REAL,
    ended_at REAL
);

CREATE TABLE IF NOT EXISTS context_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    repo_url TEXT,
    summary TEXT,
    created_at REAL DEFAULT (unixepoch())
);
"""


class TaskStore:
    """Async SQLite store for Symphony tasks."""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._db: aiosqlite.Connection | None = None

    async def init(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(self.db_path)
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(_SCHEMA)
        await self._db.commit()
        logger.info("TaskStore initialized at %s", self.db_path)

    async def close(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    @property
    def db(self) -> aiosqlite.Connection:
        assert self._db is not None, "TaskStore not initialized"
        return self._db

    # -- Task CRUD --

    async def save(self, task: Task) -> None:
        """Upsert a task (insert or update all fields)."""
        await self.db.execute(
            """
            INSERT INTO tasks (
                id, title, prompt, repo_url, branch, status, source, external_id,
                priority, depends_on, allowed_tools, max_turns, timeout_minutes,
                callback_url, attempt, max_retries, workspace_path, session_id,
                claude_session_id, tokens_in, tokens_out, cost_usd, pr_url,
                ci_status, error, tools_used, created_at, started_at, completed_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            ) ON CONFLICT(id) DO UPDATE SET
                title=excluded.title, prompt=excluded.prompt, repo_url=excluded.repo_url,
                branch=excluded.branch, status=excluded.status, source=excluded.source,
                external_id=excluded.external_id, priority=excluded.priority,
                depends_on=excluded.depends_on, allowed_tools=excluded.allowed_tools,
                max_turns=excluded.max_turns, timeout_minutes=excluded.timeout_minutes,
                callback_url=excluded.callback_url, attempt=excluded.attempt,
                max_retries=excluded.max_retries, workspace_path=excluded.workspace_path,
                session_id=excluded.session_id, claude_session_id=excluded.claude_session_id,
                tokens_in=excluded.tokens_in, tokens_out=excluded.tokens_out,
                cost_usd=excluded.cost_usd, pr_url=excluded.pr_url,
                ci_status=excluded.ci_status, error=excluded.error,
                tools_used=excluded.tools_used, started_at=excluded.started_at,
                completed_at=excluded.completed_at
            """,
            (
                task.id, task.title, task.prompt, task.repo_url, task.branch,
                task.status.value, task.source, task.external_id, task.priority,
                json.dumps(task.depends_on), json.dumps(task.allowed_tools),
                task.max_turns, task.timeout_minutes, task.callback_url,
                task.attempt, task.max_retries, task.workspace_path,
                task.session_id, task.claude_session_id,
                task.tokens_in, task.tokens_out, task.cost_usd,
                task.pr_url, task.ci_status, task.error,
                json.dumps(task.tools_used), task.created_at,
                task.started_at, task.completed_at,
            ),
        )
        await self.db.commit()

    async def load_active_tasks(self) -> list[Task]:
        """Load all non-terminal tasks for queue reconstruction on startup."""
        cursor = await self.db.execute(
            "SELECT * FROM tasks WHERE status NOT IN (?, ?, ?)",
            (TaskStatus.SUCCESS.value, TaskStatus.FAILURE.value, TaskStatus.CANCELLED.value),
        )
        rows = await cursor.fetchall()
        return [self._row_to_task(row) for row in rows]

    async def get(self, task_id: str) -> Task | None:
        cursor = await self.db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = await cursor.fetchone()
        return self._row_to_task(row) if row else None

    async def get_by_status(self, status: TaskStatus) -> list[Task]:
        cursor = await self.db.execute("SELECT * FROM tasks WHERE status = ?", (status.value,))
        rows = await cursor.fetchall()
        return [self._row_to_task(row) for row in rows]

    # -- Heartbeat runs --

    async def record_heartbeat(
        self,
        task_id: str,
        run_number: int,
        claude_session_id: str = "",
        turns_used: int = 0,
        tokens_in: int = 0,
        tokens_out: int = 0,
        cost_usd: float = 0.0,
        exit_code: int = 0,
        started_at: float = 0.0,
        ended_at: float = 0.0,
    ) -> None:
        await self.db.execute(
            """INSERT INTO heartbeat_runs
            (task_id, run_number, claude_session_id, turns_used, tokens_in,
             tokens_out, cost_usd, exit_code, started_at, ended_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (task_id, run_number, claude_session_id, turns_used,
             tokens_in, tokens_out, cost_usd, exit_code, started_at, ended_at),
        )
        await self.db.commit()

    async def get_heartbeat_count(self, task_id: str) -> int:
        cursor = await self.db.execute(
            "SELECT COUNT(*) FROM heartbeat_runs WHERE task_id = ?", (task_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else 0

    # -- Context entries --

    async def save_context(self, task_id: str, repo_url: str, summary: str) -> None:
        await self.db.execute(
            "INSERT INTO context_entries (task_id, repo_url, summary, created_at) VALUES (?, ?, ?, ?)",
            (task_id, repo_url, summary, time.time()),
        )
        await self.db.commit()

    async def get_context_for_repo(self, repo_url: str, limit: int = 5) -> list[dict]:
        cursor = await self.db.execute(
            "SELECT task_id, summary, created_at FROM context_entries WHERE repo_url = ? ORDER BY created_at DESC LIMIT ?",
            (repo_url, limit),
        )
        rows = await cursor.fetchall()
        return [{"task_id": row[0], "summary": row[1], "created_at": row[2]} for row in rows]

    # -- Helpers --

    @staticmethod
    def _row_to_task(row: aiosqlite.Row) -> Task:
        return Task(
            id=row["id"],
            title=row["title"] or "",
            prompt=row["prompt"] or "",
            repo_url=row["repo_url"] or "",
            branch=row["branch"] or "main",
            status=TaskStatus(row["status"]),
            source=row["source"] or "manual",
            external_id=row["external_id"] or "",
            priority=row["priority"] or 1,
            depends_on=json.loads(row["depends_on"] or "[]"),
            allowed_tools=json.loads(row["allowed_tools"] or "[]"),
            max_turns=row["max_turns"],
            timeout_minutes=row["timeout_minutes"],
            callback_url=row["callback_url"] or "",
            attempt=row["attempt"] or 0,
            max_retries=row["max_retries"] or 2,
            workspace_path=row["workspace_path"] or "",
            session_id=row["session_id"] or "",
            claude_session_id=row["claude_session_id"] or "",
            tokens_in=row["tokens_in"] or 0,
            tokens_out=row["tokens_out"] or 0,
            cost_usd=row["cost_usd"] or 0.0,
            pr_url=row["pr_url"] or "",
            ci_status=row["ci_status"] or "",
            error=row["error"] or "",
            tools_used=json.loads(row["tools_used"] or "[]"),
            created_at=row["created_at"] or 0.0,
            started_at=row["started_at"],
            completed_at=row["completed_at"],
        )
