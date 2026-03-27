"""Tests for task form source selection behaviour."""

from __future__ import annotations

from contextlib import asynccontextmanager

import pytest
from textual.app import App
from textual.widgets import Select

pytest.importorskip("textual")

from mutsumi.core.models import Task
from mutsumi.tui.task_form import TaskForm


class _TaskFormHarnessApp(App[None]):
    def __init__(self, form: TaskForm) -> None:
        super().__init__()
        self._form = form
        self.captured: list[TaskForm.TaskSubmitted] = []

    def on_mount(self) -> None:
        self.push_screen(self._form)

    def get_css_variables(self) -> dict[str, str]:
        return {
            **super().get_css_variables(),
            "theme-bg": "#000000",
            "theme-surface": "#111111",
            "theme-border": "#222222",
            "theme-text": "#ffffff",
            "theme-text-muted": "#888888",
            "theme-accent": "#00aaff",
        }

    def on_task_form_task_submitted(self, message: TaskForm.TaskSubmitted) -> None:
        self.captured.append(message)


@asynccontextmanager
async def _task_form_test_context(form: TaskForm):
    app = _TaskFormHarnessApp(form)
    async with app.run_test():
        yield app


@pytest.mark.asyncio
async def test_task_form_shows_source_selector_when_requested() -> None:
    form = TaskForm(
        default_scope="week",
        source_options=[("personal", "personal"), ("repo", "repo")],
        default_source="repo",
        show_source_selector=True,
    )

    async with _task_form_test_context(form):
        source_select = form.query_one("#form-source", Select)
        assert source_select.value == "repo"


@pytest.mark.asyncio
async def test_task_form_hides_source_selector_for_edit_flow() -> None:
    form = TaskForm(
        task=Task(id="T1", title="Edit me"),
        source_options=[("personal", "personal"), ("repo", "repo")],
        default_source="repo",
        show_source_selector=True,
    )

    async with _task_form_test_context(form):
        assert len(form.query("#form-source")) == 0


@pytest.mark.asyncio
async def test_task_form_hides_source_selector_for_subtask_flow() -> None:
    form = TaskForm(
        parent_id="P1",
        source_options=[("personal", "personal"), ("repo", "repo")],
        default_source="repo",
        show_source_selector=True,
    )

    async with _task_form_test_context(form):
        assert len(form.query("#form-source")) == 0


@pytest.mark.asyncio
async def test_task_form_submission_includes_selected_source() -> None:
    form = TaskForm(
        source_options=[("personal", "personal"), ("repo", "repo")],
        default_source="personal",
        show_source_selector=True,
    )

    async with _task_form_test_context(form) as app:
        form.query_one("#form-title").value = "New task"
        form.query_one("#form-source", Select).value = "repo"
        form._submit()

    assert len(app.captured) == 1
    assert app.captured[0].source_name == "repo"
    assert app.captured[0].title == "New task"
