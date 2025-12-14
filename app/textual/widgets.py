from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Pretty, Static


class Sidebar(Widget):
    CSS_PATH = "sidebar.tcss"

    menus = reactive([])

    def compose(self) -> ComposeResult:
        yield Label("Sidebar Menu", id="sidebar-title")
        with Vertical():
            self.log("Composing sidebar menus")
            for menu in self.menus:
                yield Static(
                    f"[@click='open_screen('{menu}')']{menu}[/]",
                    id=f"menu-{menu.lower()}",
                )

    def on_mount(self) -> None:
        self.log("Sidebar mounted")
        self.menus = ["Home", "Settings", "Profile", "Logout"]

    def action_open_screen(self, screen: str) -> None:
        self.log(f"Opening screen: {screen}")
        if screen == "Logout":
            self.app.exit()
        elif screen == "Home":
            self.app.pop_screen()
        else:
            pass


class ConfigView(Widget):
    """A simple widget to display configuration."""

    CSS_PATH = "config_view.tcss"

    config: reactive[dict] = reactive(dict)
    title: reactive[str] = reactive("Your Configuration")

    def watch_config(self, old_config: dict, new_config: dict) -> None:
        self.log.debug(f"Configuration updated: {[old_config, new_config]}")
        self.refresh()

    def compose(self) -> ComposeResult:
        yield Static(
            f"[bold underline]{self.title}[/bold underline]", id="config-title"
        )
        yield Pretty(self.config, id="config-pretty")
