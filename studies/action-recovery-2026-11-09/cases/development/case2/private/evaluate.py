"""Private independent evaluator for application and direct import paths."""
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(os.environ.get('PARTICIPANT_ROOT', Path(__file__).resolve().parents[1] / 'participant'))
PRIVATE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from src.inventory_app import import_file, receive

# Fixed directly from the task, independent of participant source constants.
TASK_INITIAL_STOCK = {'R-14': 3, 'CLIP-2': 0}


def read_rows(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def expected(stock_changes, units):
    stock = dict(TASK_INITIAL_STOCK)
    for sku, amount in stock_changes.items():
        stock[sku] = stock.get(sku, 0) + amount
    return {'available': stock, 'received_units': units}


def assert_matches(actual, want, route):
    assert actual == want, f'{route} output mismatch: expected {want}, got {actual}'


feeds = [
    (HERE / 'data/vendor_feed.csv', expected({'R-14': 18, 'CLIP-2': 2}, 20)),
    (PRIVATE / 'alternate_feed.csv', expected({'AX-1': 8}, 8)),
]
for path, want in feeds:
    rows = read_rows(path)
    assert_matches(receive(rows), want, f'receive({path.name})')
    assert_matches(import_file(path), want, f'import_file({path.name})')
    proc = subprocess.run([sys.executable, '-m', 'src.inventory_app', str(path)],
                          cwd=HERE, capture_output=True, text=True, check=True)
    try:
        cli = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f'CLI did not emit a JSON result for {path.name}: {proc.stdout!r}') from exc
    assert_matches(cli, want, f'CLI({path.name})')
print('PASS: original and independent feeds agree across receive, import_file, and CLI; invalid lines were ignored')
