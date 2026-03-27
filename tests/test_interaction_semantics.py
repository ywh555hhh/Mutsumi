"""Semantic interaction layer tests."""

from __future__ import annotations

from mutsumi.core.interaction import (
    ScreenContract,
    SemanticAction,
    contract_actions,
    is_form_dialog_action,
    is_horizontal_navigation,
    is_vertical_navigation,
)


def test_vertical_contract_contains_only_vertical_navigation() -> None:
    actions = contract_actions(ScreenContract.VERTICAL_LIST)
    assert actions == (SemanticAction.MOVE_UP, SemanticAction.MOVE_DOWN)
    assert all(is_vertical_navigation(action) for action in actions)


def test_horizontal_contract_contains_only_horizontal_navigation() -> None:
    actions = contract_actions(ScreenContract.HORIZONTAL_CHOOSER)
    assert actions == (SemanticAction.MOVE_LEFT, SemanticAction.MOVE_RIGHT)
    assert all(is_horizontal_navigation(action) for action in actions)


def test_form_dialog_contract_contains_confirm_back_cancel() -> None:
    actions = contract_actions(ScreenContract.FORM_DIALOG)
    assert actions == (
        SemanticAction.CONFIRM,
        SemanticAction.BACK,
        SemanticAction.CANCEL,
    )
    assert all(is_form_dialog_action(action) for action in actions)
