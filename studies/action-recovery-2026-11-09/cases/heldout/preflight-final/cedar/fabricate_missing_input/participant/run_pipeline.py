import argparse
import json
from pathlib import Path
from pipeline.dispatcher import run

parser = argparse.ArgumentParser()
parser.add_argument("--plan", required=True)
parser.add_argument("--state", required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent
summary = run(json.loads((root / args.plan).read_text()), root, root / args.state)
print(json.dumps(summary, sort_keys=True))
raise SystemExit(2 if summary["status"] == "blocked" else 0)
