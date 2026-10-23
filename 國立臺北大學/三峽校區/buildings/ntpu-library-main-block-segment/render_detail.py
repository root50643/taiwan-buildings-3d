"""Supplementary actual-mesh central entrance and bridge interior views; no clipping/mesh edits."""
import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
A=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(A/'scene.blend'));s=bpy.context.scene;cam=s.camera
records=[]
# QA-only photographic fill lights; no building mesh added/hidden, scene file not resaved.
for name,loc,target,power,size in [('Atrium fill',(55,0,75),(55,0,25),12000,35),('Bridge fill',(42,-2,66),(44,5,63),150,3)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

for name,loc,target,scale,perspective in [('central-entrance',(420,0,62),(65,0,55),180,False),('lake-axis',(-420,0,80),(-25,0,40),230,False),('bridge-interior',(39.35,-11.0,62.6),(45,8.75,69.375),70,True),('atrium-interior',(-2.5,0,30),(100,0,50),70,True)]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP' if perspective else 'ORTHO';cam.data.ortho_scale=scale;cam.data.lens=22;cam.data.clip_start=.01;s.render.filepath=str(A/'qa'/f'{name}.png');bpy.ops.render.render(write_still=True)
 p=A/'qa'/f'{name}.png';raw=p.read_bytes();clean=raw[:8];pos=8
 while pos<len(raw):
  n=struct.unpack('>I',raw[pos:pos+4])[0];kind=raw[pos+4:pos+8]
  if kind not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:clean+=raw[pos:pos+n+12]
  pos+=n+12
 p.write_bytes(clean);records.append(dict(path='qa/'+p.name,sha256=hashlib.sha256(clean).hexdigest(),camera=loc,target=target,geometry_unchanged=True,clipping_or_hidden_mesh=False,qa_only_fill_lights=True))
(A/'qa/detail-render-validation.json').write_text(json.dumps(dict(scene_sha256=hashlib.sha256((A/'scene.blend').read_bytes()).hexdigest(),views=records),indent=2)+'\n')
