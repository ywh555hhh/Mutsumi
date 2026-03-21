"""Tests for Mutsumi data models."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from mutsumi.core.models import Task, TaskFile, TaskPriority, TaskScope, TaskStatus

FIXTURE = Path(__file__).parent / "fixtures" / "tasks.json"


def test_parse_fixture() -> None:
    raw = FIXTURE.read_text()
    tf = TaskFile.model_validate_json(raw)
    assert tf.version == 1
    assert len(tf.tasks) == 7


def test_nested_children() -> None:
    raw = FIXTURE.read_text()
    tf = TaskFile.model_validate_json(raw)
    task3 = tf.tasks[2]
    assert task3.title == "Refactor Auth module"
    assert len(task3.children) == 2
    assert task3.children[0].status == TaskStatus.DONE
    assert task3.children[1].status == TaskStatus.DONE


def test_default_values() -> None:
    t = Task(id="test-1", title="Test task")
    assert t.status == TaskStatus.PENDING
    assert t.scope == TaskScope.INBOX
    assert t.priority == TaskPriority.NORMAL
    assert t.tags == []
    assert t.children == []


def test_custom_fields_preserved() -> None:
    data = {
        "id": "test-1",
        "title": "Test",
        "status": "pending",
        "custom_field": "custom_value",
        "energy_level": "high",
    }
    t = Task.model_validate(data)
    dumped = t.model_dump()
    assert dumped["custom_field"] == "custom_value"
    assert dumped["energy_level"] == "high"


def test_is_done_property() -> None:
    t = Task(id="1", title="Done task", status=TaskStatus.DONE)
    assert t.is_done is True
    t2 = Task(id="2", title="Pending task")
    assert t2.is_done is False


def test_children_progress() -> None:
    t = Task(
        id="parent",
        title="Parent",
        children=[
            Task(id="c1", title="Child 1", status=TaskStatus.DONE),
            Task(id="c2", title="Child 2", status=TaskStatus.PENDING),
            Task(id="c3", title="Child 3", status=TaskStatus.DONE),
        ],
    )
    done, total = t.children_progress()
    assert done == 2
    assert total == 3


def test_invalid_status_raises() -> None:
    with pytest.raises(ValidationError):
        Task(id="1", title="Bad", status="wip")  # type: ignore[arg-type]


def test_missing_required_field_raises() -> None:
    with pytest.raises(ValidationError):
        Task.model_validate({"id": "1"})  # missing title
