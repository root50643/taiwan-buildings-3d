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
obj = bpy.data.objects.new('USC M gym N library central court', mesh)
bpy.context.collection.objects.link(obj)
obj['source_stl_sha256'] = hashlib.sha256(raw).hexdigest()
obj['geometry_policy'] = 'Exact STL coordinates and oriented triangles; no modifiers or repair'
import json
regions=json.loads((R/'color-regions.json').read_text())
palette=[('concrete',(.73,.73,.68)),('base',(.55,.57,.57)),('glass',(.13,.29,.33)),('screen',(.48,.53,.54)),('lawn',(.27,.39,.15)),('metal',(.38,.43,.44)),('roof',(.44,.46,.44)),('skylight',(.35,.58,.63)),('walk',(.48,.40,.31))]
for name,col in palette:
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    node=mat.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(*col,1);node.inputs['Roughness'].default_value=.77
    obj.data.materials.append(mat)
lookup={n:i for i,(n,c) in enumerate(palette)}
for face in mesh.polygons:
    x,y,z=face.center
    for region in regions:
        a,b,c,d,e,f=region['bounds_mm']
        xx,yy=x,y
        if 'local_xy_frame' in region:
            frame=region['local_xy_frame'];dx=x-frame['origin_mm'][0];dy=y-frame['origin_mm'][1];ang=math.radians(frame['angle_degrees'])
            xx=math.cos(ang)*dx+math.sin(ang)*dy;yy=-math.sin(ang)*dx+math.cos(ang)*dy
        if a-1e-4<=xx<=b+1e-4 and c-1e-4<=yy<=d+1e-4 and e-1e-4<=z<=f+1e-4:
            face.material_index=lookup[region['material']]
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
scene.render.resolution_y = 750
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
    'front': ((-100,-180,155),(91,27,14),230),
    'rear': ((285,210,175),(91,27,14),230),
    'north': ((91,330,22),(91,28,22),225),
    'east': ((400,29,22),(91,29,22),160),
    'west': ((-220,29,22),(91,29,22),160),
    'south': ((91,-290,22),(91,28,22),225),
    'top': ((91,31.5,400),(91,31.5,0),225),
    'n-west-detail': ((92,55.8,23),(150,55.8,23),65),
    'm-east-detail': ((90,38,26.7),(23,38,26.7),105),
}

def pose(name):
    position, target, scale = views[name]
    camera.location = position
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera_data.ortho_scale = scale
    # The two facade detail cameras begin within the courtyard. A near plane
    # removes only foreground lawn/skylights, keeping the entire target facade.
    camera_data.clip_start = {'n-west-detail':43, 'm-east-detail':39}.get(name,.1)

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
        variable = typ in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']
        if not variable:
            out += data[offset:offset + n + 12]
        offset += n + 12
    require(offset == len(data), 'Required condition failed')
    path.write_bytes(out)

out = R / 'previews'
out.mkdir(exist_ok=True)
pose('front')
scene['stl_sha256'] = hashlib.sha256(raw).hexdigest()
scene['revision'] = '0.1.0-private; USC M+N+court source-guided exterior approximation'
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
import sys
chosen=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(views)
for name in chosen:
    scene.render.resolution_x=1000
    scene.render.resolution_y=750
    if name=='n-west-detail':scene.render.resolution_x=1400;scene.render.resolution_y=840
    if name=='m-east-detail':scene.render.resolution_x=1400;scene.render.resolution_y=600
    pose(name)
    path = out / (name + '.png')
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    strip_variable_timing(path)
manifest_path=R/'render-manifest.json'
manifest={'stl_sha256':hashlib.sha256(raw).hexdigest(),'render_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'blend_sha256':hashlib.sha256((R/'scene.blend').read_bytes()).hexdigest(),'views':{}}
if manifest_path.exists():
    old=json.loads(manifest_path.read_text())
    if old.get('stl_sha256')==manifest['stl_sha256'] and old.get('render_source_sha256')==manifest['render_source_sha256']:manifest['views']=old.get('views',{})
for name in chosen:
    path=out/(name+'.png')
    manifest['views'][name]={'png_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'camera':views[name], 'near_clip_mm':{'n-west-detail':43,'m-east-detail':39}.get(name,.1)}
manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
print('Rendered selected actual-STL previews; STL SHA256:', hashlib.sha256(raw).hexdigest())
