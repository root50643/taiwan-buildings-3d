"""Render the actual STL and save an editable Blender scene. Blender 4.3.2+.
Run: blender -b -t 4 -P render_preview.py
"""
import bpy
from mathutils import Vector
from pathlib import Path
OUT=Path(__file__).resolve().parent;PREV=OUT/'previews';PREV.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(OUT/'model.stl'));model=bpy.context.object;model.name='Printable_NHRI_MEP_Approximate_Massing'
mat=bpy.data.materials.new('Pale warm stone preview only');mat.diffuse_color=(.76,.73,.65,1);model.data.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.35
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.5;scene.display.shading.curvature_valley_factor=1.2
scene.display.shading.show_specular_highlight=True;scene.display.shading.background_type='WORLD';scene.world.color=(.055,.065,.085)
scene.view_settings.view_transform='Standard';scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001;scene.unit_settings.length_unit='MILLIMETERS'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Preview_camera';scene.camera=cam;cam.data.type='ORTHO'
def frame(loc):
    aim=Vector((0,0,12.4));cam.location=loc;cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler()
    inv=cam.rotation_euler.to_matrix().transposed();projected=[inv@(model.matrix_world@Vector(c)-cam.location) for c in model.bound_box]
    width=max(v.x for v in projected)-min(v.x for v in projected);height=max(v.y for v in projected)-min(v.y for v in projected)
    cam.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.18
for name,loc in [('front',(-150,-235,190)),('rear',(150,235,190)),('elevation',(0,-260,12.4))]:
    frame(loc);scene.render.filepath=str(PREV/(name+'.png'));bpy.ops.render.render(write_still=True)
frame((-150,-235,190));scene.render.filepath='//previews/front.png'
model['units']='mm';model['evidence']='MEDIUM identity: 2017 public aerial correlated with official 2009 labeled external map; approximate exterior massing only'
model['model_category']='Single connected printable solid; no equipment, pipes or interior'
# Remove Blender's generic host directory from saved file-browser workspaces.
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type == 'FILE_BROWSER' and space.params:
                space.params.directory = b'//'
                space.params.filename = 'scene.blend'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'))
