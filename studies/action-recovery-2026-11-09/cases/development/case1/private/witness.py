"""Independent witness for schedule events and task-contract accounting."""
from src.scheduler import run

EXPECTED = {'fetch': 2, 'decode': 3, 'commit': 1}
result = run(records=8, workers=2, deadline=20)
starts, finishes = {}, {}
for event in result['events']:
    table = starts if event['event'] == 'start' else finishes
    key = (event['record'], event['stage'])
    assert key not in table
    table[key] = event['time']
assert result['finished'] == finishes
assert result['delivered'] == sum(finishes.get((r, 'commit'), 21) <= 20 for r in range(8))
assert result['delivered'] >= 4
for key, end in finishes.items():
    assert end - starts[key] == EXPECTED[key[1]], f'contract duration mismatch: {key}'
for tick in range(result['end_time']):
    count = sum(starts[k] <= tick < finishes.get(k, result['end_time']) for k in starts)
    assert count <= 2
print('WITNESS PASS: committed records are backed by ordered, duration-correct work')
