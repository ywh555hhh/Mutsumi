"""Multi-source data coordination layer.

Manages N data sources (personal + per-project) at runtime.
Source tracking is runtime-only — no metadata is written to JSON files.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from mutsumi.core.loader import load_task_file
from mutsumi.core.watcher import TaskFileWatcher

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from mutsumi.core.models import Task, TaskFile


@dataclass
class Source:
    """A single data source (one mutsumi.json / tasks.json file)."""

    name: str
    path: Path
    task_file: TaskFile | None = None
    error: str | None = None
    is_personal: bool = False


class SourceRegistry:
    """Manages multiple data sources and their file watchers."""

    def __init__(self) -> None:
        self._sources: OrderedDict[str, Source] = OrderedDict()
        self._watchers: dict[str, TaskFileWatcher] = {}

    @property
    def sources(self) -> OrderedDict[str, Source]:
        return self._sources

    @property
    def source_names(self) -> list[str]:
        return list(self._sources.keys())

    def add_source(
        self, name: str, path: Path, *, is_personal: bool = False,
    ) -> Source:
        """Register a new data source. Does NOT load it."""
        source = Source(name=name, path=path.resolve(), is_personal=is_personal)
        self._sources[name] = source
        return source

    def remove_source(self, name: str) -> None:
        """Remove a source and stop its watcher."""
        self.stop_watching(name)
        self._sources.pop(name, None)

    def get_source(self, name: str) -> Source | None:
        return self._sources.get(name)

    def load_source(self, name: str) -> Source | None:
        """Load (or reload) a single source from disk."""
        source = self._sources.get(name)
        if source is None:
            return None
        try:
            source.task_file = load_task_file(source.path)
            source.error = None
        except FileNotFoundError:
            source.task_file = None
            source.error = None  # file just doesn't exist yet
        except Exception as exc:
            source.task_file = None
            source.error = str(exc)
        return source

    def load_all(self) -> None:
        """Load all registered sources from disk."""
        for name in self._sources:
            self.load_source(name)

    def start_watching(
        self, name: str, callback: Callable[[str], None],
    ) -> None:
        """Start file-watching for a source. Callback receives source name.

        The target file does NOT need to exist — the watcher monitors the
        parent directory and will detect file creation by an external Agent.
        The parent directory must exist, though.
        """
        source = self._sources.get(name)
        if source is None:
            return
        if name in self._watchers:
            return  # already watching
        if not source.path.parent.exists():
            return  # parent dir doesn't exist, can't watch

        def _on_change() -> None:
            callback(name)

        watcher = TaskFileWatcher(source.path, _on_change)
        watcher.start()
        self._watchers[name] = watcher

    def stop_watching(self, name: str) -> None:
        """Stop file-watching for a specific source."""
        watcher = self._watchers.pop(name, None)
        if watcher is not None:
            watcher.stop()

    def stop_all_watchers(self) -> None:
        """Stop all file watchers."""
        for watcher in self._watchers.values():
            watcher.stop()
        self._watchers.clear()

    def all_tasks(self) -> list[tuple[str, Task]]:
        """Aggregate tasks from all sources. Returns (source_name, task) pairs."""
        result: list[tuple[str, Task]] = []
        for name, source in self._sources.items():
            if source.task_file is not None:
                for task in source.task_file.tasks:
                    result.append((name, task))
        return result

    def __len__(self) -> int:
        return len(self._sources)

    def __contains__(self, name: str) -> bool:
        return name in self._sources
