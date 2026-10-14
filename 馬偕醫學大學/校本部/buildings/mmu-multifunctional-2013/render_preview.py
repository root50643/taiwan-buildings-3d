"""Render the actual STL and save an editable Blender scene. Blender 4.3.2+.
Run: blender -b -t 4 -P render_preview.py
"""
import bpy,json,os,struct
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent; PREV=OUT/'previews'; PREV.mkdir(exist_ok=True)
def strip_nondeterministic_metadata(path):
 raw=path.read_bytes(); out=raw[:8]; i=8
 while i<len(raw):
  n=struct.unpack('>I',raw[i:i+4])[0]; kind=raw[i+4:i+8]; chunk=raw[i:i+12+n]
  if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf'}:out+=chunk
  i+=12+n
 path.write_bytes(out)  # Pixel bytes unchanged; remove date/time and private-path stamps.

bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(OUT/'model.stl'));model=bpy.context.object;model.name='MMU_Multifunctional_2013'
mat=bpy.data.materials.new('Warm stone preview only');mat.diffuse_color=(.78,.80,.80,1);model.data.materials.append(mat)
glass=bpy.data.materials.new('Recess contrast only; same actual STL triangles');glass.diffuse_color=(.23,.29,.31,1);model.data.materials.append(glass)
base=bpy.data.materials.new('Base contrast only');base.diffuse_color=(.36,.42,.43,1);model.data.materials.append(base)
brick=bpy.data.materials.new('Brick preview only');brick.diffuse_color=(.50,.25,.16,1);model.data.materials.append(brick)
hall_a=Vector((29.952,35.022));hall_b=Vector((44.382,45.006));hall_u=(hall_b-hall_a).normalized();hall_n=Vector((hall_u.y,-hall_u.x));hall_mid=(hall_a+hall_b)/2
for f in model.data.polygons:
 vs=[model.data.vertices[i].co for i in f.vertices]
 if max(v.z for v in vs)<=3.00001:f.material_index=2
 # Neutral solid material avoids falsely colouring long coplanar triangles.
 if abs(f.normal.y)>.99 and any(all(abs(v.y-y)<.0002 for v in vs) for y in [46.3,46.1,-16.55,-16.45,-16.6,45.8,26.5,-46.35,-21.9,-20.4]):f.material_index=1
 if abs(f.normal.x)>.99 and any(all(abs(v.x-x)<.0002 for v in vs) for x in [-69.4,58.6,41.5]):f.material_index=1
 # Hall recess rear planes, oblique to orthogonal model axes.
 if abs(f.normal.z)<.01 and any(all(abs((Vector((v.x,v.y))-hall_mid).dot(hall_n)-depth)<.001 for v in vs) for depth in [5.1,3.5]):f.material_index=1
# Face materials expose the existing recesses only; do not change STL geometry.
target_z=(min(v.co.z for v in model.data.vertices)+max(v.co.z for v in model.data.vertices))/2
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.35
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.5;scene.display.shading.curvature_valley_factor=1.2
scene.display.shading.show_specular_highlight=True;scene.display.shading.background_type='WORLD';scene.world.color=(.055,.065,.085)
scene.view_settings.view_transform='Standard'
scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Preview_camera';scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=180
for name,loc,aim in [('front',(-155,250,150),(0,0,target_z)),('rear',(-195,-230,145),(0,0,target_z)),('elevation',(0,260,target_z),(0,0,target_z)),('west',(-260,0,90),(0,0,target_z)),('east',(260,0,90),(0,0,target_z)),('rear-elevation',(-110,-300,70),(0,-5,19)),('top',(0,0,300),(0,0,0))]:
 cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
 # Frame every actual STL corner with margin, including the entire base.
 inv=cam.rotation_euler.to_matrix().transposed(); projected=[inv@(model.matrix_world@Vector(c)-cam.location) for c in model.bound_box]
 width=max(v.x for v in projected)-min(v.x for v in projected);height=max(v.y for v in projected)-min(v.y for v in projected)
 cam.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.18
 if name=='front':front_scale=cam.data.ortho_scale
 scene.render.filepath=str(PREV/(name+'.png'));bpy.ops.render.render(write_still=True);strip_nondeterministic_metadata(PREV/(name+'.png'))
cam.location=(-155,250,150);cam.rotation_euler=(Vector((0,0,target_z))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath='//previews/front.png'
cam.data.ortho_scale=front_scale
model['units']='mm';model['evidence']='MMU official floor plans; architect plan and actual photographs; bounded non-survey model';model['model_category']='Single connected printable solid'
# Remove private default file-browser paths before delivery.
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))


(OUT/'render-manifest.json').write_text(json.dumps({'stl_sha256':__import__('hashlib').sha256((OUT/'model.stl').read_bytes()).hexdigest(),'render_source':'Imported delivered model.stl; no proxy geometry','previews':{p.name:__import__('hashlib').sha256(p.read_bytes()).hexdigest() for p in sorted(PREV.glob('*.png'))}},indent=2))
