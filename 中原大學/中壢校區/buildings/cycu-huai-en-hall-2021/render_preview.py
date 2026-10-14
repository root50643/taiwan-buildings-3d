"""Render only delivered model.stl; save editable imported mesh in scene.blend.
Run: blender -b -t 2 -P render_preview.py. PNG metadata contains no source paths.
"""
import bpy
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parent;P=R/'previews';P.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(R/'model.stl'));m=bpy.context.object;m.name='CYCU_Huai_En_Hall_circa_2021_actual_STL'
mat=bpy.data.materials.new('Warm masonry preview only');mat.diffuse_color=(.70,.63,.50,1);m.data.materials.append(mat)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.studiolight_rotate_z=.35
s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=1.5;s.display.shading.curvature_valley_factor=1.25;s.display.shading.show_specular_highlight=True;s.display.shading.background_type='WORLD';s.world.color=(.055,.065,.08)
s.view_settings.view_transform='Standard';s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.render.use_stamp=False
s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;s.unit_settings.length_unit='MILLIMETERS'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Actual_STL_camera';s.camera=cam;cam.data.type='ORTHO'
views=[('front',(-45,-180,105),(0,-2,5),900,390),('rear',(45,180,98),(0,-2,5),900,390),('south_elevation',(0,-250,6.3),(0,0,6.3),900,190),('north_elevation',(0,250,6.3),(0,0,6.3),900,190),('west_end',(-250,-32,23),(-70,0,6),900,570),('east_end',(250,-32,23),(70,0,6),900,570),('top',(0,0,300),(0,-2.5,0),900,270)]
for name,loc,aim,w,h in views:
 s.render.resolution_x=w;s.render.resolution_y=h
 cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
 inv=cam.rotation_euler.to_matrix().transposed();q=[inv@(m.matrix_world@Vector(c)-cam.location) for c in m.bound_box]
 width=max(v.x for v in q)-min(v.x for v in q);height=max(v.y for v in q)-min(v.y for v in q)
 cam.data.ortho_scale=max(width,height*w/h)*1.12
 # End detail images deliberately crop out the opposite end, retaining local roof/stair/base.
 if name in ['west_end','east_end']:cam.data.ortho_scale=40
 s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
cam.location=(-45,-180,105);cam.rotation_euler=(Vector((0,-2,5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=174
s.render.resolution_x=900;s.render.resolution_y=390;s.render.filepath='//previews/front.png'
m['units']='millimetres';m['version']='Historical circa-2021 exterior approximation, before 2024 solar';m['source_evidence']='1983 A37 plans and elevations; official 2023 roof plan; 2021 roof/rear photographs; 2018 front photograph';m['simplification']='Original mesh; coarse backed windows, stairs and ridge adjusted for miniature resolution'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scene.blend'))

# Keep only PNG image-data chunks; remove textual metadata and private render paths.
import struct
for path in P.glob('*.png'):
 raw=path.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';out=bytearray(raw[:8]);i=8
 while i<len(raw):
  n=struct.unpack('>I',raw[i:i+4])[0];kind=raw[i+4:i+8];chunk=raw[i:i+n+12]
  if kind in [b'IHDR',b'PLTE',b'IDAT',b'IEND',b'tRNS']:out.extend(chunk)
  i+=n+12
 assert i==len(raw);path.write_bytes(out)
