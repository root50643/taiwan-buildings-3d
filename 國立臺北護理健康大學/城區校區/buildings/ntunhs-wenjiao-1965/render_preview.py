"""Render the actual delivered STL and save editable mesh. Blender 4.3+.
Run: blender -b -t 2 -P render_preview.py ; python clean_previews.py
"""
import bpy
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent;PREV=OUT/'previews';PREV.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(OUT/'model.stl'));model=bpy.context.object;model.name='NTUNHS_Wenjiao_1965_actual_STL_mm'
mat=bpy.data.materials.new('Ivory_preview_only');mat.diffuse_color=(.69,.67,.61,1);model.data.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.35
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.5;scene.display.shading.curvature_valley_factor=1.2
scene.display.matcap_ssao_distance=8.0;scene.display.matcap_ssao_samples=32;scene.display.shading.cavity_valley_factor=1.4
scene.display.shading.show_specular_highlight=True;scene.display.shading.background_type='WORLD';scene.world.color=(.055,.065,.085)
scene.view_settings.view_transform='Standard';scene.render.resolution_x=900;scene.render.resolution_y=600;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Actual_STL_preview_camera';scene.camera=cam;cam.data.type='ORTHO'
views=[('front',(-170,-250,128),(0,2,19)),('rear',(170,250,120),(0,3,19)),('south',(0,-260,22),(0,0,22)),('north',(0,260,22),(0,0,22)),('east',(260,0,22),(0,0,22)),('top',(0,0,300),(0,3.2,0)),('rear-detail',(65,130,65),(23,14,16))]
for name,loc,aim in views:
 cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
 inv=cam.rotation_euler.to_matrix().transposed();pts=[inv@(model.matrix_world@Vector(c)-cam.location) for c in model.bound_box]
 width=max(v.x for v in pts)-min(v.x for v in pts);height=max(v.y for v in pts)-min(v.y for v in pts)
 cam.data.ortho_scale=max(width,height*1.5)*1.12
 if name=='rear-detail':cam.data.ortho_scale=84
 if name=='front':front_scale=cam.data.ortho_scale
 scene.render.filepath=str(PREV/(name+'.png'));bpy.ops.render.render(write_still=True)
cam.location=views[0][1];cam.rotation_euler=(Vector(views[0][2])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=front_scale
scene.render.filepath='//previews/front.png'
model['units']='millimetres';model['scope']='1965 original four-storey main building only; approximate exterior envelope';model['source']='Official 1965 permit plans and dated historical photos';model['model_category']='Original parameter geometry; actual printable STL mesh'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))
