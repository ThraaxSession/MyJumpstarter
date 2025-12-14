# from time import sleep
from typing import Callable


class Action:
    """
    Defines Jumpstart actions
    """

    group = ""  # System
    action = ""  # Update
    id = ""  # Define the action id which is unique
    callback: Callable

    def __init__(self, group, action, id, callback):
        self.group = group
        self.action = action
        self.id = id
        self.callback = callback

    def __repr__(self) -> str:
        return "group: %s, action: %s, id: %s" % (
            self.group,
            self.action,
            self.id,
        )

    def __str__(self) -> str:
        return "group: %s, action: %s, id: %s" % (
            self.group,
            self.action,
            self.id,
        )


class Packagemanager:
    """
    Defines native package managers and their installation parameters
    """

    name: str = ""
    upgrade_args = []
    install_args = []

    def __init__(self, name, upgrade_args, *install_args) -> None:
        self.name = name
        self.upgrade_args = upgrade_args
        self.install_args = install_args

    def __repr__(self) -> str:
        return "Packagemanager: %s, upgrade args: %s, install args: %s" % (
            self.name,
            self.upgrade_args,
            self.install_args,
        )
