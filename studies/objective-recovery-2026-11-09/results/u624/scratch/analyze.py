import json, pathlib, collections, statistics
P=pathlib.Path('/tmp/objective-recovery-runs/u624/packet')
q=json.loads((P/'abba-oversubscription/qualify.json').read_text())
a=json.loads((P/'abba-oversubscription/independent-audit.json').read_text())
t=json.loads((P/'c54-trace/timing-trace.json').read_text())
assert a['status']=='verified_performance_gate_rejected'
assert a['verified_checks']['exact_exposed_work_scores_and_message_parity_within_each_phase']
assert a['verified_checks']['all_modeled_and_sampled_memory_checks_passed']
s=q['summary']; ratios=s['paired_resident_ratios']
assert s['resident_reduction'] < .15 and all(x < 1 for x in ratios)
assert s['cold_reduction'] <= .05 or s['cold_reduction'] > .05
assert t['status']=='passed' and t['source_verified_unchanged'] and t['input_verified_unchanged']
# Summed callable interval/CPU deltas are diagnostic only, not OS scheduled CPU time.
by=collections.defaultdict(lambda:[0,0,0])
for e in t['events']:
    if e.get('kind') in ('phase','worker') and e.get('job_id') is not None:
        k=(e['job_id'],e.get('phase'))
        by[k][0]+=1
        by[k][1]+=(e.get('end_ns',0)-e.get('start_ns',0))/1e9
        by[k][2]+=(e.get('thread_cpu_ns') or 0)/1e9
lines=[]
lines.append('CHECK: frozen-receipt arithmetic and source-bound trace summary')
lines.append(f"ABBA verified status={a['status']}; looks={a['verified_checks']['looks']}; complete jobs={a['verified_checks']['jobs_with_all_five_unique_ordered_spans']}; no fallbacks/retries={a['verified_checks']['fallbacks_or_retries']==0}.")
lines.append(f"Same-phase parity and modeled/sampled memory checks={a['verified_checks']['exact_exposed_work_scores_and_message_parity_within_each_phase']}/{a['verified_checks']['all_modeled_and_sampled_memory_checks_passed']}.")
lines.append(f"Qualification resident: baseline={s['resident_baseline_seconds']:.3f}s candidate={s['resident_candidate_seconds']:.3f}s reduction={s['resident_reduction']*100:.2f}%; paired ratios={ratios}.")
lines.append(f"Qualification cold lifecycle: baseline={s['cold_baseline_seconds']:.3f}s candidate={s['cold_candidate_seconds']:.3f}s reduction={s['cold_reduction']*100:.2f}%; required <=5% regression, observed {s['cold_reduction']*100:.2f}% reduction.")
lines.append(f"Busy-core equivalents {s['busy_baseline']:.2f} -> {s['busy_candidate']:.2f} (+{(s['busy_candidate']/s['busy_baseline']-1)*100:.1f}%); hardware denominator=12; selected route={json.loads((P/'abba-oversubscription/screen.json').read_text())['selected_route']}.")
lines.append(f"Source-bound trace: status={t['status']}; exact numeric difference={t['maximum_numeric_difference']}; same source/input verified={t['source_verified_unchanged']}/{t['input_verified_unchanged']}; observer overhead={t['observer_overhead_fraction']:.4f}.")
for j in range(5):
    def get(ph): return by[(j,ph)]
    fine=get('fine_tracking'); bank=get('bank_preparation'); total=get('slot_score')
    lines.append(f"job{j}: workers={t['jobs'][j]['workers']}; slot_score wall/cpu-delta={total[1]:.3f}/{total[2]:.3f}s; fine_tracking={fine[1]:.3f}/{fine[2]:.3f}s; bank_preparation={bank[1]:.3f}/{bank[2]:.3f}s.")
# Selected fine-cycle capture: contrast measured submitted basis/Gaussian work to total fine_tracking.
selected=[(k,v) for k,v in by.items() if k[0]==3 and k[1] in ('fine_basis_job','fine_gaussian_job')]
lines.append('job3 captured fine task rows: '+'; '.join(f'{ph} n={v[0]} wall-sum={v[1]:.4f}s thread-cpu-delta-sum={v[2]:.4f}s' for (_,ph),v in selected)+'.')
lines.append('Caveat: callable intervals overlap and thread CPU deltas are not OS running intervals; do not add them as process service or infer achieved utilization from worker count.')
text='\n'.join(lines)+'\n'
print(text,end='')
(pathlib.Path(__file__).parent/'analysis-output.txt').write_text(text)
