"""Tests for the multi-key sequence engine (KeyManager)."""

from __future__ import annotations

import pytest

pytest.importorskip("textual")

from mutsumi.tui.key_manager import (
    COMMON_SEQUENCES,
    VIM_SEQUENCES,
    KeyManager,
    KeySequence,
    MatchResult,
    get_key_sequences,
)


class TestKeyManager:
    def test_exact_match_dd(self) -> None:
        """dd should produce an EXACT match for delete_confirm."""
        km = KeyManager(COMMON_SEQUENCES)
        result1, action1 = km.feed("d")
        assert result1 == MatchResult.PREFIX
        assert action1 is None

        result2, action2 = km.feed("d")
        assert result2 == MatchResult.EXACT
        assert action2 == "delete_confirm"

    def test_no_match_clears_buffer(self) -> None:
        """A non-matching key after prefix should clear the buffer."""
        km = KeyManager(COMMON_SEQUENCES)
        km.feed("d")
        assert km.pending

        result, action = km.feed("x")
        assert result == MatchResult.NO_MATCH
        assert action is None
        assert not km.pending

    def test_exact_match_gg(self) -> None:
        """gg in vim preset should produce cursor_top."""
        km = KeyManager(VIM_SEQUENCES)
        km.feed("g")
        result, action = km.feed("g")
        assert result == MatchResult.EXACT
        assert action == "cursor_top"

    def test_clear_resets_buffer(self) -> None:
        km = KeyManager(COMMON_SEQUENCES)
        km.feed("d")
        assert km.pending
        km.clear()
        assert not km.pending

    def test_buffer_returns_copy(self) -> None:
        km = KeyManager(COMMON_SEQUENCES)
        km.feed("d")
        buf = km.buffer
        buf.append("extra")
        assert km.buffer == ["d"]

    def test_no_match_on_unknown_key(self) -> None:
        km = KeyManager(COMMON_SEQUENCES)
        result, action = km.feed("z")
        assert result == MatchResult.NO_MATCH
        assert action is None

    def test_get_key_sequences_vim(self) -> None:
        seqs = get_key_sequences("vim")
        actions = {s.action for s in seqs}
        assert "delete_confirm" in actions
        assert "cursor_top" in actions

    def test_get_key_sequences_fallback(self) -> None:
        seqs = get_key_sequences("unknown")
        assert seqs is get_key_sequences("vim")

    def test_key_sequence_dataclass(self) -> None:
        seq = KeySequence(keys=("a", "b"), action="test_action", description="A test")
        assert seq.keys == ("a", "b")
        assert seq.action == "test_action"
        assert seq.description == "A test"

    def test_sequences_property(self) -> None:
        km = KeyManager(COMMON_SEQUENCES)
        seqs = km.sequences
        assert len(seqs) == len(COMMON_SEQUENCES)
        # Should be a copy
        seqs.append(KeySequence(keys=("x",), action="nope"))
        assert len(km.sequences) == len(COMMON_SEQUENCES)
