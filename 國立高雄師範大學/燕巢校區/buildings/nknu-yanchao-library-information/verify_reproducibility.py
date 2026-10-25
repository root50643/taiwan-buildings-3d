#!/usr/bin/env python3
"""Independent fresh-directory rebuild using only copied public source inputs."""
import argparse,pathlib,tempfile,subprocess,shutil,json,hashlib,sys
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);p.add_argument('--blender',default='blender');p.add_argument('--export-python',default=sys.executable);a=p.parse_args();root=a.out
names=['build_model.py','parameters.json','export_3mf.py','render_model.py','validate_model.py','validate_self_intersections.py','intersection_controls.py','verify_blend.py','verify_path_buffers.py','verify_png_metadata.py','reproduce.py','requirements-model.txt']
with tempfile.TemporaryDirectory(prefix='nknu-public-rebuild-')as tmp:
 base=pathlib.Path(tmp);src=base/'public-inputs';src.mkdir();out=base/'output'
 for name in names:shutil.copyfile(pathlib.Path(__file__).with_name(name),src/name)
 subprocess.run([sys.executable,str(src/'reproduce.py'),'--out',str(out),'--blender',a.blender,'--export-python',a.export_python],check=True)
 subprocess.run([sys.executable,str(src/'verify_png_metadata.py'),'--out',str(out)],check=True)
 D=np.load(root/'mesh-data.npz');E=np.load(out/'mesh-data.npz');arrays={k:bool(np.array_equal(D[k],E[k]))for k in ['vertices','faces','materials']};assert all(arrays.values())
 stl=(root/'nknu-yanchao-library-information.stl').read_bytes()==(out/'nknu-yanchao-library-information.stl').read_bytes();assert stl
 extra={n:(root/n).read_bytes()==(out/n).read_bytes()for n in ['construction-parts.json','editable-parts.json','build-summary.json']};assert all(extra.values())
 previews=[]
 for f in sorted((root/'previews').glob('*.png')):
  g=out/'previews'/f.name;aa=np.asarray(Image.open(f));bb=np.asarray(Image.open(g));eq=bool(np.array_equal(aa,bb));byt=f.read_bytes()==g.read_bytes();assert eq and byt
  previews.append({'file':'previews/'+f.name,'dimensions':list(Image.open(f).size),'pixels_identical':eq,'png_bytes_identical':byt,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 assert len(previews)==9
 report={'fresh_directory_public_inputs_only':True,'copied_input_files':names,'input_sha256':{n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},'network_or_reference_images_required':False,'geometry_arrays_identical':arrays,'stl_bytes_identical':stl,'component_data_and_build_summary_identical':extra,'preview_count':len(previews),'previews':previews,'clean_rebuild_3mf_strict_validation':json.loads((out/'qa/3mf-validation.json').read_text()),'clean_rebuild_native_edit_validation':json.loads((out/'qa/native-edit-validation.json').read_text()),'clean_rebuild_full_sdna_validation':{k:v for k,v in json.loads((out/'qa/raw-path-buffer-validation.json').read_text()).items()if k not in ('field_groups','public_authored_values')},'clean_rebuild_png_metadata_validation':json.loads((out/'qa/png-metadata-validation.json').read_text()),'clean_rebuild_saved_scene_render_validation':json.loads((out/'qa/saved-scene-render-validation.json').read_text()),'all_pass':True}
(root/'qa/clean-public-rebuild-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
