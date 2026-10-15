"""Render the exact, unrepaired STL in Blender 4.3.2.
Colors clarify visible construction only; no textures, added mesh or geometry edits.
"""

import sys
sys.dont_write_bytecode=True
def require(condition, message='Required check failed'):
    if not bool(condition): raise RuntimeError(message)
from pathlib import Path
import bpy, hashlib, math, struct
from mathutils import Vector

R = Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version=0
raw = (R / 'model.stl').read_bytes()
count = struct.unpack_from('<I', raw, 80)[0]
require((len(raw) == 84 + count * 50), ('Required check failed'))
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
obj = bpy.data.objects.new('NCKU Da Hsin Yuan east Student Salon', mesh)
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
for poly in mesh.polygons:
    x,y,z=poly.center; y=-y; nx,ny,nz=poly.normal
    index=0
    if z>=23.59: index=5 if z>23.61 else 1
    elif z>=22.59 and x>=0 and x<=80 and y>=0 and y<=80: index=1
    elif z>=19.84 and x>=0 and x<=80 and y>=0 and y<=80: index=2
    elif z>=3.61 and x<=70.63 and y<=70.63 and x>=9.37 and y>=9.37:
        index=3
        if any(abs(v-q)<.003 for v,q in [(x,9.95),(x,70.05),(y,9.95),(y,70.05),(x,10.2),(x,69.8),(y,10.2)]): index=4
    elif z>=3.61 and abs(nz)<.1:
        if any(abs(v-q)<.003 for v,q in [(x,79.2),(x,21.8),(y,131.2),(x,69.7)]): index=4
    if z>=18.59 and z<=19.61 and y>=80: index=1
    poly.material_index=index

scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = .001
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 24
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
    'front': ((-150,170,95),(40,-64,10),173),
    'rear': ((225,-265,115),(40,-65,10),173),
    'west': ((-230,-65,28),(40,-65,10),175),
    'east': ((270,-65,28),(40,-65,10),175),
    'top': ((40,-65,360),(40,-65,0),215),
    'east_detail': ((270,-65,15),(40,-65,15),145),
}

def pose(name):
    position, target, scale = views[name]
    camera.location = position
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera_data.ortho_scale = scale

def strip_variable_timing(path):
    """Remove only Cycles timing text chunks, retaining original IDAT bytes."""
    data = path.read_bytes()
    require((data[:8] == b'\x89PNG\r\n\x1a\n'), ('Required check failed'))
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
    require((offset == len(data)), ('Required check failed'))
    path.write_bytes(out)

out = R / 'previews'
out.mkdir(exist_ok=True)
pose('front')
scene['stl_sha256'] = hashlib.sha256(raw).hexdigest()
scene['revision'] = '1.0.0-rc1; source-guided exterior approximation'
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
    scene.render.resolution_x=1800 if name=='east_detail' else 1000
    scene.render.resolution_y=600 if name=='east_detail' else 760
    pose(name)
    path = out / (name + '.png')
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    strip_variable_timing(path)
print('Rendered six actual-STL previews; STL SHA256:', hashlib.sha256(raw).hexdigest())
