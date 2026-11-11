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

import statistics, hashlib
root=pathlib.Path(__file__).resolve().parent.parent
scratch=root/'review-scratch'
executables={}
for name,source in [('submitted', root/'core.cpp'), ('narrow-input',scratch/'narrow-input.cpp')]:
    exe=scratch/name
    subprocess.run(['g++','-O2','-std=c++17',str(source),'-o',str(exe)],check=True)
    executables[name]=exe
cases=[(1,0,False),(2,(1<<64)-1,False),(147,1,False),(148,(1<<64)-1,False),(149,0,False),(295,7,False),(65536,(1<<64)-1,True),(500000,(1<<63)+37,False),(500000,(1<<64)-1,False)]
quality={}
for name,exe in executables.items():
    results=[]
    for frames,seed,audit in cases:
        passed,error,finite=verify(exe,frames,seed,audit)
        results.append(dict(frames=frames,seed=seed,audit=audit,passed=passed,max_abs_error=error,finite=finite))
    quality[name]=results
# Include complete output generation and pipe capture, identically to public timing.
timings={name:[] for name in executables}
for iteration in range(8):
    order=list(executables) if iteration%2==0 else list(reversed(executables))
    for name in order:
        t0=time.perf_counter()
        result=subprocess.run([str(executables[name]),'500000',str((1<<63)+37)],capture_output=True,check=True,timeout=8)
        elapsed=time.perf_counter()-t0
        if iteration: timings[name].append(elapsed)
        assert len(result.stdout.split()) == 1+2*(((500000-1)*48000+44099)//44100)
summary={name:{'median_s':statistics.median(values),'min_s':min(values),'max_s':max(values),'samples_s':values} for name,values in timings.items()}
report={'quality':quality,'timings':summary,'frames':500000,'seed':(1<<63)+37,'compiler_flags':'g++ -O2 -std=c++17','output_count':((500000-1)*48000+44099)//44100}
(scratch/'narrow-comparison.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
assert all(item['passed'] for items in quality.values() for item in items)
