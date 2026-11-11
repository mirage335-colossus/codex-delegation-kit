import json, math, pathlib, subprocess, tempfile, time
root = pathlib.Path(__file__).resolve().parent
MASK = (1 << 64) - 1
WAIT4_WRAPPER = r'''#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>
int main(int argc, char **argv) {
  if (argc < 2) return 2;
  pid_t child = fork();
  if (child < 0) return 125;
  if (child == 0) { execvp(argv[1], argv + 1); perror("execvp"); _exit(127); }
  int status = 0; struct rusage usage;
  while (wait4(child, &status, 0, &usage) < 0) if (errno != EINTR) return 125;
  fprintf(stderr, "CHILD_RSS_KIB %ld\n", usage.ru_maxrss);
  if (WIFEXITED(status)) return WEXITSTATUS(status);
  if (WIFSIGNALED(status)) return 128 + WTERMSIG(status);
  return 125;
}'''

def sample(frame, channel, seed):
    x = ((frame + 1) * 6364136223846793005 + (channel + 3) * 1442695040888963407 + seed) & MASK
    x ^= x >> 29
    x = (x * 0x9e3779b97f4a7c15) & MASK
    x ^= x >> 32
    return (int(x % 2000001) - 1000000) * 0.000001

def reference(frames, seed):
    count = (((frames - 1) * 48000) + 44099) // 44100 if frames > 1 else 0
    out = []
    for k in range(count):
        p = k * 44100
        index, rem = divmod(p, 48000)
        frac = rem / 48000.0
        for c in range(2):
            a, b = sample(index, c, seed), sample(index + 1, c, seed)
            out.append(a + frac * (b - a))
    return count, out

def run(exe, frames, seed, audit=False):
    args = [str(exe), str(frames), str(seed)] + (['--audit'] if audit else [])
    p = subprocess.run(args, capture_output=True, text=True, check=True, timeout=8)
    vals = p.stdout.split()
    count = int(vals[0])
    return count, list(map(float, vals[1:]))

def verify(exe, frames, seed, audit=False):
    got_count, got = run(exe, frames, seed, audit)
    ref_count, ref = reference(frames, seed)
    shape_ok = got_count == ref_count and len(got) == 2 * ref_count
    finite = all(math.isfinite(value) for value in got)
    if not shape_ok or not finite:
        return False, None, finite
    tol = 1e-12 if audit else 2e-6
    max_error = max((abs(a-b) for a,b in zip(got,ref)), default=0.0)
    return max_error <= tol, max_error, finite

with tempfile.TemporaryDirectory(dir=root) as work:
    work = pathlib.Path(work)
    exe = work / 'probe'
    wrapper = work / 'measure-child'
    (work / 'measure_child.c').write_text(WAIT4_WRAPPER)
    subprocess.run(['g++','-O2','-std=c++17','core.cpp','-o',str(exe)],cwd=root,check=True)
    subprocess.run(['gcc','-O2',str(work/'measure_child.c'),'-o',str(wrapper)],check=True)

    checks = {}
    for frames, seed in [(1,7),(2,19),(17,0x12345678),(4097,(1<<63)+3)]:
        ok, error, finite = verify(exe,frames,seed)
        checks[f'{frames}_frames']={'passed':ok,'finite_samples':finite,'max_abs_error':error}
    for frames, seed in [(127,(1<<63)+11),(65536,0xABCDEF01)]:
        ok, error, finite = verify(exe,frames,seed,True)
        checks[f'audit_{frames}_frames']={'passed':ok,'finite_samples':finite,'max_abs_error':error}
    rejected = subprocess.run([str(exe),'65537','9','--audit'],capture_output=True)
    checks['audit_rejects_oversize']={'passed':rejected.returncode!=0}
    full_ok, full_error, full_finite = verify(exe,500000,(1<<63)+37)
    checks['full_output_oracle']={'passed':full_ok,'finite_samples':full_finite,'max_abs_error':full_error}

    t0=time.monotonic()
    measured=subprocess.run([str(wrapper),str(exe),'500000',str((1<<63)+37)],
                            capture_output=True,text=True,check=True,timeout=8)
    elapsed=time.monotonic()-t0
    rss=int(measured.stderr.split('CHILD_RSS_KIB')[-1].strip())
    checks['full_capture_rss_le_9_mib']={'passed':rss<=9216,'rss_kib':rss}
    print(json.dumps({'checks':checks,'elapsed_s':round(elapsed,4)}))
    assert all(v['passed'] for v in checks.values()), 'output, audit, or capacity check failed'
    print('PASS complete resampled output, audit reference, and wait4 RSS bound')
