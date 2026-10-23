"""Two unchanged-mesh detail views, no clipping, no alternate geometry."""
import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
A=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(A/'scene.blend'));scene=bpy.context.scene;cam=scene.camera
before=hashlib.sha256((A/'scene.blend').read_bytes()).hexdigest();rows=[]
for name,loc,target,scale in [('entry-detail',(-96,0,16),(4,0,35),170),('roof-detail',(-130,-170,240),(40,10,90),230)]:
 cam.data.type='ORTHO';cam.data.ortho_scale=scale;cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();p=A/'qa'/(name+'.png')
 if name=='entry-detail':
  cam.data.type='PERSP';cam.data.lens=17;cam.data.clip_start=.1
  d=bpy.data.lights.new('QA atrium studio fill','POINT');d.energy=60000;d.shadow_soft_size=12;o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=(-65,0,38)
 scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
 if name=='entry-detail':bpy.data.objects.remove(o,do_unlink=True)
 raw=p.read_bytes();clean=raw[:8];pos=8
 while pos<len(raw):
  n=struct.unpack('>I',raw[pos:pos+4])[0];kind=raw[pos+4:pos+8]
  if kind not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:clean+=raw[pos:pos+n+12]
  pos+=n+12
 p.write_bytes(clean);rows.append({'path':'qa/'+p.name,'sha256':hashlib.sha256(clean).hexdigest(),'camera':loc,'target':target,'ortho_scale':scale,'mesh_unchanged':True,'projection':('PERSP 17mm with temporary studio fill' if name=='entry-detail' else 'ORTHO')})
assert hashlib.sha256((A/'scene.blend').read_bytes()).hexdigest()==before
(A/'qa/detail-render-validation.json').write_text(json.dumps({'scene_sha256':before,'no_mesh_modification_or_cutting':True,'files':rows},indent=2)+'\n')
