"""Check evaluated world triangles, units and true physical dimensions; fail closed."""
from pathlib import Path
import argparse,json,hashlib
import bpy,numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--scene');p.add_argument('--report');a=p.parse_args()
scene_path=Path(a.scene) if a.scene else ROOT/'models/v1/scene.blend'
report_path=Path(a.report) if a.report else ROOT/'qa/scene-check.json'
bpy.ops.wm.open_mainfile(filepath=str(scene_path))
scene=bpy.context.scene
objs=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('NIU_Cultivation')]
def canonical(v,f):
    rows=[]
    for tri in np.asarray(v,dtype=np.float32)[f]:
        points=[tuple(float(c) for c in q) for q in tri]
        # Cyclic order may rotate; reversal is not allowed. No rounding or repair.
        rows.append(min(tuple(points[i:]+points[:i]) for i in range(3)))
    return sorted(rows)
stl=trimesh.load_mesh(ROOT/'models/v1/model.stl',process=False)
assert len(objs)==1,'Expected exactly one printable model object'
o=objs[0];deps=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(deps);mesh=ev.to_mesh();mesh.calc_loop_triangles()
v=np.array([list(ev.matrix_world@q.co) for q in mesh.vertices],dtype=np.float32)
f=np.array([list(t.vertices) for t in mesh.loop_triangles],dtype=np.int64)
scene_tri=canonical(v,f);stl_tri=canonical(stl.vertices,stl.faces)
span=np.ptp(v.astype(np.float64),axis=0);stl_span=stl.extents
u=scene.unit_settings
units_ok=u.system=='METRIC' and u.length_unit=='MILLIMETERS' and abs(u.scale_length-0.001)<1e-9
physical_mm=span*u.scale_length*1000
record={'one_model_object':True,'scene_sha256':hashlib.sha256(scene_path.read_bytes()).hexdigest(),'scene_triangles':len(f),'stl_triangles':len(stl.faces),'oriented_binary32_triangle_sets_equal':scene_tri==stl_tri,'comparison':'Exact float32 world coordinates, cyclic triangle rotations only; no quantization, reflection, rounding or geometry repair','bound_stl_sha256':o.get('source_stl_sha256'),'actual_stl_sha256':hashlib.sha256((ROOT/'models/v1/model.stl').read_bytes()).hexdigest(),'scene_units':{'system':u.system,'scale_length':u.scale_length,'length_unit':u.length_unit},'units_correct':units_ok,'model_object_scale':list(o.scale),'model_matrix_world':[list(row) for row in o.matrix_world],'world_coordinate_bounds':[v.min(axis=0).tolist(),v.max(axis=0).tolist()],'stl_extents_mm':stl_span.tolist(),'scene_world_coordinate_extents':span.tolist(),'physical_scene_extents_mm':physical_mm.tolist(),'physical_size_matches_stl_mm':bool(np.allclose(physical_mm,stl_span,rtol=0,atol=1e-4)),'floor_policy':'render_floor_not_model is hidden in saved scene and excluded from STL'}
ev.to_mesh_clear()
record['passed']=record['oriented_binary32_triangle_sets_equal'] and record['units_correct'] and record['physical_size_matches_stl_mm'] and record['bound_stl_sha256']==record['actual_stl_sha256'] and list(o.scale)==[1.0,1.0,1.0]
report_path.parent.mkdir(parents=True,exist_ok=True);report_path.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));raise SystemExit(0 if record['passed'] else 1)
