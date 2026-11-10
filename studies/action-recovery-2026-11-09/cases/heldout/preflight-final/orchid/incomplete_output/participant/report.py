import argparse
import json
from pathlib import Path
from telemetry.reduce import summarize

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent
config = json.loads((root / "config.json").read_text())
report = summarize(root / args.input, config["max_live_rows"])
output = root / args.output
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report["audit"], sort_keys=True))
