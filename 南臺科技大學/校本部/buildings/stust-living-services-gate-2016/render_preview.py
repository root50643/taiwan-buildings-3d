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
bpy.ops.wm.stl_import(filepath=str(OUT/'model.stl'));model=bpy.context.object;model.name='STUST_Living_Services_Draft'
mat=bpy.data.materials.new('Warm stone preview only');mat.diffuse_color=(.78,.80,.80,1);model.data.materials.append(mat)
glass=bpy.data.materials.new('Recess contrast only; same actual STL triangles');glass.diffuse_color=(.23,.29,.31,1);model.data.materials.append(glass)
base=bpy.data.materials.new('Base contrast only');base.diffuse_color=(.36,.42,.43,1);model.data.materials.append(base)
for f in model.data.polygons:
 vs=[model.data.vertices[i].co for i in f.vertices]
 if max(v.z for v in vs)<=2.00001:f.material_index=2
# Tint only actual triangular recess back faces; no surrogate geometry.
import numpy as np
params=json.loads((OUT/'draft-parameters.json').read_text());scale=params['scale_mm_per_m']
body=[((x-1000)*.1375,(800-y)*.1375) for x,y in params['source_pixel_polygons']['body_provisional']]
center=np.mean(body,axis=0)
for f in model.data.polygons:
 c=f.center;z=(c.z-1.2*scale)/scale;p=np.array([c.x,c.y])/scale
 if 13.7<z<41:
  for ia,ib in [(0,3),(3,2),(0,1)]:
   a=np.array(body[ia]);b=np.array(body[ib]);u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]])
   if np.dot(n,center-(a+b)/2)<0:n=-n
   distance=np.dot(p-a,n)
   if .11<distance<.13:f.material_index=1
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
for name,loc,aim in [('campus',(-240,200,12),(-8,6,40)),('road',(260,150,85),(0,0,35)),('rear',(130,-240,140),(0,0,35)),('top',(-1.25,3.75,300),(-1.25,3.75,0)),('campus-low',(-220,260,65),(0,0,37)),('gate',(230,200,60),(0,5,35)),('atrium',(65,130,280),(-4,-8,55)),('road-detail',(180,105,12),(10,0,40)),('campus-detail',(-240,200,12),(-8,6,40))]:
 cam.data.type='PERSP' if name in ['campus','road-detail','campus-detail'] else 'ORTHO';cam.data.lens=52
 cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
 # Frame every actual STL corner with margin, including the entire base.
 inv=cam.rotation_euler.to_matrix().transposed(); projected=[inv@(model.matrix_world@Vector(c)-cam.location) for c in model.bound_box]
 width=max(v.x for v in projected)-min(v.x for v in projected);height=max(v.y for v in projected)-min(v.y for v in projected)
 cam.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.35
 if name=='north-detail':cam.data.ortho_scale=90
 if name=='entry-detail':cam.data.ortho_scale=95
 if name=='atrium':cam.data.ortho_scale=105
 if name=='south-detail':cam.data.ortho_scale=88
 if name=='campus':front_scale=cam.data.ortho_scale
 scene.render.filepath=str(PREV/(name+'.png'));bpy.ops.render.render(write_still=True);strip_nondeterministic_metadata(PREV/(name+'.png'))
cam.location=(-240,200,12);cam.rotation_euler=(Vector((0,0,target_z))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='PERSP'
scene.render.filepath='//previews/campus.png'
cam.data.ortho_scale=front_scale
model['units']='mm';model['evidence']='STUST architect photos and2023ortho; rear walls provisional';model['model_category']='Single connected solid; not physical print tested'
# Remove private default file-browser paths before delivery.
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))



# Public limitation captions, outside model pixels.
import subprocess,shutil,hashlib
caption_code="""from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import sys
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16,index=3)
for p in Path(sys.argv[1]).glob('*.png'):
 im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im);d.rectangle((0,im.height-52,im.width,im.height),fill=(235,237,237))
 d.text((12,im.height-48),'有界近似，非測繪：背側服務牆輪廓、門梁接館支承線仍屬推配，未知背窗省略。',font=font,fill=(25,30,35))
 d.text((12,im.height-25),'官方館高42.2m／門高43m；4F天井底名義13.5m（估計12–15m）。未試印，內廊僅背靠浮雕線。',font=font,fill=(25,30,35))
 im.save(p)
"""
subprocess.run([shutil.which('python3'),'-c',caption_code,str(PREV)],check=True)
(OUT/'render-manifest.json').write_text(json.dumps({'stl_sha256':hashlib.sha256((OUT/'model.stl').read_bytes()).hexdigest(),'render_source':'Imported delivered STL only; material contrast on actual recess faces; no proxy geometry','previews':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(PREV.glob('*.png'))}},indent=2))
