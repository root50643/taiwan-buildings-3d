"""Render legible true orthographic elevations from the ACTUAL delivered STL.
Run with Blender: blender -b -t 2 -P render_elevations.py
No geometry changes and no post-processing of the generated elevations.
"""
import bpy,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(R/'model.stl'));obj=bpy.context.object
mat=bpy.data.materials.new('Neutral model');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.7,.64,.52,1);bs.inputs['Roughness'].default_value=.8;obj.data.materials.append(mat)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=False
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.35,.38,.44,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast'
s.render.resolution_x=1000;s.render.resolution_y=500;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for loc,power,size in [((-90,-150,130),250000,130),((90,150,140),250000,130),((0,0,200),170000,110)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,20))-l.location).to_track_quat('-Z','Y').to_euler()
z=max(v.co.z for v in obj.data.vertices)/2
bpy.ops.object.camera_add();c=bpy.context.object;s.camera=c;c.data.type='ORTHO';c.data.ortho_scale=163;c.data.clip_end=1000
for name,y in [('elevation',-260),('rear_elevation',260)]:
 c.location=(0,y,z);c.rotation_euler=(Vector((0,0,z))-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
