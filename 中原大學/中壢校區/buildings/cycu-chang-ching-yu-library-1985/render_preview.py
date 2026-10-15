from pathlib import Path
import bpy,hashlib,json,subprocess,shutil
from mathutils import Vector
O=Path(__file__).parent;P=O/'previews';P.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(O/'model.stl'));m=bpy.context.object;m.name='CYCU_Chang_Ching_Yu_library'
mat=bpy.data.materials.new('Single actual STL grey');mat.diffuse_color=(.73,.74,.75,1);m.data.materials.append(mat)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.world.color=(.07,.08,.10);s.view_settings.view_transform='Standard';s.render.resolution_x=1100;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
bpy.ops.object.camera_add();c=bpy.context.object;s.camera=c;c.data.type='ORTHO'
for name,loc,aim,scale in [('front',(150,-250,90),(0,-15,20),205),('rear',(125,220,90),(0,-5,22),205),('top',(0,-21,300),(0,-21,0),205),('aerial',(150,-230,220),(0,-18,15),205),('side',(-240,0,85),(0,-10,22),205),('entry',(0,-240,90),(0,-51,15),120),('garden',(120,180,100),(0,35,12),130),('roof',(150,-100,220),(0,0,38),150)]:
 c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
s.render.filepath='//previews/front.png';s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;s.unit_settings.length_unit='MILLIMETERS'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
code="""from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import sys
f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16,index=3)
for p in Path(sys.argv[1]).glob('*.png'):
 raw=Image.open(p).convert('RGB');im=Image.new('RGB',(raw.width,raw.height+50),(238,238,238));im.paste(raw,(0,0));d=ImageDraw.Draw(im)
 d.text((10,im.height-47),'有界近似，非測繪：18.85m起算由1985雙剖面推定為1F至主屋面；非梯核最高點。',font=f,fill='black')
 d.text((10,im.height-24),'地下花園／廣場下會議廳深度與地腳仍為剖面配圖估計；不含懷恩樓。未試印。',font=f,fill='black');im.save(p)
"""
subprocess.run([shutil.which('python3'),'-c',code,str(P)],check=True)
(O/'render-manifest.json').write_text(json.dumps({'stl_sha256':hashlib.sha256((O/'model.stl').read_bytes()).hexdigest(),'render_source':'Delivered actual STL only','previews':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(P.glob('*.png'))}},indent=2))
