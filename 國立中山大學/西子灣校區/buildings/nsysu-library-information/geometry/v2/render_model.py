"""Blender 4.3.2: blender --background --factory-startup --disable-autoexec -t 4 -P render_model.py -- [--out DIR].
Nine deterministic actual-mesh views; plan is the actual solid clipped at z=6 mm.
Single inherited neutral preview material, NOT source-faithful restored color.
"""
import argparse, json, pathlib, sys, struct
import bpy, numpy as np
from mathutils import Vector
ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);ap.add_argument('--views',default='');ap.add_argument('--no-render',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=a.out;p=json.loads((root/'params.json').read_text());(root/'previews').mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
mat=bpy.data.materials.new('Warm stone preview only — not restored color');mat.diffuse_color=tuple(p['neutral_preview_rgba']);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=tuple(p['neutral_preview_rgba']);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.80
mat['appearance_status']='Neutral inherited preview material only. All-side real-color reconstruction HOLD. No image textures.'
def mesh_object(name,datafile):
 d=np.load(root/datafile);m=bpy.data.meshes.new(name);m.from_pydata(d['vertices'].tolist(),[],d['faces'].tolist());m.update();o=bpy.data.objects.new(name,m);scene.collection.objects.link(o);m.materials.append(mat);return o
model=mesh_object('NSYSU Library corrected whole main block','mesh-data.npz');model['scope']='Single existing main block. Adjacent low wings, pavilion and extended connectors excluded; capped tower interfaces are model scope boundaries.';model['geometry_basis']='Drawing dimensions/proportions with dated-photo correspondence; not a site measurement or 2026 as-built.'
plan=mesh_object('QA actual mesh horizontal clip at z 6mm','plan-section-data.npz');plan.hide_render=True;plan.hide_set(True);plan['purpose']='Actual corrected model intersected by z<=6mm half-space, only for ground-plan view. Not a second building or printable alternative.'
world=bpy.data.worlds.new('Neutral studio world');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.81,.85,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.seed=0;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=1000;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.render.use_stamp=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
for name,loc,power,size in [('Key',(140,-180,260),420000,150),('Fill',(-180,120,220),300000,130),('Rear',(90,190,180),150000,120)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,45))-o.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO';cd.clip_end=1000
views=[('front',(-180,-230,155),190,(0,0,44)),('rear',(180,230,155),190,(0,0,44)),('south',(0,-300,52),130,(0,0,52)),('north',(0,300,52),130,(0,0,52)),('east',(300,0,52),174,(0,0,52)),('west',(-300,0,52),174,(0,0,52)),('roof',(0,0,350),174,(0,0,0)),('plan',(0,0,350),174,(0,0,0)),('roof-oblique',(-180,210,310),195,(0,0,42))]
def strip_png(path):
 raw=path.read_bytes();out=raw[:8];i=8
 while i<len(raw):
  n=struct.unpack('>I',raw[i:i+4])[0];tag=raw[i+4:i+8]
  if tag not in (b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'):out+=raw[i:i+n+12]
  i+=n+12
 path.write_bytes(out)
def scrub():
 for sc in bpy.data.scenes:
  n=sc.render.bl_rna.properties['filepath'].length_max;sc.render.filepath='_'*(n-1);sc.render.filepath='//previews/front.png'
 for scr in bpy.data.screens:
  for area in scr.areas:
   for space in area.spaces:
    if space.type=='FILE_BROWSER' and space.params:
     n=space.params.bl_rna.properties['directory'].length_max;space.params.directory=b'_'*(n-1);space.params.directory=b'//'
for name,loc,scale,target in views:
 if a.views and name not in a.views.split(','):continue
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale;model.hide_render=name=='plan';plan.hide_render=name=='plan' and False or True
 if name=='plan':plan.hide_render=False
 if name=='front':scrub();bpy.ops.wm.save_as_mainfile(filepath=str(root/'scene.blend'))
 if not a.no_render:
  scene.render.filepath=str(root/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True);strip_png(root/'previews'/f'{name}.png')
(root/'render-manifest.json').write_text(json.dumps({'engine':'Blender 4.3.2 Cycles CPU','samples':64,'seed':0,'textures':0,'preview_color_is_authentic':False,'views':[{'name':n,'camera':l,'orthographic_scale_mm':s,'look_at':t,'geometry':'actual model clipped at z<=6mm' if n=='plan' else 'full actual model'} for n,l,s,t in views]},indent=2)+'\n')
