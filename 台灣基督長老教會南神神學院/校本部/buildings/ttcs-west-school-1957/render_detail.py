"""Uncut delivered mesh: gallery from south and central passage at human-scale height."""
import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
A=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(A/'scene.blend'));s=bpy.context.scene;c=s.camera

def point(p):return Vector(((p[0]-4.25)*5.5,(p[1]-16.35)*5.5,p[2]*5.5))
r=[]
for name,loc,target,lens in [('corridor-detail',(7.3,-3.5,1.8),(7.3,13,1.8),23),('passage-detail',(12,15.75,1.85),(-2,15.75,1.85),25)]:
 c.data.type='PERSP';c.data.lens=lens;c.data.clip_start=.05;c.location=point(loc);c.rotation_euler=(point(target)-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(A/'qa'/(name+'.png'));bpy.ops.render.render(write_still=True);p=A/'qa'/(name+'.png');raw=p.read_bytes();clean=raw[:8];pos=8
 while pos<len(raw):
  n=struct.unpack('>I',raw[pos:pos+4])[0];kind=raw[pos+4:pos+8]
  if kind not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:clean+=raw[pos:pos+n+12]
  pos+=n+12
 p.write_bytes(clean);r.append(dict(path='qa/'+name+'.png',sha256=hashlib.sha256(clean).hexdigest(),camera_proportional=loc,target_proportional=target,mesh_clipping=False,geometry_or_material_edits=False))
(A/'qa/detail-render-validation.json').write_text(json.dumps(dict(scene_sha256=hashlib.sha256((A/'scene.blend').read_bytes()).hexdigest(),files=r,method='Reopen delivered scene; camera-only changes; no mesh clipping, hidden objects, geometry modifications or materials changes'),indent=2)+'\n')
