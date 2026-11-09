"""Recreate focused predecision packets from read-only Git blobs."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path('/home/user/___quick/p/_cur/dataPump/pumpModem')
BASE = '28f08825670b76472628b50d98cd648a87aa62e4'
LATER = '15b17f7d3886f1baadf3c22b8990083eda6f85cd'
COMMON = '''The application is a Robust radio receiver. The user wants rapid GPU-assisted estimates of complete receiver throughput on the local CPU, productive use of all 12 logical threads within one stream, credible margins, and a repeatable fast testing method. Complete work includes acquisition, fine tracking, unsuccessful candidates, recurring setup and quiet-slot completion. Independent simultaneous simulations are not same-stream capacity. Lower precision and tensor-compatible arithmetic are encouraged where qualified. Preserve accuracy and work coverage. This exercise authorizes no production changes or cloud jobs.

You see a reconstructed historical decision point, not later results. Source excerpts are exact Git blobs; the review question is reconstructed. Do not read current checkout files, other packets, reports, answer keys, conversations or other responses. Missing context is an uncertainty, not evidence of a defect. Provide at most three concrete concerns with mechanism, source locator, predicted observable outcome, cheapest decisive check and resulting action. Also identify one choice worth preserving. Distinguish an actual defect from an unverified hypothesis. Use only this packet. No tools except reading this packet and writing your assigned response are needed.
'''

def excerpt(rev, path, lo, hi):
    data = subprocess.check_output(['git','-C',str(REPO),'show',f'{rev}:{path}'], text=True)
    lines = data.splitlines()
    return f'\n### {rev[:8]} {path} lines {lo} to {hi}\n\n```python\n' + '\n'.join(f'{i+1}: {lines[i]}' for i in range(lo-1,min(hi,len(lines)))) + '\n```\n'

cases = {
 'C1': ('CPU parallel receiver', BASE, 'Before first target-task optimization. Decide which work should be optimized or parallelized first, and how to distinguish algorithmic waste, controller serialization and insufficient worker parallelism. No profile percentages are supplied. Do not assume all recurrences are parallelizable.', [
  ('tools/triad_incremental_receiver.py',239,329),('tools/triad_tracking_receiver.py',709,745),('tools/triad_dynamic_joint.py',54,109)]),
 'C2': ('GPU architecture and experiment scope', BASE, 'Before choosing the next cloud GPU experiment. The existing code can run a short CPU/CUDA fine comparison. Decide whether it is sufficient for the user goal and what minimal architectural experiment should precede a full campaign. No particular hardware choice is mandatory. Account for what actually runs where.', [
  ('tools/triad_incremental_receiver.py',239,289),('tools/triad_gpu_workload.py',172,247),('tools/triad_gpu_workload.py',264,278)]),
 'C3': ('Work comparison contract', BASE, 'Review the existing comparison helper and acceptance caller for compatibility with reliable CPU/GPU timing comparisons. Determine whether the booleans and final status can support misleading conclusions and propose the smallest discriminating check. Do not assume an error has occurred.', [
  ('tools/triad_gpu_workload.py',162,201),('tools/triad_gpu_workload.py',264,278)]),
 'C4': ('Tensor acceleration decision', LATER, 'Before the final tensor investigation. Consider replacing some coarse ZoomFFT or fine Fourier calculations with tensor-compatible matrix products using TF32 or scaled FP16 with FP32 accumulation. No candidate tensor speed, numerical outcome or later profile is supplied. Decide what to prototype first, what to compare, and what evidence would justify retaining it. Actual matrix shapes beyond the source are not supplied.', [
  ('tools/triad_gpu_bank.py',285,338),('tools/triad_gpu_fine.py',151,185)]),
 'C5': ('Mixed precision interface', BASE, 'Before implementing a new bulk GPU path. Proposed design: compute mapped templates, projected basis, correlations and Gram in FP32 on device; retain the Gaussian state and small likelihood calculations in FP64 on CPU. The proposal is a reconstructed candidate, not code known to be implemented. Review whether this boundary is adequate and propose a cheap numerical preflight. The intended spectrum generally does not require high in-band dynamic range.', [
  ('tools/triad_incremental_receiver.py',274,289),('tools/triad_gaussian_state.py',65,110),('tools/triad_gaussian_prepared.py',35,67)]),
}
freeze = HERE/'packets'/'freeze.json'
# C6 is a separately frozen historical wrapper excerpt, not a Git-only packet.
manifest = json.loads(freeze.read_text()) if freeze.exists() else {}
for case,(title,rev,question,parts) in cases.items():
    body = f'# {case} {title}\n\nRevision: `{rev}`.\n\n{COMMON}\n## Decision\n\n{question}\n'
    body += ''.join(excerpt(rev,*p) for p in parts)
    out = HERE/'packets'/f'{case}.md'
    out.write_text(body)
    manifest[case] = dict(revision=rev, sha256=hashlib.sha256(out.read_bytes()).hexdigest(), bytes=out.stat().st_size, paths=[p[0] for p in parts])
freeze.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
