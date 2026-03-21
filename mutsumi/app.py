"""Mutsumi TUI Application entry point."""

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static


class MutsumiApp(App[None]):
    """The Mutsumi TUI application."""

    TITLE = "mutsumi"
    CSS = """
    Screen {
        background: #0f0f0f;
    }

    #welcome {
        content-align: center middle;
        width: 100%;
        height: 100%;
        color: #e0e0e0;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "Welcome to Mutsumi.\n\n"
            "No tasks.json found in this directory.\n\n"
            "Press [q] to quit.",
            id="welcome",
        )
        yield Footer()


def run() -> None:
    """Launch the Mutsumi TUI."""
    app = MutsumiApp()
    app.run()


if __name__ == "__main__":
    run()
