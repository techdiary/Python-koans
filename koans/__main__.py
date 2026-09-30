"""Allow `python -m koans start` as well as the `python-koans` command."""

from __future__ import annotations

import sys

from koans.cli import main

if __name__ == "__main__":
    sys.exit(main())
