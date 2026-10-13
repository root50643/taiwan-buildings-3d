from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'scene.blend'))
s=bpy.context.scene;c=s.camera;c.location=(-180,100,27);target=Vector((-49,19,19));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=118
s.render.resolution_x=900;s.render.resolution_y=620;s.render.resolution_percentage=100;s.render.filepath=str(R/'previews/piloti.png');s.display.shading.show_shadows=False;s.display.shading.background_type='WORLD';s.world.color=(.72,.74,.76)
bpy.ops.render.render(write_still=True)
