"""Read-only independent reopen check for the A1 semantic-part Blender scene.

Usage: python check_scene.py --multicolor-dir PATH/TO/multicolor
Requires bpy and zstandard. Writes only the requested fresh JSON report. Never
saves the scene, renders, repairs meshes, or changes the 3MF. Public output uses
relative names and redacts any offending host-path value.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile

import bpy
import zstandard


NAMESPACE = {'m': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
PALETTE = {1: ('01-light-wall', '#D8D6CF'), 2: ('02-brick', '#A96754'),
           3: ('03-slate', '#566166'), 4: ('04-glazing', '#248E91')}
PRIVATE = re.compile(rb'[A-Za-z]:[\\/]+(?:Users|Program Files|Windows)[\\/]+|/(?:home|Users)/[^/\x00]+/', re.I)
ABSOLUTE = re.compile(r'^(?:[A-Za-z]:[\\/]|\\\\|/(?!/))')


def sha(value):
    return hashlib.sha256(value).hexdigest()


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def triangle_digest(vertices, faces, precision):
    h = hashlib.sha256(('independent-ordered-world-triangles-' + precision).encode())
    h.update(struct.pack('<QQ', len(vertices), len(faces)))
    for face in faces:
        for index in face:
            h.update(struct.pack('<' + precision * 3, *vertices[index]))
    return h.hexdigest()


def decoded_blend(raw):
    if raw.startswith(b'BLENDER'):
        return raw, 'uncompressed'
    if raw.startswith(b'\x1f\x8b'):
        return gzip.decompress(raw), 'gzip-all-members'
    if raw.startswith(b'\x28\xb5\x2f\xfd'):
        with zstandard.ZstdDecompressor().stream_reader(io.BytesIO(raw), read_across_frames=True) as reader:
            return reader.read(), 'zstd-all-frames'
    raise ValueError('Unknown BLEND compression')


def saved_char_fields(data):
    """Resolve SDNA char arrays dynamically; never reuse the CSU byte offsets."""
    if data[:17] != b'BLENDER17-01v0502':
        raise ValueError('Unsupported BLEND header; field offsets are not guessed')
    blocks = []
    offset = 17
    while offset < len(data):
        code, sdna, address, length, count = struct.unpack_from('<4sIQQQ', data, offset)
        start = offset + 32
        end = start + length
        if end > len(data):
            raise ValueError('BLEND block extends beyond stream')
        blocks.append((code, sdna, start, end, count))
        offset = end
        if code == b'ENDB':
            break
    if offset != len(data):
        raise ValueError('Trailing or incomplete BLEND blocks')
    dna_blocks = [b for b in blocks if b[0] == b'DNA1']
    if len(dna_blocks) != 1:
        raise ValueError('Expected one SDNA block')
    payload = data[dna_blocks[0][2]:dna_blocks[0][3]]
    pos = 0

    def marker(expected):
        nonlocal pos
        if payload[pos:pos + 4] != expected:
            raise ValueError('Invalid SDNA marker')
        pos += 4

    def strings():
        nonlocal pos
        count = struct.unpack_from('<I', payload, pos)[0]
        pos += 4
        rows = []
        for _ in range(count):
            end = payload.index(0, pos)
            rows.append(payload[pos:end].decode('ascii'))
            pos = end + 1
        pos = (pos + 3) & ~3
        return rows

    marker(b'SDNA'); marker(b'NAME')
    names = strings()
    marker(b'TYPE')
    types = strings()
    marker(b'TLEN')
    sizes = struct.unpack_from('<' + 'H' * len(types), payload, pos)
    pos += 2 * len(types)
    pos = (pos + 3) & ~3
    marker(b'STRC')
    count = struct.unpack_from('<I', payload, pos)[0]
    pos += 4
    structures = []
    for index in range(count):
        typ, n = struct.unpack_from('<HH', payload, pos)
        pos += 4
        fields = []
        field_offset = 0
        for _ in range(n):
            field_type, field_name = struct.unpack_from('<HH', payload, pos)
            pos += 4
            name = names[field_name]
            array = math.prod(int(x) for x in re.findall(r'\[(\d+)\]', name)) or 1
            pointer = '*' in name
            size = (8 if pointer else sizes[field_type]) * array
            fields.append({'name': name, 'type': types[field_type], 'offset': field_offset,
                           'size': size, 'pointer': pointer})
            field_offset += size
        structures.append({'name': types[typ], 'size': sizes[typ], 'index': index,
                           'fields': fields, 'exact_size_sum': field_offset == sizes[typ]})
    if pos != len(payload):
        raise ValueError('Unexpected SDNA tail')
    results = []
    for owner, field_name in [('FileSelectParams', 'dir'), ('FileSelectParams', 'file'),
                              ('FileGlobal', 'filename')]:
        owners = [s for s in structures if s['name'] == owner]
        if len(owners) != 1 or not owners[0]['exact_size_sum']:
            raise ValueError('Unsupported SDNA owner or field alignment')
        entry = owners[0]
        choices = [f for f in entry['fields'] if re.sub(r'\[\d+\]', '', f['name']) == field_name]
        if len(choices) != 1 or choices[0]['type'] != 'char' or choices[0]['pointer']:
            raise ValueError('Expected one fixed char array')
        field = choices[0]
        rows = []
        for code, sdna, start, end, count in blocks:
            if sdna != entry['index'] or code in {b'DNA1', b'ENDB'}:
                continue
            if end - start != entry['size'] * count:
                raise ValueError('SDNA instance stride differs')
            for instance in range(count):
                lo = start + entry['size'] * instance + field['offset']
                hi = lo + field['size']
                full = data[lo:hi]
                prefix = full.split(b'\0', 1)[0]
                value = prefix.decode('utf8', errors='replace')
                absolute = bool(ABSOLUTE.match(value))
                rows.append({'structure': owner, 'field': field['name'], 'instance': instance,
                             'expanded_byte_range': [lo, hi], 'sdna_index': entry['index'],
                             'value': '<absolute-host-path-redacted>' if absolute else value,
                             'value_sha256': sha(prefix), 'absolute': absolute,
                             'private_pattern_in_full_array': bool(PRIVATE.search(full)),
                             'trailing_bytes_all_NUL': full[len(prefix):] == b'\0' * (len(full) - len(prefix))})
        if not rows:
            raise ValueError('Named saved directory/filename field has no instance')
        results.extend(rows)
    return results


def parse_3mf(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if archive.testzip() is not None:
            raise ValueError('3MF CRC failure')
        root = ET.fromstring(archive.read('3D/3dmodel.model'))
    if root.get('unit', 'millimeter') != 'millimeter':
        raise ValueError('3MF must use millimeters')
    resources = root.find('m:resources', NAMESPACE)
    objects = {int(o.attrib['id']): o for o in resources.findall('m:object', NAMESPACE)}
    if set(objects) != set(range(1, 9)) | {10}:
        raise ValueError('Expected eight semantic meshes and parent 10')
    components = objects[10].findall('m:components/m:component', NAMESPACE)
    if sorted(int(c.attrib['objectid']) for c in components) != list(range(1, 9)):
        raise ValueError('Each semantic mesh must be instantiated once')
    build = root.findall('m:build/m:item', NAMESPACE)
    if len(build) != 1 or int(build[0].attrib['objectid']) != 10:
        raise ValueError('Expected parent build item 10')
    identity = (1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0.)
    for element in components + build:
        if element.get('transform') and tuple(map(float, element.get('transform').split())) != identity:
            raise ValueError('Unexpected 3MF transform')
    basematerials = resources.find("m:basematerials[@id='20']", NAMESPACE)
    if basematerials is None or len(basematerials.findall('m:base', NAMESPACE)) != 4:
        raise ValueError('Expected four-entry basematerials resource 20')
    for tool, base in enumerate(basematerials.findall('m:base', NAMESPACE), start=1):
        color = base.get('displaycolor', '').upper()
        if color not in {PALETTE[tool][1], PALETTE[tool][1] + 'FF'}:
            raise ValueError('Core basematerial color differs from the four-tool evidence palette')
    result = []
    for oid in range(1, 9):
        element = objects[oid]
        if element.get('pid') != '20':
            raise ValueError('Semantic object does not reference palette 20')
        tool = int(element.attrib['pindex']) + 1
        if tool not in PALETTE:
            raise ValueError('Invalid material/tool index')
        vertices = [tuple(float(v.attrib[k]) for k in ('x', 'y', 'z'))
                    for v in element.findall('m:mesh/m:vertices/m:vertex', NAMESPACE)]
        faces = [tuple(int(t.attrib[k]) for k in ('v1', 'v2', 'v3'))
                 for t in element.findall('m:mesh/m:triangles/m:triangle', NAMESPACE)]
        if not vertices or not faces or not all(math.isfinite(c) for v in vertices for c in v):
            raise ValueError('Empty or nonfinite source mesh')
        if not all(0 <= i < len(vertices) for f in faces for i in f):
            raise ValueError('Invalid triangle index')
        result.append({'id': oid, 'name': element.attrib['name'], 'tool': tool,
                       'vertices': vertices, 'faces': faces})
    if len({r['name'] for r in result}) != 8:
        raise ValueError('Semantic mesh names must be unique')
    return result


def srgb_linear(hex_color):
    values = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values] + [1.]


def public_path(value):
    value = value.decode('utf8', errors='replace') if isinstance(value, bytes) else str(value)
    absolute = bool(ABSOLUTE.match(value))
    return {'value': '<absolute-host-path-redacted>' if absolute else value,
            'absolute': absolute, 'value_sha256': sha(value.encode())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--multicolor-dir', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    args = parser.parse_args(argv)
    directory = args.multicolor_dir.resolve(strict=True)
    output = args.output or directory / 'qa/scene-reopen-validation.json'
    if output.exists():
        raise ValueError('Use a fresh output report; existing evidence is not overwritten')
    scene_path = directory / 'scene.blend'
    core_path = directory / 'a1-four-tool-core.3mf'
    scene_raw, core_raw = scene_path.read_bytes(), core_path.read_bytes()
    data, compression = decoded_blend(scene_raw)
    fields = saved_char_fields(data)
    source = parse_3mf(core_raw)
    privacy_hits = [{'representation': label, 'offsets': [m.start() for m in PRIVATE.finditer(view)]}
                    for label, view in [('raw', scene_raw), ('decoded', data),
                                        ('decoded_NUL_removed', data.replace(b'\0', b''))]]
    bpy.ops.wm.open_mainfile(filepath=str(scene_path), load_ui=True, use_scripts=False)
    scene = bpy.context.scene
    bpy.context.view_layer.update()
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    meshes = {obj.name: obj for obj in mesh_objects}
    rows = []
    for expected in source:
        original = expected['vertices']
        projected = [tuple(f32(c) for c in v) for v in original]
        faces = expected['faces']
        obj = meshes.get(expected['name'])
        if obj is None:
            rows.append({'name': expected['name'], 'present': False, 'passed': False})
            continue
        actual_vertices = [tuple(float(c) for c in obj.matrix_world @ v.co) for v in obj.data.vertices]
        actual_faces = [tuple(int(i) for i in p.vertices) for p in obj.data.polygons]
        expected_material = PALETTE[expected['tool']][0]
        row_checks = {
            'world_vertices_exact_source_float32': actual_vertices == projected,
            'triangle_indices_exact_source': actual_faces == faces,
            'triangles_only': all(len(f) == 3 for f in actual_faces),
            'no_modifiers': len(obj.modifiers) == 0,
            'no_constraints_or_parent': len(obj.constraints) == 0 and obj.parent is None,
            'no_shape_keys': obj.data.shape_keys is None,
            'visible_render': not obj.hide_render and not obj.hide_get(),
            'one_expected_tool_material': len(obj.data.materials) == 1 and obj.data.materials[0].name == expected_material,
            'all_triangles_use_that_material': all(p.material_index == 0 for p in obj.data.polygons),
            'custom_tool_matches_3mf': obj.get('active_tool_id') == expected['tool'],
            'custom_object_id_matches_3mf': obj.get('source_object_id') == expected['id'],
        }
        rows.append({'name': expected['name'], 'source_object_id': expected['id'],
                     'tool': expected['tool'], 'vertices': len(original), 'triangles': len(faces),
                     'source_triangle_digest_f64': triangle_digest(original, faces, 'd'),
                     'source_triangle_digest_f32': triangle_digest(projected, faces, 'f'),
                     'scene_world_triangle_digest_f32': triangle_digest(actual_vertices, actual_faces, 'f'),
                     'float32_projection_max_abs_delta_mm': max(abs(a - b) for v, w in zip(original, projected) for a, b in zip(v, w)),
                     'checks': row_checks, 'passed': all(row_checks.values())})
    material_rows = []
    for tool, (name, hex_color) in PALETTE.items():
        mat = bpy.data.materials.get(name)
        checks = {'present': mat is not None}
        if mat is not None:
            shader = mat.node_tree.nodes.get('Principled BSDF') if mat.use_nodes and mat.node_tree else None
            checks['principled_shader'] = shader is not None
            if shader is not None:
                color = list(shader.inputs['Base Color'].default_value)
                checks['expected_linear_RGBA'] = max(abs(a - b) for a, b in zip(color, srgb_linear(hex_color))) < 1e-6
                checks['fully_opaque'] = shader.inputs['Alpha'].default_value == 1. and color[3] == 1.
                checks['no_driven_color_or_alpha'] = not shader.inputs['Base Color'].is_linked and not shader.inputs['Alpha'].is_linked
            checks['no_texture_image_nodes'] = not any(node.type == 'TEX_IMAGE' for node in mat.node_tree.nodes) if mat.node_tree else True
        material_rows.append({'tool': tool, 'name': name, 'approximate_srgb_hex': hex_color,
                              'checks': checks, 'passed': all(checks.values())})
    runtime_directories = []
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'FILE_BROWSER':
                for space in area.spaces:
                    params = getattr(space, 'params', None)
                    if params is not None:
                        runtime_directories.append(public_path(params.directory))
    dependencies = [public_path(value) for value in bpy.utils.blend_paths()]
    render_path = public_path(scene.render.filepath)
    images = [{'name': image.name, 'type': image.type, 'packed': bool(image.packed_file),
               'filepath': public_path(image.filepath)} for image in bpy.data.images]
    saved_dirs = [f for f in fields if f['structure'] == 'FileSelectParams' and f['field'].startswith('dir[')]
    checks = {
        'eight_semantic_meshes_and_no_extra_mesh': len(mesh_objects) == 8 and set(meshes) == {r['name'] for r in source},
        'scene_contains_same_eight_meshes': sum(obj.type == 'MESH' for obj in scene.objects) == 8,
        'all_world_meshes_exact_source_float32': len(rows) == 8 and all(r['passed'] for r in rows),
        'exactly_four_tool_materials': set(mat.name for mat in bpy.data.materials) == {p[0] for p in PALETTE.values()},
        'all_tool_materials_match': all(r['passed'] for r in material_rows),
        'millimeter_scene_units': scene.unit_settings.system == 'METRIC' and math.isclose(scene.unit_settings.scale_length, .001, rel_tol=0., abs_tol=1e-10) and scene.unit_settings.length_unit == 'MILLIMETERS',
        'source_SHA_custom_property_matches_actual_core': scene.get('source_3mf_sha256') == sha(core_raw),
        'source_reference_is_relative': str(scene.get('source_3mf', '')).startswith('//'),
        'no_linked_libraries': len(bpy.data.libraries) == 0,
        'no_source_photos_or_packed_image_assets': all(i['type'] in {'RENDER_RESULT', 'COMPOSITING'} and not i['packed'] for i in images),
        'no_external_dependency_paths': not dependencies,
        'saved_FileSelectParams_directory_relative_or_empty': bool(saved_dirs) and all(not f['absolute'] and (f['value'] == '' or f['value'].startswith('//')) for f in saved_dirs),
        'all_checked_saved_filename_fields_relative_or_empty': all(not f['absolute'] and not f['private_pattern_in_full_array'] for f in fields),
        'all_decoded_and_raw_private_path_pattern_scans_clear': all(not r['offsets'] for r in privacy_hits),
        'runtime_FILE_BROWSER_directories_not_absolute': all(not row['absolute'] for row in runtime_directories),
        'render_output_relative': not render_path['absolute'] and render_path['value'].startswith('//'),
        'scene_file_unchanged': scene_path.read_bytes() == scene_raw,
        'core_3mf_unchanged': core_path.read_bytes() == core_raw,
    }
    report = {'scope': 'Independent read-only saved-scene reopen, source-3MF mesh/material/unit check and decoded saved-directory privacy audit; no render, repair or scene save.',
              'passed': all(checks.values()), 'checks': checks,
              'scene': '../scene.blend', 'scene_sha256': sha(scene_raw),
              'source_3mf': '../a1-four-tool-core.3mf', 'source_3mf_sha256': sha(core_raw),
              'checker_sha256': sha(Path(__file__).read_bytes()), 'blender_version': bpy.app.version_string,
              'scene_units': {'system': scene.unit_settings.system, 'scale_length': scene.unit_settings.scale_length, 'length_unit': scene.unit_settings.length_unit},
              'zstandard_version': zstandard.__version__, 'compression': compression,
              'decoded_bytes': len(data), 'decoded_sha256': sha(data),
              'precision_note': 'World triangles must equal source coordinates projected to IEEE754 float32. Source float64-to-display differences are measured, not declared zero.',
              'parts': rows, 'materials': material_rows, 'saved_SDNA_directory_and_filename_fields': fields,
              'private_path_pattern_findings': privacy_hits,
              'runtime_FILE_BROWSER_directories': runtime_directories,
              'external_dependency_paths': dependencies, 'images': images,
              'render_output': render_path,
              'limits': 'Finite path-pattern scan and named SDNA fields, not a generic guarantee that all possible private strings are absent. Rendering pixels, source-color interpretation and printability are reviewed separately. Runtime opening path bpy.data.filepath is not a saved-payload finding.'}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf8')
    print(json.dumps({'passed': report['passed'], 'checks': checks,
                      'mesh_count': len(mesh_objects), 'material_count': len(bpy.data.materials)}, ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
