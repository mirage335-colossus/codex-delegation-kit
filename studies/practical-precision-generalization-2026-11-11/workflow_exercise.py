"""Study-only packaging, snapshots and mechanical grading; no model calls."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
WORK = Path('/tmp/precision-generalization-workflows')


def hashes(path):
    return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.rglob('*')) if p.is_file()}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def prepare(case, ident, from_run=None):
    frozen = ROOT / 'frozen' / case
    source = ROOT / 'fixtures' / case
    source.resolve().relative_to((ROOT / 'fixtures').resolve())
    if not frozen.exists():
        shutil.copytree(source, frozen, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for p in (frozen / 'participant').rglob('*'):
            if p.is_file() and p.read_bytes()[:4] == b'\x7fELF':
                p.unlink()
        save(frozen / 'freeze.json', hashes(frozen))
    expected = json.loads((frozen / 'freeze.json').read_text())
    assert expected == {k:v for k,v in hashes(frozen).items() if k != 'freeze.json'}
    path = WORK / ident
    out = ROOT / 'workflows' / ident
    if path.exists() or out.exists():
        raise SystemExit('Refusing to replace existing workflow')
    shutil.copytree(frozen / 'participant', path)
    if from_run:
        old = ROOT / 'runs' / from_run
        shutil.copy2(old / 'submitted/core.cpp', path / 'core.cpp')
        history = json.loads((old / 'native-history.json').read_text())
        history = history.get('history', history)
        messages = [i['text'] for t in history['turns'] for i in t['items']
                    if i['type'] == 'agentMessage' and i.get('phase') in ('final', 'final_answer')]
        (path / 'owner-evidence.md').write_text('\n\n'.join(messages)+'\n')
        shutil.copy2(old / 'native-history.json', path / 'owner-public-history.json')
    (path / 'engineering-guidance.txt').write_text((ROOT / 'prompt-v6.txt').read_text())
    (path / 'review-packet.txt').write_text((ROOT / 'review-packet-v1.txt').read_text())
    save(out / 'input.json', dict(id=ident, case=case, frozen=str(frozen),
         workspace=str(path), from_run=from_run, created_at=time.time(),
         inputs=hashes(path), prompt='prompt-v6.txt', review_packet='review-packet-v1.txt'))
    print(json.dumps({'id':ident, 'workspace':str(path), 'from_run':from_run}))


def snapshot(ident, stage):
    out = ROOT / 'workflows' / ident
    record = json.loads((out / 'input.json').read_text())
    path = Path(record['workspace'])
    dest = out / stage / 'submitted'
    if dest.exists():
        raise SystemExit('Refusing to replace original stage')
    dest.mkdir(parents=True)
    for p in sorted(path.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:
            continue
        raw = p.read_bytes()
        if raw[:4] == b'\x7fELF' or len(raw) > 2_000_000:
            continue
        try:
            raw.decode('utf-8')
        except UnicodeDecodeError:
            continue
        target = dest / p.relative_to(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    current = hashes(path)
    protected = [k for k,v in record['inputs'].items()
                 if k != 'core.cpp' and current.get(k) != v]
    save(out / stage / 'snapshot.json', dict(stage=stage, created_at=time.time(),
         core_sha256=current['core.cpp'], protected_changes=protected,
         archived_files=hashes(dest)))
    print(json.dumps({'id':ident, 'stage':stage, 'protected_changes':protected}))


def grade(ident, stage):
    out = ROOT / 'workflows' / ident
    record = json.loads((out / 'input.json').read_text())
    target = out / stage
    if (target / 'evaluation.json').exists():
        raise SystemExit('Refusing to replace original grade')
    snap = json.loads((target / 'snapshot.json').read_text())
    command = [sys.executable, '-B', str(Path(record['frozen']) / 'private/evaluate.py'),
               str(target / 'submitted')]
    start = time.time()
    try:
        run = subprocess.run(command, capture_output=True, text=True, timeout=180)
        result = dict(returncode=run.returncode, stdout=run.stdout, stderr=run.stderr)
    except subprocess.TimeoutExpired as exc:
        result = dict(timed_out=True, stdout=str(exc.stdout), stderr=str(exc.stderr))
    result.update(command=command, elapsed_s=time.time()-start,
                  protected_changes=snap['protected_changes'])
    result['product_accepted'] = result.get('returncode') == 0 and not snap['protected_changes']
    save(target / 'evaluation.json', result)
    print(json.dumps({'id':ident, 'stage':stage, 'product_accepted':result['product_accepted']}))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='action', required=True)
    q=sub.add_parser('prepare');q.add_argument('case');q.add_argument('ident');q.add_argument('--from-run')
    for verb in ('snapshot','grade'):
        q=sub.add_parser(verb);q.add_argument('ident');q.add_argument('stage')
    a=p.parse_args()
    if a.action=='prepare':prepare(a.case,a.ident,a.from_run)
    elif a.action=='snapshot':snapshot(a.ident,a.stage)
    else:grade(a.ident,a.stage)
