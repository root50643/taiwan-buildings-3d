"""Render actual final STL geometry and save an inspectable Blender scene."""
import bpy, math, sys
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
root=Path(args[0]).resolve() if args else Path(__file__).resolve().parent/'output'
bpy.ops.wm.read_factory_settings(use_empty=False)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(root/'model.stl'))
obj=bpy.context.object;obj.name='THU original arts center historical study — actual STL'
mat=bpy.data.materials.new('Warm limestone');mat.diffuse_color=(.73,.68,.57,1);mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.73,.68,.57,1);bsdf.inputs['Roughness'].default_value=.82
obj.data.materials.append(mat)
# Mesh remains flat shaded so tessellation and print geometry are honest.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False
scene.render.use_stamp_filename=False
scene.render.use_stamp_hostname=False
scene.render.use_stamp_note=False
scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.world.color=(.35,.35,.35)
scene.view_settings.view_transform='AgX'
for name,loc,energy,size in [('Key',(-40,-80,160),220000,100),('Fill',(190,80,160),160000,100)]:
    bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name=name;l.data.energy=energy;l.data.shape='DISK';l.data.size=size
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=188
center=Vector((74,54,9))
def shoot(name,pos,target=center,scale=188):
    cam.location=pos;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
    scene.render.filepath='//'+name+'.png';bpy.ops.render.render(write_still=True)
cam.location=(210,-155,165);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=188
scene['historical_title']='東海大學原藝術中心（1962–1964 年史料外觀研究版本）'
scene['units']='Model mesh coordinates are millimetres; independent approximate exterior reconstruction'
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
scene.render.filepath='//preview-entrance.png'
# Clear inactive file-browser directory storage through the supported RNA API.
# A full neutral value overwrites tail bytes before the final relative directory.
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type=='FILE_BROWSER' and space.params:
                space.params.directory=b'/'*1023
                space.params.directory=b'//'
for im in list(bpy.data.images):
    if im.source=='VIEWER' and not im.filepath and not im.packed_file:
        bpy.data.images.remove(im)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'model.blend'))

# The saved scene is clean before any render. All render paths are relative,
# so fixed-length RNA storage never receives a private absolute render path.
if '--save-only' not in args:
    shoot('preview-entrance',(210,-155,165))
    shoot('preview-courtyard',(-120,165,180))
    shoot('preview-plan',(74,54,300),Vector((74,54,0)),165)
