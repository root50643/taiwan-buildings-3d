#!/usr/bin/env python3
"""blender --background --python render_appearance.py -- --out DIRECTORY"""
from pathlib import Path
import bpy,numpy as np,json,argparse,sys,struct,hashlib
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--views',default='');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[]);root=a.out
bpy.context.preferences.filepaths.save_version=0
D=np.load(root/'mesh-data.npz');palette=json.loads((root/'palette.json').read_text());(root/'previews').mkdir(exist_ok=True);(root/'qa').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):bpy.data.materials.remove(m)
mesh=bpy.data.meshes.new('Unified historical approximation with editable face materials');mesh.from_pydata(D['vertices'].tolist(),[],D['faces'].tolist());mesh.update()
obj=bpy.data.objects.new('China Medical University Chuangyan Building A2 — historical approximation',mesh);bpy.context.scene.collection.objects.link(obj)
for d in palette:
 c=[int(d['hex'][i:i+2],16)/255 for i in (1,3,5)];c=[x/12.92 if x<=.04045 else((x+.055)/1.055)**2.4 for x in c]
 m=bpy.data.materials.new(d['id']+' '+d['name']);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.65;m['source_evidence']=d['evidence'];m['limitation']='Uncalibrated historical representative color; no image texture';mesh.materials.append(m)
for poly,mi in zip(mesh.polygons,D['materials']):poly.material_index=int(mi)
mat=mesh.materials[7];mat.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=.65;mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.25
attr=mesh.attributes.new('original_stl_triangle_index','INT','FACE');attr.data.foreach_set('value',np.arange(len(mesh.polygons),dtype=np.int32))
attr=mesh.attributes.new('evidence_rule_index','INT','FACE');attr.data.foreach_set('value',D['rule_indices'].astype(np.int32))
obj['source_mesh']='model.stl';obj['scope']='Bounded whole twelve-numbered-level A2, 2020 completion with 2022 rooftop PV evidence; not surveyed or 2026 as-built';obj['unknown']='N00 is unknown closure or manufacture; not an observed finish';obj['units']='display-model millimeters only; main length 240 mm chosen for normalized proportions, not measured scale'
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.35;scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.0;scene.display.shading.show_specular_highlight=False
scene.display.shading.background_type='WORLD';scene.world.color=(.78,.80,.82);scene.view_settings.view_transform='Standard';scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.render.use_stamp=False
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.cycles.seed=0
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.81,.85,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
for name,loc,power,size in [('Key',(-220,-280,420),700000,280),('Fill',(350,320,300),450000,250)]:
 dat=bpy.data.lights.new(name,'AREA');dat.energy=power;dat.shape='DISK';dat.size=size;o=bpy.data.objects.new(name,dat);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,95))-o.location).to_track_quat('-Z','Y').to_euler()
camdat=bpy.data.cameras.new('Appearance camera');cam=bpy.data.objects.new('Appearance camera',camdat);scene.collection.objects.link(cam);scene.camera=cam;camdat.type='ORTHO'
views=[('front',(0,-600,95),(0,0,95)),('rear',(0,600,95),(0,0,95)),('oblique',(360,-440,300),(0,0,95)),('left',(-600,0,95),(0,0,95)),('right',(600,0,95),(0,0,95)),('top',(0,0,700),(0,0,0)),('rear-oblique',(-360,440,300),(0,0,95)),('underside',(350,-440,-300),(0,0,85)),('low-front',(170,-550,110),(0,0,95))]
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
bpy.ops.wm.save_as_mainfile(filepath=str(root/'cmu-chuangyan-a2.blend'))
(root/'qa'/'render-manifest.json').write_text(json.dumps({'mesh_data_sha256':hashlib.sha256((root/'mesh-data.npz').read_bytes()).hexdigest(),'stl_sha256':hashlib.sha256((root/'model.stl').read_bytes()).hexdigest(),'engine':'Blender 4.3.2 Cycles, 32 samples, seed 0, actual material rendering','images_are_actual_output_mesh':True,'image_textures':0,'dimensions_px':[1200,900],'views':manifest,'orientation':'Right-handed normalized model: +X east, +Y north/court, +Z up. front=south/street; rear=north/court; left=west; right=east; oblique=SE; rear-oblique=NW. Not surveyed azimuth. Ground, roof and raised screen are separate profiles; high rear detail and PV mounting height are simplified.'},indent=2)+'\n')
