"""Single-authority poll-and-dispatch loop with persistence and heartbeat execution."""

from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path

from symphony.agent.session import AgentSession
from symphony.agent.spawner import AgentSpawner
from symphony.agent.stream_parser import StreamEvent
from symphony.config import SymphonyConfig
from symphony.persistence.store import TaskStore
from symphony.context.manager import ContextManager
from symphony.reporting.entropy_client import EntropyClient
from symphony.reporting.proof import collect_proof
from symphony.scheduler.queue import TaskQueue
from symphony.scheduler.state_machine import Task, TaskStatus
from symphony.sources.base import TaskSource
from symphony.workspace.manager import WorkspaceManager

logger = logging.getLogger(__name__)


class Dispatcher:
    """Core orchestration loop: poll sources, dispatch to agents, handle results."""

    def __init__(self, config: SymphonyConfig):
        self.config = config
        self.queue = TaskQueue(max_concurrent=config.scheduler.max_concurrent_agents)
        self.workspace_mgr = WorkspaceManager(config)
        self.spawner = AgentSpawner(config)
        self.entropy = EntropyClient(config)
        self.store = TaskStore(config.workspace.db_path)
        self.context = ContextManager(config, self.store)
        self._sessions: dict[str, AgentSession] = {}
        self._sources: list[TaskSource] = []
        self._source_timers: dict[str, float] = {}
        self._running = True
        self._last_cleanup = time.time()

        self._init_sources()

    def _init_sources(self) -> None:
        """Initialize enabled task sources."""
        if self.config.sources.linear.enabled and self.config.sources.linear.api_key:
            from symphony.sources.linear import LinearSource
            source = LinearSource(self.config.sources.linear)
            self._sources.append(source)
            self._source_timers["linear"] = 0
            logger.info("Linear source enabled (team=%s)", self.config.sources.linear.team_key)

        if self.config.sources.entropy.enabled:
            from symphony.sources.entropy import EntropySource
            source = EntropySource(self.config.sources.entropy)
            self._sources.append(source)
            self._source_timers["entropy"] = 0
            logger.info("Entropy Reader source enabled")

    async def _init_store(self) -> None:
        """Initialize persistence and reload active tasks."""
        await self.store.init()
        active = await self.store.load_active_tasks()
        for task in active:
            # Reset RUNNING/PREPARING/RETRY tasks back to QUEUED (process died)
            if task.status in (TaskStatus.RUNNING, TaskStatus.PREPARING, TaskStatus.RETRY):
                task.status = TaskStatus.QUEUED
            # SUSPENDED tasks go back to QUEUED for next heartbeat
            if task.status == TaskStatus.SUSPENDED:
                task.status = TaskStatus.QUEUED
            self.queue.enqueue(task)
        if active:
            logger.info("Restored %d active tasks from database", len(active))

    async def submit_task(self, task: Task) -> bool:
        """Submit a task directly (for CLI or API usage)."""
        task.max_retries = self.config.scheduler.max_retries
        if task.timeout_minutes is None:
            task.timeout_minutes = self.config.scheduler.default_timeout_minutes
        accepted = self.queue.enqueue(task)
        if accepted:
            await self.store.save(task)
        return accepted

    async def run_forever(self) -> None:
        """Main dispatch loop."""
        await self._init_store()
        logger.info(
            "Dispatcher started (poll=%ds, max_concurrent=%d, sources=%d)",
            self.config.scheduler.poll_interval,
            self.config.scheduler.max_concurrent_agents,
            len(self._sources),
        )

        while self._running:
            try:
                await self._tick()
            except Exception:
                logger.exception("Error in dispatch tick")

            await asyncio.sleep(self.config.scheduler.poll_interval)

    async def run_single(self, task: Task) -> Task:
        """Run a single task to completion (for CLI mode)."""
        await self._init_store()
        self.queue.enqueue(task)
        task.max_retries = self.config.scheduler.max_retries
        if task.timeout_minutes is None:
            task.timeout_minutes = self.config.scheduler.default_timeout_minutes
        await self.store.save(task)

        # Dispatch immediately
        await self._dispatch_one(task)

        # Wait for completion
        session = self._sessions.get(task.id)
        if session:
            timeout = (task.timeout_minutes or 30) * 60
            try:
                await asyncio.wait_for(session.process.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning("Task %s timed out after %d minutes", task.id, task.timeout_minutes)
                await session.kill()
                task.error = f"Timeout after {task.timeout_minutes} minutes"

            await self._handle_completion(task, session)

        return task

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running or queued task."""
        task = self.queue.get_task(task_id)
        if not task:
            return False

        if task.status == TaskStatus.RUNNING:
            session = self._sessions.get(task_id)
            if session:
                await session.kill()
            task.transition(TaskStatus.CANCELLED)
            self.queue.mark_completed(task)
            self._sessions.pop(task_id, None)
        elif task.status in (TaskStatus.QUEUED, TaskStatus.SUSPENDED):
            task.status = TaskStatus.CANCELLED
            self.queue.mark_completed(task)
        else:
            return False

        await self.store.save(task)
        return True

    async def shutdown(self) -> None:
        """Graceful shutdown: kill all running agents, close sources."""
        self._running = False
        for session in self._sessions.values():
            await session.kill()
        for source in self._sources:
            if hasattr(source, "close"):
                await source.close()
        await self.entropy.close()
        await self.store.close()
        logger.info("Dispatcher shut down")

    # -- Internal --

    async def _tick(self) -> None:
        """One iteration of the dispatch loop."""
        # 1. Poll sources for new tasks
        await self._poll_sources()

        # 2. Check running agents for completion
        completed: list[str] = []
        for task_id, session in self._sessions.items():
            if not session.is_alive:
                completed.append(task_id)

        for task_id in completed:
            task = self.queue.get_task(task_id)
            session = self._sessions.pop(task_id)
            if task:
                await self._handle_completion(task, session)

        # 3. Check for timeouts
        for task_id, session in list(self._sessions.items()):
            task = self.queue.get_task(task_id)
            if task and task.timeout_minutes:
                if session.elapsed_seconds > task.timeout_minutes * 60:
                    logger.warning("Task %s timed out", task_id)
                    await session.kill()
                    # Mark as timed out without setting task.error, so heartbeat
                    # resumption is still possible in _handle_completion
                    task._timed_out = True

        # 4. Dispatch pending tasks
        while self.queue.has_pending and self.queue.slots_available > 0:
            task = self.queue.next()
            if task is None:
                break
            await self._dispatch_one(task)

        # 5. Periodic workspace cleanup
        await self._cleanup_old_workspaces()

    async def _poll_sources(self) -> None:
        """Poll all enabled task sources."""
        now = time.time()
        for i, source in enumerate(self._sources):
            source_name = type(source).__name__
            timer_key = source_name.lower()

            # Respect per-source poll intervals
            last_poll = self._source_timers.get(timer_key, 0)
            interval = self.config.scheduler.poll_interval
            if hasattr(source, "config") and hasattr(source.config, "poll_interval_seconds"):
                interval = source.config.poll_interval_seconds

            if now - last_poll < interval:
                continue

            self._source_timers[timer_key] = now

            try:
                new_tasks = await source.poll()
                for task in new_tasks:
                    task.max_retries = self.config.scheduler.max_retries
                    if task.timeout_minutes is None:
                        task.timeout_minutes = self.config.scheduler.default_timeout_minutes
                    if self.queue.enqueue(task):
                        await self.store.save(task)
                        # Notify source that we've claimed the task
                        await source.mark_claimed(task)
            except Exception:
                logger.exception("Error polling %s", source_name)

    async def _dispatch_one(self, task: Task) -> None:
        """Prepare workspace and spawn agent for a single task."""
        try:
            task.transition(TaskStatus.PREPARING)
            await self.store.save(task)

            # Fetch prior context for this repo
            prior_context = None
            if task.repo_url:
                prior_context = await self.context.get_prior_context(task.repo_url)

            workspace = await self.workspace_mgr.create(task, prior_context=prior_context)

            task.transition(TaskStatus.RUNNING)
            self.queue.mark_running(task)
            await self.store.save(task)

            async def on_event(event: StreamEvent) -> None:
                await self.entropy.report_event(task, event)

            session = await self.spawner.spawn(task, workspace, on_event)
            self._sessions[task.id] = session

            logger.info("Dispatched task %s (pid=%s)", task.id, session.pid)

        except Exception as e:
            logger.exception("Failed to dispatch task %s", task.id)
            task.error = str(e)
            if task.status != TaskStatus.FAILURE:
                try:
                    task.transition(TaskStatus.FAILURE)
                except ValueError:
                    task.status = TaskStatus.FAILURE
            self.queue.mark_completed(task)
            await self.store.save(task)

    async def _handle_completion(self, task: Task, session: AgentSession) -> None:
        """Handle a completed agent session with heartbeat logic."""
        # Transfer session stats to task
        task.tokens_in += session.tokens_in
        task.tokens_out += session.tokens_out
        task.cost_usd += session.cost_usd
        task.tools_used = sorted(set(task.tools_used) | set(session.tools_used))

        # Capture claude session ID for resumption
        if session.claude_session_id:
            task.claude_session_id = session.claude_session_id

        exit_code = session.process.returncode
        heartbeat_count = await self.store.get_heartbeat_count(task.id)
        max_heartbeats = self.config.agent.max_heartbeats

        # Record this heartbeat run
        await self.store.record_heartbeat(
            task_id=task.id,
            run_number=heartbeat_count + 1,
            claude_session_id=task.claude_session_id,
            tokens_in=session.tokens_in,
            tokens_out=session.tokens_out,
            cost_usd=session.cost_usd,
            exit_code=exit_code or 0,
            started_at=session.started_at,
            ended_at=time.time(),
        )

        if exit_code == 0:
            task.transition(TaskStatus.REVIEWING)
            await self.store.save(task)

            # Run post-completion hooks (PR creation, CI check)
            from symphony.hooks.lifecycle import run_after_completion_hooks
            await run_after_completion_hooks(task, self.config)

            proof = await collect_proof(task)
            logger.info("Task %s proof: %s", task.id, proof)
            task.transition(TaskStatus.SUCCESS)

            # Save context for future tasks (dual-write: SQLite + memento)
            if session.result_text and task.repo_url:
                await self.context.save(task, session.result_text[:2000])
        else:
            stderr = b""
            if session.process.stderr:
                try:
                    stderr = await asyncio.wait_for(session.process.stderr.read(), timeout=5)
                except asyncio.TimeoutError:
                    pass

            # Heartbeat: if agent ran out of turns but has more heartbeats, suspend
            if task.claude_session_id and heartbeat_count < max_heartbeats and not task.error:
                logger.info(
                    "Task %s suspending after heartbeat %d/%d (session=%s)",
                    task.id, heartbeat_count + 1, max_heartbeats, task.claude_session_id,
                )
                task.transition(TaskStatus.SUSPENDED)
                self.queue.mark_completed(task)
                # Re-enqueue for next heartbeat
                task.status = TaskStatus.QUEUED
                self.queue.enqueue_existing(task)
            elif task.can_retry():
                task.error = task.error or stderr.decode("utf-8", errors="replace")[:500]
                task.transition(TaskStatus.RETRY)
                self.queue.re_enqueue(task)
                logger.info("Task %s failed, retrying (attempt %d)", task.id, task.attempt)
            else:
                task.error = task.error or stderr.decode("utf-8", errors="replace")[:500]
                try:
                    task.transition(TaskStatus.FAILURE)
                except ValueError:
                    task.status = TaskStatus.FAILURE

        # Only mark completed if the task was not re-enqueued (e.g. SUSPENDED -> QUEUED)
        if task.status != TaskStatus.QUEUED:
            self.queue.mark_completed(task)
        await self.store.save(task)

        # Report to Entropy Reader
        await self.entropy.report_completion(task)

        # Notify source
        for source in self._sources:
            if task.source == "linear" and type(source).__name__ == "LinearSource":
                if task.status == TaskStatus.SUCCESS:
                    await source.mark_completed(task)
                elif task.status == TaskStatus.FAILURE:
                    await source.mark_failed(task)

        # Cleanup failed workspaces immediately; keep successful ones for review
        if task.is_terminal and task.status == TaskStatus.FAILURE:
            await self.workspace_mgr.cleanup(task)

        logger.info(
            "Task %s -> %s (tokens=%d+%d, cost=$%.4f, elapsed=%ss, pr=%s, heartbeats=%d)",
            task.id,
            task.status.value,
            task.tokens_in,
            task.tokens_out,
            task.cost_usd,
            f"{task.elapsed_seconds:.0f}" if task.elapsed_seconds else "?",
            task.pr_url or "none",
            heartbeat_count + 1,
        )

    async def _cleanup_old_workspaces(self) -> None:
        """Delete workspaces older than configured retention period."""
        now = time.time()
        # Run cleanup every hour
        if now - self._last_cleanup < 3600:
            return
        self._last_cleanup = now

        max_age = self.config.workspace.cleanup_after_hours * 3600
        base = Path(self.config.workspace.base_dir)
        if not base.exists():
            return

        cleaned = 0
        for workspace in base.iterdir():
            if not workspace.is_dir():
                continue
            age = now - workspace.stat().st_mtime
            if age > max_age:
                import shutil
                shutil.rmtree(workspace)
                cleaned += 1

        if cleaned:
            logger.info("Cleaned up %d old workspaces", cleaned)
