"""Tests for the task queue."""

from symphony.scheduler.queue import TaskQueue
from symphony.scheduler.state_machine import Task, TaskStatus


def test_enqueue_and_dequeue():
    q = TaskQueue(max_concurrent=2)
    t1 = Task(title="task 1", priority=1)
    t2 = Task(title="task 2", priority=0)  # Higher priority

    q.enqueue(t1)
    q.enqueue(t2)

    assert q.pending_count == 2
    assert q.slots_available == 2

    # Should get t2 first (priority 0 < 1)
    next_task = q.next()
    assert next_task is not None
    assert next_task.title == "task 2"


def test_concurrency_slots():
    q = TaskQueue(max_concurrent=1)
    t1 = Task(title="task 1")
    t2 = Task(title="task 2")

    q.enqueue(t1)
    q.enqueue(t2)

    popped = q.next()
    assert popped is not None
    popped.transition(TaskStatus.PREPARING)
    popped.transition(TaskStatus.RUNNING)
    q.mark_running(popped)

    assert q.slots_available == 0
    assert q.running_count == 1


def test_no_duplicate_enqueue():
    q = TaskQueue()
    t = Task(title="test")
    assert q.enqueue(t) is True
    assert q.enqueue(t) is False


def test_mark_completed():
    q = TaskQueue()
    t = Task(title="test")
    q.enqueue(t)
    t.transition(TaskStatus.PREPARING)
    t.transition(TaskStatus.RUNNING)
    q.mark_running(t)
    assert q.running_count == 1

    t.transition(TaskStatus.REVIEWING)
    t.transition(TaskStatus.SUCCESS)
    q.mark_completed(t)
    assert q.running_count == 0
