"""Render a separate STUST campus-side homepage cover; never save the source scene.
Run: blender --disable-autoexec --background --factory-startup --python-exit-code 1 \
    --python render_homepage_preview.py
Optional: -- --source /model/directory --out /output/directory
Uses the delivered scene.blend, model.stl and draft-parameters.json; geometry,
materials, lighting, world and the original nine technical previews are preserved.
Requires the original Noto Sans CJK font and Pillow for unchanged limitation text.
"""
import argparse, hashlib, json, math, pathlib, struct, subprocess, sys
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

HERE = pathlib.Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=pathlib.Path, default=HERE)
parser.add_argument('--out', type=pathlib.Path, default=HERE)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ROOT, OUT = args.source.resolve(), args.out.resolve()
(OUT / 'previews').mkdir(parents=True, exist_ok=True)
(OUT / 'qa').mkdir(parents=True, exist_ok=True)
source_hashes = {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest()
                 for n in ['scene.blend', 'model.stl', 'draft-parameters.json']}
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'scene.blend'), load_ui=False, use_scripts=False)
scene = bpy.context.scene
cam = scene.camera
meshes = [o for o in scene.objects if o.type == 'MESH']
assert len(meshes) == 1 and not meshes[0].hide_render
ob = meshes[0]
assert all(len(f.vertices) == 3 for f in ob.data.polygons)
assert not ob.modifiers and ob.matrix_world == __import__('mathutils').Matrix.Identity(4)

def triangle_bytes(tris):
    # Compare exact float32 STL coordinates, independent of import vertex numbering.
    return b''.join(sorted(b''.join(sorted(struct.pack('<3f', *v) for v in tri)) for tri in tris))

raw = (ROOT / 'model.stl').read_bytes()
ntri = struct.unpack_from('<I', raw, 80)[0]
assert len(raw) == 84 + ntri * 50
stl_triangles = [tuple(struct.unpack_from('<3f', raw, 84 + i * 50 + 12 + j * 12)
                       for j in range(3)) for i in range(ntri)]
blend_triangles = [[tuple(ob.data.vertices[i].co) for i in f.vertices] for f in ob.data.polygons]
assert triangle_bytes(stl_triangles) == triangle_bytes(blend_triangles), 'Source scene differs from delivered STL'

def scene_signature():
    geo = {'vertices': [list(v.co) for v in ob.data.vertices],
           'faces': [list(f.vertices) for f in ob.data.polygons],
           'materials': [f.material_index for f in ob.data.polygons],
           'transform': [list(r) for r in ob.matrix_world]}
    mats = [{'name': m.name, 'diffuse_color': list(m.diffuse_color),
             'metallic': m.metallic, 'roughness': m.roughness, 'use_nodes': m.use_nodes}
            for m in ob.data.materials]
    assert all(not m.use_nodes for m in ob.data.materials), 'Unexpected shader graph'
    shade = scene.display.shading
    rendering = {n: getattr(shade, n) for n in [
        'light', 'studio_light', 'studiolight_rotate_z', 'color_type', 'show_shadows',
        'show_cavity', 'cavity_type', 'curvature_ridge_factor', 'curvature_valley_factor',
        'show_specular_highlight', 'background_type']}
    rendering.update(world_color=list(scene.world.color), engine=scene.render.engine,
                     view_transform=scene.view_settings.view_transform,
                     look=scene.view_settings.look, exposure=scene.view_settings.exposure,
                     gamma=scene.view_settings.gamma, transparent=scene.render.film_transparent)
    return {k: hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest()
            for k, v in [('mesh_and_material_indices', geo), ('materials', mats), ('lighting_world_color_management', rendering)]}

before_signature = scene_signature()
before = {'camera': list(cam.location), 'rotation': list(cam.rotation_euler),
          'projection': cam.data.type, 'resolution': [scene.render.resolution_x, scene.render.resolution_y]}
params = json.loads((ROOT / 'draft-parameters.json').read_text())
# build_model.py: NW,SW,SE,NE=body; panelwall(NW,NE,20) is the campus face.
body = [Vector(((x - 1000) * .1375, (800 - y) * .1375, 0))
        for x, y in params['source_pixel_polygons']['body_provisional']]
NW, SW, SE, NE = body
u = (NE - NW).normalized()
normal = Vector((-u.y, u.x, 0))
centroid = sum(body, Vector()) / len(body)
if normal.dot(centroid - (NW + NE) / 2) > 0:
    normal = -normal
