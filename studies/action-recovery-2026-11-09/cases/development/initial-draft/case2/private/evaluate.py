"""Independent user-outcome oracle; assesses the supported CLI process."""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(os.environ.get('PARTICIPANT_ROOT', Path(__file__).resolve().parents[1] / 'participant'))
CMD = [sys.executable, '-m', 'src.inventory_app', 'data/vendor_feed.csv']
proc = subprocess.run(CMD, cwd=HERE, text=True, capture_output=True, check=True)
result = json.loads(proc.stdout)
assert result['available'].get('R-14') == 21, result
assert result['available'].get('CLIP-2') == 2, result
assert result['received_units'] == 20, result
print('PASS: application CLI imported both valid supplier lines; invalid lines had no effect')
