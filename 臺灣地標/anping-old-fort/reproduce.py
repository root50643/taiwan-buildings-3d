#!/usr/bin/env python3
"""Offline rebuild of existing-model materials; only public files are read."""
import argparse,pathlib,subprocess,sys,os
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[key]="2"
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);p.add_argument('--blender',default='blender');p.add_argument('--export-python',default=sys.executable);p.add_argument('--mesh-python',default=sys.executable);a=p.parse_args();src=pathlib.Path(__file__).resolve().parent;a.out.mkdir(parents=True,exist_ok=True)
def run(args):subprocess.run([str(x)for x in args],check=True)
run([sys.executable,src/'build_materials.py','--out',a.out])
run([sys.executable,src/'verify_baseline.py','--out',a.out])
run([a.export_python,src/'export_3mf.py','--out',a.out])
run([sys.executable,src/'verify_3mf_xml.py','--out',a.out])
run([a.mesh_python,src/'topology_controls.py','--out',a.out])
run([a.mesh_python,src/'intersection_controls.py','--out',a.out])
run([sys.executable,src/'verify_material_controls.py','--out',a.out])
run([a.mesh_python,src/'validate_self_intersections.py','--out',a.out])
run([a.blender,'--factory-startup','--threads','2','--python-exit-code','1','--background','--python',src/'render_preview.py','--','--out',a.out])
run([a.blender,'--factory-startup','--threads','2','--python-exit-code','1','--background',a.out/'scene.blend','--python',src/'verify_blend.py'])
run([sys.executable,src/'verify_path_buffers.py','--blend',a.out/'scene.blend','--report',a.out/'qa/raw-path-buffer-validation.json','--blender',a.blender])
run([sys.executable,src/'verify_png_metadata.py','--out',a.out])
print('Public-only exact geometry/material rebuild and all checks completed.')
