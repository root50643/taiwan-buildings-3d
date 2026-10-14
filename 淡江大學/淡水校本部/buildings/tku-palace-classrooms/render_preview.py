"""Render the actual STL and save an editable Blender scene. Blender 4.3.2+.
Run: blender -b -t 4 -P render_preview.py
"""
import bpy,json,os,struct
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent; PREV=OUT/'previews'; PREV.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(OUT/'model.stl'));model=bpy.context.object;model.name='Printable_TKU_Palace'
mat=bpy.data.materials.new('Warm stone preview only');mat.diffuse_color=(.69,.64,.54,1);model.data.materials.append(mat)
target_z=(min(v.co.z for v in model.data.vertices)+max(v.co.z for v in model.data.vertices))/2
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.35
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=False
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.5;scene.display.shading.curvature_valley_factor=1.2
scene.display.shading.show_specular_highlight=True;scene.display.shading.background_type='WORLD';scene.world.color=(.055,.065,.085)
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.21,.27,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for loc,power,size in [((-130,-160,200),350000,140),((110,70,180),250000,120)]:
 bpy.ops.object.light_add(type='AREA',location=loc); light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(Vector((0,0,20))-light.location).to_track_quat('-Z','Y').to_euler()
scene.view_settings.view_transform='AgX'
scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Preview_camera';scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=180
for name,loc,aim in [('front',(-240,0,170),(0,0,6)),('rear',(240,0,160),(0,0,6)),('left',(0,240,120),(0,0,6)),('right',(0,-240,120),(0,0,6)),('top',(0,0,300),(0,0,0)),('roof-detail',(-200,-15,10),(-53,15,5)),('porch-detail',(-53,0,5),(-53,15,5))]:
 scene.render.resolution_y=500 if name.endswith('detail') else 900
 cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
 # Frame every actual STL corner with margin, including the entire base.
 inv=cam.rotation_euler.to_matrix().transposed(); projected=[inv@(model.matrix_world@Vector(c)-cam.location) for c in model.bound_box]
 width=max(v.x for v in projected)-min(v.x for v in projected);height=max(v.y for v in projected)-min(v.y for v in projected)
 cam.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.18
 if name=='roof-detail':cam.data.ortho_scale=24
 if name=='porch-detail':cam.data.ortho_scale=28
 if name=='front':front_scale=cam.data.ortho_scale
 scene.render.filepath=str(PREV/(name+'.png'));bpy.ops.render.render(write_still=True)
 # Blender writes Date/RenderTime metadata even with visual stamps disabled.
 # Drop text-only ancillary chunks, preserving every compressed image-data byte.
 path=PREV/(name+'.png'); raw=path.read_bytes(); clean=raw[:8];pos=8
 while pos<len(raw):
  length=struct.unpack('>I',raw[pos:pos+4])[0];kind=raw[pos+4:pos+8];chunk=raw[pos:pos+length+12]
  if kind not in [b'tEXt',b'zTXt',b'iTXt']:clean+=chunk
  pos+=length+12
 path.write_bytes(clean)
cam.location=(-240,0,170);cam.rotation_euler=(Vector((0,0,6))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath='//previews/front.png'
scene.render.resolution_y=900
cam.data.ortho_scale=front_scale
model['units']='mm';model['evidence']='TKU 2015 plan, NLSC 2024 watermarked eaves, 2021 aerial photos and official ground photos; bounded approximation; unobserved elevations deliberately simplified';model['model_category']='Single connected printable solid'
# Remove private default file-browser paths before delivery.
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))

