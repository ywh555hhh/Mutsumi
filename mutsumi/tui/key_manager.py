"""Multi-key sequence engine for Mutsumi.

Dooit-inspired prefix-matching accumulator (no timeout).
Handles sequences like ``dd`` (delete) and ``gg`` (cursor top).

Single-key bindings are still handled by Textual's ``Binding`` system.
KeyManager only processes multi-key sequences.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum, auto


class MatchResult(StrEnum):
    """Outcome of feeding a key into the buffer."""

    NO_MATCH = auto()
    PREFIX = auto()
    EXACT = auto()


@dataclass(frozen=True)
class KeySequence:
    """A multi-key sequence that maps to an action."""

    keys: tuple[str, ...]
    action: str
    description: str = ""


class KeyManager:
    """Accumulates keystrokes and matches against registered sequences.

    Three-state matching:
      - NO_MATCH:  buffer doesn't match any sequence prefix → clear buffer
      - PREFIX:    buffer is a prefix of at least one sequence → keep accumulating
      - EXACT:     buffer matches a sequence exactly → return action, clear buffer

    Call ``clear()`` or press Escape to reset the buffer manually.
    """

    def __init__(self, sequences: list[KeySequence]) -> None:
        self._sequences = list(sequences)
        self._buffer: list[str] = []

    @property
    def buffer(self) -> list[str]:
        """Current accumulated keystrokes (read-only view)."""
        return list(self._buffer)

    @property
    def pending(self) -> bool:
        """True if the buffer has at least one key waiting for more input."""
        return len(self._buffer) > 0

    @property
    def sequences(self) -> list[KeySequence]:
        """All registered sequences (read-only)."""
        return list(self._sequences)

    def feed(self, key: str) -> tuple[MatchResult, str | None]:
        """Feed a key press into the manager.

        Returns ``(result, action)``:
          - ``(NO_MATCH, None)``  — no sequence starts with this buffer
          - ``(PREFIX, None)``    — buffer is a valid prefix, waiting for more
          - ``(EXACT, action)``   — matched a sequence; action string returned
        """
        self._buffer.append(key)
        buf_tuple = tuple(self._buffer)

        # Check for exact match first
        for seq in self._sequences:
            if seq.keys == buf_tuple:
                action = seq.action
                self._buffer.clear()
                return (MatchResult.EXACT, action)

        # Check for prefix match
        for seq in self._sequences:
            if seq.keys[: len(buf_tuple)] == buf_tuple:
                return (MatchResult.PREFIX, None)

        # No match at all — clear
        self._buffer.clear()
        return (MatchResult.NO_MATCH, None)

    def clear(self) -> None:
        """Reset the key buffer."""
        self._buffer.clear()


# ── Preset sequence tables ──────────────────────────────────────────

COMMON_SEQUENCES: list[KeySequence] = [
    KeySequence(keys=("d", "d"), action="delete_confirm", description="Delete task"),
]

VIM_SEQUENCES: list[KeySequence] = [
    *COMMON_SEQUENCES,
    KeySequence(keys=("g", "g"), action="cursor_top", description="Go to top"),
]

EMACS_SEQUENCES: list[KeySequence] = [
    *COMMON_SEQUENCES,
]

ARROW_SEQUENCES: list[KeySequence] = [
    *COMMON_SEQUENCES,
]

SEQUENCE_PRESET_MAP: dict[str, list[KeySequence]] = {
    "vim": VIM_SEQUENCES,
    "emacs": EMACS_SEQUENCES,
    "arrows": ARROW_SEQUENCES,
}


def get_key_sequences(preset: str) -> list[KeySequence]:
    """Get key sequences for a preset. Falls back to vim."""
    return SEQUENCE_PRESET_MAP.get(preset, VIM_SEQUENCES)
