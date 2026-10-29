import pathlib,sys,json,hashlib,numpy as np

original=pathlib.Path(sys.argv[1]);rebuilt=pathlib.Path(sys.argv[2]);report=pathlib.Path(sys.argv[3])
checks={};hashes={}
for name in ('model.stl','model.3mf','mesh-data.npz','construction-parts.json','editable-parts.json','build_model.py','render_model.py'):
    a=hashlib.sha256((original/name).read_bytes()).hexdigest()
    b=hashlib.sha256((rebuilt/name).read_bytes()).hexdigest()
    hashes[name]={'candidate':a,'clean_rebuild':b,'bytes_equal':a==b}
    checks[name+'_bytes_equal']=a==b
a=np.load(original/'mesh-data.npz');b=np.load(rebuilt/'mesh-data.npz')
for key in ('vertices','faces','materials'):
    checks[key+'_array_equal']=bool(np.array_equal(a[key],b[key]))
for name in ('construction-parts.json','editable-parts.json'):
    checks[name+'_semantic_equal']=json.loads((original/name).read_text())==json.loads((rebuilt/name).read_text())
candidate_audit=json.loads((report.parent/'candidate-scene-audit.json').read_text())
rebuild_audit=json.loads((report.parent/'rebuilt-scene-audit.json').read_text())
checks['candidate_scene_independent_audit_pass']=candidate_audit['passed']
checks['rebuilt_scene_independent_audit_pass']=rebuild_audit['passed']
for key in ('visible_vertex_hash_f32','visible_face_hash','visible_material_hash','expected_parts','actual_hidden_parts','visible_scope','visible_coordinate_frame'):
    checks['scene_'+key+'_equal']=candidate_audit['details'][key]==rebuild_audit['details'][key]
out={'passed':all(checks.values()),'checks':checks,'hashes':hashes,'scope':'Clean directory contains only copied source build/render/verify/validate scripts plus requirements; no original output geometry or source images were supplied. Scripts actually rerun. STL/3MF exact bytes and mesh-data geometry/material arrays compared. Blend bytes are intentionally not required; reopened scene full geometry, parts, transforms, material and evidence semantics independently audited.'}
report.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert out['passed']
