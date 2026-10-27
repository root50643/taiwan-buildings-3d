"""Render a separate NKNU front-terrace homepage cover without saving the source.
Run: blender --disable-autoexec --background --factory-startup --python-exit-code 1 \
    --python render_homepage_preview.py
Optional: -- --source /model/directory --out /output/directory
Only camera and square framing change. Original geometry, hidden edit components,
materials, lighting, world, native scene and nine technical previews are preserved.
"""
import argparse, hashlib, json, math, pathlib, struct, sys
import bpy
import numpy as np
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

HERE = pathlib.Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--source', type=pathlib.Path, default=HERE)
p.add_argument('--out', type=pathlib.Path, default=HERE)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ROOT, OUT = a.source.resolve(), a.out.resolve()
(OUT / 'previews').mkdir(parents=True, exist_ok=True)
(OUT / 'qa').mkdir(parents=True, exist_ok=True)
source_names = ['nknu-yanchao-library-information.blend', 'mesh-data.npz']
source_hashes = {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in source_names}
bpy.ops.wm.open_mainfile(filepath=str(ROOT / source_names[0]), load_ui=False, use_scripts=False)
scene = bpy.context.scene
cam = scene.camera
visible = [o for o in scene.objects if o.type == 'MESH' and not o.hide_render]
assert len(visible) == 1, [o.name for o in visible]
ob = visible[0]
assert not ob.modifiers and ob.matrix_world == Matrix.Identity(4)
D = np.load(ROOT / 'mesh-data.npz', allow_pickle=False)
vs = np.array([list(v.co) for v in ob.data.vertices], dtype=np.float32)
fs = np.array([list(f.vertices) for f in ob.data.polygons], dtype=np.uint32)
ms = np.array([f.material_index for f in ob.data.polygons], dtype=np.int32)
assert np.array_equal(vs, D['vertices']), 'Native scene vertices differ from delivered mesh'
assert np.array_equal(fs, D['faces']), 'Native scene faces differ from delivered mesh'
assert np.array_equal(ms, D['materials']), 'Native scene material indices differ from delivered mesh'

def scalar(v):
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    try:
        return list(v)
    except TypeError:
        return str(v)

def node_tree(tree):
    return {'nodes': [{'name': n.name, 'type': n.bl_idname,
                      'inputs': {s.identifier: scalar(s.default_value) for s in n.inputs if hasattr(s, 'default_value')}}
                     for n in tree.nodes],
            'links': [[l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier] for l in tree.links]}

def invariant_signatures():
    meshes = [{'name': o.name, 'vertices': [list(v.co) for v in o.data.vertices],
               'faces': [list(f.vertices) for f in o.data.polygons],
               'material_indices': [f.material_index for f in o.data.polygons],
               'materials': [m.name for m in o.data.materials],
               'transform': [list(row) for row in o.matrix_world],
               'hide_render': o.hide_render, 'hide_viewport': o.hide_viewport,
               'hidden': o.hide_get(), 'modifiers': [m.type for m in o.modifiers]}
              for o in sorted(scene.objects, key=lambda x: x.name) if o.type == 'MESH']
    materials = [{'name': m.name, 'diffuse_color': list(m.diffuse_color),
                  'use_nodes': m.use_nodes, 'nodes': node_tree(m.node_tree) if m.use_nodes else None}
                 for m in sorted(bpy.data.materials, key=lambda x: x.name)]
    lights = [{'name': o.name, 'transform': [list(row) for row in o.matrix_world],
               'type': o.data.type, 'color': list(o.data.color), 'energy': o.data.energy,
               'size': o.data.size, 'shape': o.data.shape}
              for o in sorted(scene.objects, key=lambda x: x.name) if o.type == 'LIGHT']
    settings = {'lights': lights, 'world_color': list(scene.world.color),
                'world_nodes': node_tree(scene.world.node_tree), 'engine': scene.render.engine,
                'samples': scene.cycles.samples, 'seed': scene.cycles.seed,
                'denoising': scene.cycles.use_denoising, 'view_transform': scene.view_settings.view_transform,
                'look': scene.view_settings.look, 'exposure': scene.view_settings.exposure,
                'gamma': scene.view_settings.gamma, 'transparent': scene.render.film_transparent}
    return {k: hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest()
            for k, v in [('all_meshes_including_hidden_and_material_indices', meshes),
                         ('materials_and_shader_nodes', materials), ('lighting_world_color_management', settings)]}

before_signature = invariant_signatures()
before = {'camera': list(cam.location), 'rotation': list(cam.rotation_euler),
          'projection': cam.data.type, 'ortho_scale': cam.data.ortho_scale,
          'resolution': [scene.render.resolution_x, scene.render.resolution_y]}
