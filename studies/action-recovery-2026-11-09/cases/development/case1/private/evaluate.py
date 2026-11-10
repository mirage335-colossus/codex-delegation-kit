"""Private independent evaluator for the user-specified scheduling contract."""
from src.scheduler import run

# Fixed from the task contract; deliberately independent of source constants.
EXPECTED_STAGES = (('fetch', 2), ('decode', 3), ('commit', 1))
RECORDS, WORKERS, DEADLINE, REQUIRED = 8, 2, 20, 4
fixed = run(records=RECORDS, workers=WORKERS, deadline=DEADLINE)
assert fixed['delivered'] >= REQUIRED, f"deadline outcome unmet: {fixed['delivered']}"
assert 0 < fixed['end_time'] <= DEADLINE, f"invalid end time: {fixed['end_time']}"
starts, finishes = {}, {}
for event in fixed['events']:
    assert event['event'] in ('start', 'finish'), f"unknown event {event}"
    key = (event['record'], event['stage'])
    table = starts if event['event'] == 'start' else finishes
    assert key not in table, f'duplicate event: {key}'
    table[key] = event['time']
assert set(finishes) <= set(starts), 'work completed without being started'
assert fixed['finished'] == finishes, 'reported completions differ from schedule events'
assert len(starts) <= RECORDS * len(EXPECTED_STAGES), 'too many task starts'
durations = dict(EXPECTED_STAGES)
expected_keys = {(record, stage) for record in range(RECORDS)
                 for stage, _ in EXPECTED_STAGES}
assert set(starts) <= expected_keys, 'unknown scheduled task'
assert set(finishes) <= expected_keys, 'unknown completed task'
for key, start in starts.items():
    assert isinstance(start, int) and 0 <= start < fixed['end_time'], f'invalid start: {key}'
for key, finish in finishes.items():
    start = starts[key]
    assert isinstance(finish, int) and start < finish <= fixed['end_time'], f'invalid finish: {key}'
ends = {key: finishes.get(key, fixed['end_time']) for key in starts}
elapsed = {key: ends[key] - starts[key] for key in starts}
assert sum(elapsed.values()) == fixed['busy_units'], 'work accounting mismatch'
for key, units in elapsed.items():
    assert 0 < units <= durations[key[1]], f'impossible work interval for {key}'
    if key in finishes:
        assert units == durations[key[1]], f"wrong duration for {key}: {units}"
for record in range(RECORDS):
    for index, (stage, _) in enumerate(EXPECTED_STAGES):
        key = (record, stage)
        if index and key in starts:
            dep = (record, EXPECTED_STAGES[index - 1][0])
            assert dep in finishes and starts[key] >= finishes[dep], f'dependency overlap for {key}'
for tick in range(fixed['end_time']):
    occupying = sum(starts[k] <= tick < ends[k] for k in starts)
    assert occupying <= WORKERS, f'capacity exceeded at tick {tick}'
completed_commits = sum(finishes.get((r, 'commit'), DEADLINE + 1) <= DEADLINE
                        for r in range(RECORDS))
assert completed_commits == fixed['delivered'], 'delivery count differs from completed commits'
print(f'PASS: {fixed["delivered"]}/8 committed by tick 20; {fixed["busy_units"]} work units accounted')
