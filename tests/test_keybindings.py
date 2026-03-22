"""Tests for keybinding presets."""

from __future__ import annotations

import pytest

pytest.importorskip("textual")

from mutsumi.config.keybindings import (
    ARROW_BINDINGS,
    EMACS_BINDINGS,
    VIM_BINDINGS,
    get_keybindings,
)


class TestKeybindings:
    def test_vim_has_jk(self) -> None:
        keys = {b.key for b in VIM_BINDINGS}
        assert "j" in keys
        assert "k" in keys

    def test_emacs_has_ctrl_np(self) -> None:
        keys = {b.key for b in EMACS_BINDINGS}
        assert "ctrl+n" in keys
        assert "ctrl+p" in keys

    def test_arrows_has_updown(self) -> None:
        keys = {b.key for b in ARROW_BINDINGS}
        assert "up" in keys
        assert "down" in keys

    def test_all_presets_have_common(self) -> None:
        for bindings in [VIM_BINDINGS, EMACS_BINDINGS, ARROW_BINDINGS]:
            keys = {b.key for b in bindings}
            # All presets have a quit binding (q or ctrl+q)
            assert "q" in keys or "ctrl+q" in keys
            assert "space" in keys
            assert "n" in keys
            assert "slash" in keys

    def test_all_presets_have_fold_bindings(self) -> None:
        """Every preset has collapse/expand actions."""
        for bindings in [VIM_BINDINGS, EMACS_BINDINGS, ARROW_BINDINGS]:
            actions = {b.action for b in bindings}
            assert "collapse_group" in actions
            assert "expand_group" in actions

    def test_get_keybindings_valid(self) -> None:
        assert get_keybindings("vim") == VIM_BINDINGS
        assert get_keybindings("emacs") == EMACS_BINDINGS
        assert get_keybindings("arrows") == ARROW_BINDINGS

    def test_get_keybindings_fallback(self) -> None:
        assert get_keybindings("unknown") == ARROW_BINDINGS

    def test_new_crud_bindings(self) -> None:
        keys = {b.key for b in VIM_BINDINGS}
        assert "n" in keys
        assert "e" in keys
        # 'd' is now handled by KeyManager, not Binding
        assert "d" not in keys

    def test_new_action_bindings(self) -> None:
        """New bindings from Step 4 plan are present."""
        for bindings in [VIM_BINDINGS, EMACS_BINDINGS, ARROW_BINDINGS]:
            actions = {b.action for b in bindings}
            assert "priority_up" in actions
            assert "priority_down" in actions
            assert "copy_task" in actions
            assert "paste_task" in actions
            assert "toggle_fold" in actions
            assert "show_help" in actions
            assert "inline_edit" in actions
            assert "sort" in actions

    def test_vim_has_shift_jk_move(self) -> None:
        actions = {b.action for b in VIM_BINDINGS}
        assert "move_up" in actions
        assert "move_down" in actions

    def test_emacs_has_ctrl_shift_move(self) -> None:
        keys = {b.key for b in EMACS_BINDINGS}
        assert "ctrl+shift+n" in keys
        assert "ctrl+shift+p" in keys

    def test_arrows_has_shift_arrow_move(self) -> None:
        keys = {b.key for b in ARROW_BINDINGS}
        assert "shift+down" in keys
        assert "shift+up" in keys
