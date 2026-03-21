"""Built-in theme definitions for Mutsumi."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeColors:
    """Color scheme for a Mutsumi theme."""

    name: str
    background: str
    surface: str
    border: str
    text: str
    text_muted: str
    accent: str
    error: str
    priority_high: str
    priority_normal: str
    priority_low: str


MONOCHROME_ZEN = ThemeColors(
    name="monochrome-zen",
    background="#0f0f0f",
    surface="#1a1a1a",
    border="#333333",
    text="#e0e0e0",
    text_muted="#666666",
    accent="#5de4c7",
    error="#e06c75",
    priority_high="#e06c75",
    priority_normal="#e5c07b",
    priority_low="#666666",
)

NORD = ThemeColors(
    name="nord",
    background="#2e3440",
    surface="#3b4252",
    border="#4c566a",
    text="#eceff4",
    text_muted="#d8dee9",
    accent="#88c0d0",
    error="#bf616a",
    priority_high="#bf616a",
    priority_normal="#ebcb8b",
    priority_low="#4c566a",
)

DRACULA = ThemeColors(
    name="dracula",
    background="#282a36",
    surface="#44475a",
    border="#6272a4",
    text="#f8f8f2",
    text_muted="#6272a4",
    accent="#bd93f9",
    error="#ff5555",
    priority_high="#ff5555",
    priority_normal="#f1fa8c",
    priority_low="#6272a4",
)

SOLARIZED = ThemeColors(
    name="solarized",
    background="#002b36",
    surface="#073642",
    border="#586e75",
    text="#839496",
    text_muted="#586e75",
    accent="#2aa198",
    error="#dc322f",
    priority_high="#dc322f",
    priority_normal="#b58900",
    priority_low="#586e75",
)

BUILTIN_THEMES: dict[str, ThemeColors] = {
    "monochrome-zen": MONOCHROME_ZEN,
    "nord": NORD,
    "dracula": DRACULA,
    "solarized": SOLARIZED,
}
