"""Blender: check every actual STL vertex against both corrected elevation cameras."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'scene.blend'));s=bpy.context.scene;c=s.camera;m=bpy.data.objects['Tajen_Admin_Library'];v=[m.matrix_world@q.co for q in m.data.vertices]
x=(min(q.x for q in v)+max(q.x for q in v))/2;z=(min(q.z for q in v)+max(q.z for q in v))/2;rows=[]
for n,y in [('south-elevation',-260),('north-elevation',260)]:
 c.location=(x,y,z);c.rotation_euler=(Vector((x,0,z))-c.location).to_track_quat('-Z','Y').to_euler();inv=c.rotation_euler.to_matrix().transposed();p=[inv@(m.matrix_world@Vector(q)-c.location) for q in m.bound_box];w=max(q.x for q in p)-min(q.x for q in p);h=max(q.y for q in p)-min(q.y for q in p);c.data.ortho_scale=max(w,h*s.render.resolution_x/s.render.resolution_y)*1.18;bpy.context.view_layer.update();a=[world_to_camera_view(s,c,q) for q in v];bad=[i for i,q in enumerate(a) if not(0<=q.x<=1 and 0<=q.y<=1 and q.z>0)];rows.append({'preview':n,'camera_x':x,'ortho_scale':c.data.ortho_scale,'vertices_checked':len(v),'outside_count':len(bad),'normalized_bounds':[[min(q[i] for q in a),max(q[i] for q in a)] for i in range(2)]});assert not bad
(R/'elevation-framing-check.json').write_text(json.dumps({'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'passed':True,'rows':rows},indent=2))
