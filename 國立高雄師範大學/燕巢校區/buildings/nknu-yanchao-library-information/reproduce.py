#!/usr/bin/env python3
"""Rebuild solely from public source inputs. No photographs, network or Blender add-ons required."""
import argparse,pathlib,subprocess,sys,shutil,json
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);p.add_argument('--blender',default='blender');p.add_argument('--export-python',default=sys.executable);p.add_argument('--skip-slow-checks',action='store_true');a=p.parse_args();src=pathlib.Path(__file__).resolve().parent;a.out.mkdir(parents=True,exist_ok=True)
def run(cmd):subprocess.run([str(x)for x in cmd],check=True)
run([sys.executable,src/'build_model.py','--out',a.out,'--params',src/'parameters.json'])
run([a.export_python,src/'export_3mf.py','--out',a.out])
run([sys.executable,src/'validate_model.py','--out',a.out])
if not a.skip_slow_checks:
 run([sys.executable,src/'validate_self_intersections.py','--out',a.out]);run([sys.executable,src/'intersection_controls.py','--out',a.out])
run([a.blender,'--factory-startup','--background','--python',src/'render_model.py','--','--out',a.out])
run([a.blender,'--factory-startup','--background',a.out/'nknu-yanchao-library-information.blend','--python',src/'verify_blend.py'])
run([sys.executable,src/'verify_path_buffers.py','--blend',a.out/'nknu-yanchao-library-information.blend','--report',a.out/'qa/raw-path-buffer-validation.json','--blender',a.blender])
run([sys.executable,src/'verify_png_metadata.py','--out',a.out])
print('Rebuild and requested checks completed.')
