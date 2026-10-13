"""Actual-STL centre detail with physical lighting; no geometry changes."""
import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(R/'model.stl'));o=bpy.context.object
m=bpy.data.materials.new('Neutral miniature');m.diffuse_color=(.6,.64,.68,1);o.data.materials.append(m)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=128;s.cycles.use_denoising=False
s.world.color=(.15,.15,.15)
for loc,power,size in [((-60,-100,125),600000,70),((80,-30,75),100000,55)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((-12,0,33))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(-12,-200,33));c=bpy.context.object;c.rotation_euler=(Vector((-12,0,33))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=68;s.camera=c
s.render.resolution_x=580;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'previews/center-detail.png');s.view_settings.view_transform='AgX';bpy.ops.render.render(write_still=True)
