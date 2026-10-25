#!/usr/bin/env python3
"""Independent native lib3mf read/write/edit QA, never an artifact exporter.

Requires lib3mf==2.5.0. All built-in native writer outputs are disposable failing precision controls.
Successful read/edit/save/reopen uses the separate native_edit_3mf.py exact
decimal adapter, never lib3mf's unsafe built-in decimal serializer.
"""
from __future__ import annotations
import argparse
from decimal import Decimal
import csv
import hashlib
import json
import math
from pathlib import Path
import struct
import xml.etree.ElementTree as ET
import zipfile

import lib3mf

ORIGINAL_APPEARANCE_SHA = 'da023d8310e2d5f73500cc35cd910ce87ca01ef266902f92e5bc0d4094e245d2'
CORE = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
EXPECTED_COUNTS = [52416, 451, 4736, 6612, 1471]
EXPECTED_DISPLAY = ['#EDEDE8FF', '#99A8ADFF', '#A6B3B6FF', '#9EB8BAFF', '#CEBAA8FF']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def collect(iterator, getter='GetCurrent'):
    out = []
    while iterator.MoveNext():
        out.append(getattr(iterator, getter)())
    return out


def rgba8(color):
    return [color.Red, color.Green, color.Blue, color.Alpha]


def encoded(rgba):
    rgb = [12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055 for c in rgba[:3]]
    return '#' + ''.join(f'{math.floor(255 * c + .5):02X}' for c in rgb + [rgba[3]])


def source_contract(stl, appearance, bindings):
    data = stl.read_bytes()
    h = appearance['source_hashes']
    need(sha(data) == h['stl_sha256'], 'STL source hash differs')
    need(sha(bindings.read_bytes()) == h['binding_csv_sha256'], 'Binding CSV hash differs')
    count, = struct.unpack_from('<I', data, 80)
    need(len(data) == 84 + count * 50 and count == 65686, 'Unexpected binary STL record count')
    xyz = b''.join(data[84 + i * 50 + 12:84 + i * 50 + 48] for i in range(count))
    need(sha(xyz) == h['ordered_triangle_xyz_f32_sha256'], 'STL ordered XYZ hash differs')
    with bindings.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    need(len(rows) == count, 'Binding record count differs')
    ids = []
    for i, row in enumerate(rows):
        need(int(row['original_stl_face_index']) == i, f'STL face index differs at {i}')
        need(int(row['existing_blend_polygon_index']) == i, f'Blend polygon index differs at {i}')
        ids.append(int(row['existing_blend_material_index']))
    need([ids.count(i) for i in range(5)] == EXPECTED_COUNTS, 'Stored material counts differ')
    need(sha(bytes(ids)) == h['face_material_index_u8_sha256'], 'Binding byte-stream hash differs')
    mats = appearance['materials']
    need(len(mats) == 5, 'Expected five original material identities')
    for i, mat in enumerate(mats):
        need(mat['index'] == i, 'Original material index ordering differs')
        raw = bytes.fromhex(mat['rgba_le_f32_hex'])
        need(len(raw) == 16, 'RGBA record must contain four float32 words')
        rgba = struct.unpack('<4f', raw)
        need([Decimal(s) for s in mat['rgba_exact_decimal']] == [Decimal.from_float(x) for x in rgba], 'Exact RGBA decimal/word mismatch')
        need(encoded(rgba) == mat['display_rgba8_hex'] == EXPECTED_DISPLAY[i], 'Linear-to-sRGB code mismatch')
        need(mat['face_count'] == EXPECTED_COUNTS[i], 'Appearance face count differs')
    return xyz, ids


