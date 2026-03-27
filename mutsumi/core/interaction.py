"""Semantic interaction primitives for RFC-010.

This module defines the smallest shared semantic action layer used by the
application, keybinding presets, and screen-level interaction contracts.
"""

from __future__ import annotations

from enum import StrEnum


class SemanticAction(StrEnum):
    """Stable semantic actions shared across input modalities."""

    CONFIRM = "confirm"
    BACK = "back"
    CANCEL = "cancel"
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    NEXT_GROUP = "next_group"
    PREV_GROUP = "prev_group"
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete"
    TOGGLE = "toggle"
    SWITCH_SCOPE = "switch_scope"
    SWITCH_SOURCE = "switch_source"


class ScreenContract(StrEnum):
    """Named interaction contracts for common screen types."""

    VERTICAL_LIST = "vertical_list"
    HORIZONTAL_CHOOSER = "horizontal_chooser"
    FORM_DIALOG = "form_dialog"


_VERTICAL_ACTIONS: tuple[SemanticAction, ...] = (
    SemanticAction.MOVE_UP,
    SemanticAction.MOVE_DOWN,
)

_HORIZONTAL_ACTIONS: tuple[SemanticAction, ...] = (
    SemanticAction.MOVE_LEFT,
    SemanticAction.MOVE_RIGHT,
)

_FORM_DIALOG_ACTIONS: tuple[SemanticAction, ...] = (
    SemanticAction.CONFIRM,
    SemanticAction.BACK,
    SemanticAction.CANCEL,
)


def contract_actions(contract: ScreenContract) -> tuple[SemanticAction, ...]:
    """Return the semantic actions expected by a screen contract."""

    return {
        ScreenContract.VERTICAL_LIST: _VERTICAL_ACTIONS,
        ScreenContract.HORIZONTAL_CHOOSER: _HORIZONTAL_ACTIONS,
        ScreenContract.FORM_DIALOG: _FORM_DIALOG_ACTIONS,
    }[contract]


def is_vertical_navigation(action: SemanticAction) -> bool:
    """Return True when *action* belongs to the vertical list contract."""

    return action in _VERTICAL_ACTIONS


def is_horizontal_navigation(action: SemanticAction) -> bool:
    """Return True when *action* belongs to the horizontal chooser contract."""

    return action in _HORIZONTAL_ACTIONS


def is_form_dialog_action(action: SemanticAction) -> bool:
    """Return True when *action* belongs to the form/dialog contract."""

    return action in _FORM_DIALOG_ACTIONS
