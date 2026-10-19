"""Render the unchanged eight semantic A1 meshes with seven photo-informed display materials.

Run with a Python environment that supplies bpy, or Blender -b -P this_file --:
    python render_appearance.py --three-mf PATH/TO/a1-four-tool-core.3mf

Default outputs, beside the input: scene.blend, previews/{front,rear,roof}.png,
and render-geometry-check.json. No source photographs or texture images are used.
Blender's mesh coordinates are float32. The script reports their difference from
the original 3MF float64 coordinates; it never writes back to the print 3MF.
The parent workflow must strip PNG metadata and reopen/inspect scene.blend.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile

import bpy
from mathutils import Vector


CORE_NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
NS = {'m': CORE_NS}
IDENTITY_3MF = (1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0.)
TOOLS = {
    1: ('01-light-wall', '#D8D6CF'),
    2: ('02-brick', '#A96754'),
    3: ('03-slate', '#566166'),
    4: ('04-glazing', '#248E91'),
}


def arguments():
    # Blender consumes its own arguments before --; ordinary Python does not.
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--three-mf', type=Path, required=True)
    p.add_argument('--output', type=Path, help='Defaults to the 3MF parent folder')
    p.add_argument('--fine-palette-reference', default='//../multicolor/color-evidence.json#fine_material_identities')
    p.add_argument('--samples', type=int, default=64)
    p.add_argument('--threads', type=int, default=6)
    p.add_argument('--views', default='front,rear,roof', help='Comma-separated views; defaults to all')
    return p.parse_args(argv)


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def coordinate_digest(vertices, faces, format_code):
    """Ordered triangle-coordinate digest, with an explicit precision tag."""
    h = hashlib.sha256(('ordered-triangles-le-' + format_code).encode('ascii'))
    h.update(struct.pack('<QQ', len(vertices), len(faces)))
    for face in faces:
        for index in face:
            h.update(struct.pack('<' + format_code * 3, *vertices[index]))
    return h.hexdigest()


def index_digest(vertices, faces):
    h = hashlib.sha256(b'ordered-triangle-indices-le-u64')
    h.update(struct.pack('<QQ', len(vertices), len(faces)))
    for face in faces:
        h.update(struct.pack('<QQQ', *face))
    return h.hexdigest()


def identity_only(element, label):
    value = element.get('transform')
    if value is None:
        return
    values = tuple(float(v) for v in value.split())
    if values != IDENTITY_3MF:
        raise ValueError(label + ': unexpected transform; explicit original coordinates required')


def read_core_3mf(path):
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError('3MF ZIP CRC failure')
        root = ET.fromstring(archive.read('3D/3dmodel.model'))
    if root.tag != '{' + CORE_NS + '}model':
        raise ValueError('Unsupported 3MF namespace')
    if root.get('unit', 'millimeter') != 'millimeter':
        raise ValueError('Input 3MF is not in millimeters')
    resources = root.find('m:resources', NS)
    if resources is None:
        raise ValueError('Missing 3MF resources')
    objects = {}
    for element in resources.findall('m:object', NS):
        oid = int(element.attrib['id'])
        if oid in objects:
            raise ValueError('Duplicate 3MF object ID')
        objects[oid] = element
    if 10 not in objects:
        raise ValueError('Missing parent object 10')
    mesh_ids = {oid for oid, element in objects.items() if element.find('m:mesh', NS) is not None}
    if not mesh_ids or set(objects) != mesh_ids | {10}:
        raise ValueError('Expected semantic child meshes and parent object 10 only')
    components = objects[10].find('m:components', NS)
    if components is None or objects[10].find('m:mesh', NS) is not None:
        raise ValueError('Object 10 must contain components only')
    children = components.findall('m:component', NS)
    if sorted(int(child.attrib['objectid']) for child in children) != sorted(mesh_ids):
        raise ValueError('Parent must instantiate each child exactly once')
    for child in children:
        identity_only(child, 'component')
    build = root.find('m:build', NS)
    items = [] if build is None else build.findall('m:item', NS)
    if len(items) != 1 or int(items[0].attrib['objectid']) != 10:
        raise ValueError('Expected one build item for parent object 10')
    identity_only(items[0], 'build item')
    data = {}
    used_names = set()
    for oid in sorted(mesh_ids):
        element = objects[oid]
        name = element.get('name', 'semantic-part-' + str(oid))
        if name in used_names:
            raise ValueError('Semantic part names must be unique')
        used_names.add(name)
        if 'pindex' not in element.attrib or 'pid' not in element.attrib:
            raise ValueError('Each semantic mesh needs an object-level basematerial pid/pindex')
        pindex = int(element.attrib['pindex'])
        tool_id = pindex + 1
        if tool_id not in TOOLS:
            raise ValueError('Material index outside four-tool palette')
        base_resource = resources.find("m:basematerials[@id='" + element.attrib['pid'] + "']", NS)
        if base_resource is None or len(base_resource.findall('m:base', NS)) != 4:
            raise ValueError('Object must reference a four-entry core basematerials resource')
        mesh = element.find('m:mesh', NS)
        if mesh is None or element.find('m:components', NS) is not None:
            raise ValueError('Each tool object must contain one mesh only')
        vertex_elements = mesh.findall('m:vertices/m:vertex', NS)
        triangle_elements = mesh.findall('m:triangles/m:triangle', NS)
        vertices = [tuple(float(v.attrib[k]) for k in ('x', 'y', 'z')) for v in vertex_elements]
        faces = [tuple(int(t.attrib[k]) for k in ('v1', 'v2', 'v3')) for t in triangle_elements]
        if not vertices or not faces:
            raise ValueError('Empty tool mesh')
        if not all(math.isfinite(c) for v in vertices for c in v):
            raise ValueError('Non-finite mesh coordinate')
        if not all(0 <= i < len(vertices) for face in faces for i in face):
            raise ValueError('Out-of-range triangle index')
        if not all(len(set(face)) == 3 for face in faces):
            raise ValueError('Triangle with repeated vertex index')
        data[oid] = {'name': name, 'tool_id': tool_id, 'pindex': pindex,
                     'vertices': vertices, 'faces': faces}
    return data


def srgb_to_linear(c):
    return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4


def material(name, hex_color):
    rgb = tuple(int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    rgba = tuple(srgb_to_linear(c) for c in rgb) + (1.,)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = rgba
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = rgba
    shader.inputs['Roughness'].default_value = .72
    shader.inputs['Metallic'].default_value = 0.
    shader.inputs['Alpha'].default_value = 1.
    mat['approximate_srgb_hex'] = hex_color
    mat['alpha'] = 1.
    mat['meaning'] = 'Photo-informed fine display material; independent of printer color/tool limits; opaque approximate glazing'
    return mat


def clean_saved_paths(scene):
    """Only relative model references remain; no file-browser private folders."""
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'FILE_BROWSER':
                for space in area.spaces:
                    params = getattr(space, 'params', None)
                    if params is not None:
                        params.directory = b'//'
                        params.filename = ''
    # This scene intentionally has no external images, fonts or linked libraries.
    if bpy.data.libraries:
        raise ValueError('Unexpected externally linked library')
    for image in bpy.data.images:
        if image.type not in {'RENDER_RESULT', 'COMPOSITING'} and image.filepath:
            raise ValueError('Unexpected image path: no textures are allowed')
    if not scene.render.filepath.startswith('//'):
        raise ValueError('Render output must be relative before saving')


def assert_mesh_invariants(records):
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    if sorted(obj.name for obj in mesh_objects) != sorted(record['name'] for record in records):
        raise ValueError('Unexpected mesh object added to scene')
    results = []
    for record in records:
        obj = record['object']
        if obj.modifiers or tuple(obj.location) != (0., 0., 0.) or tuple(obj.scale) != (1., 1., 1.):
            raise ValueError('Geometry modifier or nonidentity transform found')
        if tuple(obj.rotation_euler) != (0., 0., 0.):
            raise ValueError('Unexpected rotation')
        vertices = [tuple(float(c) for c in v.co) for v in obj.data.vertices]
        faces = [tuple(int(i) for i in p.vertices) for p in obj.data.polygons]
        if vertices != record['vertices_f32'] or faces != record['faces']:
            raise ValueError('Blender vertex positions or triangle indices changed')
        if not all(len(face) == 3 for face in faces):
            raise ValueError('A triangle became a nontriangle')
        current = coordinate_digest(vertices, faces, 'f')
        if current != record['source_triangle_digest_f32']:
            raise ValueError('Rendered triangle digest mismatch')
        result = {key: value for key, value in record.items()
                  if key not in {'object', 'vertices_f32', 'faces'}}
        result.update({'triangles_unchanged': True, 'identity_object_transform': True,
                       'modifiers': 0, 'render_triangle_digest_f32': current})
        results.append(result)
    return results


def main():
    args = arguments()
    source = args.three_mf.resolve(strict=True)
    output = (args.output if args.output else source.parent).resolve()
    output.mkdir(parents=True, exist_ok=True)
    previews = output / 'previews'
    previews.mkdir(exist_ok=True)
    source_relative = '//' + Path(os.path.relpath(source, output)).as_posix()
    fine_reference = args.fine_palette_reference
    if not fine_reference.startswith('//'):
        raise ValueError('Fine palette reference must be a // relative reference')
    data = read_core_3mf(source)
    input_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = 'A1 photo-informed seven-material appearance master'
    bpy.context.preferences.filepaths.save_version = 0
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = .001
    scene.unit_settings.length_unit = 'MILLIMETERS'
    scene['source_3mf'] = source_relative
    scene['source_3mf_sha256'] = input_sha
    scene['geometry_units'] = 'millimeter; 1 Blender coordinate = 1 mm'
    scene['display_material_count'] = 7
    scene['manufacturing_tool_mapping'] = 'Not assigned by appearance master; optional four-tool variant remains separate'
    scene['fine_palette_reference'] = fine_reference
    scene['color_status'] = 'Approximate photo-informed palette; no exact paint/material color claim'
    scene['semantic_mesh_count'] = len(data)
    scene['geometry_policy'] = 'Input eight semantic meshes only; seven display materials; no modifiers or added facade detail'
    scene['coordinate_precision'] = 'Blender float32 display projection; original 3MF is unchanged'
    records = []
    points = []
    palette_path = output / fine_reference[2:].split('#', 1)[0]
    palette = json.loads(palette_path.read_text(encoding='utf-8'))['fine_material_identities']
    colors = {p['id']: '#' + ''.join(f'{v:02X}' for v in p['candidate_rgb']) for p in palette}
    semantic = {'light_frames':'wall_and_light_frame','wall':'wall_and_light_frame','glass':'glass_teal','pv':'photovoltaic_blue_violet','roof':'metal_roof_gray_green','dark_facade':'dark_facade','plinth':'display_plinth','brick':'brick_terracotta'}
    fine_materials = {name: material(name, color) for name, color in colors.items()}
    if len(fine_materials) != 7: raise ValueError('Expected seven source-backed material identities')
    for oid, source_part in data.items():
        name = source_part['name']
        tool_id = source_part['tool_id']
        material_id = semantic[name]
        hex_color = colors[material_id]
        original_vertices, faces = source_part['vertices'], source_part['faces']
        vertices_f32 = [tuple(f32(c) for c in v) for v in original_vertices]
        delta = max(abs(a - b) for v, w in zip(original_vertices, vertices_f32) for a, b in zip(v, w))
        mesh = bpy.data.meshes.new(name + '-mesh')
        mesh.from_pydata(vertices_f32, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        scene.collection.objects.link(obj)
        obj.data.materials.append(fine_materials[material_id])
        obj.color = obj.data.materials[0].diffuse_color
        for polygon in obj.data.polygons:
            polygon.use_smooth = False
        f64_digest = coordinate_digest(original_vertices, faces, 'd')
        f32_digest = coordinate_digest(vertices_f32, faces, 'f')
        idx_digest = index_digest(original_vertices, faces)
        obj['source_3mf'] = source_relative
        obj['source_object_id'] = oid
        obj['optional_four_tool_variant_id'] = tool_id
        obj['fine_material_identity'] = material_id
        obj['source_basematerial_pindex'] = source_part['pindex']
        obj['units'] = 'mm'
        obj['source_triangle_digest_f64'] = f64_digest
        obj['source_triangle_digest_f32'] = f32_digest
        obj['source_triangle_index_digest'] = idx_digest
        obj['source_triangles'] = len(faces)
        obj['float32_projection_max_abs_delta_mm'] = delta
        obj['approximate_srgb_hex'] = hex_color
        records.append({'object': obj, 'name': name, 'object_id': oid, 'optional_four_tool_variant_id': tool_id,'fine_material_identity': material_id,'approximate_srgb_hex':hex_color,
                        'vertices': len(original_vertices), 'triangles': len(faces),
                        'vertices_f32': vertices_f32, 'faces': faces,
                        'source_triangle_digest_f64': f64_digest,
                        'source_triangle_digest_f32': f32_digest,
                        'source_triangle_index_digest': idx_digest,
                        'float32_projection_max_abs_delta_mm': delta})
        points.extend(original_vertices)
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    center = (low + high) / 2
    extent = high - low
    longest = max(extent)
    aim = Vector((center.x, center.y, low.z + extent.z * .42))
    world = bpy.data.worlds.new('Neutral studio world')
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (.16, .18, .20, 1.)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = .6

    def light(name, offset, power, size):
        lamp = bpy.data.lights.new(name, type='AREA')
        lamp.energy = power
        lamp.shape = 'DISK'
        lamp.size = size
        obj = bpy.data.objects.new(name, lamp)
        scene.collection.objects.link(obj)
        obj.location = Vector(offset) + Vector((center.x, center.y, low.z))
        obj.rotation_euler = (aim - obj.location).to_track_quat('-Z', 'Y').to_euler()

    light('Studio key', (-100, -150, 210), 350000, 140)
    light('Studio fill', (160, -50, 120), 160000, 100)
    light('Studio rim', (20, 140, 180), 350000, 110)
    camera_data = bpy.data.cameras.new('Camera')
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = longest * 1.55
    camera = bpy.data.objects.new('Camera', camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = max(1, args.samples)
    scene.cycles.use_denoising = False  # Portable CPU build may lack OpenImageDenoise.
    scene.cycles.seed = 0
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = max(1, args.threads)
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    scene.render.film_transparent = False
    scene.render.use_stamp = False
    scene.render.use_compositing = False
    scene.render.use_sequencer = False
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0.
    scene.view_settings.gamma = 1.
    checks = assert_mesh_invariants(records)
    scene['triangle_total'] = sum(row['triangles'] for row in checks)
    scene['all_input_triangles_preserved_after_float32_projection'] = True
    views = [('front', (110, -210, 170)), ('rear', (-150, 210, 175)), ('roof', (120, -185, 300))]
    for name, offset in views:
        if name not in args.views.split(','): continue
        camera_data.ortho_scale = longest * (1.75 if name == 'roof' else 1.55)
        camera.location = Vector(offset) + Vector((center.x, center.y, low.z))
        camera.rotation_euler = (aim - camera.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = '//previews/' + name + '.png'
        clean_saved_paths(scene)
        # Saving before render makes // resolve against the public output folder.
        bpy.ops.wm.save_as_mainfile(filepath=str(output / 'scene.blend'), check_existing=False)
        bpy.ops.render.render(write_still=True)
        assert_mesh_invariants(records)
    camera_data.ortho_scale = longest * 1.55
    camera.location = Vector(views[0][1]) + Vector((center.x, center.y, low.z))
    camera.rotation_euler = (aim - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = '//previews/front.png'
    clean_saved_paths(scene)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / 'scene.blend'), check_existing=False)
    if hashlib.sha256(source.read_bytes()).hexdigest() != input_sha:
        raise ValueError('Print 3MF unexpectedly changed')
    report = {'source_3mf': source_relative, 'source_3mf_sha256': input_sha,
              'blender_version': bpy.app.version_string, 'units': 'mm',
              'scene_scale_length': .001, 'mesh_objects': len(data), 'display_materials': 7,
              'model_dimensions_mm_from_source': list(extent),
              'no_extra_model_geometry': True, 'input_3mf_unchanged': True,
              'no_modifiers': True, 'opaque_materials': True,
              'precision_note': 'Blender float32 display projection; source f64 coordinates are not claimed bit-identical',
              'fine_palette_reference': fine_reference, 'parts': checks,
              'views': [name for name, _ in views],
              'rendered_this_run':args.views.split(','),
              'postprocess_pending': ['strip PNG metadata', 'reopen scene.blend and independently inspect geometry/paths/pixels']}
    (output / 'render-geometry-check.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'rendered': report['views'], 'semantic_parts': len(data), 'display_materials': 7,
                      'triangles': scene['triangle_total'], 'input_3mf_unchanged': True}))


if __name__ == '__main__':
    main()
