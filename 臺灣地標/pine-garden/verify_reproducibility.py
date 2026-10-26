#!/usr/bin/env python3
"""Fresh-directory public-source-only build, with native and interchange verification."""
import pathlib,argparse,tempfile,subprocess,shutil,sys,json,hashlib,datetime
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);p.add_argument('--blender',default='blender');p.add_argument('--export-python',default=sys.executable);p.add_argument('--mesh-python',default=sys.executable);a=p.parse_args();root=a.out
names=['model.stl','face-material-map.json','parameters.json','legacy-validation.json','build_materials.py','material_geometry.py','mesh_topology.py','export_3mf.py','verify_material_controls.py','validate_self_intersections.py','render_preview.py','verify_blend.py','verify_path_buffers.py','verify_png_metadata.py','reproduce.py','requirements.txt','topology_controls.py','intersection_controls.py','verify_3mf_xml.py']
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
with tempfile.TemporaryDirectory(prefix='pine-public-only-rebuild-')as tmp:
 base=pathlib.Path(tmp);src=base/'public-inputs';src.mkdir();out=base/'output'
 for n in names:shutil.copyfile(pathlib.Path(__file__).with_name(n),src/n)
 subprocess.run([sys.executable,src/'reproduce.py','--out',out,'--blender',a.blender,'--export-python',a.export_python,'--mesh-python',a.mesh_python],check=True)
 D=np.load(root/'mesh-data.npz');E=np.load(out/'mesh-data.npz');arrays={k:bool(np.array_equal(D[k],E[k]))for k in D.files};assert all(arrays.values())
 exact={n:(root/n).read_bytes()==(out/n).read_bytes()for n in ['model.stl','model.3mf']};assert all(exact.values())
 previews=[]
 for f in sorted((root/'previews').glob('*.png')):
  assert f.read_bytes()==(out/'previews'/f.name).read_bytes();previews.append({'file':'previews/'+f.name,'png_bytes_identical':True,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 assert len(previews)==6
 reports={n:json.loads((out/'qa'/n).read_text())for n in ['geometry-material-validation.json','3mf-validation.json','blend-validation.json','native-edit-validation.json','raw-path-buffer-validation.json','png-metadata-validation.json','saved-scene-render-validation.json','self-intersection-validation.json','3mf-xml-validation.json','topology-controls.json','self-intersection-controls.json']}
 for n in ['raw-path-buffer-validation.json']:
  reports[n]={k:v for k,v in reports[n].items()if k not in('field_groups','public_authored_values')}
 report={'all_pass':True,'started_utc':started,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fresh_directory_public_inputs_only':True,'copied_input_files':names,'input_sha256':{n:hashlib.sha256((src/n).read_bytes()).hexdigest()for n in names},'network_or_source_pixels_required':False,'exact_arrays':arrays,'exact_artifact_bytes':exact,'previews':previews,'native_bytes_not_required_identical':'Blender embeds runtime/session data. Actual native geometry/material/privacy/editability checks and all rendered preview bytes must agree.','clean_rebuild_reports':reports}
(root/'qa/clean-public-rebuild-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'all_pass':True,'completed_utc':report['completed_utc'],'exact_artifact_bytes':exact,'previews':len(previews)},indent=2))
