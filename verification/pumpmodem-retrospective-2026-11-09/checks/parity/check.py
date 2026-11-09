import ast, pathlib, numpy as np, hashlib, json
p=pathlib.Path('/tmp/pump-review-baseline28/tools/triad_gpu_workload.py')
s=p.read_text(); tree=ast.parse(s)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='compare_work')
mod=ast.Module(body=[node],type_ignores=[])
ns={'np':np,'SCORE_RTOL':1e-7,'SCORE_ATOL':1e-9}
exec(compile(mod,str(p),'exec'),ns)
f=ns['compare_work']
base=[dict(work={'ticks':1},lane_scores={'x':np.array([1.,2.])})]
unequal=[dict(work={'ticks':2},lane_scores={'x':np.array([1.,2.])})]
shape=[dict(work={'ticks':1},lane_scores={'x':np.array([[1.,2.]])})]
results={
 'work_diff_equal_scores':f(base,unequal),
 'empty_records':f([],[]),
 'shape_broadcast':f(base,shape),
 'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
 'method':'AST extraction of compare_work; actual NumPy; no other module imports',
}
print(json.dumps(results,indent=2,default=lambda x: x.tolist() if hasattr(x,'tolist') else str(x)))
