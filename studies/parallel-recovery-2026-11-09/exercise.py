"""Prepare frozen native-agent exercises and independently grade copied results."""
import argparse
import hashlib
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = Path('/tmp/delegation-recovery-runs')
CASES = {'A1': '/tmp/recovery-fixtures-a/A1',
         'A2': '/tmp/recovery-fixtures-a/A2',
         'B1': '/tmp/recovery-fixtures-b/B1',
         'B2': '/tmp/recovery-fixtures-b/B2'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def plan():
    path = HERE / 'freeze' / 'plan.json'
    if path.exists():
        return json.loads(path.read_text())
    rng = random.Random(1729)
    ids = rng.sample(range(100, 999), 16)
    entries = []
    for case in CASES:
        arms = [('baseline', 'sequential'), ('baseline', 'parallel'),
                ('candidate', 'sequential'), ('candidate', 'parallel')]
        rng.shuffle(arms)
        for prompt, schedule in arms:
            entries.append(dict(id=f'q{ids.pop()}', case=case,
                                prompt=prompt, schedule=schedule))
    write_json(path, entries)
    return entries


def prepare(case):
    fixture = Path(CASES[case])
    source = fixture / 'participant' if (fixture / 'participant').is_dir() else fixture
    frozen = HERE / 'freeze' / 'cases' / case
    if frozen.exists():
        raise SystemExit('Already frozen; refusing to replace case')
    participant = frozen / 'participant'
    participant.mkdir(parents=True)
    for p in source.rglob('*'):
        rel = p.relative_to(source)
        if not p.is_file() or '__pycache__' in rel.parts:
            continue
        if rel.name in {'evaluator.py', 'oracle.md'} or p.suffix in {'.out', '.log', '.patch'}:
            continue
        if rel.parts[0] not in {'source', 'tools', 'tests', 'fixturedata'} and not (len(rel.parts) == 1 and (p.suffix == '.py' or rel.name == 'task.md')):
            continue
        target = participant / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
    shutil.copy2(fixture / 'evaluator.py', frozen / 'evaluator.py')
    shutil.copy2(fixture / 'oracle.md', frozen / 'oracle.md')
    manifest = {str(p.relative_to(frozen)): digest(p) for p in frozen.rglob('*') if p.is_file()}
    write_json(frozen / 'manifest.json', manifest)
    for row in plan():
        if row['case'] != case:
            continue
        run = RUNS / row['id']
        if run.exists():
            raise SystemExit(f'Run already exists: {run}')
        shutil.copytree(participant, run / 'workspace')
        (run / 'results').mkdir()
        shutil.copy2(HERE / 'freeze' / (row['prompt'] + '.txt'), run / 'guidance.txt')
    print(json.dumps([x for x in plan() if x['case'] == case]))


def grade(ident, stage):
    row = next(x for x in plan() if x['id'] == ident)
    frozen = HERE / 'freeze' / 'cases' / row['case']
    workspace = RUNS / ident / 'workspace'
    out = HERE / 'results' / ident / stage
    if out.exists():
        raise SystemExit('Refusing to overwrite a sealed outcome')
    out.mkdir(parents=True)
    shutil.copytree(workspace, out / 'workspace')
    original = frozen / 'participant'
    protected = [p for p in original.rglob('*') if p.is_file() and
                 ((row['case'] == 'P1' and str(p.relative_to(original)) != 'tools/triad_dynamic_joint.py') or
                  'tests' in p.relative_to(original).parts or p.name in {'public_tests.py', 'task.md'} or
                  'fixturedata' in p.relative_to(original).parts)]
    changed = [str(p.relative_to(original)) for p in protected
               if not (workspace / p.relative_to(original)).exists() or
               digest(p) != digest(workspace / p.relative_to(original))]
    scratch = out / 'evaluation'
    shutil.copytree(workspace, scratch)
    shutil.copy2(frozen / 'evaluator.py', scratch / 'evaluator.py')
    interpreter = '/tmp/pumpmodem-cleanup-venv/bin/python' if row['case'] == 'P1' else sys.executable
    commands = [[interpreter, '-B', 'evaluator.py']]
    if row['case'] == 'P1':
        commands.append([interpreter, '-B', '-m', 'unittest',
                         'test_triad_incremental_receiver.IncrementalReceiverTests.test_batch_equivalence_dft_static_and_ou'])
    elif (scratch / 'public_tests.py').exists():
        commands.append([sys.executable, '-B', 'public_tests.py'])
    else:
        commands.append([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests'])
    results = []
    for command in commands:
        try:
            cwd = scratch / 'tests' if row['case'] == 'P1' and '-m' in command else scratch
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=60)
            results.append(dict(command=command, returncode=result.returncode,
                                stdout=result.stdout, stderr=result.stderr))
        except subprocess.TimeoutExpired as exc:
            results.append(dict(command=command, timeout=True, stdout=str(exc.stdout), stderr=str(exc.stderr)))
    accepted = not changed and all(x.get('returncode') == 0 for x in results)
    write_json(out / 'grade.json', dict(id=ident, case=row['case'], stage=stage,
               accepted=accepted, protected_changes=changed, checks=results))
    patches = subprocess.run(['diff', '-ru', str(original), str(workspace)], capture_output=True, text=True)
    (out / 'patch.diff').write_text(patches.stdout)
    if (RUNS / ident / 'results').exists():
        shutil.copytree(RUNS / ident / 'results', out / 'owner-results')
    print(json.dumps(dict(id=ident, case=row['case'], stage=stage, accepted=accepted,
                          protected_changes=changed)))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='command', required=True)
    prepare_p = sub.add_parser('prepare'); prepare_p.add_argument('case', choices=CASES)
    grade_p = sub.add_parser('grade'); grade_p.add_argument('id'); grade_p.add_argument('--stage', default='autonomous')
    sub.add_parser('plan')
    args = p.parse_args()
    if args.command == 'prepare':
        prepare(args.case)
    elif args.command == 'grade':
        grade(args.id, args.stage)
    else:
        print(json.dumps(plan(), indent=2))
