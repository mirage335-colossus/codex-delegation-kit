import argparse
import json
import sys
from .csvio import read_expenses
from .legacy import compact_export

def main(argv=None):
    parser = argparse.ArgumentParser(description="Create the monthly finance export")
    parser.add_argument("--input", required=True)
    parser.add_argument("--month", required=True)
    args = parser.parse_args(argv)
    try:
        rows = read_expenses(args.input, warn=lambda message: print(message, file=sys.stderr))
        # Keep the legacy plug-in output shape used by older callers.
        result = compact_export(rows, args.month)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    json.dump(result, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
