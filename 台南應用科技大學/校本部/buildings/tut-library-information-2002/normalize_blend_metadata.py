from pathlib import Path
import bpy
O=Path(__file__).resolve().parent
bpy.context.preferences.filepaths.save_version=0
bpy.context.scene.render.filepath='//previews/west-detail.png'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
