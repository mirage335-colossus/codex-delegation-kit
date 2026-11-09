import importlib.util, json
from pathlib import Path
import numpy as np
root=Path('/home/user/___quick/p/_cur/codex-delegation-kit/studies/parallel-recovery-2026-11-09/freeze/cases/P1/participant')
spec=importlib.util.spec_from_file_location('triad_dynamic_joint', root/'tools/triad_dynamic_joint.py')
mod=importlib.util.module_from_spec(spec); import sys; sys.path.insert(0,str(root/'tools')); spec.loader.exec_module(mod)
w=json.loads((root/'fixturedata/projection-workload.json').read_text())
n=w['samples']; fs=w['sample_rate_hz']
p=mod.BlockProjection.make(n,fs,w['required_bands_hz'],w['excluded_bands_hz'])
rng=np.random.default_rng(20261109)
x=rng.standard_normal((3,2,2,n))+1j*rng.standard_normal((3,2,2,n))
actual=p.numpy(x)
dc=x.sum(axis=-1,keepdims=True)/np.sqrt(n)
print('selected_indices=',p.indices.tolist(),'selected_count=',len(p.indices),'projection_kind=',p.kind)
print('actual_shape=',actual.shape,'actual_dtype=',actual.dtype,'direct_dc_shape=',dc.shape,'direct_dc_dtype=',dc.dtype)
print('max_abs_difference=',float(np.max(np.abs(actual-dc))),'allclose=',bool(np.allclose(actual,dc,rtol=2e-14,atol=2e-14)))
print('fixture_provenance=',w['provenance'])
