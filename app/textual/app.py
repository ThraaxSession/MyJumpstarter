import logging
from os import system

from rich.text import Text
from textual.app import App, ComposeResult, RenderResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.logging import TextualHandler
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from app.textual.controller.myjumpstarter import Jumpstart
from app.textual.widgets import ConfigView, Sidebar

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[TextualHandler()],
)


class MainScreen(Screen):
    """A Textual app demonstrating a jumpstarter component."""

    jumpstart = Jumpstart()
    config = reactive(dict)

    BINDINGS = [("s", "toggle_sidebar", "Toggle Sidebar")]

    show_sidebar = reactive(False)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Sidebar(id="menu-sidebar")

        with VerticalScroll(id="jumpstarter"):
            yield Static(
                """Welcome to [auto on teal]MyJumpstarter[/]!\n
                Press the button below to jumpstart your experience.""",
                id="welcome-text",
            )
            with Horizontal(classes="main-buttons"):
                yield Button("Jumpstart", id="jumpstart-button")
                yield Button("Edit config", id="edit-config-button")
                yield Button("Quit", id="quit-button")

            config_view = ConfigView(id="config-display")
            config_view.title = "Current Configuration"
            config_view.config = self.jumpstart.myconfig
            yield config_view
        yield Footer()

    def on_mount(self) -> None:
        self.config = self.jumpstart.myconfig

        # Fill sidebar with menu items
        sidebar: Sidebar = self.query_one(Sidebar)
        sidebar.menus = ["Home", "Settings", "About"]

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "jumpstart-button":
            # Show tooltip
            self.notify("Jumpstarting...", timeout=5)
            # await self.jumpstart.start_jumpstart()
        elif event.button.id == "quit-button":
            await self.app.action_quit()
        elif event.button.id == "edit-config-button":
            with self.app.suspend():
                ret = system("nano config.yaml")
                if ret == 0:
                    new_config = self.jumpstart.load_config()
                    config_view = self.query_one("#config-display", ConfigView)
                    config_view.config = new_config
                    self.notify("Configuration reloaded!", timeout=5)

    async def on_jumpstarter_jumpstart(self, message: Jumpstart) -> None:
        welcome_text = self.query_one("#welcome-text", Static)
        welcome_text.update(
            Text("Jumpstarted! Enjoy your experience!", style="bold green")
        )
        jumpstart_button = self.query_one("#jumpstart-button", Button)
        jumpstart_button.disabled = True

    def action_toggle_sidebar(self) -> None:
        """Toggle the sidebar visibility."""
        self.show_sidebar = not self.show_sidebar

    def watch_show_sidebar(self, show_sidebar: bool) -> None:
        """Set or unset visible class when reactive changes."""
        self.query_one(Sidebar).set_class(show_sidebar, "-visible")


class AppEntryPoint(App):
    """Application entry point."""

    CSS_PATH = "app.tcss"
    TITLE = "MyJumpstarter"
    SUB_TITLE = "An Textual application with Jumpstarter"
    BINDINGS = [("q", "on_quit", "Quit Application")]
    LOGO = "🚀"

    def on_mount(self) -> None:
        """Mount the main screen."""
        self.theme = "nord"
        self.push_screen(MainScreen())

    def action_on_quit(self) -> None:
        """Handle application quit action."""
        logging.info("Application is quitting...")
        self.exit()
