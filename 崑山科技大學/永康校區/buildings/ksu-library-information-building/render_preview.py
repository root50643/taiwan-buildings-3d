"""Render the actual STL and save an editable Blender scene. Blender 4.3.2+.
Run: blender -b -t 4 -P render_preview.py
"""
import bpy,json,os,struct,subprocess
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from pathlib import Path
OUT=Path(__file__).resolve().parent; PREV=OUT/'previews'; PREV.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(OUT/'model.stl'));model=bpy.context.object;model.name='KSU_Library_Information_Draft'
mat=bpy.data.materials.new('Warm stone preview only');mat.diffuse_color=(.69,.64,.54,1);model.data.materials.append(mat)
target_z=(min(v.co.z for v in model.data.vertices)+max(v.co.z for v in model.data.vertices))/2
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.35
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
frames=[]
for name,loc,aim in [('front',(-180,300,70),(0,0,20)),('rear',(-180,-300,70),(0,0,20)),('left',(-280,-40,95),(0,0,20)),('right',(280,-100,75),(0,0,20)),('top',(0,0,300),(0,0,0))]:
 scene.render.resolution_y=500 if name=='roof-detail' else 900
 cam.data.type='PERSP' if name in ['porch-detail','right','tower-detail','south-detail','rear-detail'] else 'ORTHO';cam.data.lens=55
 aim=(0,0,target_z)
 cam.location=loc;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
 # Frame every actual STL corner with margin, including the entire base.
 inv=cam.rotation_euler.to_matrix().transposed(); projected=[inv@(model.matrix_world@Vector(c)-cam.location) for c in model.bound_box]
 width=max(v.x for v in projected)-min(v.x for v in projected);height=max(v.y for v in projected)-min(v.y for v in projected)
 cam.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.18
 if name=='roof-detail':cam.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.18
 if name=='porch-detail':cam.data.ortho_scale=100
 if name=='north-detail':cam.data.ortho_scale=100
 if name=='tower-detail':cam.data.ortho_scale=40;cam.data.lens=190
 if name=='south-detail':cam.data.lens=60
 if name=='rear-detail':cam.data.lens=70
 # Every public preview includes the full actual STL and base.
 if cam.data.type=='PERSP':
  for _ in range(50):
   bpy.context.view_layer.update()
   ndc=[world_to_camera_view(scene,cam,model.matrix_world@Vector(c)) for c in model.bound_box]
   if all(.04<v.x<.96 and .04<v.y<.96 and v.z>0 for v in ndc):break
   cam.location=Vector(aim)+(cam.location-Vector(aim))*1.06
  else:raise RuntimeError('Cannot frame entire model')
 bpy.context.view_layer.update()
 ndc=[world_to_camera_view(scene,cam,model.matrix_world@Vector(c)) for c in model.bound_box]
 assert all(0<v.x<1 and 0<v.y<1 and v.z>0 for v in ndc), (name,ndc)
 frames.append({'file':'previews/'+name+'.png','all_original_STL_bbox_corners_in_frame':True,'ndc_bounds':[min(v.x for v in ndc),min(v.y for v in ndc),max(v.x for v in ndc),max(v.y for v in ndc)]})
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
 # Public uncertainty caption, outside the original actual-STL image (no cropping).
 caption_code="from PIL import Image,ImageDraw,ImageFont; import sys; p=sys.argv[1]; im=Image.open(p).convert('RGB'); out=Image.new('RGB',(im.width,im.height+64),(242,240,235)); out.paste(im,(0,0)); d=ImageDraw.Draw(out); f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',19); d.text((15,im.height+4),'崑山圖資館有界草稿：55m採官方總高口徑；分層／背接與局部高程為圖像推估。',font=f,fill=(30,30,30)); d.text((15,im.height+31),'未知短側細窗省略；地上11層＋地下2層，中庭帶頂封背簡化。未試印，須切片／支撐檢查。',font=f,fill=(30,30,30)); out.save(p)"
 subprocess.run(['python3','-c',caption_code,str(path)],check=True)
(OUT/'preview-framing-check.json').write_text(json.dumps({'passed':True,'checks':{'every_public_preview_includes_entire_STL_and_base':True},'frames':frames},indent=2))
cam.data.type="ORTHO";cam.location=(-180,300,70);cam.rotation_euler=(Vector((0,0,target_z))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath='//previews/front.png'
scene.render.resolution_y=900
cam.data.ortho_scale=front_scale
model['units']='mm';model['evidence']='KSU library: NLSC roof and architect north/south photos, bounded heights; exact geometry QA separate';model['model_category']='Single connected exterior miniature; not physically print-tested'
# Remove private default file-browser paths before delivery.
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))

