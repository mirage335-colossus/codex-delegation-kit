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
PRODUCTION=(1280,960,7301,15)
CASES=[PRODUCTION,(71,43,401,15),(19,11,0,21),(31,27,55,0),(4096,3,1025,127)]
DEADLINE=0.20

def compile_source(src,exe):
    cmd=FLAGS+[str(src),"-o",str(exe)]
    subprocess.run(cmd,check=True,timeout=60)
    return cmd

def execute(exe,shape,audit=False):
    w,h,seed,radius=shape
    cmd=[str(exe),str(w),str(h),str(seed),str(radius)]+(["--audit"] if audit else [])
    t=time.perf_counter();p=subprocess.run(cmd,capture_output=True,text=True,check=True,timeout=60);elapsed=time.perf_counter()-t
    return json.loads(p.stdout),elapsed,cmd

def compare(candidate,reference,shape,mode):
    w,h,_,_=shape
    assert len(candidate.get("samples",[]))==len(reference.get("samples",[]))==8,"sample shape mismatch"
    assert len(candidate.get("checksums",[]))==len(reference.get("checksums",[]))==32,"checksum bucket shape mismatch"
    assert all(len(row)==3 for row in candidate["checksums"]+reference["checksums"]),"bucket tuple shape mismatch"
    assert all(math.isfinite(v) for v in candidate["samples"]),"non-finite sample output"
    assert all(math.isfinite(v) for row in candidate["checksums"] for v in row),"non-finite bucket output"
    assert all(math.isfinite(v) for v in reference["samples"]),"non-finite reference sample"
    assert all(math.isfinite(v) for row in reference["checksums"] for v in row),"non-finite reference bucket"
    sample_error=max(abs(a-b) for a,b in zip(candidate["samples"],reference["samples"]))
    agg_error=0.0;decision_error=0
    for b in range(32):
        count=max(0,(w*h+31-b)//32)
        if count:
            agg_error=max(agg_error,abs(candidate["checksums"][b][0]-reference["checksums"][b][0])/count,
                          abs(candidate["checksums"][b][1]-reference["checksums"][b][1])/count)
            decision_error=max(decision_error,abs(candidate["checksums"][b][2]-reference["checksums"][b][2]))
        else:
            assert candidate["checksums"][b]==reference["checksums"][b]==[0,0,0],"empty bucket is nonzero"
    if mode=="audit":
        assert sample_error<=1e-12,f"audit sample error {sample_error}"
        assert agg_error<=1e-10,f"audit full-output aggregate error {agg_error}"
        assert decision_error==0,f"audit decision count mismatch {decision_error}"
    else:
        assert sample_error<=0.01,f"sample quality error {sample_error}"
        assert agg_error<=0.001,f"full-output aggregate error {agg_error}"
        assert decision_error<=64,f"threshold count mismatch per bucket {decision_error}"
    return {"shape_seed_radius":list(shape),"max_sample_error":sample_error,
            "max_mean_or_squared_mean_error":agg_error,"max_threshold_count_delta_per_bucket":decision_error}

def evaluate(candidate_src):
    with tempfile.TemporaryDirectory() as td:
        td=pathlib.Path(td)
        candexe=td/"candidate";baseexe=td/"baseline";wideexe=td/"fast-wide";oracleexe=td/"oracle"
        candbuild=compile_source(candidate_src,candexe)
        basebuild=compile_source(base/"private"/"baseline"/"core.cpp",baseexe)
        widebuild=compile_source(base/"private"/"fast_wide"/"core.cpp",wideexe)
        oraclebuild=compile_source(base/"private"/"oracle.cpp",oracleexe)
        rows=[]
        failures=[]
        # Production baseline is the direct double reference for the exact matched workload.
        baseline_prod,baseline_time,baseline_cmd=execute(baseexe,PRODUCTION)
        candidate_prod_times=[];wide_prod_times=[]
        for rep in range(3):
            cand,elapsed,cand_cmd=execute(candexe,PRODUCTION)
            wide,wide_elapsed,wide_cmd=execute(wideexe,PRODUCTION)
            ref=baseline_prod
            candidate_quality=compare(cand,ref,PRODUCTION,"normal")
            wide_quality=compare(wide,ref,PRODUCTION,"normal")
            if elapsed>DEADLINE: failures.append(f"production deadline exceeded: {elapsed:.6f}s > {DEADLINE}s")
            candidate_prod_times.append(elapsed);wide_prod_times.append(wide_elapsed)
            rows.append({"production_repetition":rep,"candidate":candidate_quality,"fast_wide":wide_quality,
                         "candidate_elapsed_seconds":elapsed,"fast_wide_elapsed_seconds":wide_elapsed,
                         "candidate_run_command":cand_cmd,"fast_wide_run_command":wide_cmd})
        cases=[]
        for shape in CASES[1:]:
            cand,elapsed,cmd=execute(candexe,shape)
            ref,ref_elapsed,ref_cmd=execute(oracleexe,shape)
            checks=compare(cand,ref,shape,"normal")
            checks.update({"elapsed_seconds":elapsed,"oracle_elapsed_seconds":ref_elapsed,
                           "run_command":cmd,"oracle_run_command":ref_cmd})
            cases.append(checks)
        audit_shape=CASES[1]
        audit,audit_time,audit_cmd=execute(candexe,audit_shape,True)
        audit_ref,audit_ref_time,audit_ref_cmd=execute(oracleexe,audit_shape)
        audit_result=compare(audit,audit_ref,audit_shape,"audit")
        audit_result.update({"elapsed_seconds":audit_time,"oracle_elapsed_seconds":audit_ref_time,
                             "run_command":audit_cmd,"oracle_run_command":audit_ref_cmd})
        cand_med=statistics.median(candidate_prod_times);wide_med=statistics.median(wide_prod_times)
        return {"passed":not failures,"failures":failures,"checks":["sample shape and finiteness","32 full-image score/squared-score/threshold buckets",
                    "high-quality audit override","production deadline","matched fast-wide arithmetic comparator"],
                "build_flags":FLAGS,"candidate_build_command":candbuild,"production_shape_seed_radius":list(PRODUCTION),
                "deadline_seconds":DEADLINE,"baseline":{"elapsed_seconds":baseline_time,"reported_storage_bytes":baseline_prod["storage_bytes"],
                    "run_command":baseline_cmd,"build_command":basebuild},
                "production_repetitions":rows,"hidden_cases":cases,"audit_mode":audit_result,
                "matched_fast_wide_comparison":{"candidate_median_seconds":cand_med,"fast_wide_double_median_seconds":wide_med,
                    "speedup_vs_fast_wide_double":wide_med/cand_med,"candidate_pixels_per_second":PRODUCTION[0]*PRODUCTION[1]/cand_med,
                    "fast_wide_pixels_per_second":PRODUCTION[0]*PRODUCTION[1]/wide_med,
                    "candidate_storage_reported_bytes":json.loads(subprocess.run([str(candexe),str(PRODUCTION[0]),str(PRODUCTION[1]),str(PRODUCTION[2]),str(PRODUCTION[3])],capture_output=True,text=True,check=True).stdout)["storage_bytes"],
                    "fast_wide_storage_reported_bytes":json.loads(subprocess.run([str(wideexe),str(PRODUCTION[0]),str(PRODUCTION[1]),str(PRODUCTION[2]),str(PRODUCTION[3])],capture_output=True,text=True,check=True).stdout)["storage_bytes"],
                    "candidate_repetitions_seconds":candidate_prod_times,"fast_wide_repetitions_seconds":wide_prod_times,
                    "fast_wide_build_command":widebuild},"oracle_build_command":oraclebuild}

if __name__=="__main__":
    try:
        result=evaluate(source);print(json.dumps(result,indent=2))
    except Exception as exc:
        print(json.dumps({"passed":False,"failure":str(exc),"checks":"compile/run/full-output/quality/audit/deadline"}));sys.exit(1)
