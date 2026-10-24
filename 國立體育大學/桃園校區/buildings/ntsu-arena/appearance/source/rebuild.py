#!/usr/bin/env python3
"""Rebuild using only original public STL, these sources, parameters and palette."""
from pathlib import Path
import sys
if sys.flags.optimize:raise RuntimeError("Run validation without -O")
import argparse,subprocess,sys,os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
p=argparse.ArgumentParser();p.add_argument('--stl',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--blender',default='blender');p.add_argument('--params',type=Path);p.add_argument('--palette',type=Path);a=p.parse_args();src=Path(__file__).resolve().parent;base=src.parent
assert not a.out.exists() or not any(a.out.iterdir()),'Use a new empty output directory'
def run(args):subprocess.run(list(map(str,args)),check=True)
run([sys.executable,src/'build_appearance.py','--stl',a.stl,'--params',a.params or base/'parameters.json','--palette',a.palette or base/'palette.json','--out',a.out])
run([a.blender,'-b','-t','4','-P',src/'render_model.py','--','--stl',a.stl,'--out',a.out])
run([sys.executable,src/'verify_3mf.py','--stl',a.stl,'--out',a.out])
run([a.blender,'-b',a.out/'ntsu-arena-appearance.blend','-t','4','-P',src/'verify_blend.py','--','--stl',a.stl,'--out',a.out])
run([sys.executable,src/'test_fail_closed.py','--stl',a.stl,'--out',a.out])
run([sys.executable,src/'verify_path_buffers.py','--blend',a.out/'ntsu-arena-appearance.blend','--report',a.out/'qa/path-buffer-audit.json'])

run([sys.executable,src/"test_privacy.py","--blend",a.out/"ntsu-arena-appearance.blend","--blender",a.blender,"--report",a.out/"qa/privacy-validation.json"])
run([sys.executable,src/"test_3mf_rejection.py","--stl",a.stl,"--out",a.out])
