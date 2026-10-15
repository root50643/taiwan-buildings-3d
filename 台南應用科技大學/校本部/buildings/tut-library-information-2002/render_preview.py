from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
O=Path(__file__).parent;P=O/'previews';P.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(O/'model.stl'));m=bpy.context.object
mat=bpy.data.materials.new('Actual STL stone');mat.diffuse_color=(.70,.64,.62,1);m.data.materials.append(mat)
for f in m.data.polygons:f.material_index=0
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.world.color=(.08,.09,.11)
s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard'
bpy.ops.object.camera_add();c=bpy.context.object;s.camera=c;c.data.type='ORTHO';c.data.ortho_scale=180
views=[('front',(230,-270,70),(0,0,40)),('rear',(-250,-20,95),(0,0,40)),('top',(0,0,350),(0,0,0)),('aerial',(200,-240,230),(0,0,30)),('west-low',(-230,-30,8),(0,0,40)),('entry',(160,-200,110),(8,-25,11)),('front-upper',(230,-270,90),(0,-8,63)),('west-detail',(-250,-50,85),(-35,-16,40))]
for name,loc,aim in views:
 c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=180
 
 if name=='entry':c.data.ortho_scale=72
 if name=='front-upper':c.data.ortho_scale=95
 if name=='west-detail':c.data.ortho_scale=125
 s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;s.unit_settings.length_unit='MILLIMETERS'
m['evidence']='TUT2002 library-information;cross-year bounded exterior,not surveyed'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))

# Deterministic PNG bytes and visible limitations, without source photos.
import subprocess,shutil
code="""from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import sys
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16,index=3)
for p in Path(sys.argv[1]).glob('*.png'):
 im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im);d.rectangle((0,im.height-50,im.width,im.height),fill=(238,238,238))
 d.text((10,im.height-48),'跨年有界近似，非測繪：主高46m名義（42–50m試配）；頂設備／矮圓帽高度未知。',font=font,fill='black')
 d.text((10,im.height-25),'北／東北未知窗省略；西後照片裁切，僅可見區分組推配。未試印。',font=font,fill='black');im.save(p)
"""
subprocess.run([shutil.which('python3'),'-c',code,str(P)],check=True)
(O/'render-manifest.json').write_text(json.dumps({'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest(),'render_source':'Single grey material on delivered STL only','previews':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(P.glob('*.png'))}},indent=2))
