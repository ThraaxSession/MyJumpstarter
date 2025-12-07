#
# This scripts shall help developers to setup their dev environments easily or if you have a new awesome Linux PC and you need a jumpstart to setup the PC. ;)
#

import subprocess
import sys

from .util.model import Action, Packagemanager

try:
    import rich
    import yaml
except ImportError:
    print("Run pip3 install rich")
    subprocess.run(["pip3", "install", "rich", "pyyaml"])
finally:
    import yaml
    from rich import pretty
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
    from rich.table import Table

console = Console()
menu_console = Console(width=80)


class Jumpstart:
    """
    Actual business logic to execute the actions
    """

    pkgManagers = [
        Packagemanager("pacman", ["-Syyu"], ["-S"]),
        Packagemanager("dnf", ["upgrade", "-y"], ["install"]),
        Packagemanager("apt", ["upgrade"], ["install"]),
        Packagemanager("zypper", ["upgrade"], ["install"]),  # TODO check this up
        Packagemanager("brew", ["upgrade"], ["install"]),
        Packagemanager("flatpak", ["upgrade"], ["install"]),
    ]

    myconfig = {}

    def __init__(self):
        # TODO add error handling
        with open("config.yaml", "r") as configfile:
            # console.log("Read config.yaml", configfile)
            self.myconfig = yaml.safe_load(configfile)

    def __find_pkgmanager__(self, named: str = "") -> Packagemanager:
        if named != "":
            return [p for p in self.pkgManagers if p.name == named][0]
        else:
            for pkgm in self.pkgManagers:
                p = subprocess.run(["command", "-v", pkgm.name])
                if p.returncode == 0:
                    return pkgm
            return Packagemanager("", [], [])

    def __getAppInstallation__(self, app) -> list[str]:
        # native, flatpak, custom
        type = app["type"]
        installationMethod: list[str] = []
        if type is None:
            Exception("Error, there is not type for %s", app)

        if type == "native":
            installationMethod += "sudo"
            pkgmanager = self.__find_pkgmanager__()
            installationMethod += [pkgmanager.name, *pkgmanager.installArgs]
            installationMethod += [app["name"]]
        elif type == "flatpak":
            pkgmanager = self.__find_pkgmanager__(type)
            installationMethod += [pkgmanager.name, *pkgmanager.installArgs]
            if app["upgrade"]:
                installationMethod += pkgmanager.upgradeArgs
            installationMethod += [app["name"]]
        elif type == "custom":
            installationMethod = [app["cmd"]]
        return installationMethod

    def install_applications(self):
        applications = self.myconfig["myjumpstarter"]["applications"]
        console.log("Will install these applications", applications)

        result = Confirm.ask("Do you want to proceed?", default="y")
        if not result:
            return 0
        else:
            with console.status("[bold green]Working on tasks... "):
                while applications:
                    app = applications.pop(0)
                    app_name = app["name"]

                    console.log("Check for", app_name)
                    p = subprocess.run(["command", "-v", app_name])
                    if p.returncode != 0:
                        console.log("Install", app_name)
                        installationMethod = self.__getAppInstallation__(app)
                        p = subprocess.run(installationMethod, shell=True)
                    else:
                        console.log(app_name, "is already installed.")

    def install_tools(self):
        tools = self.myconfig["myjumpstarter"]["tools"]
        console.log("Will install these tools", tools)

        result = Confirm.ask("Do you want to proceed?", default="y")
        if not result:
            return 0
        else:
            with console.status("[bold green]Working on tasks...") as status:
                while tools:
                    tool = tools.pop(0)
                    tool_name = tool["name"]
                    # Check if tool is already installed
                    console.log("Check for", tool_name)
                    p = subprocess.run(["command", "-v", tool_name])
                    if p.returncode != 0:
                        console.log("Install or upgrade", tool_name)
                        p = subprocess.run(tool["cmd"], shell=True, capture_output=True)
                        if p.stdout:
                            status.console.print(p.stdout.decode())
                        if p.stderr:
                            status.console.print("Error:", p.stderr.decode())
                    else:
                        console.log(tool_name, "is already installed.")

            console.print("Finished installing tools.")

    def upgrade_system(self):
        with console.status("[bold green] Upgrade system... ") as status:
            pkgm = self.__find_pkgmanager__()
            subprocess.run(["sudo", pkgm.name, *pkgm.upgradeArgs])
        console.print("Finished upgrade")

    def run(self):
        pretty.install()
        jumpstart = Jumpstart()

        while True:
            # Clear logs and show "splash"
            console.print()

            # Define actions
            installations = [
                Action("Tool", "install", "ti", jumpstart.install_tools),
                Action("Applications", "install", "ai", jumpstart.install_applications),
            ]
            system = [Action("System", "upgrade", "su", jumpstart.upgrade_system)]
            jumpstarter = [Action("Jumpstart", "Exit", "exit", lambda: sys.exit(0))]
            storage = [Action("Webdav", "create", "wc", None)]
            allActions = [installations, system, storage, jumpstarter]

            table = Table(show_header=True, header_style="bold")
            table.add_column("Group")
            table.add_column("Action")
            table.add_column("Id")
            table.add_column("Id")

            for a in allActions:
                for sa in a:
                    table.add_row(sa.group, sa.action, sa.id)

            mainlayout = Layout()
            menulayout = Layout(
                Panel(
                    "Let's Jumpstart :rocket:. Available options", title="MyJumpstarter"
                ),
                ratio=1,
            )
            actionlayout = Layout(table, ratio=3)
            mainlayout.split_column(menulayout, actionlayout)
            menu_console.print(table)

            # Still nasty to use ids.
            # Better to "enter" the group and have sub-actions to execute like "update", "delete", etc.
            choices = [b.id for a in allActions for b in a]
            userAction = Prompt.ask(
                "What do you want to do? Use the [bold cyan]id[/bold cyan]",
                choices=choices,
                default="exit",
            )
            action = [b for a in allActions for b in a if b.id == userAction][0]
            action.callback()
