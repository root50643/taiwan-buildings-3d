"""Create an editable Blender scene and render five bounded inspection views.

Run with Blender: blender -b --python source/render_preview.py
or with Blender's PyPI module: python source/render_preview.py
The STL is the sole model geometry. No third-party images are embedded.
"""
from pathlib import Path
import hashlib
import json
import math
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
STL = ROOT/'models/v1/model.stl'
OUT = ROOT/'previews/v1'


def material(name, color, roughness=0.7):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    return mat


def aim(obj, point):
    obj.rotation_euler = (Vector(point)-obj.location).to_track_quat('-Z', 'Y').to_euler()


def create_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'MILLIMETERS'
    scene.unit_settings.scale_length = 0.001
    bpy.ops.wm.stl_import(filepath=str(STL))
    obj = bpy.context.object
    obj.name = 'APOLLO_print_mesh_mm'
    obj['STL_SHA256'] = hashlib.sha256(STL.read_bytes()).hexdigest()
    obj['scope'] = 'Solid representative exterior; unknown faces neutral; estimated height'
    mats = [material('wall - display only', (0.57, 0.64, 0.65)),
            material('roof - display only', (0.24, 0.34, 0.38)),
            material('window and door recess - display only', (0.10, 0.20, 0.24)),
            material('3mm printing base', (0.36, 0.38, 0.39))]
    for mat in mats:
        obj.data.materials.append(mat)
    for face in obj.data.polygons:
        coords = [obj.data.vertices[i].co for i in face.vertices]
        center = sum(coords, Vector())/len(coords)
        if max(v.z for v in coords) <= 3.00001:
            face.material_index = 3
        elif abs(face.normal.x) < 0.9 and max(v.z for v in coords)>32.74:
            face.material_index = 1
        elif -38.5 < center.y < -37.5 and 3.01 < center.z < 29:
            face.material_index = 2
        else:
            face.material_index = 0
    ground_mat = material('render ground - not printed', (0.82, 0.84, 0.84))
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -0.12))
    ground = bpy.context.object
    ground.name = 'RenderGround_NOT_STL'
    ground.data.materials.append(ground_mat)
    world = bpy.data.worlds.new('Neutral world')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[0].default_value = (0.82,0.86,0.90,1)
    world.node_tree.nodes['Background'].inputs[1].default_value = 0.55
    scene.world = world
    for name, position, energy, size in [('Key',(-90,-140,230),30000,180),('Fill',(100,30,160),16000,160)]:
        data = bpy.data.lights.new(name, 'AREA')
        data.energy, data.shape, data.size = energy, 'DISK', size
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = position
        aim(light,(0,0,10))
    cam_data = bpy.data.cameras.new('Inspection camera')
    cam = bpy.data.objects.new('Inspection camera', cam_data)
    scene.collection.objects.link(cam)
    cam_data.type = 'ORTHO'
    cam_data.lens = 50
    cam_data.clip_end = 5000
    scene.camera = cam
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = False
    scene.cycles.seed = 0
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 4
    scene.render.resolution_x, scene.render.resolution_y = 1000, 780
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.render.use_file_extension = True
    return scene, obj


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    scene, obj = create_scene()
    views = [
        ('front', (210,-270,180), (0,0,18), 225),
        ('rear', (-210,270,180), (0,0,18), 225),
        ('long-front', (0,-300,18), (0,0,18), 212),
        ('end', (-300,0,18), (0,0,18), 130),
        ('top', (0,0,300), (0,0,0), 212),
    ]
    # Default saved view is the photographed facade side. Disable automatic backups.
    bpy.context.preferences.filepaths.save_version = 0
    bpy.context.preferences.filepaths.file_preview_type = 'NONE'
    scene.camera.location = views[0][1]
    aim(scene.camera, views[0][2])
    scene.camera.data.ortho_scale = views[0][3]
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    blend = ROOT/'models/v1/scene.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
    manifest = {'renderer':bpy.app.version_string, 'engine':'CYCLES CPU', 'samples':32,
                'denoising':False, 'pixels':[1000,780],
                'stl_sha256':hashlib.sha256(STL.read_bytes()).hexdigest(),
                'scene_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(), 'views':[]}
    for name, position, target, scale in views:
        scene.camera.location = position
        aim(scene.camera, target)
        scene.camera.data.ortho_scale = scale
        path = OUT/(name+'.png')
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        manifest['views'].append({'name':name,'position':position,'target':target,
            'ortho_scale':scale,'png_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (OUT/'render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    print('APOLLO: five views rendered; mesh and camera scene saved')


if __name__ == '__main__':
    main()
