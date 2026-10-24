#!/usr/bin/env python3
"""Rebuild only appearance assets in an explicitly selected output directory."""
from pathlib import Path
import argparse,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--input',type=Path,default=Path(__file__).resolve().parent.parent/'model.stl');p.add_argument('--blender',default='blender');p.add_argument('--threads',type=int,default=4);a=p.parse_args();src=Path(__file__).resolve().parent;a.out.mkdir(parents=True,exist_ok=True)
def run(*cmd):subprocess.run([str(x)for x in cmd],check=True)
run(sys.executable,src/'build_appearance.py','--out',a.out,'--input',a.input)
run(sys.executable,src/'export_3mf.py','--out',a.out)
run(a.blender,'--background','--threads',a.threads,'--python',src/'render_appearance.py','--','--out',a.out)
run(a.blender,'--background',a.out/'ntus-changqi-appearance.blend','--python',src/'verify_blend.py','--','--out',a.out)
run(sys.executable,src/'verify_path_buffers.py','--blend',a.out/'ntus-changqi-appearance.blend','--report',a.out/'qa'/'path-buffer-audit.json')
run(sys.executable,src/'validate_appearance.py','--out',a.out,'--input',a.input)
