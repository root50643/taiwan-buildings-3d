"""v3 replacement renderer: imports the exact binary STL without geometry edits.
The original v2 renderer/Blend/PNGs were not recovered. These are new artifacts.
Run with Blender 4.3.2, CPU Cycles, one thread. No third-party images are used.
"""
from pathlib import Path
import bpy, hashlib, math, struct
from mathutils import Vector

R = Path(__file__).resolve().parent
raw = (R / 'model.stl').read_bytes()
count = struct.unpack_from('<I', raw, 80)[0]
assert len(raw) == 84 + count * 50
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
verts, faces, index = [], [], {}
for i in range(count):
    coords = struct.unpack_from('<9f', raw, 84 + i * 50 + 12)
    face = []
    for j in range(3):
        p = tuple(coords[j * 3:j * 3 + 3])
        if p not in index:
            index[p] = len(verts)
            verts.append(p)
        face.append(index[p])
    faces.append(face)
mesh = bpy.data.meshes.new('Exact original STL triangles')
mesh.from_pydata(verts, [], faces)
mesh.update()
obj = bpy.data.objects.new('Shute partial administrative forecourt wing', mesh)
bpy.context.collection.objects.link(obj)
obj['source_stl_sha256'] = hashlib.sha256(raw).hexdigest()
obj['geometry_policy'] = 'Exact STL coordinates and oriented triangles; no modifiers or repair'
mat = bpy.data.materials.new('Neutral warm architectural model')
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (.64, .59, .49, 1)
bsdf.inputs['Roughness'].default_value = .72
obj.data.materials.append(mat)

scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = .001
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 32
scene.cycles.seed = 0
scene.cycles.use_denoising = False
scene.render.threads_mode = 'FIXED'
scene.render.threads = 1
scene.render.resolution_x = 800
scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '8'
scene.render.film_transparent = False
scene.render.use_file_extension = True
for attr in dir(scene.render):
    if attr.startswith('use_stamp'):
        try:
            setattr(scene.render, attr, False)
        except (TypeError, AttributeError):
            pass
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.82, .85, .89, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .65
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1
light = bpy.data.lights.new('Sun key', 'SUN')
light.energy = 2.1
light.angle = .16
sun = bpy.data.objects.new('Sun key', light)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(28), math.radians(-26), math.radians(-32))
light2 = bpy.data.lights.new('Sun soft fill', 'SUN')
light2.energy = .55
light2.angle = .35
fill = bpy.data.objects.new('Sun soft fill', light2)
bpy.context.collection.objects.link(fill)
fill.rotation_euler = (math.radians(-20), math.radians(32), math.radians(140))
camera_data = bpy.data.cameras.new('Camera')
camera = bpy.data.objects.new('Camera', camera_data)
bpy.context.collection.objects.link(camera)
scene.camera = camera
camera_data.type = 'ORTHO'
camera_data.lens = 45
camera_data.clip_end = 2000
views = {
    'front': ((165, -265, 165), (0, -6, 45), 205),
    'rear': ((-165, 265, 165), (0, -6, 45), 205),
    'elevation': ((0, -320, 52), (0, 0, 52), 180),
    'top': ((0, -7.5, 360), (0, -7.5, 0), 180),
}
def pose(name):
    position, target, scale = views[name]
    camera.location = position
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera_data.ortho_scale = scale

def strip_variable_timing(path):
    """Remove only Cycles timing text chunks, retaining original IDAT bytes."""
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    out = data[:8]
    offset = 8
    while offset < len(data):
        n = struct.unpack_from('>I', data, offset)[0]
        typ = data[offset + 4:offset + 8]
        body = data[offset + 8:offset + 8 + n]
        key = body.split(b'\0', 1)[0]
        variable = typ == b'tEXt' and key.startswith(b'cycles.') and key.endswith((b'.total_time', b'.render_time', b'.synchronization_time'))
        if not variable:
            out += data[offset:offset + n + 12]
        offset += n + 12
    assert offset == len(data)
    path.write_bytes(out)

out = R / 'previews'
out.mkdir(exist_ok=True)
pose('front')
scene['stl_sha256'] = hashlib.sha256(raw).hexdigest()
scene['revision'] = 'recovered-release-v3, replacement scene'
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(R / 'scene.blend'))
for name in views:
    pose(name)
    path = out / (name + '.png')
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    strip_variable_timing(path)
print('Rendered four actual-STL previews; STL SHA256:', hashlib.sha256(raw).hexdigest())
