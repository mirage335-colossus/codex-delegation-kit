import json, pathlib, subprocess, statistics, time
root = pathlib.Path.cwd()
scratch = root / 'review-scratch'
source = (root / 'core.cpp').read_text()
# Read public definitions without executing its test driver.
namespace = {'__file__': str(root / 'public_check.py')}
exec((root / 'public_check.py').read_text().split('with tempfile.TemporaryDirectory(dir=root) as work:')[0], namespace)
function = source[source.index('static double input_sample'):source.index('\nint main')]
float_function = function.replace('static double input_sample', 'static float input_sample_float').replace('* 0.000001;', '* 0.000001f;')
narrow = source.replace('\nint main', '\n' + float_function + '\nint main').replace('static_cast<float>(input_sample(index, c, seed))', 'input_sample_float(index, c, seed)').replace('static_cast<float>(input_sample(index + 1, c, seed))', 'input_sample_float(index + 1, c, seed)')
reused = narrow.replace('#include <string>', '#include <string>\n#include <vector>').replace('  std::cout.precision', '  std::vector<float> input;\n  if (!audit) {\n    input.resize(frames * channels);\n    for (std::uint64_t i = 0; i < frames; ++i)\n      for (int c = 0; c < channels; ++c)\n        input[i * channels + c] = input_sample_float(i, c, seed);\n  }\n\n  std::cout.precision').replace('const float a = input_sample_float(index, c, seed);', 'const float a = input[index * channels + c];').replace('const float b = input_sample_float(index + 1, c, seed);', 'const float b = input[(index + 1) * channels + c];')
variants = {'submitted':source, 'narrow_sample':narrow, 'narrow_reused':reused}
for name, text in variants.items():
    (scratch / (name + '.cpp')).write_text(text)
    subprocess.run(['g++','-O2','-std=c++17',str(scratch/(name+'.cpp')),'-o',str(scratch/name)], check=True)
(scratch / 'measure_child.c').write_text(namespace['WAIT4_WRAPPER'])
subprocess.run(['gcc','-O2',str(scratch/'measure_child.c'),'-o',str(scratch/'measure-child')], check=True)
checks = {}
for name in variants:
    exe = scratch / name
    checks[name] = {}
    for frames, seed, audit in [(1, (1<<64)-1, False), (161, 0, False), (500000,(1<<64)-1,False), (65536,(1<<64)-1,True)]:
        checks[name][str((frames,seed,audit))] = namespace['verify'](exe,frames,seed,audit)
    p = subprocess.run([str(scratch/'measure-child'), str(exe), '500000', str((1<<64)-1)], capture_output=True, check=True)
    checks[name]['rss_kib'] = int(p.stderr.split(b'CHILD_RSS_KIB')[-1])
    assert all(v[0] for k,v in checks[name].items() if k != 'rss_kib')
    assert checks[name]['rss_kib'] <= 9216
    print(name, json.dumps(checks[name]), flush=True)
times = {name:[] for name in variants}
names = list(variants)
# All variants include startup, input preparation, interpolation, formatting,
# pipe transfer, and capture of the complete full-size output.
for round_id in range(9):
    order = names[round_id % 3:] + names[:round_id % 3]
    for name in order:
        start = time.monotonic()
        result = subprocess.run([str(scratch/name),'500000',str((1<<63)+37)],capture_output=True,check=True)
        elapsed = time.monotonic() - start
        assert int(result.stdout.split(b'\n',1)[0]) == 544217
        times[name].append(elapsed)
report = {'checks':checks, 'times_s':times, 'median_s':{name:statistics.median(values) for name,values in times.items()}}
(scratch/'comparison.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report), flush=True)
