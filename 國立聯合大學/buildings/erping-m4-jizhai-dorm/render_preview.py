"""Render the actual model.stl and save an editable Blender scene.
Usage: blender -b -t 4 -P render_preview.py
Blender 4.x required. Colors are display materials; STL contains no color.
"""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
bpy.context.preferences.filepaths.save_version=0
HERE=Path(__file__).resolve().parent;PREV=HERE/'previews';PREV.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(HERE/'model.stl'));model=bpy.context.object;model.name='Print-ready exterior (mm)'
code=HERE.name
mat=bpy.data.materials.new('Exterior material (display only)');mat.diffuse_color=(.62,.33,.22,1) if code=='m1' else (.68,.70,.70,1);model.data.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.4;scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.6;scene.display.shading.curvature_valley_factor=1.2
scene.display.shading.background_type='WORLD';scene.world.color=(.12,.145,.17)
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS';scene.view_settings.view_transform='Standard'
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.lens=50
bb=[model.matrix_world@Vector(c) for c in model.bound_box];center=sum(bb,Vector())/8
aim=Vector((center.x,center.y,center.z*.94));dimensions=model.dimensions
for name,delta in [('front',(1.15,-1.75,1.1)),('rear',(-1.25,1.7,1.2))]:
 cam.location=aim+Vector(delta)*180;cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler()
 inv=cam.matrix_world.inverted();bpy.context.view_layer.update();inv=cam.matrix_world.inverted();pts=[inv@v for v in bb]
 width=max(v.x for v in pts)-min(v.x for v in pts);height=max(v.y for v in pts)-min(v.y for v in pts)
 cam.data.ortho_scale=max(width*1.23,height*1.23*1600/1200)
 scene.render.filepath=str(PREV/(name+'.png'));bpy.ops.render.render(write_still=True)
scene.render.filepath='//previews/rear.png'
# Select only the print mesh when the file opens; studio camera is separate.
bpy.ops.object.select_all(action='DESELECT');model.select_set(True);bpy.context.view_layer.objects.active=model
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'scene.blend'))
