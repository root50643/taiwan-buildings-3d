"""Render the actual STL and save an editable Blender scene. Blender 4.3.2+.
Run: blender -b -t 4 -P render_preview.py
"""
import bpy,json,os,struct,math
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
bpy.ops.wm.stl_import(filepath=str(OUT/'model.stl'));model=bpy.context.object;model.name='TCU_Hexin_Bounded_Draft'
mat=bpy.data.materials.new('Warm stone preview only');mat.diffuse_color=(.78,.80,.80,1);model.data.materials.append(mat)
glass=bpy.data.materials.new('Recess contrast only; same actual STL triangles');glass.diffuse_color=(.23,.29,.31,1);model.data.materials.append(glass)
base=bpy.data.materials.new('Base contrast only');base.diffuse_color=(.36,.42,.43,1);model.data.materials.append(base)
for f in model.data.polygons:
 vs=[model.data.vertices[i].co for i in f.vertices]
 if max(v.z for v in vs)<=2.00001:f.material_index=2
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
for name,loc,aim in [('north',(140,-220,100),(5,20,target_z)),('east',(270,60,65),(5,25,target_z)),('south',(100,250,110),(0,30,target_z)),('west',(-240,80,110),(0,25,target_z)),('north-low',(95,-280,40),(15,-10,13)),('entry',(240,90,40),(-2,55,13)),('top',(0,30,300),(0,30,0)),('north-detail',(85,-250,18),(35,-15,14)),('entry-detail',(260,100,18),(-1,59,13)),('south-detail',(130,50,18),(30,2,13))]:
 loc=(loc[0],-loc[1],loc[2]);aim=(aim[0],-aim[1],aim[2])
 cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
 # Frame every actual STL corner with margin, including the entire base.
 inv=cam.rotation_euler.to_matrix().transposed(); projected=[inv@(model.matrix_world@Vector(c)-cam.location) for c in model.bound_box]
 width=max(v.x for v in projected)-min(v.x for v in projected);height=max(v.y for v in projected)-min(v.y for v in projected)
 cam.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.18
 if name=='north-detail':cam.data.ortho_scale=90
 if name=='entry-detail':cam.data.ortho_scale=95
 if name=='south-detail':cam.data.ortho_scale=88
 if name=='north':front_scale=cam.data.ortho_scale
 scene.render.filepath=str(PREV/(name+'.png'));bpy.ops.render.render(write_still=True);strip_nondeterministic_metadata(PREV/(name+'.png'))
cam.location=(140,-220,100);cam.rotation_euler=(Vector((0,30,target_z))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath='//previews/north.png'
cam.data.ortho_scale=front_scale
model['units']='mm';model['evidence']='TCU official2025map;2018StreetView and2018/2024ortho; bounded unmeasured draft';model['model_category']='Single connected solid; not physical print tested'
# Remove private default file-browser paths before delivery.
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))


# Add an explicit uncertainty caption outside the building image, deterministically.
import subprocess,shutil
caption_code="""from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import sys
for p in Path(sys.argv[1]).glob('*.png'):
 im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im)
 d.rectangle((0,im.height-38,im.width,im.height),fill=(235,237,237))
 d.text((12,im.height-32),'BOUNDED ESTIMATE / NOT SURVEYED: west windows omitted; F/G low roof level uncertain.',fill=(25,30,35))
 d.text((12,im.height-17),'A16m / E13m / F-G14.5m / low roof11.8m are provisional image-fit values. Actual STL.',fill=(25,30,35))
 im.save(p)
"""
subprocess.run([shutil.which('python3'),'-c',caption_code,str(PREV)],check=True)
(OUT/'render-manifest.json').write_text(json.dumps({'stl_sha256':__import__('hashlib').sha256((OUT/'model.stl').read_bytes()).hexdigest(),'render_source':'Imported delivered model.stl; no proxy geometry','previews':{p.name:__import__('hashlib').sha256(p.read_bytes()).hexdigest() for p in sorted(PREV.glob('*.png'))}},indent=2))
