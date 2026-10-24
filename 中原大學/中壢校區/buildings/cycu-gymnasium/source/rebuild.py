#!/usr/bin/env python3
"""Rebuild every model format and render from scripts + parameters + palette only."""
import argparse,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--geometry-python',default=sys.executable);p.add_argument('--three-mf-python',default='python3');p.add_argument('--blender',default='blender');p.add_argument('--threads',type=int,default=4);a=p.parse_args();s=Path(__file__).resolve().parent;a.out.mkdir(parents=True,exist_ok=True)
def run(*cmd):subprocess.run([str(v)for v in cmd],check=True)
run(a.geometry_python,s/'build_geometry.py','--out',a.out)
run(a.geometry_python,s/'validate_geometry.py','--out',a.out)
run(a.three_mf_python,s/'export_3mf.py','--out',a.out)
run(a.blender,'--background','--python-exit-code','1','--threads',a.threads,'--python',s/'render_model.py','--','--out',a.out)
run(a.blender,'--background','--python-exit-code','1','--threads',a.threads,a.out/'cycu-gymnasium.blend','--python',s/'verify_blend.py','--','--out',a.out)
run(a.three_mf_python,s/'verify_path_buffers.py','--blend',a.out/'cycu-gymnasium.blend','--report',a.out/'qa/path-buffer-audit.json')