# render_model.py documents local -Y as front terrace, +Y as convex rear hall.
# Map the canonical NUU front (-Y) and right (+X) basis directly to this facade.
front, side = Vector((0, -1, 0)), Vector((1, 0, 0))
delta = front * 240 + side * 180 + Vector((0, 0, 130))
yaw = math.degrees(math.atan2(delta.dot(side), delta.dot(front)))
elevation = math.degrees(math.atan2(delta.z, math.hypot(delta.x, delta.y)))
assert abs(yaw - math.degrees(math.atan2(180, 240))) < 1e-6
assert abs(elevation - math.degrees(math.atan2(130, 300))) < 1e-6
target = Vector((-10, -28, 15))
cam.location = target + delta
cam.rotation_euler = (-delta).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
scene.render.resolution_x = scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.pixel_aspect_x = scene.render.pixel_aspect_y = 1
# Center projected extrema and fit every vertex, including the complete base.
R = cam.rotation_euler.to_matrix()
right, up = R @ Vector((1, 0, 0)), R @ Vector((0, 1, 0))
points = [ob.matrix_world @ v.co for v in ob.data.vertices]
xs, ys = [v.dot(right) for v in points], [v.dot(up) for v in points]
target += right * ((min(xs) + max(xs)) / 2 - target.dot(right))
target += up * ((min(ys) + max(ys)) / 2 - target.dot(up))
cam.location = target + delta
cam.data.ortho_scale = max(max(xs) - min(xs), max(ys) - min(ys)) / .82
bpy.context.view_layer.update()
q = [world_to_camera_view(scene, cam, v) for v in points]
assert all(.035 < v.x < .965 and .035 < v.y < .965 and cam.data.clip_start < v.z < cam.data.clip_end for v in q)
assert invariant_signatures() == before_signature
outfile = OUT / 'previews/homepage-three-quarter.png'
scene.render.filepath = str(outfile)
scene.render.use_stamp = False
bpy.ops.render.render(write_still=True)
raw = outfile.read_bytes(); clean = raw[:8]; pos = 8
while pos < len(raw):
    n = struct.unpack('>I', raw[pos:pos + 4])[0]; kind = raw[pos + 4:pos + 8]
    if kind not in [b'tEXt', b'zTXt', b'iTXt', b'eXIf', b'tIME']:
        clean += raw[pos:pos + n + 12]
    pos += n + 12
outfile.write_bytes(clean)
after_signature = invariant_signatures()
assert before_signature == after_signature
assert source_hashes == {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in source_names}
report = {
    'source_commit': 'a597bc4c2531ff99954dcea47efd23017c7204fc',
    'source_blend_git_blob_sha': '389259377cafe18eb26664c5bcc8aef09386b6e8',
    'source_mesh_git_blob_sha': '97d497c406aaf4b491f7743021b34536e3acf464',
    'source_file_sha256': source_hashes, 'blender_version': bpy.app.version_string,
    'scope': 'Separate camera and square framing only; all geometry, materials, lights, world and original nine technical views unchanged; original native scene is never saved.',
    'geometry_exact_match': {'vertices': True, 'faces': True, 'material_indices': True},
    'before_signature': before_signature, 'after_signature': after_signature,
    'visible_mesh_count': len(visible), 'vertex_count': len(vs), 'triangle_count': len(fs),
    'material_count': len(ob.data.materials), 'original_saved_scene_camera': before,
    'original_cover_camera': {'camera': [-10, -380, 110], 'target': [-10, -28, 15], 'projection': 'ORTHO'},
    'facade_basis': {'source': 'render_model.py: -Y front terrace; +Y convex rear hall; local axes are not surveyed cardinal directions',
                     'front_outward_normal': list(front), 'view_right_side': list(side)},
    'candidate': {'camera': list(cam.location), 'target': list(target), 'camera_delta': list(delta),
                  'projection': cam.data.type, 'ortho_scale': cam.data.ortho_scale, 'resolution': [1200, 1200],
                  'yaw_from_front_terrace_deg': yaw, 'elevation_deg': elevation,
                  'screen_bounds': {'min_x': min(v.x for v in q), 'max_x': max(v.x for v in q),
                                    'min_y': min(v.y for v in q), 'max_y': max(v.y for v in q)},
                  'all_vertices_in_frame': True},
    'output': {'file': outfile.name, 'bytes': len(clean), 'sha256': hashlib.sha256(clean).hexdigest()}}
(OUT / 'qa/homepage-camera-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
