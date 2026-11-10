"""Independent witness: combines stable legacy behavior with actual CLI output."""
import json
import os
import subprocess
import sys
from pathlib import Path
from src.inventory_app import normalize_vendor_feed, receive

HERE = Path(os.environ.get('PARTICIPANT_ROOT', Path(__file__).resolve().parents[1] / 'participant'))
legacy = receive([{'sku': 'R-14', 'quantity': '4'}])
assert legacy['available']['R-14'] == 7 and legacy['received_units'] == 4
rows = [{'part_code': 'R-14', 'units': '8', 'shipment_ref': 'A'},
        {'part_code': 'R-14', 'units': '-4', 'shipment_ref': 'A'}]
assert normalize_vendor_feed(rows) == [{'sku': 'R-14', 'quantity': 8, 'reference': 'A'}]
p = subprocess.run([sys.executable, '-m', 'src.inventory_app', 'data/vendor_feed.csv'],
                   cwd=HERE, capture_output=True, text=True, check=True)
out = json.loads(p.stdout)
assert out['available'] == {'CLIP-2': 2, 'R-14': 21}
assert out['received_units'] == 20
print('WITNESS PASS: helper behavior, legacy input and user-facing import all agree')
