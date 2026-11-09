"""Capture numeric local session evidence, excluding prompts and account details."""
import collections
import datetime
import json
from pathlib import Path

ROOT = '01a1c18b-2d0e-7510-8b29-f1afa3b47c78'
HERE = Path(__file__).resolve().parent
rows = []
for path in Path('/home/user/.codex/sessions/2026/11/09').glob('*.jsonl'):
    with path.open() as stream:
        first = json.loads(next(stream))
        meta = first.get('payload', {})
        source = meta.get('source', {})
        spawn = source.get('subagent', {}).get('thread_spawn', {}) if isinstance(source, dict) else {}
        is_root = meta.get('id') == ROOT
        if not is_root and spawn.get('parent_thread_id') != ROOT:
            continue
        row = dict(agent=meta.get('agent_path', '/root'), thread_id=meta.get('id'),
                   role=meta.get('agent_role'), first_timestamp=first.get('timestamp'),
                   is_root=is_root, models=[], efforts=[], completed_turns=0, usage=None)
        for line in stream:
            d = json.loads(line)
            p = d.get('payload', {})
            if d.get('type') == 'turn_context':
                for key, dest in [('model', 'models'), ('effort', 'efforts')]:
                    if p.get(key) is not None and p[key] not in row[dest]:
                        row[dest].append(p[key])
            if d.get('type') == 'event_msg' and p.get('type') == 'task_complete':
                row['completed_turns'] += 1
                row['last_completed_timestamp'] = d.get('timestamp')
            if d.get('type') == 'event_msg' and p.get('type') == 'token_count':
                usage = (p.get('info') or {}).get('total_token_usage')
                if usage:
                    row['usage'] = usage
                    row['usage_timestamp'] = d.get('timestamp')
        rows.append(row)
totals = collections.defaultdict(lambda: dict(sessions=0, input_tokens=0, cached_input_tokens=0, output_tokens=0))
for row in rows:
    key = '/'.join(row['models']) or 'unobserved'
    total = totals[key]
    total['sessions'] += 1
    for field in ('input_tokens', 'cached_input_tokens', 'output_tokens'):
        total[field] += (row['usage'] or {}).get(field, 0)
result = dict(captured_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              method='Latest cumulative token_count per session; cached input is a subset of input. Main chat and active continuations are partial at capture. Local runtime metadata, not provider billing or subscription allowance.',
              totals_by_observed_model=dict(totals), sessions=rows)
(HERE/'results'/'telemetry.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({'session_count':len(rows), 'models':dict(totals)}, indent=2))
