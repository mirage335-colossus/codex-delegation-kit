"""Run explicitly prepared isolated exercises with at most four model sessions."""
import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys
import time
import threading

HERE = Path(__file__).resolve().parent
SETUP_LOCK = threading.Lock()


def run_one(run_id):
    started = time.time()
    records = []
    for action in ("run", "collect"):
        command = [sys.executable, "-B", str(HERE / "harness.py"), action,
                   "--run-id", run_id]
        if action == "run":
            # The shared runtime can stall when several fresh app-servers
            # initialize together. Serialize only setup, not model work.
            with SETUP_LOCK:
                process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, text=True)
                setup_started = time.monotonic()
                result_path = Path("/tmp/action-recovery-runs") / run_id / "operation/backend-result.json"
                while process.poll() is None:
                    try:
                        if json.loads(result_path.read_text()).get("settings_verified"):
                            break
                    except (OSError, ValueError):
                        pass
                    if time.monotonic() - setup_started > 245:
                        break  # The owned executor retains its existing deadline.
                    time.sleep(0.25)
            stdout, stderr = process.communicate(timeout=280)
            records.append(dict(action=action, returncode=process.returncode,
                                stdout=stdout, stderr=stderr))
        else:
            result = subprocess.run(command, capture_output=True, text=True, timeout=280)
            records.append(dict(action=action, returncode=result.returncode,
                                stdout=result.stdout, stderr=result.stderr))
    record = dict(run_id=run_id, started=started, finished=time.time(), stages=records)
    (HERE / "results" / (run_id + "-lifecycle.json")).write_text(
        json.dumps(record, indent=2) + "\n")
    print(json.dumps(record), flush=True)
    return record


if __name__ == "__main__":
    if not sys.argv[1:] or len(set(sys.argv[1:])) != len(sys.argv[1:]):
        raise SystemExit("Supply distinct, already-prepared run IDs")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(run_one, identity) for identity in sys.argv[1:]]
        for future in concurrent.futures.as_completed(futures):
            future.result()
