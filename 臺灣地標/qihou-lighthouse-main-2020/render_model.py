#!/usr/bin/env python3
# blender --background --python render_model.py -- --out DIRECTORY
import bpy, json, math, pathlib, sys, argparse, struct
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);p.add_argument('--no-render',action='store_true');p.add_argument('--views',default='');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=a.out;(root/'qa').mkdir(parents=True,exist_ok=True); info=json.loads((root/'editable-parts.json').read_text()); parts=json.loads((root/'construction-parts.json').read_text())
import numpy as np
with np.load(root/'mesh-data.npz') as archive:D={k:archive[k].copy() for k in ['vertices','faces','materials']}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
mats=[]
for d in info['palette']:
 h=d['hex'].lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
 # Blender colors are linear; convert photographic display sRGB.
 c=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c]
 m=bpy.data.materials.new(d['id']);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.64; m.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=.25 if d['id'] in ['metal_frame','cable'] else 0.0;m['source_evidence']=d['evidence'];mats.append(m)
def mesh_obj(name,verts,faces,coll):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);coll.objects.link(o);return o
final=mesh_obj('Qihou Lighthouse — unified printable material mesh',D['vertices'].tolist(),D['faces'].tolist(),scene.collection)
for m in mats:final.data.materials.append(m)
for poly,mi in zip(final.data.polygons,D['materials']):poly.material_index=int(mi)
final['scope']='One complete connected Qihou Lighthouse main-building exterior circa July-August 2020: tower, neck and entire office/exhibition wing. Not whole precinct, survey, full interior or current-2026 condition. No photographic textures.'
final['print_note']='Watertight geometry is not an FFF printing guarantee. Supports and scale checks required.'
construction=bpy.data.collections.new('EDITABLE authored components (hidden; overlaps pre-union)');scene.collection.children.link(construction)
for part,op in zip(parts,info['features']):
 o=mesh_obj(part['name'],part['vertices'],part['faces'],construction);o.data.materials.append(mats[part['material']]);o['evidence']=op['evidence'];o.hide_render=True;o.hide_set(True)
construction.hide_render=True;construction.hide_viewport=True
scene.world.color=(.8,.8,.8);scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.81,.85,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
# Deterministic Cycles studio render using actual authored materials.
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.seed=0;scene.render.threads_mode="FIXED";scene.render.threads=2;scene.cycles.use_denoising=False
scene.render.resolution_x=1100;scene.render.resolution_y=920;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.render.use_stamp=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast' if 'Medium High Contrast' in [x.identifier for x in scene.view_settings.bl_rna.properties['look'].enum_items] else 'None'
scene.view_settings.exposure=0;scene.view_settings.gamma=1
for name,loc,power,size in [('Key',(-150,-230,430),650000,210),('Fill',(280,220,350),380000,200)]:
 dat=bpy.data.lights.new(name,'AREA');dat.energy=power;dat.shape='DISK';dat.size=size;o=bpy.data.objects.new(name,dat);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,35,120))-o.location).to_track_quat('-Z','Y').to_euler()
camdat=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdat);scene.collection.objects.link(cam);scene.camera=cam;camdat.type='ORTHO';camdat.lens=52

views=[
 ('front',(360,-520,345),355,(0,35,141)),
 ('oblique',(-360,520,345),355,(0,35,141)),
 ('front-elevation',(0,-520,142),350,(0,35,142)),
 ('rear-elevation',(0,620,142),350,(0,35,142)),
 ('southwest-elevation',(520,35,142),350,(0,35,142)),
 ('northeast-elevation',(-520,35,142),350,(0,35,142)),
 ('top',(0,35,650),340,(0,35,0)),
 ('roof-oblique',(355,-220,600),380,(0,35,142)),
 ('ground-plan',(0,35,650),340,(0,35,0))]

