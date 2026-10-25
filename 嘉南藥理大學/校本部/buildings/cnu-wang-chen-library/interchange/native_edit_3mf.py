#!/usr/bin/env python3
"""Precision-safe, limited CNU 3MF editing adapter for lib3mf 2.5.0.

This is NOT lib3mf's built-in writer. Read and edit in lib3mf, serialize the
actual native float32 positions with exact decimals, then reopen in lib3mf.
The built-in writer in tested lib3mf 2.5.0 loses coordinate bits at every
precision tested (6..16). Never use it to replace the exact production 3MF.

Only a face's existing material assignment or one opaque sRGB8 display colour
can change. Geometry and original exact appearance metadata remain unchanged.
The original metadata describes ORIGINAL appearance, not an edited rendition.
This utility does not edit Blender files or claim measured building materials.
"""
from __future__ import annotations
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import struct
from xml.sax.saxutils import escape, quoteattr
import zipfile
import lib3mf

CORE = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
VENDOR = 'https://github.com/root50643/taiwan-buildings-3d/ns/interchange/1'
ORIGINAL_APPEARANCE_SHA = 'da023d8310e2d5f73500cc35cd910ce87ca01ef266902f92e5bc0d4094e245d2'
EXPECTED_XYZ = 'cf80fd91ee40f3f89dc711404ef27731763ce3d265bafd26e1ad8e7fe354e85a'
MEMBERS = ('[Content_Types].xml', '_rels/.rels', '3D/3dmodel.model')


