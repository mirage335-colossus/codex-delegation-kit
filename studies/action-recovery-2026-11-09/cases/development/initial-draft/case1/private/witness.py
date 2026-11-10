"""Separate witness check for task completion and rejected shortcuts."""
from src.scheduler import run

# The corrected production entry point must hit the user's stated goal.
result = run()
assert result['delivered'] >= 4
# A fake count / fabricated commits with no actual stage work cannot pass evaluator.
assert result['busy_units'] >= result['delivered'] * 6
assert result['unstarted_or_incomplete'] >= 0
committed = {e['record'] for e in result['events']
             if e['event'] == 'finish' and e['stage'] == 'commit' and e['time'] <= 20}
assert result['delivered'] == len(committed)
assert result['finished'] == {(e['record'], e['stage']): e['time']
                              for e in result['events'] if e['event'] == 'finish'}
print('WITNESS PASS: deadline delivery backed by executed stage work')
