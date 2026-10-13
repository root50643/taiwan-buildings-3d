"""Render the actual STL and save an editable Blender scene. Blender 4.3.2+.
Run: blender -b -t 4 -P render_preview.py
"""
import bpy,json,os
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent; PREV=OUT/'previews'; PREV.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(OUT/'model.stl'));model=bpy.context.object;model.name='Printable_NDHU'
# Preview colours only; STL remains a single monochrome connected printable mesh.
for name,col in [('Cream walls',(.79,.70,.50,1)),('Slate roofs',(.16,.21,.25,1)),('Base stone',(.62,.62,.57,1)),('Portico',(.71,.48,.23,1)),('Cornice',(.59,.62,.61,1))]:
 mat=bpy.data.materials.new(name);mat.diffuse_color=col;model.data.materials.append(mat)
for p in model.data.polygons:
 c=p.center
 # Roof colours identify only actual pitched facets; monochrome STL geometry is unchanged.
 roof=(p.normal.z>.1 and c.z>25 and (abs(p.normal.z)<.999 or c.z>39))
 p.material_index=2 if c.z<3.0 else (1 if roof else 0)
target_z=(min(v.co.z for v in model.data.vertices)+max(v.co.z for v in model.data.vertices))/2
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.35
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.5;scene.display.shading.curvature_valley_factor=1.2
scene.display.shading.show_specular_highlight=True;scene.display.shading.background_type='WORLD';scene.world.color=(.055,.065,.085)
scene.view_settings.view_transform='Standard'
scene.render.resolution_x=900;scene.render.resolution_y=700;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Preview_camera';scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=180
for name,loc,aim in [('front',(300,100,210),(0,0,target_z)),('rear',(-260,-175,200),(0,0,target_z)),('top',(0,0,300),(0,0,0))]:
 scene.display.shading.show_shadows=(name!='top')
 cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
 # Frame every actual STL corner with margin, including the entire base.
 inv=cam.rotation_euler.to_matrix().transposed(); projected=[inv@(model.matrix_world@v.co-cam.location) for v in model.data.vertices]
 width=max(v.x for v in projected)-min(v.x for v in projected);height=max(v.y for v in projected)-min(v.y for v in projected)
 cam.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.18
 cam.data.shift_x=(max(v.x for v in projected)+min(v.x for v in projected))/2/cam.data.ortho_scale
 cam.data.shift_y=(max(v.y for v in projected)+min(v.y for v in projected))/2/cam.data.ortho_scale
 if name=='front':front_scale=cam.data.ortho_scale;front_shift=(cam.data.shift_x,cam.data.shift_y)
 scene.render.filepath=str(PREV/(name+'.png'));bpy.ops.render.render(write_still=True)
cam.location=(300,100,210);cam.rotation_euler=(Vector((0,0,target_z))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath='//previews/front.png'
cam.data.ortho_scale=front_scale
cam.data.shift_x,cam.data.shift_y=front_shift
model['units']='mm';model['evidence']='NDHU official 2006-2017 completed exterior photos and official B1-4F humanities II plans for boundaries; historical exterior, not 2026 post-quake as-built';model['model_category']='Single connected printable solid'
# Remove private default file-browser paths before delivery.
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))

