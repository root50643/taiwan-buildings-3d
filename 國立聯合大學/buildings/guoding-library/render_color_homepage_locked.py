"""Render latest published NUU Guoding colors at exact original school cover camera.
Run Blender with -- --source BUILDING_ROOT --out BUILDING_ROOT (or separate output).
Reads appearance/scene.blend and guoding_library_150mm.stl; no source saves.
Produces only appearance/previews/homepage-front-elevation.png and separate QA.
Preserves geometry, material shaders, source lighting/world; camera/render frame only.
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
(OUT / 'appearance/previews').mkdir(parents=True, exist_ok=True)
(OUT / 'qa').mkdir(parents=True, exist_ok=True)
source_hashes = {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest()
                 for n in ['appearance/scene.blend', 'guoding_library_150mm.stl']}
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'appearance/scene.blend'), load_ui=False, use_scripts=False)
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

raw = (ROOT / 'guoding_library_150mm.stl').read_bytes()
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
# Exact original Guoding front_elevation camera from published render_preview.py.
normal,right_side=Vector((0,-1,0)),Vector((1,0,0))
target=Vector((0,0,27));cam.location=(0,-260,82);delta=cam.location-target
cam.rotation_euler=(-delta).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=184
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.pixel_aspect_x=scene.render.pixel_aspect_y=1
points=[ob.matrix_world@v.co for v in ob.data.vertices];bpy.context.view_layer.update()
projection=[world_to_camera_view(scene,cam,p) for p in points]
assert all(0<p.x<1 and 0<p.y<1 and p.z>0 for p in projection)
yaw=math.degrees(math.atan2(delta.x,-delta.y));elevation=math.degrees(math.atan2(delta.z,math.hypot(delta.x,delta.y)))
p=OUT/'appearance/previews/homepage-front-elevation.png'
scene.render.filepath = str(p)
scene.render.use_stamp = False
bpy.ops.render.render(write_still=True)
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
    'source_commit': '46f63f2', 'observed_tree': '7a534f5f5449ea494cf738f0d1d4ad13d22da9e7',
    'source_blend_git_blob_sha': '2e2842717c6c29f1c0d63aa2cc555efbb42cee98',
    'source_stl_git_blob_sha': '483394959176d639b1e34c8bdea36eefe7417adf',
    'source_file_sha256': source_hashes, 'blender_version': bpy.app.version_string,
    'scope': 'Separate color representative camera/framing only; published appearance BLEND geometry, material indices, shader nodes, lights/world and source bytes unchanged. Exact original front_elevation camera/target/scale/resolution retained; no caption originally, no BLEND saved.',
    'scene_stl_exact_float32_triangle_match': True,
    'before_signature': before_signature, 'after_signature': after_signature,
    'vertex_count': len(ob.data.vertices), 'triangle_count': len(ob.data.polygons), 'material_count': len(ob.data.materials),
    'original_saved_scene_camera': before,
    'original_cover_camera': {'camera': [0,-260,82], 'target': [0,0,27], 'projection': 'ORTHO','scale':184,'resolution':[1600,1200]},
    'candidate': {'camera': list(cam.location), 'target': list(target), 'camera_delta': list(delta),
                  'projection': cam.data.type, 'ortho_scale': cam.data.ortho_scale, 'resolution': [1600, 1200],
                  'yaw_from_south_facade_deg': yaw,
                  'elevation_deg': elevation,
                  'screen_bounds': {'min_x': min(p.x for p in projection), 'max_x': max(p.x for p in projection),
                                    'min_y': min(p.y for p in projection), 'max_y': max(p.y for p in projection)},
                  'all_vertices_in_frame': True, 'caption_height_pixels': 0},
    'output': {'file': p.name, 'bytes': len(clean), 'sha256': hashlib.sha256(clean).hexdigest()}}
(OUT / 'qa/guoding-color-cover-camera-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
