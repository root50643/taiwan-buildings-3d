#!/usr/bin/env python3
"""blender --background --python render_model.py -- --out DIRECTORY"""
from pathlib import Path
import bpy,numpy as np,json,argparse,sys,struct,hashlib
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--views',default='');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[]);root=a.out
bpy.context.preferences.filepaths.save_version=0
D=np.load(root/'mesh-data.npz');palette=json.loads((root/'palette.json').read_text());(root/'previews').mkdir(exist_ok=True);(root/'qa').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):bpy.data.materials.remove(m)
mesh=bpy.data.meshes.new('Unified D–G exterior with editable face materials');mesh.from_pydata(D['vertices'].tolist(),[],D['faces'].tolist());mesh.update()
obj=bpy.data.objects.new('MMU second teaching/research D–G — whole complex',mesh);bpy.context.scene.collection.objects.link(obj)
for d in palette:
 c=[int(d['hex'][i:i+2],16)/255 for i in (1,3,5)];c=[x/12.92 if x<=.04045 else((x+.055)/1.055)**2.4 for x in c]
 m=bpy.data.materials.new(d['id']+' '+d['name']);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.75;m['source_evidence']=d['evidence'];m['limitation']='Uncalibrated representative color; no image texture';mesh.materials.append(m)
for poly,mi in zip(mesh.polygons,D['materials']):poly.material_index=int(mi)
attr=mesh.attributes.new('original_stl_triangle_index','INT','FACE');attr.data.foreach_set('value',np.arange(len(mesh.polygons),dtype=np.int32))

obj['source_mesh']='model.stl';obj['scope']='Whole connected D–G complex; 2014/2016 early published appearance cross-checked against later official topology; not exact 2013 or current 2026';obj['unknown']='Neutral roof/grade support; no unverified equipment';obj['units']='authored model millimetres; not surveyed building dimensions'
info=json.loads((root/'editable-parts.json').read_text());parts=json.loads((root/'construction-parts.json').read_text());coll=bpy.data.collections.new('EDITABLE components — hidden pre-union overlaps');bpy.context.scene.collection.children.link(coll)
for part,op in zip(parts,info['features']):
 pm=bpy.data.meshes.new(part['name']);pm.from_pydata(part['vertices'],[],part['faces']);pm.update();po=bpy.data.objects.new(part['name'],pm);coll.objects.link(po);po.data.materials.append(mesh.materials[part['material']]);po['certainty']=op['certainty'];po['source']=op['source'];po.hide_render=True;po.hide_set(True)
coll.hide_render=True;coll.hide_viewport=True
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.35;scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.0;scene.display.shading.show_specular_highlight=False
scene.display.shading.background_type='WORLD';scene.world.color=(.78,.80,.82);scene.view_settings.view_transform='Standard';scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.render.use_stamp=False
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.cycles.seed=0
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.81,.85,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
for name,loc,power,size in [('Key',(-250,-350,450),700000,280),('Fill',(320,180,330),450000,250)]:
 dat=bpy.data.lights.new(name,'AREA');dat.energy=power;dat.shape='DISK';dat.size=size;o=bpy.data.objects.new(name,dat);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,5,30))-o.location).to_track_quat('-Z','Y').to_euler()
camdat=bpy.data.cameras.new('Appearance camera');cam=bpy.data.objects.new('Appearance camera',camdat);scene.collection.objects.link(cam);scene.camera=cam;camdat.type='ORTHO'
views=[('front',(450,-330,95),(5,5,35)),('oblique',(380,-400,250),(5,5,33)),('right',(500,0,80),(5,5,35)),('left',(-500,0,80),(5,5,35)),('rear',(-260,500,100),(5,5,35)),('top',(5,5,500),(5,5,0)),('road-side',(190,500,135),(5,5,35)),('rear-g',(-420,-260,190),(5,5,32)),('aerial',(340,-430,370),(5,5,28))]
manifest=[]
def aim_view(loc,target):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 inv=cam.rotation_euler.to_matrix().transposed();vv=[inv@(obj.matrix_world@Vector(c)-cam.location)for c in obj.bound_box];width=max(v.x for v in vv)-min(v.x for v in vv);height=max(v.y for v in vv)-min(v.y for v in vv);camdat.ortho_scale=max(width,height*1200/900)*1.15

def strip_metadata(path):
 raw=path.read_bytes();result=raw[:8];i=8
 while i<len(raw):
  n=struct.unpack_from('>I',raw,i)[0];tag=raw[i+4:i+8]
  if tag not in (b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'):result+=raw[i:i+n+12]
  i+=n+12
 path.write_bytes(result)
for name,loc,target in views:
 aim_view(loc,target)
 manifest.append({'name':name,'camera_model_mm':loc,'target_model_mm':target,'orthographic_scale_mm':camdat.ortho_scale})
 if a.views and name not in a.views.split(','):continue
 scene.render.filepath=str(root/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True);strip_metadata(root/'previews'/f'{name}.png')
aim_view(views[0][1],views[0][2]);bpy.context.view_layer.objects.active=obj;obj.select_set(True);cam.select_set(False)
for ss in bpy.data.scenes:
 limit=ss.render.bl_rna.properties['filepath'].length_max;ss.render.filepath='_'*(limit-1);ss.render.filepath='//previews/front.png'
 # No sequencer is part of this model; remove unused remembered image/sound directories.
 if ss.sequence_editor is not None:ss.sequence_editor_clear()
 limit=ss.render.bake.bl_rna.properties['filepath'].length_max;ss.render.bake.filepath='_'*(limit-1);ss.render.bake.filepath='//'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER'and space.params:
    limit=space.params.bl_rna.properties['directory'].length_max;space.params.directory=b'_'*(limit-1);space.params.directory=b'//'
    limit=space.params.bl_rna.properties['filename'].length_max;space.params.filename='_'*(limit-1);space.params.filename=''
   if space.type=='VIEW_3D':space.shading.color_type='MATERIAL';space.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'mmu-teaching-phase2.blend'))
(root/'qa'/'render-manifest.json').write_text(json.dumps({'mesh_data_sha256':hashlib.sha256((root/'mesh-data.npz').read_bytes()).hexdigest(),'stl_sha256':hashlib.sha256((root/'model.stl').read_bytes()).hexdigest(),'engine':'Blender 4.3.2 Cycles, 32 samples, seed 0, actual material rendering','images_are_actual_output_mesh':True,'image_textures':0,'dimensions_px':[1200,900],'views':manifest,'orientation':'+X plan-right, +Y plan-up, +Z up. Front/aerial are D–E garden-side; road-side shows the back corridor; rear-g proves G extent. No compass azimuth asserted.'},indent=2)+'\n')
