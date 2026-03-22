"""Internationalization for Mutsumi.

Loads locale TOML files and provides dot-notation key lookup
with fallback chain: locale → en → raw key.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

_LOCALES_DIR = Path(__file__).parent / "locales"

_i18n: I18n | None = None

# Locales we ship (filename stems under locales/)
_SUPPORTED_LOCALES = {"en", "ja", "zh"}


def _detect_locale_from_env() -> str:
    """Detect locale from environment or system settings.

    Checks $LC_ALL / $LANG (Unix), then falls back to locale.getdefaultlocale()
    for Windows compatibility. Returns the best matching supported locale,
    or "en" as fallback.
    """
    import locale as _locale

    raw = os.environ.get("LC_ALL") or os.environ.get("LANG") or ""
    if not raw or raw in ("C", "POSIX"):
        # Fallback: use Python's locale detection (works on Windows too)
        try:
            system_locale = _locale.getdefaultlocale()[0] or ""
        except (ValueError, AttributeError):
            system_locale = ""
        raw = system_locale
        return "en"
    # Strip encoding (e.g. ".UTF-8")
    lang = raw.split(".")[0]  # "zh_CN"
    # Try exact match first (unlikely but safe)
    if lang in _SUPPORTED_LOCALES:
        return lang
    # Try language prefix (e.g. "zh" from "zh_CN")
    prefix = lang.split("_")[0]
    if prefix in _SUPPORTED_LOCALES:
        return prefix
    return "en"


class I18n:
    """Internationalization helper with dot-notation key lookup."""

    def __init__(self, locale: str = "en") -> None:
        self._locale = locale
        self._strings: dict[str, dict[str, str]] = {}
        self._fallback: dict[str, dict[str, str]] = {}
        self.load(locale)

    @property
    def locale(self) -> str:
        return self._locale

    def load(self, locale: str) -> None:
        """Load a locale file. Also loads 'en' as fallback if locale != 'en'."""
        self._locale = locale
        self._strings = self._load_toml(locale)
        if locale != "en":
            self._fallback = self._load_toml("en")
        else:
            self._fallback = {}

    def _load_toml(self, locale: str) -> dict[str, dict[str, str]]:
        """Load a single TOML locale file into a nested dict."""
        path = _LOCALES_DIR / f"{locale}.toml"
        if not path.exists():
            return {}
        with open(path, "rb") as f:
            data = tomllib.load(f)
        # Flatten to str -> str mapping per section
        result: dict[str, dict[str, str]] = {}
        for section, values in data.items():
            if isinstance(values, dict):
                result[section] = {k: str(v) for k, v in values.items()}
        return result

    def t(self, key: str, **kwargs: str | int) -> str:
        """Translate a dot-notation key with optional format arguments.

        Fallback chain: locale strings → en strings → raw key.
        Example: t("tabs.today") → "Today"
        Example: t("status.tasks", count=5) → "5 tasks"
        """
        parts = key.split(".", 1)
        if len(parts) != 2:
            return key

        section, name = parts

        # Try current locale
        value = self._strings.get(section, {}).get(name)
        # Try fallback (en)
        if value is None:
            value = self._fallback.get(section, {}).get(name)
        # Raw key fallback
        if value is None:
            return key

        if kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, IndexError):
                return value
        return value


def init_i18n(locale: str = "en") -> I18n:
    """Initialize the global i18n instance.

    Pass ``"auto"`` to detect from ``$LANG`` / ``$LC_ALL``.
    """
    global _i18n  # noqa: PLW0603
    if locale == "auto":
        locale = _detect_locale_from_env()
    _i18n = I18n(locale)
    return _i18n


def get_i18n() -> I18n:
    """Get the global i18n instance, initializing with 'en' if needed."""
    global _i18n  # noqa: PLW0603
    if _i18n is None:
        _i18n = I18n("en")
    return _i18n


def reset_i18n() -> None:
    """Reset the global i18n instance (for testing)."""
    global _i18n  # noqa: PLW0603
    _i18n = None
