from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).parent;P=R/'previews';P.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.wm.stl_import(filepath=str(R/'model.stl'));m=bpy.context.object;m.name='CSU_Library_Technology_Original_STL'
a=bpy.data.materials.new('neutral actual mesh');a.diffuse_color=(.70,.69,.65,1);m.data.materials.append(a)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=1.8;s.display.shading.curvature_valley_factor=1.5;s.world.color=(.08,.095,.12);s.display.shading.background_type='WORLD';s.view_settings.view_transform='Standard';s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
for prop in s.render.bl_rna.properties:
 if prop.identifier.startswith('use_stamp') and prop.type=='BOOLEAN':setattr(s.render,prop.identifier,False)
s.render.image_settings.file_format='PNG'
bpy.ops.object.camera_add();c=bpy.context.object;s.camera=c;c.data.type='ORTHO';c.data.ortho_scale=185
for name,loc,aim,typ in [('fit008',(6.286487398444933, 57.95108453649795, 94.27682392718572),(3.4124605838576136, -22.744305803944872, 30.232094802499997),'PERSP'),('front',(-25,280,180),(0,0,37),'ORTHO'),('north',(0,270,130),(0,0,37),'ORTHO'),('rear',(-220,-140,150),(0,0,37),'ORTHO'),('west',(-260,-30,130),(0,0,37),'ORTHO'),('east',(260,-30,130),(0,0,37),'ORTHO'),('top',(0,-2.88,320),(0,-2.88,0),'ORTHO'),('aerial',(-25,280,260),(0,0,37),'ORTHO'),('swfit',(25,150,130),(0,-2,24),'PERSP'),('eastfit',(-40,540,300),(0,-2,24),'PERSP')]:
 c.data.type=typ;c.data.lens=25.311411369810642 if name=="fit008" else 100 if name=='eastfit' else 35 if typ=='PERSP' else 55;c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();
 if typ=='ORTHO':
  target=Vector((0,-2.88,30.3)) if name!='top' else Vector((0,-2.88,0));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();
  if name=='top':c.rotation_euler=(0,0,0) # Image up is geographic north/+Y, no camera-track roll.
  inv=c.rotation_euler.to_matrix().transposed();bb=[inv@(Vector(v)-target)for v in m.bound_box];w=max(v.x for v in bb)-min(v.x for v in bb);h=max(v.y for v in bb)-min(v.y for v in bb);c.data.ortho_scale=max(w,h*4/3)*1.12
 s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
# Save relative preview path and clear private file browser defaults.
s.render.filepath='//previews/front.png'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;s.unit_settings.length_unit='MILLIMETERS';bpy.ops.wm.save_as_mainfile(filepath=str(R/'scene.blend'))
