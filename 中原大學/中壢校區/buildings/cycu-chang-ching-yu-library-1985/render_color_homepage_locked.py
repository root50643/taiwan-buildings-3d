"""Render separate color CYCU homepage cover at original locked angle; never save source scene.
Run: blender --disable-autoexec --background --factory-startup --python-exit-code 1 \
    --python render_homepage_preview.py
Optional: -- --source /model/directory --out /output/directory
Uses the published appearance.blend, model.stl and draft-parameters.json; geometry,
materials, lighting, world and the original eight technical previews are preserved.
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
(OUT / 'appearance').mkdir(parents=True, exist_ok=True)
(OUT / 'qa').mkdir(parents=True, exist_ok=True)
source_hashes = {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest()
                 for n in ['appearance.blend', 'model.stl', 'draft-parameters.json']}
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'appearance.blend'), load_ui=False, use_scripts=False)
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
    # Preserve actual published shader graphs, not only diffuse viewport color.
    for m,rec in zip(ob.data.materials,mats):
        rec['nodes']=[{'name':n.name,'type':n.type,'inputs':{i.name:(list(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value) for i in n.inputs if hasattr(i,'default_value') and isinstance(i.default_value,(int,float,str,bool)) or (hasattr(i,'default_value') and type(i.default_value).__name__ in ['bpy_prop_array','Color','Vector'])}} for n in m.node_tree.nodes] if m.use_nodes else []
        rec['links']=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links] if m.use_nodes else []
    shade = scene.display.shading
    rendering = {n: getattr(shade, n) for n in [
        'light', 'studio_light', 'studiolight_rotate_z', 'color_type', 'show_shadows',
        'show_cavity', 'cavity_type', 'curvature_ridge_factor', 'curvature_valley_factor',
        'show_specular_highlight', 'background_type']}
    rendering.update(world_color=list(scene.world.color), engine=scene.render.engine,
                     view_transform=scene.view_settings.view_transform,
                     look=scene.view_settings.look, exposure=scene.view_settings.exposure,
                     gamma=scene.view_settings.gamma, transparent=scene.render.film_transparent)
    rendering['actual_lights']=[{'name':o.name,'matrix':[list(r) for r in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color)} for o in scene.objects if o.type=='LIGHT']
    rendering['world_nodes']=[{'name':n.name,'type':n.type,'values':[list(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value for i in n.inputs if hasattr(i,'default_value') and (isinstance(i.default_value,(int,float,str,bool)) or type(i.default_value).__name__ in ['bpy_prop_array','Color','Vector'])]} for n in scene.world.node_tree.nodes] if scene.world.use_nodes else []
    return {k: hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest()
            for k, v in [('mesh_and_material_indices', geo), ('materials', mats), ('lighting_world_color_management', rendering)]}

before_signature = scene_signature()
before = {'camera': list(cam.location), 'rotation': list(cam.rotation_euler),
          'projection': cam.data.type, 'resolution': [scene.render.resolution_x, scene.render.resolution_y]}
# README.md explicitly sets X east, Y north and south entry at -Y.
# build_model.py places the main stairs at y=-53.2 and south plaza at negative Y.
# Preserve the current +X/-Y south/east visible side, mapped to NUU's facade basis.
normal, right_side = Vector((0, -1, 0)), Vector((1, 0, 0))
delta = normal * 240 + right_side * 180 + Vector((0, 0, 130))
assert delta.x > 0 and delta.y < 0
yaw = math.degrees(math.atan2(delta.dot(right_side), delta.dot(normal)))
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
# Bottom caption occupies 50/1200=4.17%; 9% minimum model margin protects it.
p = OUT / 'appearance/homepage-three-quarter.png'
scene.render.filepath = str(p)
scene.render.use_stamp = False
bpy.ops.render.render(write_still=True)
caption_code = """from PIL import Image,ImageDraw,ImageFont
import sys
p=sys.argv[1]
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16,index=3)
im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im);d.rectangle((0,im.height-50,im.width,im.height),fill=(238,238,238))
d.text((10,im.height-47),'有界近似，非測繪：18.85m起算由1985雙剖面推定為1F至主屋面；非梯核最高點。',font=font,fill='black')
d.text((10,im.height-24),'地下花園／廣場下會議廳深度與地腳仍為剖面配圖估計；不含懷恩樓。未試印。',font=font,fill='black')
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
    'render_script_sha256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    'source_commit': '1cf1c7cdc42fba416d03423169935af78b6960de', 'observed_tree': '7a534f5f5449ea494cf738f0d1d4ad13d22da9e7',
    'source_blend_git_blob_sha': '5e2b998d0ade8ada5d05400d5a0d9061cd5440c7',
    'source_stl_git_blob_sha': '9f6cd50094e369b39994515a94647cd0162e47e4',
    'source_file_sha256': source_hashes, 'blender_version': bpy.app.version_string,
    'scope': 'Separate color representative camera/framing only; published appearance BLEND geometry, material indices, shader nodes, lights/world and source bytes unchanged. Same original locked angle, framing and limitation captions retained; no BLEND saved.',
    'scene_stl_exact_float32_triangle_match': True,
    'before_signature': before_signature, 'after_signature': after_signature,
    'vertex_count': len(ob.data.vertices), 'triangle_count': len(ob.data.polygons), 'material_count': len(ob.data.materials),
    'original_saved_scene_camera': before,
    'original_cover_camera': {'camera': [150, -250, 90], 'target': [0, -15, 20], 'projection': 'ORTHO'},
    'facade_basis': {'source': 'README.md: X east, Y north, south entry -Y; build_model.py stairs y=-53.2; same +X/-Y side as original front view', 'outward_normal': list(normal), 'view_right_side': list(right_side)},
    'candidate': {'camera': list(cam.location), 'target': list(target), 'camera_delta': list(delta),
                  'projection': cam.data.type, 'ortho_scale': cam.data.ortho_scale, 'resolution': [1200, 1200],
                  'yaw_from_south_facade_deg': yaw,
                  'elevation_deg': elevation,
                  'screen_bounds': {'min_x': min(p.x for p in projection), 'max_x': max(p.x for p in projection),
                                    'min_y': min(p.y for p in projection), 'max_y': max(p.y for p in projection)},
                  'all_vertices_in_frame': True, 'caption_height_pixels': 50},
    'output': {'file': p.name, 'bytes': len(clean), 'sha256': hashlib.sha256(clean).hexdigest()}}
(OUT / 'qa/color-homepage-camera-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
