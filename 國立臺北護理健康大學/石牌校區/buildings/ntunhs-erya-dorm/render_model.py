"""Blender 4.3.2+, render actual unchanged surface and save editable scene."""
import bpy,json,zipfile,xml.etree.ElementTree as E,hashlib,struct,os,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
A=Path(__file__).resolve().parent;NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
with zipfile.ZipFile(A/'model.3mf') as z:root=E.fromstring(z.read('3D/3dmodel.model'))
mesh=root.find('m:resources/m:object/m:mesh',NS);vs=[[float(v.get(k)) for k in 'xyz'] for v in mesh.findall('m:vertices/m:vertex',NS)];ts=mesh.findall('m:triangles/m:triangle',NS);fs=[[int(t.get(k)) for k in ['v1','v2','v3']] for t in ts]
me=bpy.data.meshes.new('NTUNHS Erya third student dormitory / 北護爾雅樓');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('NTUNHS Erya third student dormitory / 北護爾雅樓 - bounded approximate study',me);bpy.context.collection.objects.link(ob)
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
for p in json.loads((A/'palette.json').read_text())['materials']:
 m=bpy.data.materials.new(p['id']);m.use_nodes=True;rgba=[lin(int(p['srgb'][i:i+2],16)/255) for i in [1,3,5]]+[p.get('alpha',255)/255];m.diffuse_color=rgba;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=rgba;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.28 if 'metal' in p['id'] else .62;m.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=p.get('alpha',255)/255;m.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=.65 if 'metal' in p['id'] else .01;me.materials.append(m)
for poly,t in zip(me.polygons,ts):poly.material_index=int(t.get('p1'))
ob['original_STL_sha256']=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest();ob['limitations']='2021 contractor completion-photo exterior approximation. 13 aboveground floors; no B2, no Xuesi, gym or old dormitories. Rear upper windows and gym-side low openings approximate, not surveyed. Opaque glazing; supports required; no physical print.'
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
world=bpy.data.worlds.new('Neutral studio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.36,.40,.46,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7
# Studio lights only; no floor mesh that could be mistaken for delivered geometry.
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
for i,(loc,power,size) in enumerate([((-140,-180,280),700000,180),((180,70,240),500000,160),((80,220,120),250000,130)]):
 d=bpy.data.lights.new('Softbox '+str(i),'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,35))
camd=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camd);scene.collection.objects.link(cam);scene.camera=cam;camd.type='ORTHO';camd.clip_end=2000
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=48;scene.cycles.use_denoising=False;scene.cycles.seed=0;scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
views={'front':((-280,370,260),(0,0,101),265),'rear':((280,-370,250),(0,0,100),265),'elevation':((0,440,103),(0,0,103),245),'top':((0,0,500),(0,0,0),180),'left_oblique':((320,300,255),(0,0,101),265)}
records=[]
for name,(loc,target,scale) in views.items():
 camd.type='ORTHO';camd.lens=22;cam.location=loc;aim(cam,target);camd.ortho_scale=scale;bpy.context.view_layer.update();q=[world_to_camera_view(scene,cam,Vector(v)) for v in vs];assert all(.035<p.x<.965 and .035<p.y<.965 and p.z>0 for p in q),name
 scene.render.filepath=str(A/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
 p=A/'previews'/(name+'.png');raw=p.read_bytes();clean=raw[:8];pos=8
 while pos<len(raw):
  n=struct.unpack('>I',raw[pos:pos+4])[0];kind=raw[pos+4:pos+8]
  if kind not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:clean+=raw[pos:pos+n+12]
  pos+=n+12
 p.write_bytes(clean);records.append({'path':'previews/'+name+'.png','bytes':len(clean),'sha256':hashlib.sha256(clean).hexdigest(),'camera':loc,'target':target,'ortho_scale':scale,'all_vertices_in_frame':True})
camd.type='ORTHO';camd.lens=22;cam.location=views['front'][0];aim(cam,views['front'][1]);camd.ortho_scale=views['front'][2];scene.render.filepath='//previews/front.png'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
os.chdir(A);bpy.ops.wm.save_as_mainfile(filepath=str(A/'scene.blend'),compress=False)
(A/'qa/render-manifest.json').write_text(json.dumps({'blender':bpy.app.version_string,'samples':48,'resolution':[1200,1200],'files':records},indent=2)+'\n')
