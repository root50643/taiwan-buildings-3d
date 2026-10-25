#!/usr/bin/env python3
# blender --background --python render_model.py -- --out DIRECTORY
import bpy, json, math, pathlib, sys, argparse, struct
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
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
 m=bpy.data.materials.new(d['id']);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.64; m.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=.24 if d['id'] in ['silver_metal','pale_frame','panel_seam'] else 0.0;m['source_evidence']=d['evidence'];mats.append(m)
def mesh_obj(name,verts,faces,coll):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);coll.objects.link(o);return o
final=mesh_obj('Xiangshan — unified printable material mesh',D['vertices'].tolist(),D['faces'].tolist(),scene.collection)
for m in mats:final.data.materials.append(m)
for poly,mi in zip(final.data.polygons,D['materials']):poly.material_index=int(mi)
final['scope']='Xiangshan Visitor Center and Administration Office whole paired complex, 2010 completed-design exterior interpretation. Individual photograph dates unknown. Normalized desktop proportions, not a survey or verified 2026 state. No interiors or source textures.'
final['print_note']='Watertight geometry is not an FFF printing guarantee. Supports and scale checks required.'
construction=bpy.data.collections.new('EDITABLE authored components (hidden; overlaps pre-union)');scene.collection.children.link(construction)
for part,op in zip(parts,info['features']):
 o=mesh_obj(part['name'],part['vertices'],part['faces'],construction);o.data.materials.append(mats[part['material']]);o['evidence']=op['evidence'];o.hide_render=True;o.hide_set(True)
construction.hide_render=True;construction.hide_viewport=True
scene.world.color=(.8,.8,.8);scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.81,.85,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
# Deterministic Cycles studio render using actual authored materials.
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.seed=0;scene.render.threads_mode="FIXED";scene.render.threads=6;scene.cycles.use_denoising=False
scene.render.resolution_x=1100;scene.render.resolution_y=920;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.render.use_stamp=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast' if 'Medium High Contrast' in [x.identifier for x in scene.view_settings.bl_rna.properties['look'].enum_items] else 'None'
scene.view_settings.exposure=0;scene.view_settings.gamma=1
for name,loc,power,size in [('Key',(-80,-180,320),500000,180),('Fill',(230,210,260),300000,170)]:
 dat=bpy.data.lights.new(name,'AREA');dat.energy=power;dat.shape='DISK';dat.size=size;o=bpy.data.objects.new(name,dat);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-10,-25,15))-o.location).to_track_quat('-Z','Y').to_euler()
camdat=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdat);scene.collection.objects.link(cam);scene.camera=cam;camdat.type='ORTHO';camdat.lens=52

views=[
 ('front',(-420,0,5),290,(-6,-1,5)),
 ('oblique',(-334,-317,250),340,(-20,12,5)),
 ('admin-west',(0,-420,7),260,(0,30,7)),
 ('admin-east',(0,420,7),260,(0,30,7)),
 ('visitor-east',(-32,420,6),215,(-32,-31,6)),
 ('visitor-west',(-32,-420,6),215,(-32,-31,6)),
 ('top',(-6,-1,480),295,(-6,-1,0)),
 ('canopy-detail',(-340,0,27),170,(-88,5,6)),
 ('ground-plan',(-6,-1,480),295,(-6,-1,0))]

def strip_png_metadata(path):
 raw=path.read_bytes();out=raw[:8];i=8
 while i<len(raw):
  n=struct.unpack('>I',raw[i:i+4])[0];tag=raw[i+4:i+8]
  if tag not in (b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'):out+=raw[i:i+n+12]
  i+=n+12
 path.write_bytes(out)

(root/'previews').mkdir(exist_ok=True)
framing=[]
for name,loc,scale,target in views:
 if a.views and name not in a.views.split(','):continue
 scene.render.resolution_y=360 if name in ['front','admin-west','admin-east','visitor-east','visitor-west'] else 460 if name=='canopy-detail' else 920
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
  bpy.ops.wm.save_as_mainfile(filepath=str(root/'xiangshan-whole-2010.blend'))
 diagnostic=None;clipper=None;modifier=None
 if name in ['admin-west','admin-east','visitor-east','visitor-west']:
  gid=1 if name.startswith('admin') else 2
  keep=(D['groups']==gid)
  diagnostic=mesh_obj('Temporary exact triangle wing isolation',D['vertices'].tolist(),D['faces'][keep].tolist(),scene.collection)
  for m in mats:diagnostic.data.materials.append(m)
  for poly,mi in zip(diagnostic.data.polygons,D['materials'][keep]):poly.material_index=int(mi)
  final.hide_render=True
 if name=='ground-plan':
  bpy.ops.mesh.primitive_cube_add(size=1,location=(-5,0,-49));clipper=bpy.context.object;clipper.name='Temporary horizontal section clip';clipper.dimensions=(500,500,103);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);clipper.hide_render=True
  modifier=final.modifiers.new('Actual mesh horizontal section at 2.5 mm','BOOLEAN');modifier.operation='INTERSECT';modifier.solver='EXACT';modifier.object=clipper
 bpy.context.view_layer.update()
 if name in ['admin-west','admin-east','visitor-east','visitor-west']:
  active_vertices=D['vertices'][np.unique(D['faces'][D['groups']==gid])]
 elif name=='ground-plan':
  evaluated=final.evaluated_get(bpy.context.evaluated_depsgraph_get());cutmesh=evaluated.to_mesh();active_vertices=np.asarray([tuple(v.co)for v in cutmesh.vertices]);evaluated.to_mesh_clear()
 else:active_vertices=D['vertices']
 projected=np.asarray([tuple(world_to_camera_view(scene,cam,Vector(v)))for v in active_vertices]);low=projected[:,:2].min(axis=0);high=projected[:,:2].max(axis=0);inside=bool((low>=0).all()and(high<=1).all()and(projected[:,2]>0).all())
 intentional_detail=name=='canopy-detail'
 assert inside or intentional_detail,('Unexpected cropped model view',name,low.tolist(),high.tolist())
 framing.append({'name':name,'projected_image_bounds_normalized':[low.tolist(),high.tolist()],'whole_shown_geometry_inside_frame':inside,'intentional_cropped_detail':intentional_detail,'actual_vertices_checked':len(projected)})
 if not a.no_render:scene.render.filepath=str(root/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True);strip_png_metadata(root/'previews'/f'{name}.png')
 if diagnostic:bpy.data.objects.remove(diagnostic,do_unlink=True);final.hide_render=False
 if modifier:final.modifiers.remove(modifier)
 if clipper:bpy.data.objects.remove(clipper,do_unlink=True)

(root/'qa'/'render-manifest.json').write_text(json.dumps({'engine':'Blender 4.3.2 Cycles','texture_images':0,'diagnostic_view_policy':'The four named wing elevations isolate that wing without contextual ground using exact final-mesh triangle groups, not substitute geometry. Ground-plan is an exact Boolean horizontal cut of the final mesh at 2.5 mm. All other views show the whole final mesh.','views':[{'name':n,'camera':l,'orthographic_scale_model_mm':s,'look_at':t}for n,l,s,t in views],'coordinates':'building-local -X lakeward; +X inland; +Y administration side; -Y visitor side. Elevation names correspond to architect A10 labels; no surveyed azimuth claim'},indent=2)+'\n')

(root/'qa/frame-validation.json').write_text(json.dumps({'all_expected_outcomes':True,'method':'Actual rendered camera projection of every used final-mesh vertex; exact isolated-wing triangle groups and evaluated Boolean ground-section mesh. Only named canopy detail may crop outer context.','checks':framing},indent=2)+'\n')
