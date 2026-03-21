"""Pydantic data models for Mutsumi task schema."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class TaskStatus(StrEnum):
    PENDING = "pending"
    DONE = "done"


class TaskScope(StrEnum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    INBOX = "inbox"


class TaskPriority(StrEnum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


PRIORITY_SORT_ORDER: dict[TaskPriority, int] = {
    TaskPriority.HIGH: 0,
    TaskPriority.NORMAL: 1,
    TaskPriority.LOW: 2,
}


class Task(BaseModel):
    """A single task in the Mutsumi task file."""

    model_config = ConfigDict(extra="allow")

    id: str
    title: str
    status: TaskStatus = TaskStatus.PENDING
    scope: TaskScope = TaskScope.INBOX
    priority: TaskPriority = TaskPriority.NORMAL
    tags: list[str] = []
    children: list[Task] = []
    created_at: str | None = None
    due_date: str | None = None
    completed_at: str | None = None
    description: str | None = None

    @property
    def is_done(self) -> bool:
        return self.status == TaskStatus.DONE

    @property
    def priority_sort_key(self) -> int:
        return PRIORITY_SORT_ORDER[self.priority]

    def children_progress(self, max_depth: int = 3) -> tuple[int, int]:
        """Return (done_count, total_count) for direct children."""
        if not self.children:
            return (0, 0)
        done = sum(1 for c in self.children if c.is_done)
        return (done, len(self.children))


class TaskFile(BaseModel):
    """Root structure of a Mutsumi tasks.json file."""

    model_config = ConfigDict(extra="allow")

    version: int = 1
    tasks: list[Task] = []