def read_native(wrapper, path, appearance):
    model = wrapper.CreateModel()
    reader = model.QueryReader('3mf')
    reader.SetStrictModeActive(True)
    reader.ReadFromFile(str(path))
    warnings = [reader.GetWarning(i) for i in range(reader.GetWarningCount())]
    need(not warnings, f'Native strict reader warnings: {warnings!r}')
    need(model.GetUnit() == lib3mf.ModelUnit.MilliMeter, 'Native model unit is not millimetres')
    meshes = collect(model.GetMeshObjects(), 'GetCurrentMeshObject')
    groups = collect(model.GetBaseMaterialGroups(), 'GetCurrentBaseMaterialGroup')
    builds = collect(model.GetBuildItems())
    need(len(meshes) == len(groups) == len(builds) == 1, 'Expected one mesh, material group and build item')
    need(len(collect(model.GetResources())) == 2, 'Unexpected native resource/hidden geometry')
    need(model.GetAttachmentCount() == 0, 'Unexpected native attachment')
    mesh, group, build = meshes[0], groups[0], builds[0]
    need(build.GetObjectResourceID() == mesh.GetResourceID(), 'Build references wrong object')
    transform = [list(row) for row in build.GetObjectTransform().Fields]
    need(transform == [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.], [0., 0., 0.]], 'Non-identity native build transform')
    vertices = [list(p.Coordinates) for p in mesh.GetVertices()]
    triangles = [list(t.Indices) for t in mesh.GetTriangleIndices()]
    need(len(vertices) == 32643 and len(triangles) == 65686, 'Native geometry size differs')
    materials = []
    native_ids = group.GetAllPropertyIDs()
    need(len(native_ids) == 5 and len(set(native_ids)) == 5, 'Native material property identities differ')
    # lib3mf uses opaque property IDs (1..5 here), not XML's 0-based indices.
    property_to_index = {pid: i for i, pid in enumerate(native_ids)}
    for i in native_ids:
        materials.append({'name': group.GetName(i), 'rgba8': rgba8(group.GetDisplayColor(i))})
    props = mesh.GetAllTriangleProperties()
    need(len(props) == len(triangles), 'Missing native per-face material property')
    face_ids = []
    for i, p in enumerate(props):
        values = list(p.PropertyIDs)
        need(p.ResourceID == group.GetResourceID(), f'Face {i} has wrong native resource')
        need(values[0] == values[1] == values[2] and values[0] in property_to_index, f'Face {i} has invalid/gradient native properties')
        face_ids.append(property_to_index[values[0]])
    fallback = mesh.GetObjectLevelProperty()
    need(fallback == (group.GetResourceID(), native_ids[0], True), f'Neutral object fallback differs: {fallback!r}')
    exact = []
    meta_group = model.GetMetaDataGroup()
    metadata = []
    for i in range(meta_group.GetMetaDataCount()):
        md = meta_group.GetMetaData(i)
        value = md.GetValue()
        metadata.append({'namespace': md.GetNameSpace(), 'name': md.GetName(), 'must_preserve': md.GetMustPreserve()})
        try:
            parsed = json.loads(value)
        except (ValueError, TypeError):
            continue
        if parsed == appearance:
            exact.append(md)
    need(len(exact) == 1 and exact[0].GetMustPreserve(), 'Exact appearance metadata missing/changed/not preserve=1')
    xyz = b''.join(struct.pack('<3f', *vertices[vid]) for tri in triangles for vid in tri)
    snapshot = {'vertices': vertices, 'triangles': triangles, 'face_materials': face_ids, 'materials': materials}
    summary = {
        'reader_strict_mode': True, 'reader_warnings': warnings, 'unit': 'millimeter',
        'mesh_count': 1, 'build_item_count': 1, 'vertex_count': len(vertices),
        'triangle_count': len(triangles), 'material_group_count': 1,
        'material_counts': [face_ids.count(i) for i in range(5)],
        'ordered_triangle_xyz_f32_sha256': sha(xyz),
        'face_material_index_u8_sha256': sha(bytes(face_ids)),
        'manifold_and_oriented': mesh.IsManifoldAndOriented(), 'native_is_valid': mesh.IsValid(),
        'neutral_fallback_material_index': 0, 'identity_build_transform': True,
        'exact_appearance_metadata_retained': True, 'metadata': metadata,
    }
    return model, mesh, group, snapshot, xyz, summary


def write_native(model, path, precision):
    writer = model.QueryWriter('3mf')
    writer.SetStrictModeActive(True)
    writer.SetDecimalPrecision(precision)
    writer.WriteToFile(str(path))
    warnings = [writer.GetWarning(i) for i in range(writer.GetWarningCount())]
    need(not warnings, f'Native writer warnings: {warnings!r}')


