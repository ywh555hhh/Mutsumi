"""File watcher with debounce for tasks.json hot-reload."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

if TYPE_CHECKING:
    from collections.abc import Callable

    from watchdog.events import FileSystemEvent

DEBOUNCE_SECONDS = 0.1


class _DebouncedHandler(FileSystemEventHandler):
    """Watches for modifications to a specific file with debounce."""

    def __init__(self, target_path: Path, callback: Callable[[], Any]) -> None:
        super().__init__()
        self._target = target_path.resolve()
        self._callback = callback
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        src = Path(str(event.src_path)).resolve()
        if src != self._target:
            return
        self._schedule()

    def on_created(self, event: FileSystemEvent) -> None:
        # Handle atomic writes (temp + rename shows as create)
        self.on_modified(event)

    def _schedule(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(DEBOUNCE_SECONDS, self._fire)
            self._timer.daemon = True
            self._timer.start()

    def _fire(self) -> None:
        self._callback()


class TaskFileWatcher:
    """Watches tasks.json for changes and calls back on modifications."""

    def __init__(self, path: Path, callback: Callable[[], Any]) -> None:
        self._path = path.resolve()
        self._callback = callback
        self._observer: Observer | None = None  # type: ignore[valid-type]
        self._handler = _DebouncedHandler(self._path, self._callback)

    def start(self) -> None:
        """Start watching the file's parent directory."""
        if self._observer is not None:
            return
        self._observer = Observer()
        watch_dir = str(self._path.parent)
        self._observer.schedule(self._handler, watch_dir, recursive=False)
        self._observer.daemon = True
        self._observer.start()

    def stop(self) -> None:
        """Stop the file watcher."""
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=2)
            self._observer = None

    @property
    def is_running(self) -> bool:
        return self._observer is not None and self._observer.is_alive()
