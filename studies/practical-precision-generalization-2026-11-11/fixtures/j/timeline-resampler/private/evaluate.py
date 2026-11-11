import json, math, pathlib, subprocess, sys, tempfile, time
src = pathlib.Path(sys.argv[1]).resolve() / 'core.cpp'
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
    result = []
    for k in range(count):
        position = k * 44100
        index, remainder = divmod(position, 48000)
        fraction = remainder / 48000.0
        for channel in range(2):
            left = sample(index, channel, seed)
            right = sample(index + 1, channel, seed)
            result.append(left + fraction * (right - left))
    return count, result

def run(exe, wrapper, frames, seed, audit=False, measured=False):
    args = [str(exe), str(frames), str(seed)] + (['--audit'] if audit else [])
    if measured:
        t0 = time.monotonic()
        p = subprocess.run([str(wrapper), *args], capture_output=True, text=True, check=True, timeout=8)
        rss = int(p.stderr.split('CHILD_RSS_KIB')[-1].strip())
        return p.stdout, rss, time.monotonic()-t0
    p = subprocess.run(args, capture_output=True, text=True, check=True, timeout=8)
    return p.stdout, None, None

def compare(stdout, frames, seed, audit=False):
    fields = stdout.split()
    expected_count, expected = reference(frames, seed)
    if not fields:
        return False, None, 'missing output count', False
    try:
        actual_count = int(fields[0])
        actual = list(map(float, fields[1:]))
    except ValueError:
        return False, None, 'invalid output field', False
    finite = all(math.isfinite(value) for value in actual)
    shape_ok = actual_count == expected_count and len(actual) == 2 * expected_count
    if not finite:
        return False, None, 'non-finite output sample', False
    if not shape_ok:
        return False, None, 'output count/shape mismatch', finite
    maximum = max((abs(a-b) for a,b in zip(actual, expected)), default=0.0)
    tolerance = 1e-12 if audit else 2e-6
    return maximum <= tolerance, maximum, None, finite

with tempfile.TemporaryDirectory() as td:
    td = pathlib.Path(td)
    exe, wrapper = td/'candidate', td/'measure-child'
    (td/'measure_child.c').write_text(WAIT4_WRAPPER)
    subprocess.run(['g++','-O2','-std=c++17',str(src),'-o',str(exe)],check=True)
    subprocess.run(['gcc','-O2',str(td/'measure_child.c'),'-o',str(wrapper)],check=True)
    checks, observations = {}, {}
    for frames, seed in [(1,7),(2,19),(17,0x12345678),(4097,(1<<63)+3),(65537,0xABCDEF01)]:
        stdout, _, _ = run(exe,wrapper,frames,seed)
        ok, error, shape, finite = compare(stdout,frames,seed)
        key=f'{frames}_frames_seed_{seed}'
        checks[key]=ok
        observations[key]={'max_abs_error':error,'shape_error':shape,'finite_samples':finite}
    for frames, seed in [(127,(1<<63)+11),(65536,0xABCDEF01)]:
        stdout, _, _ = run(exe,wrapper,frames,seed,audit=True)
        ok,error,shape,finite=compare(stdout,frames,seed,audit=True)
        checks[f'audit_{frames}_frames']=ok
        observations[f'audit_{frames}']={'max_abs_error':error,'shape_error':shape,'finite_samples':finite}
    rejected=subprocess.run([str(exe),'65537','9','--audit'],capture_output=True)
    checks['audit_rejects_oversize']=rejected.returncode!=0

    stdout,rss,elapsed=run(exe,wrapper,500000,(1<<63)+37,measured=True)
    ok,error,shape,finite=compare(stdout,500000,(1<<63)+37)
    checks['full_500k_stream_oracle']=ok
    checks['full_capture_rss_le_9_mib']=rss<=9216
    observations['full_capture']={'max_abs_error':error,'shape_error':shape,'finite_samples':finite,'rss_kib':rss,'elapsed_s':round(elapsed,4)}
    passed=all(checks.values())
    print(json.dumps({'passed':passed,'checks':checks,'observations':observations}))
    raise SystemExit(0 if passed else 1)
