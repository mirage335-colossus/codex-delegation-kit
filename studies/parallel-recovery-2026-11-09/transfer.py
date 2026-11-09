"""Reuse the frozen-copy and grading mechanics for the separate replay."""
import json
import sys
import exercise

exercise.plan = lambda: json.loads((exercise.HERE / 'freeze' / 'transfer-plan.json').read_text())
exercise.CASES['P1'] = '/tmp/recovery-projection-transfer'

if __name__ == '__main__':
    if sys.argv[1] == 'prepare':
        exercise.prepare('P1')
    elif sys.argv[1] == 'grade':
        exercise.grade(sys.argv[2], 'autonomous')
    else:
        raise SystemExit('prepare | grade OWNER_ID')
