#
# This scripts shall help developers to setup their dev environments easily or if you have a new awesome Linux PC and you need a jumpstart to setup the PC. ;)
#

import subprocess
import sys
from typing import Dict

from app.textual.models.myjumpstarter import Action, Packagemanager

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

    myconfig: dict = {}
    config_path: str = "config.yaml"

    def __init__(self):
        # TODO add error handling
        with open(self.config_path, "r") as configfile:
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
            raise Exception("Error, there is no type for %s" % app["name"])

        if type == "native":
            installationMethod.append("sudo")
            pkgmanager = self.__find_pkgmanager__()
            installationMethod += [pkgmanager.name, *pkgmanager.install_args]
            installationMethod += [app["name"]]
        elif type == "flatpak":
            pkgmanager = self.__find_pkgmanager__(type)
            installationMethod += [pkgmanager.name, *pkgmanager.install_args]
            if app["upgrade"]:
                installationMethod += pkgmanager.upgrade_args
            installationMethod += [app["name"]]
        elif type == "custom":
            installationMethod = [app["cmd"]]
        return installationMethod

    def load_config(self) -> Dict:
        with open(self.config_path, "r") as configfile:
            myconfig = yaml.safe_load(configfile)
            return myconfig

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
                        p = subprocess.run(installationMethod)
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
        with console.status("[bold green] Upgrade system... "):
            pkgm = self.__find_pkgmanager__()
            subprocess.run(["sudo", pkgm.name, *pkgm.upgrade_args])
        console.print("Finished upgrade")

    def get_actions(self):
        # Define actions
        installations = [
            Action("Tool", "install", "ti", self.install_tools),
            Action("Applications", "install", "ai", self.install_applications),
        ]
        system = [Action("System", "upgrade", "su", self.upgrade_system)]
        jumpstarter = [Action("Jumpstart", "Exit", "exit", lambda: sys.exit(0))]
        storage = [Action("Webdav", "create", "wc", None)]
        actions = [installations, system, storage, jumpstarter]

        return actions