def strip_png_metadata(path):
 raw=path.read_bytes();out=raw[:8];i=8
 while i<len(raw):
  n=struct.unpack('>I',raw[i:i+4])[0];tag=raw[i+4:i+8]
  if tag not in (b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'):out+=raw[i:i+n+12]
  i+=n+12
 path.write_bytes(out)

(root/'previews').mkdir(exist_ok=True)
effective_views=[]
for name,loc,scale,target in views:
 if a.views and name not in a.views.split(','):continue
 scene.render.resolution_y=920
 camdat.type='ORTHO';camdat.lens=52
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 # Fit the complete actual geometry with a reproducible 8% margin. This keeps
 # roof tips, deep-plan corners and the plinth inside every orthographic frame.
 local=(D['vertices']-np.asarray(target))@np.asarray(cam.rotation_euler.to_matrix())
 ex=float(np.max(np.abs(local[:,0])));ey=float(np.max(np.abs(local[:,1])));aspect=scene.render.resolution_x/scene.render.resolution_y
 fit=max(2*ex,2*ey*aspect)*1.12;camdat.ortho_scale=max(scale,fit)
 bpy.context.view_layer.update()
 from bpy_extras.object_utils import world_to_camera_view
 projected=np.asarray([tuple(world_to_camera_view(scene,cam,Vector(v)))[:2] for v in D['vertices']])
 need=2*float(np.abs(projected-.5).max())
 if need>.90:
  camdat.ortho_scale*=need/.89
  bpy.context.view_layer.update()
  projected=np.asarray([tuple(world_to_camera_view(scene,cam,Vector(v)))[:2] for v in D['vertices']])
 measured_margin=1-2*float(np.abs(projected-.5).max())
 assert measured_margin>=.08,(name,measured_margin)
 effective_views.append({'name':name,'camera':loc,'orthographic_scale_model_mm':float(camdat.ortho_scale),'look_at':target,'whole_geometry_frame_margin_fraction':measured_margin,'actual_camera_projection_bounds_normalized':[projected.min(axis=0).tolist(),projected.max(axis=0).tolist()]})
 if name=='front':
  for saved_scene in bpy.data.scenes:
   limit=saved_scene.render.bl_rna.properties['filepath'].length_max
   saved_scene.render.filepath='_'*(limit-1)
   saved_scene.render.filepath='//previews/front.png'
  for screen in bpy.data.screens:
   for area in screen.areas:
    for space in area.spaces:
     if space.type=='FILE_BROWSER' and space.params:
      limit=space.params.bl_rna.properties['directory'].length_max
      space.params.directory=b'_'*(limit-1)
      space.params.directory=b'//'
  bpy.ops.wm.save_as_mainfile(filepath=str(root/'qihou-lighthouse-main-2020.blend'))
 diagnostic=None;clipper=None;modifier=None;inspection_light=None
 if name=='ground-plan':
  bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-30));clipper=bpy.context.object;clipper.name='Temporary horizontal section clip';clipper.dimensions=(500,500,120);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);clipper.hide_render=True
  modifier=final.modifiers.new('Actual mesh horizontal section at 30 mm','BOOLEAN');modifier.operation='INTERSECT';modifier.solver='EXACT';modifier.object=clipper
 if not a.no_render:scene.render.filepath=str(root/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True);strip_png_metadata(root/'previews'/f'{name}.png')
 if diagnostic:bpy.data.objects.remove(diagnostic,do_unlink=True);final.hide_render=False
 if modifier:final.modifiers.remove(modifier)
 if clipper:bpy.data.objects.remove(clipper,do_unlink=True)
 if inspection_light:bpy.data.objects.remove(inspection_light,do_unlink=True)

(root/'qa'/'render-manifest.json').write_text(json.dumps({'engine':'Blender 4.3.2 Cycles','texture_images':0,'diagnostic_view_policy':'Ground-plan is an exact Boolean horizontal cut of the final mesh at 30 mm, showing the whole connected main-building footprint and both open reentrant exterior spaces. Every other view shows the complete final mesh, without substitute geometry. All views use the saved studio lighting.','views':effective_views,'coordinates':'Source facade-relative coordinates: SE front=-Y, NW rear=+Y, SW doorway=+X, NE blind wing=-X. Model axes are not surveyed compass coordinates.'},indent=2)+'\n')
