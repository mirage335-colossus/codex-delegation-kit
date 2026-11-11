#!/usr/bin/env python3
import pathlib, subprocess, tempfile
p=pathlib.Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='burst-public-') as td:
    exe=pathlib.Path(td)/'participant'
    subprocess.run([str(p/'build.sh'),str(exe)],check=True)
    r=subprocess.run([str(exe),'4','200000'],text=True,capture_output=True,check=True)
    print(r.stdout,end='')
