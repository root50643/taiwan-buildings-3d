"""blender -b -t 6 --python appearance/source/render_appearance.py
Four new appearance views from exact core-3MF triangles. No photos/textures.
"""
from pathlib import Path
import bpy,json,zipfile,xml.etree.ElementTree as E,os,struct,hashlib,sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
A=Path(__file__).resolve().parents[1];NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def lin(s):return s/12.92 if s<=.04045 else ((s+.055)/1.055)**2.4
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
scene['purpose']='Han Pao-Teh museum, photograph-informed exterior concrete/red/glass colors; not a printer profile'
scene['uncertainties']='Photo colors approximate; flat roof/unobserved flank neutral; only exterior prism red; original geometry/11 layer warnings retained; no physical-print validation'
with zipfile.ZipFile(A/'han-appearance.3mf') as z:r=E.fromstring(z.read('3D/3dmodel.model'))
me=r.find('m:resources/m:object/m:mesh',NS);vs=[[float(v.get(k)) for k in 'xyz'] for v in me.findall('m:vertices/m:vertex',NS)];ts=me.findall('m:triangles/m:triangle',NS);fs=[[int(t.get(k)) for k in ['v1','v2','v3']] for t in ts]
mesh=bpy.data.meshes.new('Exact original STL');mesh.from_pydata(vs,[],fs);mesh.update();ob=bpy.data.objects.new('HAN_unchanged_original_mesh',mesh);scene.collection.objects.link(ob)
ob['source_stl']='../model.stl';ob['source_sha256']='e4f25a2d8c02e58a57a263ee7ac93289e8818c456be86c251a1a26f9e0337e8e'
for p in json.loads((A/'palette.json').read_text())['materials']:
 m=bpy.data.materials.new(p['id']);rgba=[lin(int(p['srgb'][i:i+2],16)/255) for i in [1,3,5]]+[1];m.diffuse_color=rgba;m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=rgba;bs.inputs['Roughness'].default_value=.35 if 'glazing' in p['id'] else .75;m['approximate_srgb']=p['srgb'];mesh.materials.append(m)
for f,t in zip(mesh.polygons,ts):f.material_index=int(t.get('p1'))
world=bpy.data.worlds.new('Neutral world');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.52,.59,.65,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6
for i,(loc,power,size) in enumerate([((-110,-140,200),500000,130),((140,90,180),320000,140)]):
 d=bpy.data.lights.new('Softbox '+str(i),'AREA');d.energy=power;d.shape='DISK';d.size=size;l=bpy.data.objects.new(d.name,d);scene.collection.objects.link(l);l.location=loc;aim(l,(0,0,8))
camd=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camd);scene.collection.objects.link(cam);scene.camera=cam;camd.type='ORTHO';camd.clip_end=2000
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=96;scene.cycles.use_denoising=False;scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.2
views={'front':((-195,-240,170),(0,0,42),270),'rear':((195,230,165),(0,0,42),270),'top':((0,0,350),(0,0,0),230),'box-detail':((-90,-210,18),(8,-46,73),90)}
# Full-model views are all checked before any renders; detail view deliberately cropped.
for name,(loc,target,scale) in views.items():
 cam.location=loc;aim(cam,target);camd.ortho_scale=scale;bpy.context.view_layer.update()
 if name!='box-detail':
  q=[world_to_camera_view(scene,cam,Vector(v)) for v in vs];assert all(.035<v.x<.965 and .035<v.y<.965 and v.z>0 for v in q),name
# The projecting prism itself must remain inside the detail image; the
# surrounding building may be cropped intentionally.
loc,target,scale=views['box-detail'];cam.location=loc;aim(cam,target);camd.ortho_scale=scale;bpy.context.view_layer.update()
for v in vs:
 if -11<=v[0]<=33 and -61<=v[1]<=-42 and 58<=v[2]<=94:
  q=world_to_camera_view(scene,cam,Vector(v));assert .035<q.x<.965 and .035<q.y<.965 and q.z>0
(A/'previews').mkdir(exist_ok=True)
selected=views
if '--view' in sys.argv:
 name=sys.argv[sys.argv.index('--view')+1];assert name in views;selected={name:views[name]}
 records=[r for r in json.loads((A/'qa/render-manifest.json').read_text())['files'] if Path(r['path']).stem!=name]
else:records=[]
for name,(loc,target,scale) in selected.items():
 cam.location=loc;aim(cam,target);camd.ortho_scale=scale;scene.render.filepath=str(A/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
 p=A/'previews'/(name+'.png');raw=p.read_bytes();clean=raw[:8];pos=8
 while pos<len(raw):
  length=struct.unpack('>I',raw[pos:pos+4])[0];kind=raw[pos+4:pos+8]
  if kind not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:clean+=raw[pos:pos+length+12]
  pos+=length+12
 p.write_bytes(clean);records.append({'path':str(p.relative_to(A)),'bytes':len(clean),'sha256':hashlib.sha256(clean).hexdigest(),'camera_location':loc,'target':target,'ortho_scale':scale,'full_model':name!='box-detail'})
cam.location=views['front'][0];aim(cam,views['front'][1]);camd.ortho_scale=views['front'][2];scene.render.filepath='//previews/front.png'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
os.chdir(A);bpy.ops.wm.save_as_mainfile(filepath=str(A/'scene.blend'),compress=False)
(A/'qa/render-manifest.json').write_text(json.dumps({'blender':bpy.app.version_string,'samples':96,'denoising':False,'resolution':[1400,1000],'source':'Exact original STL triangles via appearance 3MF; no photos','visual_inspection_pending':True,'files':records},ensure_ascii=False,indent=2)+'\n')
