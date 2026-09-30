"""Walk the koans in lesson order. Stop at the first failure.

Prefer `python-koans start`. It runs the same walk from any directory.
"""

from __future__ import annotations

import sys

from koans.catalog import KOAN_MODULES
from koans.runner import run_path


def main() -> int:
    return run_path(KOAN_MODULES)


if __name__ == "__main__":
    sys.exit(main())
