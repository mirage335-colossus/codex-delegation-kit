"""Original checks: inputs must be fully accounted for and dependencies ordered."""
import unittest
from src.scheduler import STAGES, run


class OriginalChecks(unittest.TestCase):
    def test_total_work_is_not_lost(self):
        result = run(records=5, deadline=60)
        self.assertEqual(result['busy_units'], 5 * sum(d for _, d in STAGES))
        self.assertEqual(result['delivered'], 5)

    def test_each_completion_follows_its_dependency(self):
        result = run(records=5, deadline=60)
        end = result['finished']
        for r in range(5):
            for i in range(1, len(STAGES)):
                before = end[(r, STAGES[i-1][0])]
                after = end[(r, STAGES[i][0])]
                self.assertLessEqual(before, after)

    def test_no_more_workers_than_capacity(self):
        result = run(records=8, deadline=60, workers=2)
        active = set()
        for e in result['events']:
            key = (e['record'], e['stage'])
            if e['event'] == 'start':
                active.add(key)
                self.assertLessEqual(len(active), 2)
            else:
                active.remove(key)

if __name__ == '__main__':
    unittest.main()
