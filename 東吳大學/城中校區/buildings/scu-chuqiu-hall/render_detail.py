"""Supplemental true-mesh east facade view; no cuts, hidden objects or substitute mesh."""
import bpy,hashlib,json,struct
from pathlib import Path
from mathutils import Vector
A=Path(__file__).resolve().parent
before=hashlib.sha256((A/'scene.blend').read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(A/'scene.blend'));s=bpy.context.scene;c=s.camera
c.data.type='PERSP';c.data.lens=50;c.data.clip_start=.1;c.location=Vector((280,-68,30));target=Vector((110,0,41));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler()
s.cycles.samples=64;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.filepath=str(A/'qa/east-entry-detail.png');bpy.ops.render.render(write_still=True)
p=A/'qa/east-entry-detail.png';b=p.read_bytes();clean=b[:8];pos=8
while pos<len(b):
 n=struct.unpack('>I',b[pos:pos+4])[0];typ=b[pos+4:pos+8]
 if typ not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:clean+=b[pos:pos+n+12]
 pos+=n+12
p.write_bytes(clean);assert before==hashlib.sha256((A/'scene.blend').read_bytes()).hexdigest()
(A/'qa/east-entry-detail.json').write_text(json.dumps({'scene_sha256':before,'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'image_sha256':hashlib.sha256(clean).hexdigest(),'camera_mm':list(c.location),'target_mm':list(target),'no_geometry_modified_hidden_or_clipped':True,'samples':64,'denoising':False,'purpose':'Close true-mesh east facade: real 3F–5F recessed wall, projecting 6F narrow-window band and soffit ribs, supported entrance canopy. Not a source photo.'},indent=2)+'\n')
