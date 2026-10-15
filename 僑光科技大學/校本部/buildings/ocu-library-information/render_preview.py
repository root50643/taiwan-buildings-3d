from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).parent;P=R/'previews';P.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.wm.stl_import(filepath=str(R/'model.stl'));m=bpy.context.object;m.name='OCU_Library_Information_Original_STL'
a=bpy.data.materials.new('neutral actual mesh');a.diffuse_color=(.70,.69,.65,1);m.data.materials.append(a)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=1.8;s.display.shading.curvature_valley_factor=1.5;s.world.color=(.08,.095,.12);s.display.shading.background_type='WORLD';s.view_settings.view_transform='Standard';s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
for prop in s.render.bl_rna.properties:
 if prop.identifier.startswith('use_stamp') and prop.type=='BOOLEAN':setattr(s.render,prop.identifier,False)
s.render.image_settings.file_format='PNG'
bpy.ops.object.camera_add();c=bpy.context.object;s.camera=c;c.data.type='ORTHO';c.data.ortho_scale=185
for name,loc in [('front',(5,-290,165)),('rear',(-190,230,150)),('west',(-280,-20,145)),('east',(280,-20,145)),('top',(0,0,330)),('aerial',(-145,-235,220)),('frontfit',(80,-230,5)),('backfit',(-175,190,14)),('crown',(-110,-40,91))]:
 c.data.type='PERSP' if name.endswith('fit') else 'ORTHO';c.data.lens=45;c.location=loc;target=Vector((0,-3,48));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler()
 if name=='top':target=Vector((0,0,0));c.rotation_euler=(0,0,0)
 if c.data.type=='ORTHO':
  inv=c.rotation_euler.to_matrix().transposed();bb=[inv@(Vector(v)-target)for v in m.bound_box];w=max(v.x for v in bb)-min(v.x for v in bb);h=max(v.y for v in bb)-min(v.y for v in bb);c.data.ortho_scale=max(w,h*4/3)*1.12
 if name=='crown':
  c.data.type='PERSP';c.data.lens=50;target=Vector((-44.8,0.3,94));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
# Save relative preview path and clear private file browser defaults.
s.render.filepath='//previews/front.png'
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;s.unit_settings.length_unit='MILLIMETERS';bpy.ops.wm.save_as_mainfile(filepath=str(R/'scene.blend'))
