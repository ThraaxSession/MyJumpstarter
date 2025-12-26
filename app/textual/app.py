import logging
import re
from typing import Dict

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.logging import TextualHandler
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    Log,
    Markdown,
    MarkdownViewer,
    Static,
    TabbedContent,
    TabPane,
)

from app.textual.controller.myjumpstarter import Jumpstart
from app.textual.models.myjumpstarter import Action
from app.textual.widgets import ActionWidget, ConfigView

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[TextualHandler()],
)


class MainScreen(Screen):
    """A Textual app demonstrating a jumpstarter component."""

    def compose(self) -> ComposeResult:
        yield Header()

        with VerticalScroll(id="jumpstarter"):
            yield Static(
                """
                Welcome to [auto on teal]MyJumpstarter[/]!

                MyJumpstarter is a TUI application to help with setup your GNU/Linux environment as you wish.
                It makes it easy to configure and customize your system with just a few clicks and few receipts.
                """,
                id="welcome-text",
            )
        yield Footer()

    async def on_jumpstarter_jumpstart(self, message: Jumpstart) -> None:
        welcome_text = self.query_one("#welcome-text", Static)
        welcome_text.update(
            Text("Jumpstarted! Enjoy your experience!", style="bold green")
        )
        jumpstart_button = self.query_one("#jumpstart-button", Button)
        jumpstart_button.disabled = True


class JumpstartScreen(Screen):
    # receiptTabList: reactive[list[str]] = reactive([])
    jumpstart: Jumpstart = Jumpstart()

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="", id="receipt-tabs"):
            yield Markdown("")
        yield Footer()

    async def on_mount(self) -> None:
        # Clear existing tabs
        receipt_tabs = self.query_one("#receipt-tabs", TabbedContent)
        await receipt_tabs.clear_panes()

        # Add Config Tab
        config_tab_pane = TabPane(
            "Config",
            VerticalScroll(ConfigView(id="config-view")),
            id="tab-config",
        )
        receipt_tabs.add_pane(config_tab_pane)

        # Actions
        actions: list[list[Action]] = self.jumpstart.get_actions()

        # Add System Receipts Tabs
        system_actions = ActionWidget()
        system_actions.actions = [p for a in actions for p in a if p.group == "System"]
        system_tab_pane = TabPane(
            "System",
            system_actions,
            id="tab-system",
        )
        receipt_tabs.add_pane(system_tab_pane)

        # Populate receipt tabs
        config = await self.jumpstart.load_config()

        receipts: list[str] = [r for r in config["receipts"].keys()]
        for receipt in receipts:
            # Create action widget for the receipt
            action_widget = ActionWidget()
            action_widget.actions = [
                p for a in actions for p in a if p.group == receipt.capitalize()
            ]

            tab_pane = TabPane(
                f"{receipt}".capitalize(),
                self.__create_datatable(config["receipts"][receipt]),
                action_widget,
                id=f"tab-{receipt}",
            )
            receipt_tabs.add_pane(tab_pane)

    def __create_datatable(self, receipt: Dict) -> DataTable:
        data_table = DataTable(id="config-datatable", show_cursor=False)

        headers = receipt[0].keys()
        data_table.add_columns(*[str(header) for header in headers])
        for entry in receipt:
            data_table.add_row(*[str(entry[header]) for header in headers])

        return data_table


class AboutScreen(Screen):
    about_text = """\
    # MyJumpstarter

    MyJumpstarter is a Textual application to jumpstart your GNU/Linux environment.
    It provides an easy-to-use interface to configure and customize your system with just a few clicks and receipts.

    ## Features

    - User-friendly TUI interface
    - Configurable system setup
    - Supports multiple GNU/Linux distributions
    - Extensible with custom receipts

    ## Version

    1.0.0

    ## License

    MyJumpstarter is licensed under the MIT License.

    ## Author

    Developed by Thraax Session
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Markdown(
            self.about_text,
            id="about-markdownviewer",
        )
        yield Footer()


class AppEntryPoint(App):
    """Application entry point."""

    CSS_PATH = "app.tcss"
    TITLE = "MyJumpstarter"
    SUB_TITLE = "A Textual application with Jumpstarter"
    BINDINGS = [
        ("q", "on_quit", "Quit Application"),
        # ("t", "on_toggle_dark_light_mode", "Toggle Dark/Light"),
        ("m", "switch_mode('main')", "Main Mode"),
        ("j", "switch_mode('jumpstart')", "Jumpstart Mode"),
        ("a", "switch_mode('about')", "About Mode"),
    ]
    LOGO = "🚀"

    MODES = {
        "main": MainScreen,
        "jumpstart": JumpstartScreen,
        "about": AboutScreen,
    }

    def on_mount(self) -> None:
        """Mount the main screen."""
        # self.theme = "nord"
        self.dark = False
        self.switch_mode("main")

    def action_on_quit(self) -> None:
        """Handle application quit action."""
        logging.info("Application is quitting...")
        self.exit()

    def action_on_toggle_dark_light_mode(self) -> None:
        """Toggle between dark and light themes."""
        self.dark = not self.dark
