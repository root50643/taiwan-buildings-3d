"""Render the exact, unrepaired STL in Blender 4.3.2.
Colors clarify visible construction only; no textures, added mesh or geometry edits.
"""

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

from pathlib import Path
import bpy, hashlib, math, struct
from mathutils import Vector

R = Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version=0
raw = (R / 'model.stl').read_bytes()
count = struct.unpack_from('<I', raw, 80)[0]
require(len(raw) == 84 + count * 50, 'Required condition failed')
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
obj = bpy.data.objects.new('NCKU Da Hsin Yuan west Alumni Club', mesh)
bpy.context.collection.objects.link(obj)
obj['source_stl_sha256'] = hashlib.sha256(raw).hexdigest()
obj['geometry_policy'] = 'Exact STL coordinates and oriented triangles; no modifiers or repair'
def material(name,color):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    node=mat.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value=(*color,1)
    node.inputs['Roughness'].default_value=.74
    obj.data.materials.append(mat)
for name,col in [('Concrete and ground',(.58,.60,.58)),('Light roof',(.82,.82,.76)),('Timber soffit',(.46,.25,.10)),('Steel framing',(.09,.14,.15)),('Opaque printed glazing',(.17,.31,.33)),('White roof unit',(.88,.87,.81))]: material(name,col)
# Material indices are applied to original triangles by source-supported region.
# They clarify the monochrome printable solid without adding transparent parts.
for poly in mesh.polygons:
    x,y,z=poly.center; y=-y; nx,ny,nz=poly.normal
    index=0
    if z>26.0751: index=5
    elif z>=24.9249 and 0<=x<=99 and 0<=y<=99: index=1
    elif z>=22.3899 and 0<=x<=99 and 0<=y<=99: index=2
    elif 20.0249<=z<=21.1251 and 10.9<=x<=115.6 and 87.9<=y<=132.1: index=1
    elif z>=3.8001 and 10.9<=x<=88.1 and 10.9<=y<=88.1:
        index=3
        if any(abs(v-q)<.004 for v,q in [(x,11.65),(x,87.35),(x,11.85),(x,87.15),(y,11.65),(y,11.85),(y,87.35)]): index=4
    elif z>=4.0 and abs(nz)<.1:
        if any(abs(v-q)<.004 for v,q in [(x,11.85),(x,114.65),(y,131.15),(x,24.225),(x,69.275)]): index=4
    poly.material_index=index

scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = .001
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 64
scene.cycles.seed = 0
scene.cycles.use_denoising = False
scene.render.threads_mode = 'FIXED'
scene.render.threads = 1
scene.render.resolution_x = 1000
scene.render.resolution_y = 760
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
if scene.world is None: scene.world=bpy.data.worlds.new('Neutral environment')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.82, .85, .89, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .65
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
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
    'front': ((-165,175,100),(57,-65,12),220),
    'rear': ((245,-280,120),(57,-65,12),220),
    'west': ((-240,-65,23),(57,-65,12),185),
    'east': ((285,-65,23),(57,-65,12),185),
    'top': ((57,-65,365),(57,-65,0),225),
    'south': ((57,-300,25),(57,-65,12),185),
}

def pose(name):
    position, target, scale = views[name]
    camera.location = position
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera_data.ortho_scale = scale

def strip_variable_timing(path):
    """Remove only Cycles timing text chunks, retaining original IDAT bytes."""
    data = path.read_bytes()
    require(data[:8] == b'\x89PNG\r\n\x1a\n', 'Required condition failed')
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
    require(offset == len(data), 'Required condition failed')
    path.write_bytes(out)

out = R / 'previews'
out.mkdir(exist_ok=True)
pose('front')
scene['stl_sha256'] = hashlib.sha256(raw).hexdigest()
scene['revision'] = '2.0.0-rc3; west source-guided exterior approximation'
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
scene.render.filepath='//previews/front.png'
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type=='FILE_BROWSER' and space.params:
                space.params.directory=b'//'
                space.params.filename='scene.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(R / 'scene.blend'))
for name in views:
    scene.render.resolution_x=1000
    scene.render.resolution_y=760
    pose(name)
    path = out / (name + '.png')
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    strip_variable_timing(path)
print('Rendered six actual-STL previews; STL SHA256:', hashlib.sha256(raw).hexdigest())
