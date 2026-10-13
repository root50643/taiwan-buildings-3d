"""Detailed courtyard view of actual saved STL mesh, no geometry changes."""
from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'scene.blend'))
s=bpy.context.scene;c=s.camera;c.location=(-85,80,125)
c.rotation_euler=(Vector((6,-15,15))-c.location).to_track_quat('-Z','Y').to_euler()
c.data.ortho_scale=115;c.data.shift_x=0;c.data.shift_y=0
s.render.resolution_x=900;s.render.resolution_y=700
s.render.filepath=str(R/'previews/courtyard.png');bpy.ops.render.render(write_still=True)
