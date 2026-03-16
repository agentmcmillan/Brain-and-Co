"""Tests for the task state machine."""

import pytest
from symphony.scheduler.state_machine import Task, TaskStatus


def test_initial_state():
    task = Task(title="test")
    assert task.status == TaskStatus.QUEUED


def test_valid_transitions():
    task = Task(title="test")
    task.transition(TaskStatus.PREPARING)
    assert task.status == TaskStatus.PREPARING
    task.transition(TaskStatus.RUNNING)
    assert task.status == TaskStatus.RUNNING
    assert task.started_at is not None
    task.transition(TaskStatus.REVIEWING)
    assert task.status == TaskStatus.REVIEWING
    task.transition(TaskStatus.SUCCESS)
    assert task.status == TaskStatus.SUCCESS
    assert task.completed_at is not None


def test_invalid_transition():
    task = Task(title="test")
    with pytest.raises(ValueError):
        task.transition(TaskStatus.SUCCESS)  # Can't go QUEUED -> SUCCESS


def test_retry_increments_attempt():
    task = Task(title="test", max_retries=2)
    task.transition(TaskStatus.PREPARING)
    task.transition(TaskStatus.RUNNING)
    task.transition(TaskStatus.RETRY)
    assert task.attempt == 1
    assert task.can_retry()


def test_max_retries():
    task = Task(title="test", max_retries=1)
    task.transition(TaskStatus.PREPARING)
    task.transition(TaskStatus.RUNNING)
    task.transition(TaskStatus.RETRY)
    assert task.attempt == 1
    assert not task.can_retry()


def test_cancel_from_queued():
    task = Task(title="test")
    task.transition(TaskStatus.CANCELLED)
    assert task.is_terminal


def test_cancel_from_running():
    task = Task(title="test")
    task.transition(TaskStatus.PREPARING)
    task.transition(TaskStatus.RUNNING)
    task.transition(TaskStatus.CANCELLED)
    assert task.is_terminal


def test_to_dict():
    task = Task(title="test", prompt="do something", repo_url="https://example.com")
    d = task.to_dict()
    assert d["title"] == "test"
    assert d["status"] == "QUEUED"
    assert d["tokens"]["input"] == 0
