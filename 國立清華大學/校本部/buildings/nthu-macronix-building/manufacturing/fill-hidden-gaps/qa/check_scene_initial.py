"""Read saved variant Blender scene; compare every world-space triangle."""
from pathlib import Path
import hashlib, json
import bpy
import numpy as np
import trimesh

HERE=Path(__file__).resolve().parent
V=HERE.parent
output=HERE/'scene-check.json'
if output.exists():raise FileExistsError('Refusing to overwrite scene evidence.')
def canonical(tri):
    rows=sorted(tuple(sorted(tuple(np.rint(v*1e5).astype(np.int64)) for v in face)) for face in tri)
    return hashlib.sha256(np.asarray(rows,dtype='<i8').tobytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(V/'scene.blend'))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
if len(objects)!=1:raise ValueError('Expected precisely one model mesh.')
obj=objects[0];obj.data.calc_loop_triangles()
world=np.array([tuple(obj.matrix_world@v.co) for v in obj.data.vertices])
tri=world[np.array([tuple(t.vertices) for t in obj.data.loop_triangles])]
mesh=trimesh.load(V/'model.stl',force='mesh',process=False)
report=dict(stl_sha256=hashlib.sha256((V/'model.stl').read_bytes()).hexdigest(),scene_sha256=hashlib.sha256((V/'scene.blend').read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),mesh_objects=len(objects),scene_triangles=len(tri),stl_triangles=len(mesh.triangles),world_coordinate_quantum_mm=1e-5,scene_triangle_multiset_sha256=canonical(tri),stl_triangle_multiset_sha256=canonical(mesh.triangles),unit_system=bpy.context.scene.unit_settings.system,unit_scale=bpy.context.scene.unit_settings.scale_length,length_unit=bpy.context.scene.unit_settings.length_unit,model_stl_sha256_property=obj.get('stl_sha256'),formal_slicer_run=False,physical_print_test=False)
report['triangle_multisets_equal']=report['scene_triangle_multiset_sha256']==report['stl_triangle_multiset_sha256']
report['passed']=report['triangle_multisets_equal'] and report['model_stl_sha256_property']==report['stl_sha256'] and report['unit_scale']==.001 and report['length_unit']=='MILLIMETERS'
output.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
assert report['passed']
