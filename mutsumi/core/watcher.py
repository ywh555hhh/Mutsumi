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

    def _matches_target(self, path_str: str) -> bool:
        """Check if a path matches the target file."""
        return Path(path_str).resolve() == self._target

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        if self._matches_target(str(event.src_path)):
            self._schedule()

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        if self._matches_target(str(event.src_path)):
            self._schedule()

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle atomic writes that appear as rename/move events.

        os.replace() uses rename(2) which watchdog may report as a
        FileMovedEvent. Check if the destination matches the target.
        """
        if event.is_directory:
            return
        dest = getattr(event, "dest_path", None)
        if dest is not None and self._matches_target(str(dest)):
            self._schedule()

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
    """Watches a task file's parent directory for changes.

    Starts watching the parent directory immediately — the target file
    does NOT need to exist yet. This allows detecting when an Agent
    creates the file for the first time.
    """

    def __init__(self, path: Path, callback: Callable[[], Any]) -> None:
        self._path = path.resolve()
        self._callback = callback
        self._observer: Observer | None = None  # type: ignore[valid-type]
        self._handler = _DebouncedHandler(self._path, self._callback)

    def start(self) -> None:
        """Start watching the file's parent directory.

        The parent directory must exist, but the target file itself
        does not need to exist — we'll detect its creation.
        """
        if self._observer is not None:
            return
        watch_dir = self._path.parent
        if not watch_dir.exists():
            return
        self._observer = Observer()
        self._observer.schedule(self._handler, str(watch_dir), recursive=False)
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
