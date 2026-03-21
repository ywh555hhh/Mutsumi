"""Tests for the file watcher with debounce."""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

import pytest

from mutsumi.core.watcher import TaskFileWatcher

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def tasks_file(tmp_path: Path) -> Path:
    p = tmp_path / "tasks.json"
    p.write_text(json.dumps({"version": 1, "tasks": []}))
    return p


def test_watcher_detects_change(tasks_file: Path) -> None:
    """Watcher should fire callback when file changes."""
    fired: list[bool] = []

    def on_change() -> None:
        fired.append(True)

    watcher = TaskFileWatcher(tasks_file, on_change)
    watcher.start()
    assert watcher.is_running

    try:
        # Modify the file
        time.sleep(0.2)
        tasks_file.write_text(json.dumps({"version": 1, "tasks": [{"id": "t1", "title": "New"}]}))
        # Wait for debounce + processing
        time.sleep(0.5)
        assert len(fired) >= 1
    finally:
        watcher.stop()
        assert not watcher.is_running


def test_watcher_debounce(tasks_file: Path) -> None:
    """Multiple rapid writes should be debounced into fewer callbacks."""
    fire_count: list[int] = [0]

    def on_change() -> None:
        fire_count[0] += 1

    watcher = TaskFileWatcher(tasks_file, on_change)
    watcher.start()

    try:
        time.sleep(0.2)
        # Rapid writes
        for i in range(5):
            tasks_file.write_text(json.dumps({"version": 1, "tasks": [], "n": i}))
            time.sleep(0.02)
        # Wait for debounce to settle
        time.sleep(0.5)
        # Should have fired fewer times than 5
        assert fire_count[0] < 5
    finally:
        watcher.stop()


def test_watcher_stop_is_idempotent(tasks_file: Path) -> None:
    watcher = TaskFileWatcher(tasks_file, lambda: None)
    watcher.start()
    watcher.stop()
    watcher.stop()  # Should not raise
