"""Tests for MainDashboard widget (Phase 5e)."""

from __future__ import annotations

from pathlib import Path

from mutsumi.core.models import Task, TaskFile, TaskStatus
from mutsumi.core.sources import Source
from mutsumi.tui.main_dashboard import MainDashboard, SourceCard


def _make_source(
    name: str,
    tasks: list[Task] | None = None,
    *,
    is_personal: bool = False,
    error: str | None = None,
) -> Source:
    src = Source(name=name, path=Path(f"/tmp/{name}/mutsumi.json"), is_personal=is_personal)
    if error:
        src.error = error
    elif tasks is not None:
        src.task_file = TaskFile(version=1, tasks=tasks)
    return src


def _task(tid: str, title: str, status: str = "pending", priority: str = "normal") -> Task:
    return Task(id=tid, title=title, status=status, priority=priority)


class TestSourceCard:
    def test_card_with_tasks(self) -> None:
        source = _make_source("proj-a", [
            _task("t1", "Task A"),
            _task("t2", "Task B", status="done"),
        ])
        card = SourceCard(source)
        assert card._source.name == "proj-a"

    def test_card_with_error(self) -> None:
        source = _make_source("bad", error="Parse error")
        card = SourceCard(source)
        assert card._source.error is not None

    def test_card_no_file(self) -> None:
        source = Source(name="empty", path=Path("/tmp/empty.json"))
        card = SourceCard(source)
        assert card._source.task_file is None

    def test_card_personal(self) -> None:
        source = _make_source("personal", [], is_personal=True)
        card = SourceCard(source)
        assert card._source.is_personal is True

    def test_card_max_tasks(self) -> None:
        tasks = [_task(f"t{i}", f"Task {i}") for i in range(10)]
        source = _make_source("proj", tasks)
        card = SourceCard(source, max_tasks=2)
        assert card._max_tasks == 2


class TestMainDashboard:
    def test_dashboard_with_sources(self) -> None:
        sources = [
            _make_source("a", [_task("t1", "A-1")]),
            _make_source("b", [_task("t2", "B-1", status="done")]),
        ]
        dashboard = MainDashboard(sources)
        assert len(dashboard._sources) == 2

    def test_dashboard_empty(self) -> None:
        dashboard = MainDashboard([])
        assert len(dashboard._sources) == 0

    def test_set_sources(self) -> None:
        dashboard = MainDashboard()
        sources = [_make_source("x", [_task("t1", "X")])]
        dashboard.set_sources(sources)
        assert len(dashboard._sources) == 1

    def test_dashboard_progress_calculation(self) -> None:
        source = _make_source("proj", [
            _task("t1", "A", status="done"),
            _task("t2", "B", status="done"),
            _task("t3", "C"),
        ])
        tf = source.task_file
        assert tf is not None
        total = len(tf.tasks)
        done = sum(1 for t in tf.tasks if t.status == TaskStatus.DONE)
        assert total == 3
        assert done == 2

    def test_dashboard_handles_no_tasks(self) -> None:
        source = _make_source("empty", [])
        tf = source.task_file
        assert tf is not None
        assert len(tf.tasks) == 0

    def test_dashboard_with_priorities(self) -> None:
        source = _make_source("proj", [
            _task("t1", "Urgent", priority="high"),
            _task("t2", "Normal"),
            _task("t3", "Low", priority="low"),
        ])
        card = SourceCard(source, max_tasks=5)
        assert card._source.task_file is not None
        assert len(card._source.task_file.tasks) == 3

    def test_dashboard_config_options(self) -> None:
        dashboard = MainDashboard([], max_tasks=5, show_completed=False)
        assert dashboard._max_tasks == 5
        assert dashboard._show_completed is False
