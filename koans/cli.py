"""`python-koans start` continues the path from any working directory."""

from __future__ import annotations

import sys

from cleo.application import Application
from cleo.commands.command import Command
from cleo.io.inputs.option import Option

from koans.catalog import KOAN_MODULES
from koans.progress import lesson_rows, restart_journey, write_lesson_list
from koans.prompt import is_terminal, offer_fill
from koans.runner import (
    classify_stop,
    failing_lineno,
    hint_in,
    hint_on,
    message_of,
    open_output,
    run_journey,
    source_path,
)


class StartCommand(Command):
    name = "start"
    description = "Continue from the first unfinished koan."
    help = (
        "Walk the lessons in order and stop at the first failure. "
        "In a terminal, show that test and ask for each blank, then run again. "
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
        return continue_journey(KOAN_MODULES)


def continue_journey(module_names: list[str]) -> int:
    """Run the path. On a terminal, fill the failing test and run it again."""
    reload_modules = False
    while True:
        stop = run_journey(module_names, reload_modules=reload_modules)
        if stop.code == 0 or stop.test is None or stop.err is None:
            return stop.code
        if not is_terminal(sys.stdin, sys.stdout):
            return stop.code
        wrote = offer_fill(
            source_path(stop.test),
            getattr(stop.test, "_testMethodName", ""),
            kind=classify_stop(stop.err),
            failing_lineno=failing_lineno(stop.test, stop.err),
            hint=hint_on(stop.test) or hint_in(message_of(stop.err)),
            stdin=sys.stdin,
            output=open_output(sys.stdout),
        )
        if not wrote:
            return stop.code
        reload_modules = True


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
