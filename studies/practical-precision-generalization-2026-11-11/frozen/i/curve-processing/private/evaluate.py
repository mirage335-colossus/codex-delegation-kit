import json
import math
import pathlib
import statistics
import subprocess
import sys
import tempfile
import time

base=pathlib.Path(__file__).resolve().parents[1]
source=(pathlib.Path(sys.argv[1])/"core.cpp" if len(sys.argv)>1 and pathlib.Path(sys.argv[1]).is_dir()
        else pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else base/"participant"/"core.cpp")
FLAGS=["c++","-O3","-std=c++17","-DNDEBUG","-march=native"]
PRODUCTION=(4096,2048,13)
CASES=[PRODUCTION,(999,731,7),(63,37,2025),(2,1,0),(1,1,91)]
DEADLINE=0.12

def compile_source(src,exe):
    cmd=FLAGS+[str(src),"-o",str(exe)]
    subprocess.run(cmd,check=True,timeout=60)
    return cmd

def execute(exe,shape,audit=False,noargs=False):
    w,h,seed=shape
    cmd=[str(exe)] if noargs else [str(exe),str(w),str(h),str(seed)]
    if audit:cmd.append("--audit")
    t=time.perf_counter();p=subprocess.run(cmd,capture_output=True,text=True,check=True,timeout=30);elapsed=time.perf_counter()-t
    return json.loads(p.stdout),elapsed,cmd

