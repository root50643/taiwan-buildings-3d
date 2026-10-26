#!/usr/bin/env python3
# blender --background --python render_model.py -- --out DIRECTORY
import bpy, json, math, pathlib, sys, argparse, struct
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);p.add_argument('--no-render',action='store_true');p.add_argument('--views',default='');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=a.out;(root/'qa').mkdir(parents=True,exist_ok=True); info=json.loads((root/'editable-parts.json').read_text()); parts=json.loads((root/'construction-parts.json').read_text())
import numpy as np
D=np.load(root/'mesh-data.npz')
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
final=mesh_obj('Puli Paper Dome — unified printable material mesh',D['vertices'].tolist(),D['faces'].tolist(),scene.collection)
for m in mats:final.data.materials.append(m)
for poly,mi in zip(final.data.polygons,D['materials']):poly.material_index=int(mi)
final['scope']='One complete approximate 2008–2009 Puli Paper Dome hall. Taiwan photos plus documented numbered-frame transfer and Kobe historical comparator; not a Taiwan as-built or current survey. No source pixels or textures.'
final['print_note']='Watertight geometry is not an FFF printing guarantee. Supports and scale checks required.'
construction=bpy.data.collections.new('EDITABLE authored components (hidden; overlaps pre-union)');scene.collection.children.link(construction)
for part,op in zip(parts,info['features']):
 o=mesh_obj(part['name'],part['vertices'],part['faces'],construction);o.data.materials.append(mats[part['material']]);o['evidence']=op['evidence'];o.hide_render=True;o.hide_set(True)
construction.hide_render=True;construction.hide_viewport=True
scene.world.color=(.8,.8,.8);scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.81,.85,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
# Deterministic Cycles studio render using actual authored materials.
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.seed=0;scene.render.threads_mode="FIXED";scene.render.threads=4;scene.cycles.use_denoising=False
scene.render.resolution_x=1100;scene.render.resolution_y=920;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.render.use_stamp=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast' if 'Medium High Contrast' in [x.identifier for x in scene.view_settings.bl_rna.properties['look'].enum_items] else 'None'
scene.view_settings.exposure=0;scene.view_settings.gamma=1
for name,loc,power,size in [('Key',(-80,-180,320),500000,180),('Fill',(230,210,260),300000,170)]:
 dat=bpy.data.lights.new(name,'AREA');dat.energy=power;dat.shape='DISK';dat.size=size;o=bpy.data.objects.new(name,dat);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-10,-25,15))-o.location).to_track_quat('-Z','Y').to_euler()
camdat=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdat);scene.collection.objects.link(cam);scene.camera=cam;camdat.type='ORTHO';camdat.lens=52

views=[
 ('front',(245,-340,135),320,(0,-7,42)),
 ('oblique',(-275,315,190),320,(0,-4,42)),
 ('front-elevation',(0,-450,52),285,(0,0,52)),
 ('rear-elevation',(0,450,52),285,(0,0,52)),
 ('nonpond-elevation',(450,0,52),250,(0,0,52)),
 ('pond-elevation',(-450,0,52),250,(0,0,52)),
 ('top',(0,-6,450),285,(0,-6,0)),
 ('interior',(0,-54,25),150,(0,8,80)),
 ('ground-plan',(0,-6,450),285,(0,-6,0))]

def strip_png_metadata(path):
 raw=path.read_bytes();out=raw[:8];i=8
 while i<len(raw):
  n=struct.unpack('>I',raw[i:i+4])[0];tag=raw[i+4:i+8]
  if tag not in (b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'):out+=raw[i:i+n+12]
  i+=n+12
 path.write_bytes(out)

(root/'previews').mkdir(exist_ok=True)
for name,loc,scale,target in views:
 if a.views and name not in a.views.split(','):continue
 scene.render.resolution_y=600 if name.endswith('elevation') else 920
 camdat.type='PERSP' if name=='interior' else 'ORTHO';camdat.lens=21 if name=='interior' else 52
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdat.ortho_scale=scale
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
  bpy.ops.wm.save_as_mainfile(filepath=str(root/'paper-dome-taiwan-whole-2008-2009.blend'))
 diagnostic=None;clipper=None;modifier=None;inspection_light=None
 if name=='interior':
  dat=bpy.data.lights.new('Temporary interior inspection light','AREA');dat.energy=80000;dat.size=80;inspection_light=bpy.data.objects.new('Temporary interior inspection light',dat);scene.collection.objects.link(inspection_light);inspection_light.location=(0,-35,30);inspection_light.rotation_euler=(Vector((0,10,83))-inspection_light.location).to_track_quat('-Z','Y').to_euler()
 if name=='ground-plan':
  bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-40));clipper=bpy.context.object;clipper.name='Temporary horizontal section clip';clipper.dimensions=(500,500,120);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);clipper.hide_render=True
  modifier=final.modifiers.new('Actual mesh horizontal section at 20 mm','BOOLEAN');modifier.operation='INTERSECT';modifier.solver='EXACT';modifier.object=clipper
 if not a.no_render:scene.render.filepath=str(root/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True);strip_png_metadata(root/'previews'/f'{name}.png')
 if diagnostic:bpy.data.objects.remove(diagnostic,do_unlink=True);final.hide_render=False
 if modifier:final.modifiers.remove(modifier)
 if clipper:bpy.data.objects.remove(clipper,do_unlink=True)
 if inspection_light:bpy.data.objects.remove(inspection_light,do_unlink=True)

(root/'qa'/'render-manifest.json').write_text(json.dumps({'engine':'Blender 4.3.2 Cycles','texture_images':0,'diagnostic_view_policy':'Ground-plan is an exact Boolean horizontal cut of the final mesh at 20 mm, through the column and pivot-panel zone. Every other view shows the complete final mesh, without substitute geometry. Interior is a perspective view with a temporary inspection area light; other views use the saved studio lighting.','views':[{'name':n,'camera':l,'orthographic_scale_model_mm':s,'look_at':t}for n,l,s,t in views],'coordinates':'Source-relative coordinates: front = -Y, rear = +Y, nonpond short side = +X, pond short side = -X; source-relative, not compass directions. A04 and C01 show the same pond-side short face.'},indent=2)+'\n')
