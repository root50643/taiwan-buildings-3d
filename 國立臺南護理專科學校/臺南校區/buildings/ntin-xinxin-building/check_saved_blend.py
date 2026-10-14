"""Run inside Blender; inspect the saved Blend against actual STL, then rerender."""
from pathlib import Path
import bpy,json,struct,sys,hashlib
from mathutils import Vector
import numpy as np
R=Path(__file__).resolve().parent
D=Path(sys.argv[sys.argv.index('--')+1]);D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'scene.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1
m=meshes[0];m.data.calc_loop_triangles()
a=np.array([[list(m.matrix_world@m.data.vertices[i].co) for i in face.vertices] for face in m.data.loop_triangles],dtype=np.float32)
raw=(R/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0]
b=np.frombuffer(raw,dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')]),offset=84,count=n)['vertices']
def canonical(tris):
 rows=[]
 for tri in tris:
  p=[tuple(float(z) for z in v) for v in tri]
  # Cyclic shifts preserve winding; do not permit a flipped triangle.
  rows.append(min(tuple(p[i:]+p[:i]) for i in range(3)))
 return sorted(rows)
checks={'one_printable_mesh_object':len(meshes)==1,'saved_blend_oriented_triangles_match_stl_exactly':canonical(a)==canonical(b),'saved_blend_stl_sha256_matches':m['source_stl_sha256']==hashlib.sha256(raw).hexdigest(),'unit_scale_is_mm':abs(bpy.context.scene.unit_settings.scale_length-.001)<1e-9,'no_modifiers_changing_printable_geometry':len(m.modifiers)==0,'scene_has_no_external_images':all(im.source!='FILE' for im in bpy.data.images)}
assert all(checks.values()),checks
scene=bpy.context.scene;cam=scene.camera
for name,loc,aim in [('front',(-100,-225,105),(0,-1,18)),('rear',(100,225,100),(0,-1,18)),('elevation',(0,-260,23),(0,0,23)),('side',(-250,-25,68),(0,0,18)),('top',(0,0,300),(0,0,0))]:
 cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
 inv=cam.rotation_euler.to_matrix().transposed();q=[inv@(m.matrix_world@Vector(c)-cam.location) for c in m.bound_box]
 width=max(v.x for v in q)-min(v.x for v in q);height=max(v.y for v in q)-min(v.y for v in q)
 cam.data.ortho_scale=max(width,height*900/580)*1.16
 scene.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)
(D/'blend-check.json').write_text(json.dumps({'checks':checks,'passed':True,'triangles':len(a)},indent=2))
