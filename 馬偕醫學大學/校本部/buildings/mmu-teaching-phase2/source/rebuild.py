#!/usr/bin/env python3
"""Rebuild from public numeric parameters and Python only; source photos are not used."""
import argparse,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--parameters',type=Path);p.add_argument('--model-python',default=sys.executable);p.add_argument('--export-python',default=sys.executable);p.add_argument('--blender',default='blender');p.add_argument('--skip-renders',action='store_true');a=p.parse_args();src=Path(__file__).resolve().parent;params=a.parameters or src.parent/'parameters.json';a.out.mkdir(parents=True,exist_ok=True)
def run(cmd):subprocess.run([str(x)for x in cmd],check=True)
run([a.model_python,src/'build_geometry.py','--parameters',params,'--out',a.out]);run([a.export_python,src/'export_3mf.py','--out',a.out]);run([a.model_python,src/'validate_geometry.py','--out',a.out])
if not a.skip_renders:
 run([a.blender,'--background','--factory-startup','--python',src/'render_model.py','--','--out',a.out]);run([a.blender,'--background',a.out/'mmu-teaching-phase2.blend','--python',src/'verify_blend.py','--','--out',a.out]);run([a.model_python,src/'verify_path_buffers.py','--blend',a.out/'mmu-teaching-phase2.blend','--report',a.out/'qa/blend-path-validation.json'])
run([a.model_python,src/'validate_self_intersections.py','--out',a.out])
