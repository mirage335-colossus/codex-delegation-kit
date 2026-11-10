"""Deterministic three-stage scheduler used by the exercise."""
from collections import deque

STAGES = (('fetch', 2), ('decode', 3), ('commit', 1))


def run(records=8, workers=2, deadline=20):
    """Execute records under the original stage-wide barrier scheduler.

    Each record's stage N+1 depends on completion of stage N. A task consumes
    one worker unit per tick and remains on that worker until it finishes.
    """
    remaining = {(r, stage): duration for r in range(records)
                 for stage, duration in STAGES}
    finished, active, events = {}, {}, []
    busy = time = wave = 0
    while (remaining or active) and time < deadline:
        stage = STAGES[wave][0]
        candidates = [(r, stage) for r in range(records)
                      if (r, stage) in remaining and (r, stage) not in active]
        for key in candidates:
            if len(active) >= workers:
                break
            active[key] = remaining.pop(key)
            events.append({'event': 'start', 'record': key[0], 'stage': key[1], 'time': time})
        done = []
        for key in list(active):
            active[key] -= 1
            busy += 1
            if active[key] == 0:
                done.append(key)
        time += 1
        for key in done:
            del active[key]
            finished[key] = time
            events.append({'event': 'finish', 'record': key[0], 'stage': key[1], 'time': time})
        if not active and not any(k[1] == stage for k in remaining):
            wave = min(wave + 1, len(STAGES) - 1)
    delivered = sum(finished.get((r, 'commit'), deadline + 1) <= deadline
                    for r in range(records))
    return {'records': records, 'workers': workers, 'deadline': deadline,
            'busy_units': busy, 'finished': finished, 'events': events,
            'delivered': delivered, 'end_time': time,
            'unstarted_or_incomplete': len(remaining) + len(active)}
