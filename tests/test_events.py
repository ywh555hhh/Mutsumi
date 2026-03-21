"""Tests for the event logger."""

from __future__ import annotations

import json
import threading
from typing import TYPE_CHECKING

from mutsumi.events import EventLogger

if TYPE_CHECKING:
    from pathlib import Path


class TestEventLogger:
    def test_log_creates_file(self, tmp_path: Path) -> None:
        log_path = tmp_path / "events.jsonl"
        logger = EventLogger(log_path)
        logger.log("task_added", title="Test Task")
        assert log_path.exists()

    def test_log_jsonl_format(self, tmp_path: Path) -> None:
        log_path = tmp_path / "events.jsonl"
        logger = EventLogger(log_path)
        logger.log("task_added", title="Test")
        logger.log("task_done", task_id="abc123")

        lines = log_path.read_text().strip().split("\n")
        assert len(lines) == 2

        event1 = json.loads(lines[0])
        assert event1["type"] == "task_added"
        assert event1["title"] == "Test"
        assert "timestamp" in event1

        event2 = json.loads(lines[1])
        assert event2["type"] == "task_done"
        assert event2["task_id"] == "abc123"

    def test_read_events(self, tmp_path: Path) -> None:
        log_path = tmp_path / "events.jsonl"
        logger = EventLogger(log_path)
        logger.log("test_event", value="hello")
        events = logger.read_events()
        assert len(events) == 1
        assert events[0]["type"] == "test_event"

    def test_read_empty(self, tmp_path: Path) -> None:
        log_path = tmp_path / "nonexistent.jsonl"
        logger = EventLogger(log_path)
        events = logger.read_events()
        assert events == []

    def test_thread_safety(self, tmp_path: Path) -> None:
        log_path = tmp_path / "events.jsonl"
        logger = EventLogger(log_path)

        def write_events(n: int) -> None:
            for i in range(10):
                logger.log("thread_event", thread=n, index=i)

        threads = [threading.Thread(target=write_events, args=(t,)) for t in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        events = logger.read_events()
        assert len(events) == 50

    def test_nested_directory_creation(self, tmp_path: Path) -> None:
        log_path = tmp_path / "deep" / "nested" / "events.jsonl"
        logger = EventLogger(log_path)
        logger.log("test", msg="ok")
        assert log_path.exists()
