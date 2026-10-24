#!/usr/bin/env python3
"""blender --background --python render_appearance.py -- --out DIRECTORY"""
from pathlib import Path
import bpy,numpy as np,json,argparse,sys,struct
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--views',default='');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[]);root=a.out
bpy.context.preferences.filepaths.save_version=0
D=np.load(root/'mesh-data.npz');palette=json.loads((root/'palette.json').read_text());(root/'previews').mkdir(exist_ok=True);(root/'qa').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):bpy.data.materials.remove(m)
mesh=bpy.data.meshes.new('Unified historical approximation with editable face materials');mesh.from_pydata(D['vertices'].tolist(),[],D['faces'].tolist());mesh.update()
obj=bpy.data.objects.new('NTIN Xin-Xin — original 3114 triangles',mesh);bpy.context.scene.collection.objects.link(obj)
for d in palette:
 c=[int(d['hex'][i:i+2],16)/255 for i in (1,3,5)];c=[x/12.92 if x<=.04045 else((x+.055)/1.055)**2.4 for x in c]
 c=d.get('linear_rgba',(*c,1))[:3]
 m=bpy.data.materials.new(d['id']+' '+d['name']);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.75;m['source_evidence']=d['evidence'];m['limitation']='Uncalibrated historical representative color; no image texture';mesh.materials.append(m)
for poly,mi in zip(mesh.polygons,D['materials']):poly.material_index=int(mi)
attr=mesh.attributes.new('original_stl_triangle_index','INT','FACE');attr.data.foreach_set('value',np.arange(len(mesh.polygons),dtype=np.int32))
attr=mesh.attributes.new('evidence_rule_index','INT','FACE');attr.data.foreach_set('value',D['rule_indices'].astype(np.int32))
obj['source_mesh']='../model.stl';obj['source_stl_sha256']='d9b3a2a55439f8d7a8650942128def62f7f7d9ca505aa71c31b3ff2c4e22b161';obj['scope']='2014–2015 post-renovation approximation; EXIF-declared local 2014-12-30; not 2026';obj['unknown']='2916 original triangles retain neutral material; not a finish assertion';obj['units']='display-model millimeters; no physical building scale ratio claimed'
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.35;scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.0;scene.display.shading.show_specular_highlight=False
scene.display.shading.background_type='WORLD';scene.world.color=(.78,.80,.82);scene.view_settings.view_transform='Standard';scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.render.use_stamp=False
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.cycles.seed=0
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.81,.85,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
for name,loc,power,size in [('Key',(-110,-140,200),150000,180),('Fill',(140,30,120),70000,140)]:
 dat=bpy.data.lights.new(name,'AREA');dat.energy=power;dat.shape='DISK';dat.size=size;o=bpy.data.objects.new(name,dat);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,30))-o.location).to_track_quat('-Z','Y').to_euler()
camdat=bpy.data.cameras.new('Appearance camera');cam=bpy.data.objects.new('Appearance camera',camdat);scene.collection.objects.link(cam);scene.camera=cam;camdat.type='ORTHO'
views=[('front',(-100,-225,105),(0,-1,18)),('front-right',(100,-225,105),(0,-1,18)),('elevation',(0,-260,23),(0,0,23)),('rear',(100,225,100),(0,-1,18)),('left',(-250,-25,68),(0,0,18)),('right',(250,-25,68),(0,0,18)),('top',(0,0,300),(0,0,0)),('underside',(100,-225,-130),(0,-1,18)),('gallery-detail',(-20,-180,42),(0,-9,29))]
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
 if name=='gallery-detail':camdat.ortho_scale=74
 manifest.append({'name':name,'camera_model_mm':loc,'target_model_mm':target,'orthographic_scale_mm':camdat.ortho_scale})
 if a.views and name not in a.views.split(','):continue
 scene.render.filepath=str(root/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True);strip_metadata(root/'previews'/f'{name}.png')
aim_view(views[0][1],views[0][2]);bpy.context.view_layer.objects.active=obj;obj.select_set(True);cam.select_set(False)
for ss in bpy.data.scenes:
 limit=ss.render.bl_rna.properties['filepath'].length_max;ss.render.filepath='_'*(limit-1);ss.render.filepath='//previews/front.png'
 # No sequencer is part of this model; drop its unused remembered image/sound paths.
 if ss.sequence_editor is not None:ss.sequence_editor_clear()
 limit=ss.render.bake.bl_rna.properties['filepath'].length_max;ss.render.bake.filepath='_'*(limit-1);ss.render.bake.filepath='//'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER'and space.params:
    limit=space.params.bl_rna.properties['directory'].length_max;space.params.directory=b'_'*(limit-1);space.params.directory=b'//'
    limit=space.params.bl_rna.properties['filename'].length_max;space.params.filename='_'*(limit-1);space.params.filename=''
   if space.type=='VIEW_3D':space.shading.color_type='MATERIAL';space.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'ntin-xinxin-appearance.blend'))
(root/'qa'/'render-manifest.json').write_text(json.dumps({'engine':'Blender 4.3.2 Cycles, 32 samples, seed 0, actual material rendering','images_are_actual_output_mesh':True,'image_textures':0,'dimensions_px':[1200,900],'views':manifest,'orientation':'Front is negative Y, not a surveyed bearing. Gray only on 2 front roof triangles, dark on 36 upper window-back triangles, cream on 160 front shaft-arc triangles; 2916 other original triangles stay neutral. Gallery detail is a closer view of the same mesh.'},indent=2)+'\n')
