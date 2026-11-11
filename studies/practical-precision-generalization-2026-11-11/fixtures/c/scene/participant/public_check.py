#!/usr/bin/env python3
import pathlib, subprocess, tempfile
p=pathlib.Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='scene-public-') as td:
    exe=pathlib.Path(td)/'participant'
    subprocess.run([str(p/'build.sh'),str(exe)],check=True)
    r=subprocess.run([str(exe),'12','320','180','1280','720','8','auto'],text=True,capture_output=True,check=True)
    print(r.stdout,end='')
