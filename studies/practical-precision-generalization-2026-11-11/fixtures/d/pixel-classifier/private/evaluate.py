import json
import math
import pathlib
import statistics
import subprocess
import sys
import tempfile
import time

base = pathlib.Path(__file__).resolve().parents[1]
source = (pathlib.Path(sys.argv[1]) / "core.cpp" if len(sys.argv) > 1 and pathlib.Path(sys.argv[1]).is_dir()
          else pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else base / "participant" / "core.cpp")
flags = ["c++", "-O3", "-std=c++17", "-DNDEBUG", "-march=native"]
CASES = [(2048, 1536, 12791), (1009, 769, 4093), (379, 255, 8765)]
CAP = 140 * 1024 * 1024

TRACKER = r'''#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <malloc.h>
#include <new>
namespace { std::atomic<size_t> live_bytes{0}, peak_bytes{0}; inline void add_bytes(size_t n){size_t v=live_bytes.fetch_add(n)+n,p=peak_bytes.load();while(v>p&&!peak_bytes.compare_exchange_weak(p,v)){} } inline void sub_bytes(void*p){if(p)live_bytes.fetch_sub(malloc_usable_size(p));} }
void* operator new(size_t n){if(void*p=std::malloc(n?n:1)){add_bytes(malloc_usable_size(p));return p;}throw std::bad_alloc();}
void* operator new[](size_t n){return ::operator new(n);}
void operator delete(void*p) noexcept{sub_bytes(p);std::free(p);}
void operator delete[](void*p) noexcept{::operator delete(p);}
void operator delete(void*p,size_t) noexcept{::operator delete(p);}
void operator delete[](void*p,size_t) noexcept{::operator delete(p);}
__attribute__((destructor)) static void report_peak(){std::fprintf(stderr,"TRACKED_PEAK_BYTES=%zu\n",peak_bytes.load());}
'''

def compile_one(src, exe, tracker):
    cmd = flags + ["-include", str(tracker), str(src), "-o", str(exe)]
    subprocess.run(cmd, check=True)
    return cmd

def run_one(exe, shape, audit=False):
    w, h, seed = shape
    cmd = [str(exe), str(w), str(h), str(seed)] + (["--audit"] if audit else [])
    start = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    elapsed = time.perf_counter() - start
    tracked = int(proc.stderr.split("TRACKED_PEAK_BYTES=")[-1].strip())
    return json.loads(proc.stdout), elapsed, tracked, cmd

def validate(candidate, oracle, shape, mode):
    w, h, seed = shape
    assert len(candidate.get("samples", [])) == len(oracle.get("samples", [])) == 7, "sample shape mismatch"
    assert len(candidate.get("checksums", [])) == len(oracle.get("checksums", [])) == 32, "checksum bucket shape mismatch"
    assert all(len(r) == 3 for r in candidate["checksums"] + oracle["checksums"]), "checksum tuple shape mismatch"
    assert all(math.isfinite(v) for v in candidate["samples"]), "non-finite sample"
    assert all(math.isfinite(v) for row in candidate["checksums"] for v in row), "non-finite checksum"
    assert all(math.isfinite(v) for v in oracle["samples"]), "non-finite oracle sample"
    assert all(math.isfinite(v) for row in oracle["checksums"] for v in row), "non-finite oracle checksum"
    sample_error = max(abs(a-b) for a,b in zip(candidate["samples"], oracle["samples"]))
    per_bucket = []
    decision_mismatches = []
    for b in range(32):
        count = (w*h + 31-b) // 32
        sums = [abs(candidate["checksums"][b][j]-oracle["checksums"][b][j])/count for j in (0,1)]
        per_bucket.append(max(sums))
        decision_mismatches.append(abs(candidate["checksums"][b][2]-oracle["checksums"][b][2]))
    checksum_error = max(per_bucket)
    max_decision_diff = max(decision_mismatches)
    if mode == "audit":
        assert sample_error <= 1e-12, f"audit sample mismatch {sample_error}"
        assert checksum_error <= 1e-10, f"audit checksum mismatch {checksum_error}"
        assert max_decision_diff == 0, f"audit decision mismatch {max_decision_diff}"
    else:
        assert sample_error <= 2e-5, f"sample quality error {sample_error}"
        assert checksum_error <= 2e-5, f"full-output checksum error {checksum_error}"
        assert max_decision_diff <= 4, f"decision mismatch per bucket {max_decision_diff}"
    return {"shape_seed": list(shape), "sample_max_error": sample_error,
            "full_output_checksum_max_error_per_element": checksum_error,
            "max_decision_count_difference_per_bucket": max_decision_diff}

