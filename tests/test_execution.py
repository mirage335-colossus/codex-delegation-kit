"""Real bounded Linux subprocess tests; no model calls or global resource claims."""

from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import execution


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.directory = self.root / "operation"
        self.addCleanup(self.cleanup_execution)

    def cleanup_execution(self):
        if self.directory.exists():
            execution.cancel(self.directory, "test cleanup")
            end = time.monotonic() + 4
            while time.monotonic() < end:
                result = execution.observe(self.directory)
                if result.get("released") or result["state"] == "uncertain":
                    break
                time.sleep(0.02)

    def spec(self, script="print('ok')", **changes):
        result = {"argv": [sys.executable, "-c", script], "cwd": str(self.root),
                  "env": {}, "timeout_seconds": 10, "operation_id": "test-op"}
        result.update(changes)
        return result

    def wait(self, predicate=lambda value: value.get("released"), seconds=5):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            result = execution.observe(self.directory)
            if predicate(result):
                return result
            time.sleep(0.02)
        self.fail(f"operation did not reach expected state: {result}")

    def test_real_completion_and_log_and_idempotent_result(self):
        spec = self.spec("import os; print(os.environ['EXECUTION_TEST'])", env={"EXECUTION_TEST": "owned"})
        execution.launch(self.directory, spec)
        result = self.wait()
        self.assertEqual(result["state"], "completed")
        self.assertEqual(result["returncode"], 0)
        self.assertEqual((self.directory / "stdout").read_text(), "owned\n")
        self.assertIn("start_ticks", result["runner"])
        self.assertIn("boot_id", result["command"])
        self.assertEqual(execution.launch(self.directory, spec), result)
        with self.assertRaisesRegex(execution.ExecutionError, "different specification"):
            execution.launch(self.directory, self.spec("print('other')"))

    def test_duplicate_concurrent_launch_executes_once(self):
        script = "import time; open('count', 'a').write('one\\n'); time.sleep(.15)"
        spec = self.spec(script)
        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(lambda _: execution.launch(self.directory, spec), range(6)))
        self.assertEqual(self.wait()["returncode"], 0)
        self.assertEqual((self.root / "count").read_text(), "one\n")
        self.assertEqual(len(list(self.directory.glob("spec.json"))), 1)

    def test_reobserve_from_new_process_after_launching_process_exits(self):
        # The original client has no surviving Python state or Popen handle.
        script = ("import sys; sys.path.insert(0, sys.argv[1]); import execution,json; "
                  "from pathlib import Path; execution.launch(Path(sys.argv[2]),json.loads(sys.argv[3]))")
        spec = self.spec("import time; time.sleep(.35); print('recovered')")
        client = subprocess.run([sys.executable, "-c", script, str(ROOT), str(self.directory), json.dumps(spec)],
                                capture_output=True, text=True, timeout=3)
        self.assertEqual(client.returncode, 0, client.stderr)
        result = self.wait()
        self.assertEqual(result["state"], "completed")
        self.assertEqual((self.directory / "stdout").read_text(), "recovered\n")

    def test_cancel_waits_for_child_and_escaped_grandchild(self):
        child = "import os,time; from pathlib import Path; os.setsid(); Path('grandchild').write_text(str(os.getpid())); time.sleep(20)"
        parent = ("import subprocess,sys,time; "
                  f"subprocess.Popen([sys.executable,'-c',{child!r}]); time.sleep(20)")
        execution.launch(self.directory, self.spec(parent))
        end = time.monotonic() + 2
        while not (self.root / "grandchild").exists() and time.monotonic() < end:
            time.sleep(0.02)
        self.assertTrue((self.root / "grandchild").exists())
        pid = int((self.root / "grandchild").read_text())
        identity = execution._identity(pid)
        execution.cancel(self.directory, "scheduler preemption")
        result = self.wait()
        self.assertEqual(result["state"], "cancelled")
        self.assertEqual(result["detail"], "scheduler preemption")
        self.assertFalse(execution._alive(identity))

    def test_parent_completion_does_not_release_live_background_child(self):
        child = "import time; time.sleep(.5)"
        script = f"import subprocess,sys; subprocess.Popen([sys.executable,'-c',{child!r}])"
        started = time.monotonic()
        execution.launch(self.directory, self.spec(script))
        result = self.wait()
        self.assertEqual(result["state"], "completed")
        self.assertGreater(time.monotonic() - started, .45)

    def test_setup_failure_is_separate_from_real_exit_failure(self):
        execution.launch(self.directory, self.spec(argv=[str(self.root / "missing")]))
        result = self.wait()
        self.assertEqual(result["state"], "setup_error")
        self.assertIsNone(result["returncode"])
        other = self.root / "nonzero"
        execution.launch(other, self.spec("raise SystemExit(3)", operation_id="nonzero"))
        end = time.monotonic() + 3
        while time.monotonic() < end and not execution.observe(other).get("released"):
            time.sleep(.02)
        result = execution.observe(other)
        self.assertEqual(result["state"], "completed")
        self.assertEqual(result["returncode"], 3)

    def test_timeout_is_cancelled_and_kill_escalates(self):
        script = "import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(20)"
        execution.launch(self.directory, self.spec(script, timeout_seconds=.15))
        result = self.wait()
        self.assertEqual(result["state"], "cancelled")
        self.assertEqual(result["detail"], "execution timeout")
        self.assertEqual(result["returncode"], -signal.SIGKILL)

    def test_unacknowledged_launch_and_stale_runner_are_never_retried(self):
        self.directory.mkdir()
        spec = self.spec("from pathlib import Path; Path('forbidden-retry').touch()")
        execution._write(self.directory / "spec.json", spec)
        execution._write(self.directory / "receipt.json", {
            "state": "prepared", "released": False, "prepared_at": time.time() - 10,
        })
        self.assertEqual(execution.launch(self.directory, spec)["state"], "uncertain")
        self.assertFalse((self.root / "forbidden-retry").exists())
        identity = execution._identity(os.getpid())
        identity["start_ticks"] -= 1
        execution._write(self.directory / "receipt.json", {
            "state": "running", "released": False, "runner": identity,
        })
        result = execution.cancel(self.directory, "stop unknown operation")
        self.assertEqual(result["state"], "uncertain")
        self.assertFalse(result["released"])
        self.assertTrue((self.directory / "cancel.json").exists())
        self.assertFalse(execution._signal_owned(identity, signal.SIGTERM))

    def test_runner_crash_retains_reservation_for_surviving_process(self):
        spec = self.spec("import time; time.sleep(20)")
        execution.launch(self.directory, spec)
        receipt = self.wait(lambda value: "command" in value)
        command = receipt["command"]
        try:
            self.assertTrue(execution._signal_owned(receipt["runner"], signal.SIGKILL))
            result = self.wait(lambda value: value["state"] == "uncertain")
            self.assertFalse(result["released"])
            self.assertTrue(execution._alive(command))
            self.assertEqual(execution.launch(self.directory, spec)["state"], "uncertain")
        finally:
            # The test retains the verified child identity; the generic observer
            # cannot infer that it has this complete inventory after runner death.
            execution._signal_owned(command, signal.SIGKILL)

    def test_cancel_first_allows_wrapper_to_interrupt_its_server(self):
        child = "import time; time.sleep(20)"
        script = ("import subprocess,sys,signal,time; from pathlib import Path; "
                  f"p=subprocess.Popen([sys.executable,'-c',{child!r}]); "
                  "signal.signal(signal.SIGTERM, lambda *args: (Path('interrupted').write_text('yes'), p.terminate())); "
                  "p.wait()")
        execution.launch(self.directory, self.spec(script))
        self.wait(lambda value: len(value.get("descendants", [])) >= 2)
        execution.cancel(self.directory, "cooperative stop")
        self.assertEqual(self.wait()["state"], "cancelled")
        self.assertEqual((self.root / "interrupted").read_text(), "yes")

    def test_bad_spec_and_symlink_refused_before_launch(self):
        with self.assertRaises(execution.ExecutionError):
            execution.launch(self.directory, self.spec(argv="echo unsafe"))
        self.directory.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(execution.ExecutionError):
            execution.launch(self.directory, self.spec())
        self.directory.unlink()


if __name__ == "__main__":
    unittest.main()
