"""Supplemental true-mesh courtyard view from an internal camera; no cuts, hides or added geometry."""
import bpy,hashlib,json,struct
from pathlib import Path
from mathutils import Vector
A=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(A/'scene.blend'));s=bpy.context.scene;c=s.camera
before=hashlib.sha256((A/'scene.blend').read_bytes()).hexdigest()
def cv(p):return Vector(((40-p[0])*2.7,(p[1]-23)*2.7,p[2]*2.7))
c.data.type='PERSP';c.data.lens=19;c.data.clip_start=.1;c.location=cv((33,24,12));target=cv((55,18.5,5));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler()
# Interior studio fill lights reveal actual bridges/air gaps; no mesh is added.
for i,loc in enumerate([(46,21,14),(58,22,10)]):
 d=bpy.data.lights.new('QA interior fill '+str(i),'AREA');d.energy=70000;d.shape='DISK';d.size=30;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=cv(loc);o.rotation_euler=(cv((50,20,2))-o.location).to_track_quat('-Z','Y').to_euler()
s.cycles.samples=64;s.cycles.use_denoising=False
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.filepath=str(A/'qa/courtyard-detail.png');bpy.ops.render.render(write_still=True)
p=A/'qa/courtyard-detail.png';b=p.read_bytes();clean=b[:8];pos=8
while pos<len(b):
 n=struct.unpack('>I',b[pos:pos+4])[0];typ=b[pos+4:pos+8]
 if typ not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:clean+=b[pos:pos+n+12]
 pos+=n+12
p.write_bytes(clean);assert before==hashlib.sha256((A/'scene.blend').read_bytes()).hexdigest()
(A/'qa/courtyard-detail.json').write_text(json.dumps({'scene_sha256':before,'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'image_sha256':hashlib.sha256(clean).hexdigest(),'camera_mm':list(c.location),'target_mm':list(target),'no_geometry_modified_hidden_or_clipped':True,'studio_fill_lights':2,'samples':64,'denoising':False,'purpose':'Supplemental internal camera to expose court floor, bridges and stairs normally concealed by the actual membrane. Not an exterior source photo.'},indent=2)+'\n')
