"""Import the actual STL, render full-framed previews, and save an editable scene.
Usage: blender -b -t 4 -P render_preview.py
"""
from pathlib import Path
import bpy
from mathutils import Vector

OUT = Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(OUT/'model.stl'))
model = bpy.context.object
model.name = 'Printable_NHRI_Station48_Exterior'
stone = bpy.data.materials.new('White facade - preview color only')
stone.diffuse_color = (.79, .79, .75, 1)
glass = bpy.data.materials.new('Recessed glass - preview color only')
glass.diffuse_color = (.15, .28, .30, 1)
model.data.materials.append(stone)
model.data.materials.append(glass)
# Only the already modeled recess backing faces receive glass-color materials.
# This changes no geometry. STL contains no color or material data.
for p in model.data.polygons:
    x,y,z = p.center
    narrow = -44 < x < -35 and abs(y+31.25) < .015 and 4 < z < 139
    right = 27.25 < x < 46.75 and abs(y+31.2) < .015 and 43 < z < 128
    ground = -26 < x < 12 and abs(y+32.35) < .015 and 9 < z < 31
    entry = 20.75 < x < 41.25 and abs(y+35.65) < .015 and 5 < z < 29
    if p.normal.y < -.9 and (narrow or right or ground or entry):
        p.material_index = 1
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.studiolight_rotate_z = .35
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.curvature_ridge_factor = 1.35
scene.display.shading.curvature_valley_factor = 1.2
scene.display.shading.show_specular_highlight = True
scene.display.shading.background_type = 'WORLD'
scene.world.color = (.06, .075, .10)
scene.view_settings.view_transform = 'Standard'
scene.render.resolution_x = 1400
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = .001
scene.unit_settings.length_unit = 'MILLIMETERS'
bpy.ops.object.camera_add()
cam = bpy.context.object
cam.name = 'Preview_camera'
cam.data.type = 'ORTHO'
scene.camera = cam

def frame(loc):
    aim = Vector((1, -1, 75))
    cam.location = loc
    cam.rotation_euler = (aim-cam.location).to_track_quat('-Z','Y').to_euler()
    inv = cam.rotation_euler.to_matrix().transposed()
    points = [inv@(model.matrix_world@Vector(c)-cam.location) for c in model.bound_box]
    width = max(v.x for v in points)-min(v.x for v in points)
    height = max(v.y for v in points)-min(v.y for v in points)
    cam.data.ortho_scale = max(width, height*scene.render.resolution_x/scene.render.resolution_y)*1.16

for name, loc in [('front', (200,-290,180)), ('rear', (-210,270,190)),
                  ('elevation', (1,-350,75))]:
    frame(loc)
    scene.render.filepath = str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
frame((200,-290,180))
scene.render.filepath = '//front.png'
model['units'] = 'mm'
model['source'] = 'https://campus.nhri.org.tw/ ; station 48 ; 2017 Spring'
model['scope'] = 'Selected exterior tower mass only; bridge omitted; depth and unseen elevations approximate'
model['model_category'] = 'Single connected printable solid; no internal layout'
# Keep the saved file-browser UI portable rather than exposing a build-home path.
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type == 'FILE_BROWSER' and space.params:
                space.params.directory = b'//'
                space.params.filename = 'scene.blend'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))
