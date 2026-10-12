"""Run: blender -b scene.blend -P check_blend.py
Checks that the saved editable mesh has exactly the final STL's triangle geometry.
Studio props are excluded by selecting the explicitly named printable object.
"""
import bpy,numpy as np,struct,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
obj=bpy.data.objects.get('Print-ready exterior (mm)')
assert obj is not None and obj.type=='MESH','Printable object missing'
obj.data.calc_loop_triangles()
v=np.array([obj.matrix_world@p.co for p in obj.data.vertices],dtype=float)
f=np.array([list(t.vertices) for t in obj.data.loop_triangles],dtype=int);tri=v[f]
b=(HERE/'model.stl').read_bytes();count=struct.unpack_from('<I',b,80)[0]
dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attr','<u2')]);stl=np.frombuffer(b,dtype=dtype,offset=84,count=count)['vertices']
def canonical(t):
 rows=[]
 for vv in np.round(np.asarray(t,dtype=np.float64),5):
  vv=vv[np.lexsort((vv[:,2],vv[:,1],vv[:,0]))];rows.append(vv.reshape(-1))
 rows=np.array(rows);rows=rows[np.lexsort(tuple(rows[:,i] for i in range(8,-1,-1)))];return hashlib.sha256(rows.astype('<f8').tobytes()).hexdigest()
r={'passed':canonical(tri)==canonical(stl),'blend_triangle_count':len(tri),'stl_triangle_count':len(stl),'blend_geometry_sha256':canonical(tri),'stl_geometry_sha256':canonical(stl),'selected_print_object':obj.name,'scene_unit_scale_m':bpy.context.scene.unit_settings.scale_length,'studio_is_not_print_geometry':True}
(HERE/'blend_validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));assert r['passed']
