#!/usr/bin/env python3
"""Discover and disable the applicable DK installation; retain runtime and evidence."""

import sys

from install import main


if __name__ == "__main__":
    raise SystemExit(main(["--uninstall", *sys.argv[1:]]))