def compare(candidate,reference,shape,mode):
    w,h,seed=shape
    assert len(candidate.get("samples",[]))==len(reference.get("samples",[]))==8,"sample shape mismatch"
    assert len(candidate.get("checksums",[]))==len(reference.get("checksums",[]))==32,"checksum bucket shape mismatch"
    assert all(len(r)==3 for r in candidate["checksums"]+reference["checksums"]),"bucket tuple shape mismatch"
    assert all(math.isfinite(v) for v in candidate["samples"]),"non-finite sample"
    assert all(math.isfinite(v) for row in candidate["checksums"] for v in row),"non-finite output bucket"
    assert all(math.isfinite(v) for v in reference["samples"]),"non-finite reference sample"
    assert all(math.isfinite(v) for row in reference["checksums"] for v in row),"non-finite reference bucket"
    sample_error=max(abs(a-b) for a,b in zip(candidate["samples"],reference["samples"]))
    aggregate_error=0.0;threshold_error=0
    for b in range(32):
        count=max(0,(w*h+31-b)//32)
        if count:
            aggregate_error=max(aggregate_error,
                abs(candidate["checksums"][b][0]-reference["checksums"][b][0])/count,
                abs(candidate["checksums"][b][1]-reference["checksums"][b][1])/count)
            threshold_error=max(threshold_error,abs(candidate["checksums"][b][2]-reference["checksums"][b][2]))
        else:assert candidate["checksums"][b]==reference["checksums"][b]==[0,0,0],"nonzero empty bucket"
    if mode=="audit":
        assert sample_error<=1e-12,f"audit sample error {sample_error}"
        assert aggregate_error<=1e-10,f"audit full-output aggregate error {aggregate_error}"
        assert threshold_error==0,f"audit threshold count mismatch {threshold_error}"
    else:
        assert sample_error<=2e-5,f"sample quality error {sample_error}"
        assert aggregate_error<=2e-5,f"full-output aggregate error {aggregate_error}"
        assert threshold_error<=4,f"threshold count mismatch per bucket {threshold_error}"
    return {"shape_seed":list(shape),"max_sample_error":sample_error,
            "max_mean_or_squared_mean_error_per_reading":aggregate_error,
            "max_threshold_count_delta_per_bucket":threshold_error}

def evaluate(candidate_src):
    with tempfile.TemporaryDirectory() as td:
        td=pathlib.Path(td);candexe=td/"candidate";baseexe=td/"baseline";wideexe=td/"fast-wide";oracleexe=td/"oracle"
        candbuild=compile_source(candidate_src,candexe)
        basebuild=compile_source(base/"private"/"baseline"/"core.cpp",baseexe)
        widebuild=compile_source(base/"private"/"fast_wide"/"core.cpp",wideexe)
        oraclebuild=compile_source(base/"private"/"oracle.cpp",oracleexe)
        failures=[];rows=[]
        baseline_runs=[execute(baseexe,PRODUCTION,noargs=True) for _ in range(3)]
        baseline_prod,baseline_elapsed,baseline_cmd=baseline_runs[0]
        baseline_times=[run[1] for run in baseline_runs]
        candidate_prod_times=[];wide_prod_times=[]
        for rep in range(3):
            cand,ct,ccmd=execute(candexe,PRODUCTION,noargs=True)
            wide,wt,wcmd=execute(wideexe,PRODUCTION,noargs=True)
            cq=compare(cand,baseline_prod,PRODUCTION,"normal")
            wq=compare(wide,baseline_prod,PRODUCTION,"normal")
            if ct>DEADLINE:failures.append(f"normal production deadline exceeded {ct:.6f}s > {DEADLINE}s")
            candidate_prod_times.append(ct);wide_prod_times.append(wt)
            rows.append({"repetition":rep,"candidate_quality":cq,"fast_wide_quality":wq,
                         "candidate_elapsed_seconds":ct,"fast_wide_elapsed_seconds":wt,
                         "candidate_run_command":ccmd,"fast_wide_run_command":wcmd})
        hidden=[]
        for shape in CASES[1:]:
            cand,elapsed,cmd=execute(candexe,shape)
            ref,ref_elapsed,refcmd=execute(oracleexe,shape)
            q=compare(cand,ref,shape,"normal");q.update({"elapsed_seconds":elapsed,"oracle_elapsed_seconds":ref_elapsed,"run_command":cmd,"oracle_run_command":refcmd})
            hidden.append(q)
        audit_shape=CASES[1]
        audit,audit_elapsed,audit_cmd=execute(candexe,audit_shape,audit=True)
        audit_ref,audit_ref_elapsed,audit_ref_cmd=execute(oracleexe,audit_shape)
        auditq=compare(audit,audit_ref,audit_shape,"audit")
        auditq.update({"elapsed_seconds":audit_elapsed,"oracle_elapsed_seconds":audit_ref_elapsed,"run_command":audit_cmd,"oracle_run_command":audit_ref_cmd})
        candmed=statistics.median(candidate_prod_times);widemed=statistics.median(wide_prod_times)
        return {"passed":not failures,"failures":failures,"checks":["sample shape and finiteness","32 complete-output score/squared-score/threshold buckets","high-accuracy audit invocation","normal production deadline","matched fast-wide comparator"],
            "build_flags":FLAGS,"candidate_build_command":candbuild,"production_shape_seed":list(PRODUCTION),"deadline_seconds":DEADLINE,
            "baseline":{"elapsed_seconds":baseline_elapsed,"median_elapsed_seconds":statistics.median(baseline_times),
                "repetitions_seconds":baseline_times,"reported_storage_bytes":baseline_prod["storage_bytes"],
                "run_command":baseline_cmd,"build_command":basebuild},
            "production_repetitions":rows,"hidden_cases":hidden,"audit_mode":auditq,
            "matched_fast_wide_comparison":{"candidate_median_seconds":candmed,"fast_wide_wide_arithmetic_median_seconds":widemed,
                "speedup_vs_fast_wide":widemed/candmed,"candidate_samples_per_second":PRODUCTION[0]*PRODUCTION[1]/candmed,
                "fast_wide_samples_per_second":PRODUCTION[0]*PRODUCTION[1]/widemed,
                "candidate_storage_reported_bytes":json.loads(subprocess.run([str(candexe)],capture_output=True,text=True,check=True,timeout=30).stdout)["storage_bytes"],
                "fast_wide_storage_reported_bytes":json.loads(subprocess.run([str(wideexe)],capture_output=True,text=True,check=True,timeout=30).stdout)["storage_bytes"],
                "candidate_repetitions_seconds":candidate_prod_times,"fast_wide_repetitions_seconds":wide_prod_times,
                "fast_wide_build_command":widebuild},"oracle_build_command":oraclebuild}

if __name__=="__main__":
    try:
        result=evaluate(source);print(json.dumps(result,indent=2))
        if not result["passed"]:sys.exit(1)
    except Exception as exc:
        print(json.dumps({"passed":False,"failure":str(exc),"checks":"compile/run/full-output/quality/audit/deadline"}));sys.exit(1)
