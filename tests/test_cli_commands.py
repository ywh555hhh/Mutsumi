"""Tests for CLI CRUD commands (add, list, done, rm, edit)."""

from __future__ import annotations

import json

from click.testing import CliRunner

from mutsumi.cli import main


def _write_tasks(tasks: list[dict[str, str | list[str]]]) -> None:
    """Write a mutsumi.json with given tasks."""
    data = {"version": 1, "tasks": tasks}
    with open("mutsumi.json", "w") as f:
        json.dump(data, f)


def _read_tasks() -> list[dict[str, str | list[str]]]:
    with open("mutsumi.json") as f:
        return json.load(f)["tasks"]  # type: ignore[no-any-return]


class TestCliAdd:
    def test_add_basic(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["add", "New Task"])
            assert result.exit_code == 0
            assert "Added" in result.output
            tasks = _read_tasks()
            assert len(tasks) == 2  # template + new

    def test_add_with_options(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, [
                "add", "Priority Task",
                "--priority", "high",
                "--scope", "day",
                "--tags", "urgent,bug",
            ])
            assert result.exit_code == 0
            tasks = _read_tasks()
            new_task = tasks[-1]
            assert new_task["priority"] == "high"
            assert new_task["scope"] == "day"
            assert "urgent" in new_task["tags"]

    def test_add_creates_file(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["add", "First Task"])
            assert result.exit_code == 0
            tasks = _read_tasks()
            assert len(tasks) == 1


class TestCliList:
    def test_list_all(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _write_tasks([
                {"id": "t1", "title": "Task A", "status": "pending"},
                {"id": "t2", "title": "Task B", "status": "done"},
            ])
            result = runner.invoke(main, ["list"])
            assert result.exit_code == 0
            assert "Task A" in result.output
            assert "Task B" in result.output

    def test_list_done_only(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _write_tasks([
                {"id": "t1", "title": "Task A", "status": "pending"},
                {"id": "t2", "title": "Task B", "status": "done"},
            ])
            result = runner.invoke(main, ["list", "--done"])
            assert result.exit_code == 0
            assert "Task B" in result.output
            assert "Task A" not in result.output

    def test_list_empty(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _write_tasks([])
            result = runner.invoke(main, ["list"])
            assert "No tasks found" in result.output


class TestCliDone:
    def test_done_by_id(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            task_id = "ABCD1234EFGH5678JKLM0000NP"
            _write_tasks([{"id": task_id, "title": "My Task", "status": "pending"}])
            result = runner.invoke(main, ["done", task_id])
            assert result.exit_code == 0
            assert "Done" in result.output
            tasks = _read_tasks()
            assert tasks[0]["status"] == "done"

    def test_done_prefix(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            task_id = "ABCD1234EFGH5678JKLM0000NP"
            _write_tasks([{"id": task_id, "title": "My Task", "status": "pending"}])
            result = runner.invoke(main, ["done", "ABCD1234"])
            assert result.exit_code == 0

    def test_done_not_found(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _write_tasks([{"id": "ABCD1234", "title": "My Task", "status": "pending"}])
            result = runner.invoke(main, ["done", "ZZZZ"])
            assert result.exit_code != 0


class TestCliRm:
    def test_rm_by_id(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _write_tasks([{"id": "RMTEST00", "title": "Delete Me", "status": "pending"}])
            result = runner.invoke(main, ["rm", "RMTEST00"])
            assert result.exit_code == 0
            assert "Removed" in result.output
            tasks = _read_tasks()
            assert len(tasks) == 0

    def test_rm_not_found(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _write_tasks([])
            result = runner.invoke(main, ["rm", "ZZZZ"])
            assert result.exit_code != 0


class TestCliEdit:
    def test_edit_title(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _write_tasks([{"id": "EDIT0001", "title": "Old Title", "status": "pending"}])
            result = runner.invoke(main, ["edit", "EDIT0001", "--title", "New Title"])
            assert result.exit_code == 0
            assert "Updated" in result.output
            tasks = _read_tasks()
            assert tasks[0]["title"] == "New Title"

    def test_edit_priority(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _write_tasks([{
                "id": "EDIT0002", "title": "Task",
                "status": "pending", "priority": "normal",
            }])
            result = runner.invoke(main, ["edit", "EDIT0002", "--priority", "high"])
            assert result.exit_code == 0
            tasks = _read_tasks()
            assert tasks[0]["priority"] == "high"

    def test_edit_no_fields(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _write_tasks([{"id": "EDIT0003", "title": "Task", "status": "pending"}])
            result = runner.invoke(main, ["edit", "EDIT0003"])
            assert "No fields to update" in result.output
