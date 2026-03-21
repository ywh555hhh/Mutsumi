"""Tests for the i18n system."""

from __future__ import annotations

from mutsumi.i18n import I18n, get_i18n, init_i18n, reset_i18n


class TestI18n:
    def test_load_en(self) -> None:
        i18n = I18n("en")
        assert i18n.locale == "en"
        assert i18n.t("tabs.today") == "Today"

    def test_load_zh(self) -> None:
        i18n = I18n("zh")
        assert i18n.t("tabs.today") == "今天"

    def test_load_ja(self) -> None:
        i18n = I18n("ja")
        assert i18n.t("tabs.today") == "今日"

    def test_format_args(self) -> None:
        i18n = I18n("en")
        result = i18n.t("status.tasks", count=5)
        assert result == "5 tasks"

    def test_fallback_to_en(self) -> None:
        # Non-existent locale should fall back to 'en' strings
        i18n_fake = I18n("nonexistent")
        assert i18n_fake.t("tabs.today") == "Today"

    def test_missing_key_returns_raw(self) -> None:
        i18n = I18n("en")
        assert i18n.t("nonexistent.key") == "nonexistent.key"

    def test_invalid_key_format(self) -> None:
        i18n = I18n("en")
        assert i18n.t("nodot") == "nodot"

    def test_dot_notation_detail(self) -> None:
        i18n = I18n("en")
        assert i18n.t("detail.status") == "Status"
        assert i18n.t("detail.priority") == "Priority"

    def test_cli_keys(self) -> None:
        i18n = I18n("en")
        result = i18n.t("cli.add_success", title="Test", id="ABC123")
        assert "Test" in result
        assert "ABC123" in result


class TestGlobalI18n:
    def test_get_i18n_default(self) -> None:
        reset_i18n()
        i18n = get_i18n()
        assert i18n.locale == "en"

    def test_init_i18n(self) -> None:
        reset_i18n()
        i18n = init_i18n("zh")
        assert i18n.locale == "zh"
        assert get_i18n().locale == "zh"
        reset_i18n()
