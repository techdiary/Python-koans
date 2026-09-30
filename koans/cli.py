"""`python-koans start` continues the path from any working directory."""

from __future__ import annotations

import sys

from cleo.application import Application
from cleo.commands.command import Command
from cleo.io.inputs.option import Option

from koans.catalog import KOAN_MODULES
from koans.progress import lesson_rows, restart_journey, write_lesson_list
from koans.runner import open_output, run_path


class StartCommand(Command):
    name = "start"
    description = "Continue from the first unfinished koan."
    help = (
        "Walk the lessons in order and stop at the first failure. "
        "The command uses the installed package, so the working directory does not matter. "
        "Pass --restart to overwrite the lessons from the pristine copy and begin again."
    )
    options = [
        Option(
            "restart",
            flag=True,
            description="Reset the working lessons to the first koan, then start.",
        )
    ]

    def handle(self) -> int:
        if self.option("restart"):
            restart_journey()
            open_output(sys.stdout).write_line("<comment>Journey reset.</comment>")
        return run_path(KOAN_MODULES)


class ListCommand(Command):
    name = "list"
    description = "Show the path and which lessons are finished."

    def handle(self) -> int:
        write_lesson_list(open_output(sys.stdout), lesson_rows())
        return 0


def main() -> int:
    application = Application("python-koans", "0.1.0")
    application.auto_exits(False)
    application._init()
    application.add(StartCommand())
    application.add(ListCommand())
    return application.run()


if __name__ == "__main__":
    sys.exit(main())
