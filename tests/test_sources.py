"""Tests for SourceRegistry multi-source data layer (Phase 5b)."""

from __future__ import annotations

import json
from pathlib import Path

from mutsumi.core.sources import Source, SourceRegistry


def _make_tasks_file(path: Path, tasks: list[dict[str, str]]) -> None:
    """Write a valid task file."""
    data = {"version": 1, "tasks": tasks}
    path.write_text(json.dumps(data), encoding="utf-8")


class TestSource:
    def test_source_defaults(self) -> None:
        s = Source(name="test", path=Path("/tmp/test.json"))
        assert s.task_file is None
        assert s.error is None
        assert s.is_personal is False

    def test_source_personal(self) -> None:
        s = Source(name="personal", path=Path("/tmp/p.json"), is_personal=True)
        assert s.is_personal is True


class TestSourceRegistry:
    def test_add_source(self) -> None:
        reg = SourceRegistry()
        src = reg.add_source("proj-a", Path("/tmp/a.json"))
        assert "proj-a" in reg
        assert len(reg) == 1
        assert src.name == "proj-a"

    def test_remove_source(self) -> None:
        reg = SourceRegistry()
        reg.add_source("proj-a", Path("/tmp/a.json"))
        reg.remove_source("proj-a")
        assert "proj-a" not in reg
        assert len(reg) == 0

    def test_remove_nonexistent(self) -> None:
        reg = SourceRegistry()
        reg.remove_source("nope")  # should not raise

    def test_get_source(self) -> None:
        reg = SourceRegistry()
        reg.add_source("x", Path("/tmp/x.json"))
        assert reg.get_source("x") is not None
        assert reg.get_source("y") is None

    def test_source_names(self) -> None:
        reg = SourceRegistry()
        reg.add_source("a", Path("/a"))
        reg.add_source("b", Path("/b"))
        assert reg.source_names == ["a", "b"]

    def test_load_source(self, tmp_path: Path) -> None:
        f = tmp_path / "mutsumi.json"
        _make_tasks_file(f, [{"id": "t1", "title": "Task 1", "status": "pending"}])

        reg = SourceRegistry()
        reg.add_source("proj", f)
        src = reg.load_source("proj")
        assert src is not None
        assert src.task_file is not None
        assert len(src.task_file.tasks) == 1
        assert src.error is None

    def test_load_source_missing_file(self, tmp_path: Path) -> None:
        reg = SourceRegistry()
        reg.add_source("ghost", tmp_path / "nonexistent.json")
        src = reg.load_source("ghost")
        assert src is not None
        assert src.task_file is None
        assert src.error is None  # not an error, just doesn't exist

    def test_load_source_invalid_json(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.json"
        f.write_text("not json {{{", encoding="utf-8")

        reg = SourceRegistry()
        reg.add_source("bad", f)
        src = reg.load_source("bad")
        assert src is not None
        assert src.task_file is None
        assert src.error is not None

    def test_load_nonexistent_source(self) -> None:
        reg = SourceRegistry()
        assert reg.load_source("nope") is None

    def test_load_all(self, tmp_path: Path) -> None:
        fa = tmp_path / "a.json"
        fb = tmp_path / "b.json"
        _make_tasks_file(fa, [{"id": "a1", "title": "A Task", "status": "pending"}])
        _make_tasks_file(fb, [{"id": "b1", "title": "B Task", "status": "done"}])

        reg = SourceRegistry()
        reg.add_source("a", fa)
        reg.add_source("b", fb)
        reg.load_all()

        src_a = reg.get_source("a")
        src_b = reg.get_source("b")
        assert src_a is not None and src_a.task_file is not None
        assert src_b is not None and src_b.task_file is not None

    def test_all_tasks_aggregation(self, tmp_path: Path) -> None:
        fa = tmp_path / "a.json"
        fb = tmp_path / "b.json"
        _make_tasks_file(fa, [
            {"id": "a1", "title": "A1", "status": "pending"},
            {"id": "a2", "title": "A2", "status": "done"},
        ])
        _make_tasks_file(fb, [
            {"id": "b1", "title": "B1", "status": "pending"},
        ])

        reg = SourceRegistry()
        reg.add_source("a", fa)
        reg.add_source("b", fb)
        reg.load_all()

        all_tasks = reg.all_tasks()
        assert len(all_tasks) == 3
        sources = [name for name, _ in all_tasks]
        assert sources.count("a") == 2
        assert sources.count("b") == 1

    def test_all_tasks_empty_source(self, tmp_path: Path) -> None:
        reg = SourceRegistry()
        reg.add_source("empty", tmp_path / "nope.json")
        reg.load_all()
        assert reg.all_tasks() == []

    def test_watcher_lifecycle(self, tmp_path: Path) -> None:
        f = tmp_path / "watch.json"
        _make_tasks_file(f, [])

        changed: list[str] = []

        reg = SourceRegistry()
        reg.add_source("w", f)
        reg.start_watching("w", lambda name: changed.append(name))

        # Verify watcher is running
        assert "w" in reg._watchers
        assert reg._watchers["w"].is_running

        reg.stop_watching("w")
        assert "w" not in reg._watchers

    def test_stop_all_watchers(self, tmp_path: Path) -> None:
        f1 = tmp_path / "f1.json"
        f2 = tmp_path / "f2.json"
        _make_tasks_file(f1, [])
        _make_tasks_file(f2, [])

        reg = SourceRegistry()
        reg.add_source("s1", f1)
        reg.add_source("s2", f2)
        reg.start_watching("s1", lambda n: None)
        reg.start_watching("s2", lambda n: None)

        assert len(reg._watchers) == 2
        reg.stop_all_watchers()
        assert len(reg._watchers) == 0

    def test_watcher_not_started_for_missing_file(self, tmp_path: Path) -> None:
        reg = SourceRegistry()
        reg.add_source("ghost", tmp_path / "nope.json")
        reg.start_watching("ghost", lambda n: None)
        assert "ghost" not in reg._watchers

    def test_watcher_not_started_for_nonexistent_source(self) -> None:
        reg = SourceRegistry()
        reg.start_watching("nope", lambda n: None)
        assert len(reg._watchers) == 0

    def test_ordered_sources(self) -> None:
        reg = SourceRegistry()
        reg.add_source("z", Path("/z"))
        reg.add_source("a", Path("/a"))
        reg.add_source("m", Path("/m"))
        assert reg.source_names == ["z", "a", "m"]

    def test_personal_source_flag(self, tmp_path: Path) -> None:
        reg = SourceRegistry()
        reg.add_source("personal", tmp_path / "p.json", is_personal=True)
        src = reg.get_source("personal")
        assert src is not None
        assert src.is_personal is True