def check(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def items(iterator, getter='GetCurrent'):
    out = []
    while iterator.MoveNext():
        out.append(getattr(iterator, getter)())
    return out


def native_state(model, appearance):
    check(model.GetUnit() == lib3mf.ModelUnit.MilliMeter, 'Expected millimetres')
    meshes = items(model.GetMeshObjects(), 'GetCurrentMeshObject')
    groups = items(model.GetBaseMaterialGroups(), 'GetCurrentBaseMaterialGroup')
    builds = items(model.GetBuildItems())
    check(len(meshes) == len(groups) == len(builds) == 1, 'Only this single-mesh CNU model is supported')
    check(len(items(model.GetResources())) == 2 and model.GetAttachmentCount() == 0, 'Unsupported additional resources/attachments')
    mesh, group, build = meshes[0], groups[0], builds[0]
    check(build.GetObjectResourceID() == mesh.GetResourceID(), 'Unexpected build reference')
    check(mesh.GetMetaDataGroup().GetMetaDataCount() == 0 and mesh.GetTriangleSetCount() == 0 and not mesh.HasSlices(False), 'Unsupported object metadata, triangle sets or slices')
    check([list(x) for x in build.GetObjectTransform().Fields] == [[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,0.]], 'Nonidentity transform is unsupported')
    vertices = [list(p.Coordinates) for p in mesh.GetVertices()]
    triangles = [list(t.Indices) for t in mesh.GetTriangleIndices()]
    check(len(vertices) == 32643 and len(triangles) == 65686, 'Unexpected geometry counts')
    xyz = b''.join(struct.pack('<3f', *vertices[i]) for tri in triangles for i in tri)
    check(sha(xyz) == EXPECTED_XYZ == appearance['source_hashes']['ordered_triangle_xyz_f32_sha256'], 'Geometry is not exact original ordered float32 corners')
    pids = group.GetAllPropertyIDs()
    check(len(pids) == 5 and len(set(pids)) == 5, 'Expected five distinct native material properties')
    pindex = {pid: i for i, pid in enumerate(pids)}
    materials = []
    for i, pid in enumerate(pids):
        name = group.GetName(pid)
        check(name == appearance['materials'][i]['name'], 'Original material names/order must remain unchanged')
        c = group.GetDisplayColor(pid)
        rgba = [c.Red, c.Green, c.Blue, c.Alpha]
        check(rgba[3] == 255, 'Only opaque preview display colours are supported')
        materials.append({'name': name, 'rgba8': rgba})
    indices = []
    for p in mesh.GetAllTriangleProperties():
        ids = list(p.PropertyIDs)
        check(p.ResourceID == group.GetResourceID() and ids[0] == ids[1] == ids[2] and ids[0] in pindex, 'Unsupported face properties or gradients')
        indices.append(pindex[ids[0]])
    check(len(indices) == len(triangles), 'Missing explicit face assignments')
    check(mesh.GetObjectLevelProperty() == (group.GetResourceID(), pids[0], True), 'Neutral fallback missing')
    matches = []
    mg = model.GetMetaDataGroup()
    for i in range(mg.GetMetaDataCount()):
        md = mg.GetMetaData(i)
        check((md.GetNameSpace(), md.GetName()) in {('', 'Title'), ('', 'Description'), (VENDOR, 'appearance-original'), (VENDOR, 'adapter-workflow')}, 'Unsupported metadata would be lost; refusing adaptation')
        try:
            v = json.loads(md.GetValue())
        except (TypeError, ValueError):
            continue
        if v == appearance:
            matches.append(md.GetMustPreserve())
    check(matches == [True], 'Original exact appearance metadata missing or changed')
    return mesh, group, {'vertices': vertices, 'triangles': triangles, 'face_materials': indices, 'materials': materials}


def read_model(wrapper, path, appearance):
    model = wrapper.CreateModel()
    reader = model.QueryReader('3mf')
    reader.SetStrictModeActive(True)
    reader.ReadFromFile(str(path))
    check(reader.GetWarningCount() == 0, 'Native strict reader reported warnings')
    mesh, group, state = native_state(model, appearance)
    return model, mesh, group, state


def exact_parts(state, appearance, operation):
    metadata = json.dumps(appearance, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    note = json.dumps({'workflow': 'lib3mf 2.5.0 read/edit; supplied exact-decimal serializer; lib3mf reopen',
        'built_in_writer_used': False, 'appearance_original_is_historical_not_edited_display': True,
        'operation': operation}, sort_keys=True, separators=(',', ':'))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
        f'<model unit="millimeter" xml:lang="zh-TW" xmlns="{CORE}" xmlns:tb="{VENDOR}">',
        '<metadata name="Title">CNU existing-model contrast display - exact adapter copy</metadata>',
        '<metadata name="Description">User-edited/disposable adapter copy. Original geometry and original appearance record retained. Display colors are quantized sRGB8, not measured material colors. Original model README warnings remain applicable.</metadata>',
        '<metadata name="tb:appearance-original" preserve="1">'+escape(metadata)+'</metadata>',
        '<metadata name="tb:adapter-workflow" preserve="1">'+escape(note)+'</metadata>',
        '<resources><basematerials id="1">']
    for mat in state['materials']:
        color = '#' + ''.join(f'{n:02X}' for n in mat['rgba8'])
        lines.append('<base name='+quoteattr(mat['name'])+' displaycolor='+quoteattr(color)+'/>')
    lines += ['</basematerials>', '<object id="2" type="model" name="CNU_Wang_Chen_Library" pid="1" pindex="0"><mesh><vertices>']
    for v in state['vertices']:
        x, y, z = [format(Decimal.from_float(float(c)), 'f') for c in v]
        lines.append(f'<vertex x="{x}" y="{y}" z="{z}"/>')
    lines.append('</vertices><triangles>')
    for tri, mat in zip(state['triangles'], state['face_materials']):
        a,b,c = tri
        lines.append(f'<triangle v1="{a}" v2="{b}" v3="{c}" pid="1" p1="{mat}" p2="{mat}" p3="{mat}"/>')
    lines += ['</triangles></mesh></object></resources>', '<build><item objectid="2"/></build></model>']
    types = '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>\n'
    rels = '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" Target="/3D/3dmodel.model"/></Relationships>\n'
    return [types.encode(), rels.encode(), ('\n'.join(lines)+'\n').encode()]


def edit_copy(source, appearance_path, output, face_index=None, material_index=None, display_rgba8=None, overwrite=False):
    source, appearance_path, output = Path(source), Path(appearance_path), Path(output)
    check(source.resolve() != output.resolve() and appearance_path.resolve() != output.resolve(), 'Refusing input overwrite')
    check(output.suffix.lower() == '.3mf', 'Output must be a separate .3mf file, never a Blend')
    check(overwrite or not output.exists(), 'Output exists; use a new path or explicit --overwrite')
    check(not output.is_symlink(), 'Output symlinks are not supported')
    if output.exists():
        check(not output.samefile(source) and not output.samefile(appearance_path), 'Refusing a hard-link alias of an input')
    before = source.read_bytes()
    app_bytes = appearance_path.read_bytes()
    check(sha(app_bytes) == ORIGINAL_APPEARANCE_SHA, 'Pinned original appearance record hash differs')
    appearance = json.loads(app_bytes)
    check(not (face_index is not None and display_rgba8 is not None), 'Choose face assignment OR display colour, not both')
    if face_index is not None:
        check(0 <= face_index < 65686 and material_index is not None and 0 <= material_index < 5, 'Face/material index outside original ranges')
    elif display_rgba8 is not None:
        check(material_index is not None and 0 <= material_index < 5 and re.fullmatch(r'#[0-9a-fA-F]{6}[fF]{2}', display_rgba8), 'Use an existing material index and opaque #RRGGBBFF sRGB8 colour')
    else:
        check(material_index is None, 'Material index without an edit is invalid')
    wrapper = lib3mf.Wrapper()
    check(wrapper.GetLibraryVersion() == (2,5,0), 'This adapter is tested with lib3mf 2.5.0 only')
    model, mesh, group, initial = read_model(wrapper, source, appearance)
    operation = {'type': 'roundtrip-no-edit'}
    if face_index is not None:
        prop = mesh.GetTriangleProperties(face_index)
        for c in range(3):
            prop.PropertyIDs[c] = group.GetAllPropertyIDs()[material_index]
        mesh.SetTriangleProperties(face_index, prop)
        operation = {'type': 'face-material', 'face_index': face_index, 'old_material_index': initial['face_materials'][face_index], 'new_material_index': material_index}
    elif display_rgba8 is not None:
        pid = group.GetAllPropertyIDs()[material_index]
        color = group.GetDisplayColor(pid)
        rgba = bytes.fromhex(display_rgba8[1:])
        color.Red, color.Green, color.Blue, color.Alpha = rgba
        group.SetDisplayColor(pid, color)
        operation = {'type': 'material-display', 'material_index': material_index, 'old_rgba8': initial['materials'][material_index]['rgba8'], 'new_rgba8': list(rgba)}
    _, _, edited = native_state(model, appearance)
    check(edited['vertices'] == initial['vertices'] and edited['triangles'] == initial['triangles'], 'Native edit unexpectedly modified geometry')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
        for name, data in zip(MEMBERS, exact_parts(edited, appearance, operation)):
            info = zipfile.ZipInfo(name, (1980,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    _, _, _, reopened = read_model(wrapper, output, appearance)
    check(reopened == edited, 'Adapter save/reopen changed native mesh or material state')
    check(source.read_bytes() == before and appearance_path.read_bytes() == app_bytes, 'Immutable input changed')
    return {'status': 'PASS_SUPPLIED_EXACT_ADAPTER_WORKFLOW', 'input_sha256': sha(before),
        'output_sha256': sha(output.read_bytes()), 'operation': operation,
        'native_reader_and_editor': 'lib3mf 2.5.0', 'native_builtin_writer_used': False,
        'serializer': 'supplied exact float32 decimal / deterministic ZIP_STORED',
        'geometry_unchanged': True, 'exact_original_appearance_record_unchanged': True,
        'same_state_after_native_reopen': True}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model', required=True, type=Path)
    p.add_argument('--appearance', type=Path, default=Path(__file__).with_name('appearance-original.json'))
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--face-index', type=int)
    p.add_argument('--material-index', type=int)
    p.add_argument('--display-rgba8')
    p.add_argument('--overwrite', action='store_true')
    args = p.parse_args()
    print(json.dumps(edit_copy(args.model, args.appearance, args.output, args.face_index, args.material_index, args.display_rgba8, args.overwrite), indent=2))


if __name__ == '__main__':
    main()
