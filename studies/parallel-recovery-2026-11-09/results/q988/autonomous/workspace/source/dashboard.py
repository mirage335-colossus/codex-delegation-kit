import argparse
import json
import sys
from pathlib import Path
from .loader import SnapshotLoader
from .select import build_dashboard

def main(argv=None):
    parser = argparse.ArgumentParser(description="Display latest deployment per service")
    parser.add_argument("--input", required=True, help="directory containing service snapshots")
    args = parser.parse_args(argv)
    root = Path(args.input)
    loader = SnapshotLoader()
    try:
        snapshots = [loader.load(path) for path in sorted(root.glob("*.json"))]
        if not snapshots:
            raise ValueError("no service snapshots found")
        json.dump(build_dashboard(snapshots), sys.stdout, sort_keys=True)
        sys.stdout.write("\n")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
