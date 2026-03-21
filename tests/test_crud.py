"""Tests for CRUD operations and ID generation."""

from __future__ import annotations

from mutsumi.core.id import generate_task_id
from mutsumi.core.models import Task, TaskFile, TaskPriority, TaskScope, TaskStatus
from mutsumi.core.writer import (
    add_task,
    create_task_from_args,
    find_task,
    remove_task,
    resolve_partial_id,
    update_task,
)


def _make_task_file() -> TaskFile:
    return TaskFile(
        version=1,
        tasks=[
            Task(id="01ABC00000DEFGH000000JKLM0", title="Task A", status="pending"),
            Task(
                id="01ABC00000DEFGH000000JKLM1",
                title="Task B",
                status="done",
                children=[
                    Task(id="01ABC00000DEFGH000000CHILD", title="Child", status="pending"),
                ],
            ),
        ],
    )


class TestGenerateTaskId:
    def test_length_is_26(self) -> None:
        task_id = generate_task_id()
        assert len(task_id) == 26

    def test_unique(self) -> None:
        ids = {generate_task_id() for _ in range(100)}
        assert len(ids) == 100

    def test_crockford_charset(self) -> None:
        valid = set("0123456789ABCDEFGHJKMNPQRSTVWXYZ")
        task_id = generate_task_id()
        assert all(c in valid for c in task_id)


class TestFindTask:
    def test_find_top_level(self) -> None:
        tf = _make_task_file()
        task = find_task(tf, "01ABC00000DEFGH000000JKLM0")
        assert task is not None
        assert task.title == "Task A"

    def test_find_child(self) -> None:
        tf = _make_task_file()
        task = find_task(tf, "01ABC00000DEFGH000000CHILD")
        assert task is not None
        assert task.title == "Child"

    def test_not_found(self) -> None:
        tf = _make_task_file()
        assert find_task(tf, "NONEXISTENT") is None


class TestAddTask:
    def test_add(self) -> None:
        tf = _make_task_file()
        original_count = len(tf.tasks)
        new_task = Task(id="NEWTASK", title="New", status="pending")
        add_task(tf, new_task)
        assert len(tf.tasks) == original_count + 1
        assert tf.tasks[-1].title == "New"


class TestRemoveTask:
    def test_remove_top_level(self) -> None:
        tf = _make_task_file()
        assert remove_task(tf, "01ABC00000DEFGH000000JKLM0")
        assert len(tf.tasks) == 1

    def test_remove_child(self) -> None:
        tf = _make_task_file()
        assert remove_task(tf, "01ABC00000DEFGH000000CHILD")
        assert len(tf.tasks[1].children) == 0

    def test_remove_nonexistent(self) -> None:
        tf = _make_task_file()
        assert not remove_task(tf, "NONEXISTENT")


class TestUpdateTask:
    def test_update_title(self) -> None:
        tf = _make_task_file()
        assert update_task(tf, "01ABC00000DEFGH000000JKLM0", title="Updated")
        task = find_task(tf, "01ABC00000DEFGH000000JKLM0")
        assert task is not None
        assert task.title == "Updated"

    def test_update_nonexistent(self) -> None:
        tf = _make_task_file()
        assert not update_task(tf, "NONEXISTENT", title="Nope")


class TestResolvePartialId:
    def test_unique_prefix(self) -> None:
        tf = _make_task_file()
        # "01ABC00000DEFGH000000CHILD" is the only one starting with "01ABC00000DEFGH000000C"
        result = resolve_partial_id(tf, "01ABC00000DEFGH000000C")
        assert result == "01ABC00000DEFGH000000CHILD"

    def test_ambiguous_prefix(self) -> None:
        tf = _make_task_file()
        # "01ABC" matches all three tasks
        result = resolve_partial_id(tf, "01ABC")
        assert result is None

    def test_no_match(self) -> None:
        tf = _make_task_file()
        result = resolve_partial_id(tf, "ZZZZZ")
        assert result is None


class TestCreateTaskFromArgs:
    def test_defaults(self) -> None:
        task = create_task_from_args("My Task")
        assert task.title == "My Task"
        assert task.status == TaskStatus.PENDING
        assert task.scope == TaskScope.INBOX
        assert task.priority == TaskPriority.NORMAL
        assert task.tags == []
        assert task.created_at is not None
        assert len(task.id) == 26

    def test_custom_fields(self) -> None:
        task = create_task_from_args(
            "Important",
            priority="high",
            scope="day",
            tags=["urgent", "bug"],
        )
        assert task.priority == TaskPriority.HIGH
        assert task.scope == TaskScope.DAY
        assert task.tags == ["urgent", "bug"]
