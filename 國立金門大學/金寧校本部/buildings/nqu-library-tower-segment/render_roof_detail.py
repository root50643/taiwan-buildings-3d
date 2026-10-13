from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'scene.blend'))
s=bpy.context.scene;s.render.use_stamp_filename=False;c=s.camera;c.location=(170,-240,110);c.rotation_euler=(Vector((0,0,132))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=82
s.render.resolution_x=900;s.render.resolution_y=500;s.render.filepath=str(R/'previews/roof-detail.png');bpy.ops.render.render(write_still=True)
