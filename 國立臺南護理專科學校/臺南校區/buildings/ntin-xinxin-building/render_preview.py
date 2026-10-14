"""Render only the actual distributed STL; save that same editable mesh in Blend.
Run blender -b -t 4 -P render_preview.py. Then run Python strip_preview_metadata.py to remove PNG metadata.
"""
import bpy,json,hashlib,sys
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent; PREV=OUT/'previews';PREV.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(OUT/'model.stl'));model=bpy.context.object;model.name='XinXin_2014_2015_ActualSTL'
mat=bpy.data.materials.new('Neutral architectural preview');mat.diffuse_color=(.76,.72,.63,1);model.data.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.3
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.5;scene.display.shading.curvature_valley_factor=1.6
scene.display.shading.show_specular_highlight=True;scene.display.shading.background_type='WORLD';scene.world.color=(.065,.075,.095)
scene.view_settings.view_transform='Standard';scene.render.resolution_x=900;scene.render.resolution_y=580;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.render.use_stamp=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='ActualSTL_camera';scene.camera=cam;cam.data.type='ORTHO'
views=[('front',(-100,-225,105),(0,-1,18)),('rear',(100,225,100),(0,-1,18)),('elevation',(0,-260,23),(0,0,23)),('side',(-250,-25,68),(0,0,18)),('top',(0,0,300),(0,0,0))]
for name,loc,aim in views:
 cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
 inv=cam.rotation_euler.to_matrix().transposed();q=[inv@(model.matrix_world@Vector(c)-cam.location) for c in model.bound_box]
 width=max(v.x for v in q)-min(v.x for v in q);height=max(v.y for v in q)-min(v.y for v in q)
 cam.data.ortho_scale=max(width,height*900/580)*1.16
 if name=='front':front_scale=cam.data.ortho_scale
 scene.render.filepath=str(PREV/(name+'.png'));bpy.ops.render.render(write_still=True)
cam.location=views[0][1];cam.rotation_euler=(Vector(views[0][2])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=front_scale
scene.render.filepath='//previews/front.png'
model['units']='mm';model['source_stl_sha256']=hashlib.sha256((OUT/'model.stl').read_bytes()).hexdigest()
model['scope']='Xin-Xin main building; 2014–2015 exterior approximation, not measured current conditions'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))
# Export numeric evidence for an independent raw STL / saved Blend comparison.
model.data.calc_loop_triangles()
(OUT/'blend-mesh-evidence.json').write_text(json.dumps({'stl_sha256':model['source_stl_sha256'],'vertices':[list(v.co) for v in model.data.vertices],'faces':[list(f.vertices) for f in model.data.loop_triangles]}))
