"""Event logger for Mutsumi.

Appends structured events to a JSONL file for audit trail.
Thread-safe via threading.Lock.
Default path: platform data dir / mutsumi / events.jsonl.
"""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def _default_event_log_path() -> Path:
    from mutsumi.core.paths import mutsumi_data_dir

    return mutsumi_data_dir() / "events.jsonl"


class EventLogger:
    """Thread-safe JSONL event logger."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or _default_event_log_path()
        self._lock = threading.Lock()

    @property
    def path(self) -> Path:
        return self._path

    def log(self, event_type: str, **data: str | int | list[str] | None) -> None:
        """Append a single event to the log file.

        Each event is a JSON object on its own line with:
        - timestamp: ISO 8601 UTC
        - type: event type string
        - additional key-value data
        """
        entry: dict[str, str | int | list[str] | None] = {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "type": event_type,
            **data,
        }
        line = json.dumps(entry, ensure_ascii=False) + "\n"

        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(line)

    def read_events(self) -> list[dict[str, str | int | list[str] | None]]:
        """Read all events from the log file."""
        if not self._path.exists():
            return []
        events: list[dict[str, str | int | list[str] | None]] = []
        with open(self._path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        return events