# NUU front basis (-Y, +X) rotated to this facade; keep the current west-side
# campus view (including the short triangular return), not the road/rear side.
right_side = Vector((-normal.y, normal.x, 0))
delta = normal * 240 + right_side * 180 + Vector((0, 0, 130))
assert delta.x < 0 and delta.y > 0
yaw = math.degrees(math.atan2(abs(delta.dot(right_side)), delta.dot(normal)))
elevation = math.degrees(math.atan2(delta.z, math.hypot(delta.x, delta.y)))
assert abs(normal.dot(right_side)) < 1e-6
assert abs(yaw - math.degrees(math.atan2(180, 240))) < 1e-4
assert abs(elevation - math.degrees(math.atan2(130, 300))) < 1e-4
points = [ob.matrix_world @ v.co for v in ob.data.vertices]
target = sum(points, Vector()) / len(points)
cam.location = target + delta
cam.rotation_euler = (-delta).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
scene.render.resolution_x = scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.pixel_aspect_x = scene.render.pixel_aspect_y = 1
R = cam.rotation_euler.to_matrix()
right, up = R @ Vector((1, 0, 0)), R @ Vector((0, 1, 0))
xs, ys = [p.dot(right) for p in points], [p.dot(up) for p in points]
target += right * ((min(xs) + max(xs)) / 2 - target.dot(right))
target += up * ((min(ys) + max(ys)) / 2 - target.dot(up))
cam.location = target + delta
cam.data.ortho_scale = max(max(xs) - min(xs), max(ys) - min(ys)) / .82
bpy.context.view_layer.update()
projection = [world_to_camera_view(scene, cam, p) for p in points]
assert all(.035 < p.x < .965 and .09 - 1e-6 < p.y < .965 and p.z > 0 for p in projection)
# Bottom caption occupies 52/1200=4.33%; 9% minimum model margin protects it.
p = OUT / 'previews/homepage-three-quarter.png'
scene.render.filepath = str(p)
scene.render.use_stamp = False
bpy.ops.render.render(write_still=True)
caption_code = """from PIL import Image,ImageDraw,ImageFont
import sys
p=sys.argv[1]
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16,index=3)
im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im);d.rectangle((0,im.height-52,im.width,im.height),fill=(235,237,237))
d.text((12,im.height-48),'有界近似，非測繪：背側服務牆輪廓、門梁接館支承線仍屬推配，未知背窗省略。',font=font,fill=(25,30,35))
d.text((12,im.height-25),'官方館高42.2m／門高43m；4F天井底名義13.5m（估計12–15m）。未試印，內廊僅背靠浮雕線。',font=font,fill=(25,30,35))
im.save(p)
"""
subprocess.run(['python3', '-c', caption_code, str(p)], check=True)
raw = p.read_bytes(); clean = raw[:8]; pos = 8
while pos < len(raw):
    n = struct.unpack('>I', raw[pos:pos + 4])[0]; kind = raw[pos + 4:pos + 8]
    if kind not in [b'tEXt', b'zTXt', b'iTXt', b'eXIf', b'tIME']:
        clean += raw[pos:pos + n + 12]
    pos += n + 12
p.write_bytes(clean)
after_signature = scene_signature()
assert before_signature == after_signature
assert source_hashes == {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in source_hashes}
report = {
    'source_commit': '127ff76533dfc0983b14b5d6c657a998fda0a611',
    'source_blend_git_blob_sha': '5332773f6c1af957519cec3e6939574b27f21623',
    'source_stl_git_blob_sha': 'fa01ad8df441f42060531adc0592ad582cfe3320',
    'source_file_sha256': source_hashes, 'blender_version': bpy.app.version_string,
    'scope': 'Separate camera/framing only; source scene, STL, 3 materials and 9 technical views unchanged. Same limitation captions retained.',
    'scene_stl_exact_float32_triangle_match': True,
    'before_signature': before_signature, 'after_signature': after_signature,
    'vertex_count': len(ob.data.vertices), 'triangle_count': len(ob.data.polygons), 'material_count': len(ob.data.materials),
    'original_saved_scene_camera': before,
    'original_cover_camera': {'camera': [-240, 200, 12], 'target': [-8, 6, 40], 'projection': 'PERSP'},
    'facade_basis': {'source': 'build_model.py: NW,SW,SE,NE=body; panelwall(NW,NE,20) campus facade',
                     'NW': list(NW), 'NE': list(NE), 'outward_normal': list(normal), 'view_right_side': list(right_side)},
    'candidate': {'camera': list(cam.location), 'target': list(target), 'camera_delta': list(delta),
                  'projection': cam.data.type, 'ortho_scale': cam.data.ortho_scale, 'resolution': [1200, 1200],
                  'yaw_from_campus_facade_deg': yaw,
                  'elevation_deg': elevation,
                  'screen_bounds': {'min_x': min(p.x for p in projection), 'max_x': max(p.x for p in projection),
                                    'min_y': min(p.y for p in projection), 'max_y': max(p.y for p in projection)},
                  'all_vertices_in_frame': True, 'caption_height_pixels': 52},
    'output': {'file': p.name, 'bytes': len(clean), 'sha256': hashlib.sha256(clean).hexdigest()}}
(OUT / 'qa/homepage-camera-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
