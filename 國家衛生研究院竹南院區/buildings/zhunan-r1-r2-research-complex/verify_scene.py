"""Verify the saved Blender building mesh matches every STL triangle.
Usage: blender -b -t 6 -P verify_scene.py
"""
import bpy,hashlib,json,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(HERE/'scene.blend'))
obj=bpy.data.objects.get('NHRI R1 R2 printable solid')
assert obj and obj.type=='MESH'
blob=(HERE/'model.stl').read_bytes();count=struct.unpack_from('<I',blob,80)[0]
assert len(blob)==84+50*count
triangles=[]
for i in range(count):
    vals=struct.unpack_from('<12fH',blob,84+i*50)
    triangles.append([vals[3:6],vals[6:9],vals[9:12]])
def canonical(tris):
    faces=sorted(tuple(sorted(tuple(round(float(c),5) for c in vert) for vert in tri)) for tri in tris)
    return hashlib.sha256(json.dumps(faces,separators=(',',':')).encode()).hexdigest()
obj.data.calc_loop_triangles()
world_tris=[[(obj.matrix_world @ obj.data.vertices[j].co)[:] for j in t.vertices] for t in obj.data.loop_triangles]
a=canonical(triangles);b=canonical(world_tris)
report={'passed':a==b,'stl_triangles':count,'blend_triangles':len(world_tris),'coordinate_rounding_mm':0.00001,'stl_geometry_sha256':a,'blend_geometry_sha256':b,'stl_file_sha256':hashlib.sha256(blob).hexdigest(),'mesh_object':obj.name,'other_objects':'Only studio floor, cameras and lights; not part of print geometry.'}
(HERE/'scene-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2));assert report['passed']