def evaluate(src):
    with tempfile.TemporaryDirectory() as scratch:
        scratch = pathlib.Path(scratch)
        tracker = scratch / "tracker.hpp"
        tracker.write_text(TRACKER)
        candidate_exe = scratch / "candidate"
        baseline_exe = scratch / "baseline"
        oracle_exe = scratch / "oracle"
        storage_exe = scratch / "storage-only"
        candidate_build = compile_one(src, candidate_exe, tracker)
        baseline_build = compile_one(base / "private" / "baseline.cpp", baseline_exe, tracker)
        oracle_build = compile_one(base / "private" / "oracle.cpp", oracle_exe, tracker)
        storage_build = compile_one(base / "private" / "storage_only.cpp", storage_exe, tracker)
        failures = []
        rows = []
        for case in CASES:
            cand, elapsed, tracked, run_cmd = run_one(candidate_exe, case)
            oracle, oracle_elapsed, oracle_tracked, oracle_cmd = run_one(oracle_exe, case)
            storage_only, storage_elapsed, storage_tracked, storage_cmd = run_one(storage_exe, case)
            checks = validate(cand, oracle, case, "normal")
            storage_checks = validate(storage_only, oracle, case, "normal")
            is_production = case == CASES[0]
            if is_production and cand.get("storage_bytes", CAP+1) > CAP:
                failures.append(f"reported production bulk storage {cand.get('storage_bytes')} > {CAP}")
            if is_production and tracked > CAP:
                failures.append(f"tracked production allocation peak {tracked} > {CAP}")
            if is_production and storage_only.get("storage_bytes", CAP+1) > CAP:
                failures.append("storage-only comparator exceeds production storage cap")
            if is_production and storage_tracked > CAP:
                failures.append("storage-only comparator tracked allocation exceeds production cap")
            checks.update({"production_storage_cap_applies": is_production,
                           "reported_storage_bytes": cand["storage_bytes"],
                           "tracked_allocation_peak_bytes": tracked,
                           "elapsed_seconds": elapsed,
                           "pixels_per_second": case[0]*case[1]/elapsed,
                           "oracle_elapsed_seconds": oracle_elapsed,
                           "oracle_run_command": oracle_cmd,
                           "run_command": run_cmd,
                           "storage_only_full_output_check": storage_checks,
                           "storage_only_reported_storage_bytes": storage_only["storage_bytes"],
                           "storage_only_tracked_allocation_peak_bytes": storage_tracked,
                           "storage_only_elapsed_seconds": storage_elapsed,
                           "storage_only_run_command": storage_cmd})
            rows.append(checks)

        production = CASES[0]
        audit, audit_elapsed, audit_tracked, audit_cmd = run_one(candidate_exe, production, audit=True)
        audit_ref, audit_ref_elapsed, _, audit_ref_cmd = run_one(oracle_exe, production, audit=True)
        audit_result = validate(audit, audit_ref, production, "audit")
        audit_result.update({"elapsed_seconds": audit_elapsed, "tracked_allocation_peak_bytes": audit_tracked,
                             "storage_cap_applies": False, "run_command": audit_cmd,
                             "oracle_elapsed_seconds": audit_ref_elapsed, "oracle_run_command": audit_ref_cmd})

        # Matched end-to-end timing: same optimized flags, input, shape and seed for both implementations.
        candidate_times = []
        baseline_times = []
        storage_only_times = []
        candidate_storage = None
        baseline_storage = None
        storage_only_storage = None
        for _ in range(3):
            c, ct, cm, _ = run_one(candidate_exe, production)
            so, sot, som, _ = run_one(storage_exe, production)
            b, bt, bm, _ = run_one(baseline_exe, production)
            candidate_times.append(ct)
            storage_only_times.append(sot)
            baseline_times.append(bt)
            candidate_storage = (c["storage_bytes"], cm)
            storage_only_storage = (so["storage_bytes"], som)
            baseline_storage = (b["storage_bytes"], bm)
        cmed, somed, bmed = statistics.median(candidate_times), statistics.median(storage_only_times), statistics.median(baseline_times)
        result = {"passed": not failures, "failures": failures,
                  "checks": ["same-build full output against independent double oracle",
                             "finite samples and all 32 output checksum/decision buckets",
                             "140 MiB normal-mode cap from output report and tracked C++ heap peak",
                             "high-accuracy audit mode", "matched end-to-end starter comparison"],
                  "build_flags": flags, "candidate_build_command": candidate_build,
                  "cases": rows, "audit_mode": audit_result,
                  "matched_throughput": {"shape_seed": list(production), "build_flags": flags,
                      "candidate_elapsed_median_seconds": cmed, "starter_elapsed_median_seconds": bmed,
                      "storage_only_double_arithmetic_elapsed_median_seconds": somed,
                      "candidate_pixels_per_second": production[0]*production[1]/cmed,
                      "starter_pixels_per_second": production[0]*production[1]/bmed,
                      "storage_only_double_arithmetic_pixels_per_second": production[0]*production[1]/somed,
                      "speedup_vs_starter": bmed/cmed,
                      "speedup_vs_storage_only_double_arithmetic": somed/cmed,
                      "candidate_repetitions_seconds": candidate_times,
                      "storage_only_repetitions_seconds": storage_only_times,
                      "starter_repetitions_seconds": baseline_times,
                      "candidate_storage_reported_and_tracked_bytes": list(candidate_storage),
                      "storage_only_storage_reported_and_tracked_bytes": list(storage_only_storage),
                      "starter_storage_reported_and_tracked_bytes": list(baseline_storage),
                      "storage_only_build_command": storage_build,
                      "starter_build_command": baseline_build},
                  "oracle_build_command": oracle_build}
        return result

if __name__ == "__main__":
    try:
        result = evaluate(source)
        print(json.dumps(result, indent=2))
        if not result["passed"]: sys.exit(1)
    except Exception as exc:
        print(json.dumps({"passed":False, "failure":str(exc), "checks":"compile/run/full-output/resource/audit/timing"}))
        sys.exit(1)
