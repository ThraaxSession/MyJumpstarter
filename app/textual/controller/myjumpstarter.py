#
# This scripts shall help developers to setup their dev environments easily or if you have a new awesome Linux PC and you need a jumpstart to setup the PC. ;)
#

import subprocess
import sys
from typing import Dict

import aiofiles
import yaml
from rich.console import Console
from rich.prompt import Confirm

from app.textual.models.myjumpstarter import Action, Packagemanager

console = Console()


class Jumpstart(object):
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
    config_path: str = ""

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Jumpstart, cls).__new__(cls)
        return cls.instance

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path

        try:
            with open(self.config_path, "r") as configfile:
                self.myconfig = yaml.safe_load(configfile)
        except Exception as e:
            console.log(f"Error reading config file: {e}")
            raise Exception("Cannot read config file")

    def __clear_screen(self):
        console.clear()

    def __find_pkgmanager(self, named: str = "") -> Packagemanager:
        if named != "":
            return [p for p in self.pkgManagers if p.name == named][0]
        else:
            for pkgm in self.pkgManagers:
                p = subprocess.run(
                    f"command -v {pkgm.name}", shell=True, capture_output=True
                )
                if p.returncode == 0:
                    return pkgm
            return Packagemanager("", [], [])

    def __getAppInstallation(self, app) -> list[str]:
        # native, flatpak, custom
        type = app["type"]
        installationMethod: list[str] = []
        if type is None:
            raise Exception("Error, there is no type for %s" % app["name"])

        if type == "native":
            installationMethod.append("sudo")
            pkgmanager = self.__find_pkgmanager()
            installationMethod += [pkgmanager.name, *pkgmanager.install_args]
            installationMethod += [app["name"]]
        elif type == "flatpak":
            pkgmanager = self.__find_pkgmanager(type)
            installationMethod += [pkgmanager.name, *pkgmanager.install_args]
            if app["upgrade"]:
                installationMethod += pkgmanager.upgrade_args
            installationMethod += [app["name"]]
        elif type == "custom":
            installationMethod = [app["cmd"]]
        return installationMethod

    async def load_config(self) -> Dict:
        async with aiofiles.open(self.config_path, "r") as configfile:
            content = await configfile.read()
            myconfig = yaml.safe_load(content)
            return myconfig

    def install_applications(self):
        self.__clear_screen()
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
                    p = subprocess.run(
                        f"command -v {app_name}", shell=True, capture_output=True
                    )
                    if p.returncode != 0:
                        console.log("Install", app_name)
                        installationMethod = self.__getAppInstallation(app)
                        p = subprocess.run(
                            installationMethod, shell=True, capture_output=True
                        )
                        if p.stderr is not None:
                            console.log(p.stderr.decode())
                        elif p.stdout is not None:
                            console.log(p.stdout.decode())
                    else:
                        console.log(app_name, "is already installed.")

    def run_tools(self):
        self.__clear_screen()
        tools = self.myconfig["receipts"]["tools"]
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
                    p_check_tool = subprocess.check_call(
                        ["/usr/bin/bash", "-c", tool_name]
                    )
                    console.log(f"Check too: {p_check_tool}")
                    if p_check_tool.returncode != 0:
                        install_log = f"Installing {tool_name}..."
                        status.update(install_log)
                        yield install_log

                        proc = subprocess.Popen(
                            tool["cmd"].split(" "),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        )
                        stdout, stderr = proc.communicate()
                        if stderr is not None:
                            console.log(stderr.decode())
                            yield stderr.decode()
                        elif stdout is not None:
                            console.log(stdout.decode())
                            yield stdout.decode()
                    else:
                        finished = f"{tool_name} is already installed."
                        status.update(finished)
                        yield finished

            finished_log = "Finished installing tools."
            console.log(finished_log)
            yield finished_log

    def upgrade_system(self):
        self.__clear_screen()
        with console.status("[bold green] Upgrade system... "):
            pkgm = self.__find_pkgmanager()
            try:
                proc_update = subprocess.Popen(
                    ["sudo", pkgm.name, "update"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, stderr = proc_update.communicate()
                for line in io.TextIOWrapper(stdout, encoding="utf-8"):
                    console.log(line)
                    yield line
                for line in io.TextIOWrapper(stderr, encoding="utf-8"):
                    console.log(line)
                    yield line

            except Exception as e:
                console.log("Error during update:", e)
                proc_upgrade = subprocess.Popen(
                    ["sudo", pkgm.name, *pkgm.upgrade_args],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, stderr = proc_upgrade.communicate()
                if stderr is not None:
                    console.log(stderr.decode())
                    yield stderr.decode()
                elif stdout is not None:
                    console.log(stdout.decode())
                    yield stdout.decode()

        console.print("Finished upgrade")

    def get_actions(self):
        # Define actions
        system = [Action("System", "Upgrade", "su", self.upgrade_system)]
        applications = [
            Action("Applications", "Install", "ai", self.install_applications)
        ]
        tools = [Action("Tools", "Run", "ti", self.run_tools)]
        jumpstarter = [Action("Jumpstart", "Exit", "exit", lambda: sys.exit(0))]
        storage = [Action("Storage", "Create", "wc", None)]
        actions = [system, applications, tools, storage, jumpstarter]

        return actions
