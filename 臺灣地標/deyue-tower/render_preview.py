"""Render the actual STL in a clean workbench studio and save editable.blend.
Run with Blender 4.x: blender -b -t 4 -P render_preview.py.
Only the named printable object is mesh geometry; camera is not for printing.
"""
import bpy,os,math
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__));P=os.path.join(OUT,'previews');os.makedirs(P,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=os.path.join(OUT,'model.stl'));obj=bpy.context.object;obj.name='Print-ready exterior (mm)'
mat=bpy.data.materials.new('Ivory architectural maquette');mat.diffuse_color=(.72,.69,.61,1);obj.data.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1400;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.1;scene.display.shading.cavity_ridge_factor=1.3;scene.display.shading.cavity_valley_factor=1.15;scene.display.shading.show_specular_highlight=True;scene.display.shading.background_type='WORLD';scene.world.color=(.065,.075,.09);scene.display.render_aa='32';scene.view_settings.view_transform='Standard'
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';corners=[obj.matrix_world@Vector(c) for c in obj.bound_box];center=sum(corners,Vector())/8
views=[('front',(1.2,-2,1.05)),('rear',(-1.25,2,1.25))]
for name,delta in views:
 cam.location=center+Vector(delta).normalized()*400;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();rot=cam.rotation_euler.to_matrix().transposed();p=[rot@(c-center) for c in corners];maxx=max(abs(q.x) for q in p);maxy=max(abs(q.y) for q in p);aspect=scene.render.resolution_x/scene.render.resolution_y;cam.data.ortho_scale=max(maxx*2,maxy*2*aspect)*1.20
 scene.render.filepath=os.path.join(P,name+'.png');bpy.ops.render.render(write_still=True)
cam.location=center+Vector(views[0][1]).normalized()*400;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  area.spaces.active.region_3d.view_distance=220;area.spaces.active.region_3d.view_location=center
scene.render.filepath='//previews/front.png';bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'editable.blend'),compress=True)
