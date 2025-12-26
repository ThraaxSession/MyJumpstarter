from os import system
from typing import Iterable

from textual import on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Log, OptionList, Pretty, RichLog, Static

from app.textual.controller.myjumpstarter import Jumpstart
from app.textual.models.myjumpstarter import Action


class ConfigView(Widget):
    """A simple widget to display configuration."""

    BINDINGS = [("e", "edit_config", "Edit Configuration")]

    title: reactive[str] = reactive("Your Configuration")
    config: reactive[object] = reactive(None, recompose=True)
    editor: reactive[str] = reactive("vim", recompose=True)
    jumpstart: Jumpstart = Jumpstart()

    editor_list = ["vim", "nvim", "nano", "emacs", "hx"]

    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="config-controls"):
            option_list = OptionList()
            option_list.focus()
            option_list.border_title = "Select your favorite Editor"
            for editor in self.editor_list:
                option_list.add_option(editor)
            yield option_list
            # yield Button("Edit config", id="edit-config-button")

        yield Static(
            f"[bold underline]{self.title}[/bold underline]", id="config-title"
        )
        yield Pretty(self.config, id="config-pretty")

    async def on_mount(self) -> None:
        # Build the selection list
        option_list = self.query_one(OptionList)
        option_list.focus()
        option_list.border_title = "Select your favorite Editor"
        # Select default editor
        option_list.highlighted = self.editor_list.index(self.editor)
        # Populate the option list
        for editor in self.editor_list:
            option_list.add_option(editor)

        try:
            self.config = await self.jumpstart.load_config()
        except Exception as e:
            self.notify(f"Failed to load configuration: {e}", timeout=5)

    @on(OptionList.OptionMessage)
    def on_selection_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        index = event.option_index
        self.editor = self.editor_list[index]

    async def action_edit_config(self) -> None:
        """Action to edit the configuration file."""
        with self.app.suspend():
            try:
                ret = system(f"{self.editor} {self.jumpstart.config_path}")
                if ret == 0:
                    try:
                        self.config = await self.jumpstart.load_config()
                        self.notify("Configuration reloaded!", timeout=5)
                    except Exception as e:
                        self.notify(f"Failed to reload configuration: {e}", timeout=5)
                else:
                    self.notify(
                        "Editor not found",
                        timeout=5,
                        severity="warning",
                    )
            except Exception as e:
                self.notify(
                    f"Failed to edit configuration: {e}", timeout=5, severity="error"
                )


class ActionWidget(Widget):
    """A simple widget to display an action."""

    actions: reactive[list[Action]] = reactive([], recompose=True)

    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="action-controls"):
            for action in self.actions:
                if action is not None:
                    yield Button(
                        action.action, id=f"{action.action}", variant="primary"
                    )
            yield Button("Clear Logs", id="clear-logs")
        yield Log(id="logs")

    # @work(exclusive=True, thread=True)
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        for action in self.actions:
            if action is not None and event.button.id == action.action:
                with self.app.suspend():
                    try:
                        log_widget = self.query_one("#logs", Log)
                        log = action.callback()
                        if log is not None:
                            if log is isinstance(log, str):
                                log_widget.write_line(log)
                            elif isinstance(log, Iterable):
                                log_widget.write_lines(log)

                        self.notify(f"Action '{action.action}' executed!", timeout=5)
                    except Exception as e:
                        self.notify(
                            f"Failed to execute action '{action.action}': {e}",
                            timeout=5,
                            severity="error",
                        )
                        log_widget = self.query_one("#logs", Log)
                        log_widget.write_line(f"Error: {e}")
        if event.button.id == "clear-logs":
            log_widget = self.query_one("#logs", Log)
            log_widget.clear()
