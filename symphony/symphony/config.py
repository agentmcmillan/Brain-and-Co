"""Configuration loaded from symphony.yaml + environment variables."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class SchedulerConfig(BaseModel):
    poll_interval: int = 30
    max_concurrent_agents: int = 3
    max_retries: int = 2
    default_timeout_minutes: int = 30
    default_max_turns: int = 25


class LinearSourceConfig(BaseModel):
    enabled: bool = False
    api_key: str = ""
    team_key: str = "ENG"
    claimable_states: list[str] = Field(default_factory=lambda: ["Todo"])
    in_progress_state: str = "In Progress"
    done_state: str = "Done"
    failed_state: str = "Needs Review"
    label_filter: list[str] = Field(default_factory=lambda: ["symphony"])
    poll_interval_seconds: int = 60


class EntropySourceConfig(BaseModel):
    enabled: bool = True
    base_url: str = "http://host.docker.internal:8080"
    bearer_token: str = ""
    poll_interval_seconds: int = 30


class SourcesConfig(BaseModel):
    linear: LinearSourceConfig = Field(default_factory=LinearSourceConfig)
    entropy: EntropySourceConfig = Field(default_factory=EntropySourceConfig)


class WorkspaceConfig(BaseModel):
    base_dir: str = "/data/symphony/workspaces"
    db_path: str = "/data/symphony/symphony.db"
    cleanup_after_hours: int = 24
    default_branch: str = "main"
    inject_network_mcp: bool = True
    network_mcp_url: str = "http://host.docker.internal"
    memento_port: int = 56332
    network_tools_port: int = 8091


class AgentConfig(BaseModel):
    claude_path: str = "/usr/local/bin/claude"
    anthropic_api_key: str = ""
    default_allowed_tools: list[str] = Field(
        default_factory=lambda: ["Read", "Edit", "Write", "Bash", "Grep", "Glob", "WebFetch"]
    )
    model: str = "opus"
    github_token: str = ""
    max_heartbeats: int = 5
    turns_per_heartbeat: int = 25


class HooksConfig(BaseModel):
    auto_create_pr: bool = True
    check_ci: bool = True
    post_linear_comment: bool = True
    notify_entropy: bool = True


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 9100
    api_token: str = ""


class ReportingConfig(BaseModel):
    entropy_base_url: str = "http://host.docker.internal:8080"
    entropy_bearer_token: str = ""


class SymphonyConfig(BaseModel):
    server: ServerConfig = Field(default_factory=ServerConfig)
    scheduler: SchedulerConfig = Field(default_factory=SchedulerConfig)
    sources: SourcesConfig = Field(default_factory=SourcesConfig)
    workspace: WorkspaceConfig = Field(default_factory=WorkspaceConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    hooks: HooksConfig = Field(default_factory=HooksConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)


def _resolve_env_vars(data: Any) -> Any:
    """Recursively resolve ${ENV_VAR} references in config values."""
    if isinstance(data, str) and data.startswith("${") and data.endswith("}"):
        env_key = data[2:-1]
        return os.environ.get(env_key, "")
    if isinstance(data, dict):
        return {k: _resolve_env_vars(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_resolve_env_vars(item) for item in data]
    return data


def load_config(config_path: str | Path | None = None) -> SymphonyConfig:
    """Load configuration from YAML file with environment variable resolution."""
    if config_path is None:
        config_path = Path("symphony.yaml")
    else:
        config_path = Path(config_path)

    if config_path.exists():
        with open(config_path) as f:
            raw = yaml.safe_load(f) or {}
        resolved = _resolve_env_vars(raw)
        config = SymphonyConfig.model_validate(resolved)
    else:
        config = SymphonyConfig()

    # Override from environment variables (higher priority than YAML)
    if key := os.environ.get("ANTHROPIC_API_KEY"):
        config.agent.anthropic_api_key = key
    if key := os.environ.get("LINEAR_API_KEY"):
        config.sources.linear.api_key = key
    if key := os.environ.get("ENTROPY_BEARER_TOKEN"):
        config.sources.entropy.bearer_token = key
        config.reporting.entropy_bearer_token = key
    if key := os.environ.get("GITHUB_TOKEN"):
        config.agent.github_token = key
    if key := os.environ.get("SYMPHONY_API_TOKEN"):
        config.server.api_token = key

    return config
