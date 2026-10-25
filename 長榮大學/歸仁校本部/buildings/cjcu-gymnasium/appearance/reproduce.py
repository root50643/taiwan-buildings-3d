#!/usr/bin/env python3
"""Rebuild from original public STL + authored scripts and JSON only; no binaries copied."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=HERE.parent/'model.stl');p.add_argument('--out',type=Path,required=True);p.add_argument('--blender',default='blender');p.add_argument('--reader-python',default=sys.executable);a=p.parse_args();out=a.out.resolve();source=a.input.resolve()
assert out!=HERE and not out.exists(),'Choose a new empty output directory'
out.mkdir(parents=True)
inputs=['build_appearance.py','export_3mf.py','render_appearance.py','validate_appearance.py','verify_blend.py','verify_3mf.py','verify_path_buffers.py','test_controls.py','reproduce.py','roof-face-contract.json','palette.json','sources.json','requirements.txt','README.md']
for name in inputs:shutil.copy2(HERE/name,out/name)
def run(cmd):subprocess.run(cmd,check=True)
run([sys.executable,str(out/'build_appearance.py'),'--input',str(source),'--out',str(out)])
run([sys.executable,str(out/'export_3mf.py'),'--out',str(out)])
run([a.blender,'-b','--factory-startup','-t','4','--python-exit-code','1','-P',str(out/'render_appearance.py'),'--','--out',str(out)])
run([sys.executable,str(out/'validate_appearance.py'),'--input',str(source),'--out',str(out)])
run([a.reader_python,str(out/'verify_3mf.py'),'--out',str(out)])
run([a.blender,'-b',str(out/'cjcu-gymnasium-roof-illustration.blend'),'-t','4','--python-exit-code','1','-P',str(out/'verify_blend.py'),'--','--out',str(out)])
run([sys.executable,str(out/'verify_path_buffers.py'),'--blend',str(out/'cjcu-gymnasium-roof-illustration.blend'),'--report',str(out/'qa'/'path-buffer-validation.json')])
run([sys.executable,str(out/'test_controls.py'),'--input',str(source),'--out',str(out),'--blender',a.blender])
from PIL import Image
rows=[]
for path in sorted((HERE/'previews').glob('*.png')):
 fresh=out/'previews'/path.name;aimg=Image.open(path).convert('RGBA');bimg=Image.open(fresh).convert('RGBA');same=path.read_bytes()==fresh.read_bytes();pixels=aimg.size==bimg.size and aimg.tobytes()==bimg.tobytes();assert same and pixels;rows.append({'name':path.name,'bytes_identical':same,'pixels_identical':pixels,'sha256':hashlib.sha256(fresh.read_bytes()).hexdigest()})
assert len(rows)==9
for name in ('mesh-data.npz','face-materials.csv','cjcu-gymnasium-roof-illustration.3mf'):assert (HERE/name).read_bytes()==(out/name).read_bytes()
report={'only_input_geometry':'original public model.stl','input_stl_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'copied_inputs':inputs,'copied_model_or_scene_or_preview_binaries':False,'rebuilt_npz_face_CSV_and_3MF_bytes_identical':True,'Blender_semantic_geometry_materials_native_edits_and_privacy_reverified':True,'PNG_count':9,'renders':rows,'scope':'Identical bytes/pixels on tested Blender 4.3.2/software-renderer environment; GPU or Blender changes may change preview bytes.'}
(out/'qa'/'clean-rebuild-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
