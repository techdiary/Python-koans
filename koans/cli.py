"""`python-koans start` continues the path from any working directory."""

from __future__ import annotations

import sys

from cleo.application import Application
from cleo.commands.command import Command

from koans.catalog import KOAN_MODULES
from koans.runner import run_path


class StartCommand(Command):
    name = "start"
    description = "Continue from the first unfinished koan."
    help = (
        "Walk the lessons in order and stop at the first failure. "
        "The command uses the installed package, so the working directory does not matter."
    )

    def handle(self) -> int:
        return run_path(KOAN_MODULES)


def main() -> int:
    application = Application("python-koans", "0.1.0")
    application.auto_exits(False)
    application.add(StartCommand())
    return application.run()


if __name__ == "__main__":
    sys.exit(main())
