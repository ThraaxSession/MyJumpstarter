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
    upgradeArgs = []
    installArgs = []

    def __init__(self, name, upgradeArgs, *installArgs) -> None:
        self.name = name
        self.upgradeArgs = upgradeArgs
        self.installArgs = installArgs

    def __repr__(self) -> str:
        return "Packagemanager: %s, upgrade args: %s, install args: %s" % (
            self.name,
            self.upgradeArgs,
            self.installArgs,
        )
