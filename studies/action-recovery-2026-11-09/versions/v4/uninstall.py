#!/usr/bin/env python3
"""Disable global delegation without deleting retained bundle or evidence."""

import sys

from install import main


if __name__ == "__main__":
    raise SystemExit(main(["--uninstall", *sys.argv[1:]]))
