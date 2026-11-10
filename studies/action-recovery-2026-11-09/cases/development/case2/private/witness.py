"""Independent witness over an evaluator-private alternate supplier feed."""
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(os.environ.get('PARTICIPANT_ROOT', Path(__file__).resolve().parents[1] / 'participant'))
FEED = Path(__file__).resolve().parent / 'alternate_feed.csv'
sys.path.insert(0, str(HERE))
from src.inventory_app import import_file, receive

with FEED.open(newline='', encoding='utf-8') as stream:
    rows = list(csv.DictReader(stream))
expected = {'available': {'R-14': 3, 'CLIP-2': 0, 'AX-1': 8}, 'received_units': 8}
assert receive(rows) == expected
assert import_file(FEED) == expected
proc = subprocess.run([sys.executable, '-m', 'src.inventory_app', str(FEED)],
                      cwd=HERE, capture_output=True, text=True, check=True)
assert json.loads(proc.stdout) == expected
print('WITNESS PASS: independent feed reaches inventory through both import entry points')
