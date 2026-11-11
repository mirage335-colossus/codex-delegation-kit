#!/usr/bin/env python3
import pathlib, subprocess, tempfile
p=pathlib.Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='dispatch-public-') as td:
    exe=pathlib.Path(td)/'participant'
    subprocess.run([str(p/'build.sh'),str(exe)],check=True)
    for args in (['500000'],['500000','--deny-avx2']):
        r=subprocess.run([str(exe),*args],text=True,capture_output=True,check=True)
        print(r.stdout,end='')