def decimal_audit(path):
    with zipfile.ZipFile(path) as archive:
        names = [n for n in archive.namelist() if n.lower().endswith('.model')]
        need(len(names) == 1, 'Expected one model XML for decimal audit')
        root = ET.fromstring(archive.read(names[0]))
    mismatch = 0
    max_error = Decimal(0)
    exponent = 0
    for v in root.iter(CORE + 'vertex'):
        for axis in 'xyz':
            s = v.attrib[axis]
            exponent += int('e' in s.lower())
            value, = struct.unpack('<f', struct.pack('<f', float(s)))
            error = abs(Decimal(s) - Decimal.from_float(value))
            if error:
                mismatch += 1
                max_error = max(max_error, error)
    return {'coordinate_decimal_not_exact_float32_count': mismatch,
            'max_decimal_absolute_difference': str(max_error),
            'exponent_notation_coordinate_count': exponent}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ['model', 'stl', 'appearance', 'bindings', 'work-dir', 'report']:
        p.add_argument('--' + arg, required=True, type=Path)
    args = p.parse_args()
    # Disposable outputs cannot overwrite input/public artifacts.
    protected = {x.resolve() for x in [args.model, args.stl, args.appearance, args.bindings]}
    for public_root in [Path(__file__).resolve().parent, args.model.resolve().parent]:
        need(not args.work_dir.resolve().is_relative_to(public_root), 'Use a disposable work directory outside the public/model folder')
        need(not args.report.resolve().is_relative_to(public_root), 'Write the test report outside the public/model folder')
    args.work_dir.mkdir(parents=True, exist_ok=True)
    outputs = [args.work_dir / n for n in ['native-mesh.json', 'adapter-roundtrip.3mf', 'adapter-face-edit.3mf', 'adapter-material-edit.3mf', 'guard-invalid-face.3mf', 'guard-alpha.3mf', 'guard-drift.3mf'] + [f'native-precision-{i}.3mf' for i in range(6, 17)]] + [args.report]
    for output in outputs:
        need(output.resolve() not in protected, 'Unsafe disposable output path')
        need(not output.is_symlink(), 'Unsafe output symlink')
        if output.exists():
            need(not any(output.samefile(source) for source in [args.model, args.stl, args.appearance, args.bindings]), 'Unsafe hard-link alias of an input')
    initial_hashes = {str(x): sha(x.read_bytes()) for x in [args.model, args.stl, args.appearance, args.bindings]}
    need(sha(args.appearance.read_bytes()) == ORIGINAL_APPEARANCE_SHA, 'Pinned original appearance record hash differs')
    appearance = json.loads(args.appearance.read_text(encoding='utf-8'))
    source_xyz, ids = source_contract(args.stl, appearance, args.bindings)
    wrapper = lib3mf.Wrapper()
    need(wrapper.GetLibraryVersion() == (2, 5, 0), 'This tested consumer contract pins lib3mf 2.5.0')
    model, mesh, group, original, xyz, initial = read_native(wrapper, args.model, appearance)
    need(xyz == source_xyz, 'Native 3MF import changed same-index triangle/corner float32 geometry')
    need(original['face_materials'] == ids, 'Native 3MF import changed original stored face binding')
    for i, mat in enumerate(original['materials']):
        need(mat['name'] == appearance['materials'][i]['name'], 'Native material identity/name differs')
        need('#' + ''.join(f'{x:02X}' for x in mat['rgba8']) == EXPECTED_DISPLAY[i], 'Native encoded display differs')
    need(initial['manifold_and_oriented'] and initial['native_is_valid'], 'Native validity/orientation check failed')
    source_decimal = decimal_audit(args.model)
    need(source_decimal['coordinate_decimal_not_exact_float32_count'] == 0, 'Production 3MF decimals are not exact original float32 values')
    need(source_decimal['exponent_notation_coordinate_count'] == 0, 'Production 3MF uses exponent coordinates')
    mesh_export = dict(original, model_sha256=initial_hashes[str(args.model)], reader='lib3mf 2.5.0')
    (args.work_dir / 'native-mesh.json').write_text(json.dumps(mesh_export, separators=(',', ':'), ensure_ascii=False) + '\n', encoding='utf-8')

    # lib3mf's built-in serializer is tested, NOT assumed to be safe. Each
    # failure is retained; the adapter below is a separate, explicit workflow.
    raw_writer = []
    for precision in range(6, 17):
        raw_path = args.work_dir / f'native-precision-{precision}.3mf'
        write_native(model, raw_path, precision)
        _, _, _, raw_state, raw_xyz, raw_summary = read_native(wrapper, raw_path, appearance)
        changed_words = sum(source_xyz[i:i+4] != raw_xyz[i:i+4] for i in range(0, len(source_xyz), 4))
        need(changed_words > 0, f'Known lib3mf {precision}-decimal limitation unexpectedly absent; investigate version/environment')
        need(raw_state['triangles'] == original['triangles'] and raw_state['face_materials'] == ids and raw_state['materials'] == original['materials'], 'Raw writer changed more than its known coordinate serializer limitation')
        raw_writer.append({'precision': precision, 'status': 'FAIL_EXACT_GEOMETRY',
            'changed_ordered_float32_coordinate_words': changed_words,
            'triangle_indices_materials_and_assignments_unchanged': True,
            'exact_appearance_metadata_retained': raw_summary['exact_appearance_metadata_retained'],
            'decimal_audit': decimal_audit(raw_path)})

    import native_edit_3mf as adapter
    roundtrip = args.work_dir / 'adapter-roundtrip.3mf'
    adapter_roundtrip = adapter.edit_copy(args.model, args.appearance, roundtrip, overwrite=True)
    _, _, _, reread, reread_xyz, rt = read_native(wrapper, roundtrip, appearance)
    need(reread == original and reread_xyz == source_xyz, 'Supplied adapter roundtrip changes geometry/material/face data')
    rt['decimal_audit'] = decimal_audit(roundtrip)
    need(rt['decimal_audit']['coordinate_decimal_not_exact_float32_count'] == 0, 'Adapter coordinate decimals not exact')
    rt['status'] = 'PASS_SUPPLIED_EXACT_ADAPTER_NOT_NATIVE_BUILTIN_WRITER'

    face_id, new_id = 0, (ids[0] + 1) % 5
    edit_path = args.work_dir / 'adapter-face-edit.3mf'
    adapter_face = adapter.edit_copy(args.model, args.appearance, edit_path,
        face_index=face_id, material_index=new_id, overwrite=True)
    _, _, _, edited, edited_xyz, face_result = read_native(wrapper, edit_path, appearance)
    changed_faces = [i for i, (a, b) in enumerate(zip(ids, edited['face_materials'])) if a != b]
    need(changed_faces == [face_id] and edited['face_materials'][face_id] == new_id, 'Face edit changed unintended bindings')
    need(edited_xyz == source_xyz and edited['vertices'] == original['vertices'] and edited['triangles'] == original['triangles'], 'Face edit changed geometry')
    need(edited['materials'] == original['materials'], 'Face edit changed global materials')
    face_decimal = decimal_audit(edit_path)
    need(face_decimal['coordinate_decimal_not_exact_float32_count'] == 0, 'Face edit lost exact coordinate decimal values')

    material_id = 3
    old_red = original['materials'][material_id]['rgba8'][0]
    expected_mats = json.loads(json.dumps(original['materials']))
    expected_mats[material_id]['rgba8'][0] += 1
    edit_color = '#' + ''.join(f'{x:02X}' for x in expected_mats[material_id]['rgba8'])
    edit_path = args.work_dir / 'adapter-material-edit.3mf'
    adapter_material = adapter.edit_copy(args.model, args.appearance, edit_path,
        material_index=material_id, display_rgba8=edit_color, overwrite=True)
    _, _, _, edited, edited_xyz, color_result = read_native(wrapper, edit_path, appearance)
    need(edited['materials'] == expected_mats, 'Material edit changed an unintended name/channel/material')
    need(edited['face_materials'] == ids and edited_xyz == source_xyz, 'Material edit changed bindings or geometry')
    need(edited['vertices'] == original['vertices'] and edited['triangles'] == original['triangles'], 'Material edit changed mesh indices')
    color_decimal = decimal_audit(edit_path)
    need(color_decimal['coordinate_decimal_not_exact_float32_count'] == 0, 'Material edit lost exact coordinate decimal values')

    # Adapter guards must fail before writes. Deliberately lossy native output
    # cannot be laundered through the adapter as an original model.
    guards = []
    for label, source, output, kwargs in [
        ('input-overwrite', args.model, args.model, {}),
        ('invalid-face-index', args.model, args.work_dir/'guard-invalid-face.3mf', {'face_index': 65686, 'material_index': 0}),
        ('nonopaque-color', args.model, args.work_dir/'guard-alpha.3mf', {'material_index': 3, 'display_rgba8': '#9FB8BA80'}),
        ('native-writer-coordinate-drift', args.work_dir/'native-precision-6.3mf', args.work_dir/'guard-drift.3mf', {})
    ]:
        try:
            adapter.edit_copy(source, args.appearance, output, overwrite=True, **kwargs)
        except ValueError as exc:
            guards.append({'case': label, 'status': 'REJECTED_AS_EXPECTED', 'reason': str(exc)})
        else:
            raise AssertionError('Adapter accepted forbidden case: '+label)
    need(all(sha(Path(x).read_bytes()) == h for x, h in initial_hashes.items()), 'An immutable input changed during native QA')
    report = {
        'schema': 'cnu-interchange-native-lib3mf-qa-v2',
        'status': 'PASS_NATIVE_READ_AND_SUPPLIED_ADAPTER_WORKFLOW_WITH_RAW_WRITER_LIMITATION',
        'consumer': 'lib3mf', 'consumer_version': '2.5.0',
        'model_sha256': initial_hashes[str(args.model)],
        'original_source_hashes': appearance['source_hashes'],
        'native_initial_read': initial,
        'production_decimal_audit': source_decimal,
        'native_builtin_writer': {'status': 'UNSAFE_FOR_EXACT_GEOMETRY', 'used_for_deliverable': False,
            'precision_sweep': raw_writer,
            'example_precision_16': {'source_decimal': '-75', 'written_decimal': '-75.0000039769669632', 'native_reopened_float32': '-75.00000762939453125'}},
        'supplied_adapter_roundtrip': dict(adapter_roundtrip, validation=rt),
        'supplied_adapter_face_edit_save_reopen': dict(adapter_face,
            changed_face_indices=changed_faces, all_other_face_assignments_identical=True,
            global_materials_identical=True, exact_decimal_audit=face_decimal),
        'supplied_adapter_material_edit_save_reopen': dict(adapter_material,
            all_other_channels_names_and_materials_identical=True,
            face_assignments_identical=True, exact_decimal_audit=color_decimal),
        'adapter_negative_controls': guards,
        'immutable_inputs_unchanged': True,
        'limitations': [
            'Only lib3mf 2.5.0 is the tested native reader/editor; no universal slicer claim.',
            'The built-in lib3mf writer failed exact geometry at all tested precisions 6 through 16; every raw failure is retained.',
            'Successful save/reopen tests use the explicitly supplied native_edit_3mf.py exact-decimal adapter, NOT the built-in writer.',
            'Native API edits occur before the adapter reads actual native mesh/material state and serializes it; edited QA files are not delivered.',
            'Standard 3MF colours are quantized 8-bit sRGB, not lossless original linear RGBA.',
            'Exact-value metadata remains unchanged during deliberate edits and describes original appearance, not edited test colours.',
            'No original Blend write, reclassification, source-corrected material claim, geometry repair or physical print certification.'
        ]
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'consumer': 'lib3mf 2.5.0', 'model_sha256': report['model_sha256'],
        'same_index_triangles': 65686, 'material_counts': EXPECTED_COUNTS,
        'native_builtin_writer': 'UNSAFE_ALL_TESTED_PRECISIONS_6_TO_16',
        'supplied_adapter_roundtrip_and_edits_exact': True,
        'face_edit_verified': True, 'material_edit_verified': True,
        'original_exact_rgba_metadata_preserved': True}, indent=2))


if __name__ == '__main__':
    main()
