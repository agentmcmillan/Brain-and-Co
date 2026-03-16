"""Workspace isolation: git clone per task with CLAUDE.md injection."""

from __future__ import annotations

import asyncio
import json
import logging
import shutil
from pathlib import Path

from symphony.config import SymphonyConfig
from symphony.scheduler.state_machine import Task
from symphony.workspace.templates import render_claude_md

logger = logging.getLogger(__name__)


class WorkspaceManager:
    def __init__(self, config: SymphonyConfig):
        self.config = config
        self.base_dir = Path(config.workspace.base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def create(self, task: Task, prior_context: list[dict] | None = None) -> Path:
        """Create an isolated workspace for a task via git clone."""
        workspace = self.base_dir / f"task-{task.id}"
        if workspace.exists():
            shutil.rmtree(workspace)

        if task.repo_url:
            branch = task.branch or self.config.workspace.default_branch
            cmd = [
                "git", "clone",
                "--depth=1",
                "--branch", branch,
                task.repo_url,
                str(workspace),
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                raise RuntimeError(f"git clone failed: {stderr.decode().strip()}")
            logger.info("Cloned %s (branch=%s) to %s", task.repo_url, branch, workspace)
        else:
            # No repo — create empty workspace
            workspace.mkdir(parents=True, exist_ok=True)
            proc = await asyncio.create_subprocess_exec(
                "git", "init", str(workspace),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.wait()

        self._inject_claude_md(workspace, task, prior_context)
        self._inject_claude_json(workspace)
        self._inject_settings(workspace, task)

        task.workspace_path = str(workspace)
        return workspace

    async def cleanup(self, task: Task) -> None:
        """Remove a task's workspace."""
        if task.workspace_path:
            workspace = Path(task.workspace_path)
            if workspace.exists():
                shutil.rmtree(workspace)
                logger.info("Cleaned up workspace for task %s", task.id)

    def _inject_claude_md(self, workspace: Path, task: Task, prior_context: list[dict] | None = None) -> None:
        """Write a task-specific CLAUDE.md into the workspace."""
        content = render_claude_md(task, prior_context=prior_context)
        claude_md = workspace / "CLAUDE.md"

        # Append to existing CLAUDE.md if present
        if claude_md.exists():
            existing = claude_md.read_text()
            content = existing + "\n\n" + content
        claude_md.write_text(content)

    def _inject_claude_json(self, workspace: Path) -> None:
        """Inject .claude.json with Network MCP access."""
        if not self.config.workspace.inject_network_mcp:
            return

        claude_json = workspace / ".claude.json"
        config_data: dict = {}
        if claude_json.exists():
            try:
                config_data = json.loads(claude_json.read_text())
            except json.JSONDecodeError:
                pass

        mcp_servers = config_data.get("mcpServers", {})
        base = self.config.workspace.network_mcp_url
        mcp_servers["memento"] = {
            "type": "sse",
            "url": f"{base}:{self.config.workspace.memento_port}/sse?accessKey=YOUR_MEMENTO_ACCESS_KEY",
        }
        mcp_servers["network-tools"] = {
            "type": "sse",
            "url": f"{base}:{self.config.workspace.network_tools_port}/mcp",
        }
        config_data["mcpServers"] = mcp_servers
        claude_json.write_text(json.dumps(config_data, indent=2))

    def _inject_settings(self, workspace: Path, task: Task) -> None:
        """Create .claude/settings.json with allowed tools."""
        claude_dir = workspace / ".claude"
        claude_dir.mkdir(exist_ok=True)

        allowed = task.allowed_tools or self.config.agent.default_allowed_tools
        settings = {
            "permissions": {
                "allow": allowed,
                "deny": [],
            }
        }
        (claude_dir / "settings.json").write_text(json.dumps(settings, indent=2))
