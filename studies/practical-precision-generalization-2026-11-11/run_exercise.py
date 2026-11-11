"""Local native-agent fixture packaging and outcome retention; no model calls."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
RUNS = Path('/tmp/precision-generalization-runs')


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + '\n')


def prepare(case, ident, prompt, wave):
    source = (ROOT / 'fixtures' / case).resolve()
    source.relative_to(ROOT / 'fixtures')
    frozen = ROOT / 'frozen' / case
    if not frozen.exists():
        shutil.copytree(source, frozen, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        # Public checks may have generated a probe during author preflight. Such
        # build outputs are not immutable participant inputs.
        for p in (frozen / 'participant').rglob('*'):
            if p.is_file() and p.read_bytes()[:4] == b'\x7fELF':
                p.unlink()
        save(frozen / 'freeze.json', hashes(frozen))
    else:
        expected = json.loads((frozen / 'freeze.json').read_text())
        assert expected == {k: v for k, v in hashes(frozen).items() if k != 'freeze.json'}
    run = RUNS / ident
    if run.exists():
        raise SystemExit('Existing run will not be replaced: ' + str(run))
    shutil.copytree(frozen / 'participant', run)
    text = (ROOT / prompt).read_text()
    (run / 'engineering-guidance.txt').write_text(text)
    record = dict(id=ident, case=case, wave=wave, prompt=prompt,
                  prompt_sha256=hashlib.sha256(text.encode()).hexdigest(),
                  workspace=str(run), frozen=str(frozen), inputs=hashes(run),
                  created_at=time.time())
    save(ROOT / 'runs' / ident / 'input.json', record)
    print(json.dumps(record))


def grade(ident):
    out = ROOT / 'runs' / ident
    if (out / 'evaluation.json').exists():
        raise SystemExit('Refusing to replace original result')
    record = json.loads((out / 'input.json').read_text())
    run = Path(record['workspace'])
    protected = {k: v for k, v in record['inputs'].items() if k != 'core.cpp'}
    now = hashes(run)
    violations = [k for k, v in protected.items() if now.get(k) != v]
    # Archive original public files and actual patched core, not compiled binaries.
    snapshot = out / 'submitted'
    snapshot.mkdir()
    for name in record['inputs']:
        if (run / name).is_file():
            dest = snapshot / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(run / name, dest)
    extra_checks = [p for p in run.glob('*') if p.is_file() and p.name not in record['inputs']
                    and p.suffix in {'.py', '.md', '.txt', '.sh', '.json'} and p.stat().st_size < 100_000]
    for p in extra_checks:
        shutil.copy2(p, snapshot / p.name)
    evaluator = Path(record['frozen']) / 'private' / 'evaluate.py'
    command = [sys.executable, '-B', str(evaluator), str(snapshot)]
    started = time.time()
    try:
        r = subprocess.run(command, capture_output=True, text=True, timeout=120)
        result = dict(command=command, returncode=r.returncode, stdout=r.stdout, stderr=r.stderr)
    except subprocess.TimeoutExpired as exc:
        result = dict(command=command, timed_out=True, stdout=str(exc.stdout), stderr=str(exc.stderr))
    result.update(id=ident, case=record['case'], elapsed_s=time.time()-started,
                  protected_changes=violations, core_changed=now.get('core.cpp') != record['inputs'].get('core.cpp'))
    result['accepted'] = (result.get('returncode') == 0 and not violations and result['core_changed'])
    save(out / 'evaluation.json', result)
    diff = subprocess.run(['diff', '-u', str(Path(record['frozen']) / 'participant' / 'core.cpp'),
                           str(snapshot / 'core.cpp')], capture_output=True, text=True)
    (out / 'patch.diff').write_text(diff.stdout)
    print(json.dumps({k: result[k] for k in ('id', 'case', 'accepted', 'protected_changes', 'elapsed_s')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='action', required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('case'); prep.add_argument('id'); prep.add_argument('--prompt', default='prompt-v1.txt')
    prep.add_argument('--wave', required=True)
    grd = sub.add_parser('grade'); grd.add_argument('id')
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare(args.case, args.id, args.prompt, args.wave)
    else:
        grade(args.id)
