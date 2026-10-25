#!/usr/bin/env python3
"""Export only the pinned existing CNU model; no rebuilding or reclassification.

Python 3.11+ standard library. Deterministic ZIP_STORED and exact float32 decimals.
Run from this supplement: python export_3mf.py --model-dir .. --output model.3mf
"""
import argparse
import csv
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import struct
from xml.sax.saxutils import escape, quoteattr
import zipfile

HERE = Path(__file__).resolve().parent
STL_SHA = '353a5ce7fcd15a798f8bbf932e73d67b95ef856c60623cc3d7831f46dd609897'
BLEND_SHA = 'd63ad8d2dcf1c896dda145966e4bad84e9475634c3080755fe60251e0cd0189a'
BINDING_SHA = 'acd713223dc352c9dedb7902273d28db5b58c0288dbd9308b6c3b389ec338f54'
APPEARANCE_SHA = 'da023d8310e2d5f73500cc35cd910ce87ca01ef266902f92e5bc0d4094e245d2'
XYZ_SHA = 'cf80fd91ee40f3f89dc711404ef27731763ce3d265bafd26e1ad8e7fe354e85a'
INDEX_SHA = '7565653b6de1aed06d7785ddf83c5839d55a15977bde3d7073f41334e02ecb12'
COUNTS = [52416, 451, 4736, 6612, 1471]
CORE = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
VENDOR = 'https://github.com/root50643/taiwan-buildings-3d/ns/interchange/1'
MEMBERS = ('[Content_Types].xml', '_rels/.rels', '3D/3dmodel.model')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def checked(path, expected):
    data = Path(path).read_bytes()
    if sha(data) != expected:
        raise ValueError(f'Pinned input hash mismatch: {Path(path).name}')
    return data


def linear_to_srgb8(rgba):
    rgb = [12.92*x if x <= .0031308 else 1.055*x**(1/2.4)-.055 for x in rgba[:3]]
    return '#' + ''.join(f'{math.floor(255*x+.5):02X}' for x in rgb+[rgba[3]])


def inputs(stl, blend, appearance=HERE/'appearance-original.json', bindings=HERE/'face-materials.csv'):
    raw = checked(stl, STL_SHA)
    checked(blend, BLEND_SHA)
    a = json.loads(checked(appearance, APPEARANCE_SHA))
    checked(bindings, BINDING_SHA)
    count = struct.unpack_from('<I', raw, 80)[0]
    if count != 65686 or len(raw) != 84+50*count:
        raise ValueError('Unexpected binary STL layout')
    corners = b''.join(raw[84+50*i+12:84+50*i+48] for i in range(count))
    if sha(corners) != XYZ_SHA:
        raise ValueError('Ordered corner hash mismatch')
    with Path(bindings).open(newline='') as f:
        rows = list(csv.DictReader(f))
    indices = []
    for i, row in enumerate(rows):
        if int(row['original_stl_face_index']) != i or int(row['existing_blend_polygon_index']) != i:
            raise ValueError('Stored source order mismatch')
        indices.append(int(row['existing_blend_material_index']))
    if len(indices) != count or sha(bytes(indices)) != INDEX_SHA:
        raise ValueError('Stored face assignments mismatch')
    if [indices.count(i) for i in range(5)] != COUNTS:
        raise ValueError('Stored material counts mismatch')
    for i, m in enumerate(a['materials']):
        rgba = struct.unpack('<4f', bytes.fromhex(m['rgba_le_f32_hex']))
        if m['index'] != i or linear_to_srgb8(rgba) != m['display_rgba8_hex']:
            raise ValueError('Color encoding mismatch')
        if [format(Decimal.from_float(x), 'f') for x in rgba] != m['rgba_exact_decimal']:
            raise ValueError('Exact RGBA record mismatch')
    return corners, indices, a


def exact_vertex_table(corners):
    # Identity is all 12 float32 bytes, not a tolerance or decimal-rounded key.
    table, vertices, triangles = {}, [], []
    for i in range(0, len(corners), 36):
        triangle = []
        for j in (0, 12, 24):
            word = corners[i+j:i+j+12]
            if word not in table:
                table[word] = len(vertices)
                xyz = struct.unpack('<3f', word)
                if not all(math.isfinite(x) for x in xyz):
                    raise ValueError('Nonfinite coordinate')
                vertices.append(tuple(format(Decimal.from_float(x), 'f') for x in xyz))
            triangle.append(table[word])
        triangles.append(triangle)
    if len(vertices) != 32643:
        raise ValueError('Unexpected exact-bit vertex count')
    return vertices, triangles


def make_parts(corners, indices, appearance):
    vertices, triangles = exact_vertex_table(corners)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             f'<model unit="millimeter" xml:lang="zh-TW" xmlns="{CORE}" xmlns:tb="{VENDOR}">',
             '<metadata name="Title">CNU Wang Chen Library - existing contrast display interchange</metadata>',
             '<metadata name="Description">Existing whole L-building only; Q excluded. Unchanged geometry and stored preview contrast assignments. Standard display colors are quantized sRGB8, not measured materials or lossless original float color. Original README warnings remain applicable.</metadata>',
             '<metadata name="tb:appearance-original" preserve="1">'+escape(json.dumps(appearance, ensure_ascii=False, sort_keys=True, separators=(',', ':')))+'</metadata>',
             '<resources><basematerials id="1">']
    for m in appearance['materials']:
        lines.append('<base name='+quoteattr(m['name'])+' displaycolor='+quoteattr(m['display_rgba8_hex'])+'/>')
    lines += ['</basematerials>', '<object id="2" type="model" name="CNU_Wang_Chen_Library" pid="1" pindex="0">', '<mesh><vertices>']
    lines += [f'<vertex x="{x}" y="{y}" z="{z}"/>' for x,y,z in vertices]
    lines += ['</vertices><triangles>']
    for (v1,v2,v3), m in zip(triangles, indices):
        lines.append(f'<triangle v1="{v1}" v2="{v2}" v3="{v3}" pid="1" p1="{m}" p2="{m}" p3="{m}"/>')
    lines += ['</triangles></mesh></object></resources>', '<build><item objectid="2"/></build></model>']
    types = '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>\n'
    rels = '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" Target="/3D/3dmodel.model"/></Relationships>\n'
    return dict(zip(MEMBERS, [types.encode(), rels.encode(), ('\n'.join(lines)+'\n').encode()]))


def write_package(path, parts):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED, allowZip64=False) as z:
        for name in MEMBERS:
            info = zipfile.ZipInfo(name, date_time=(1980,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.extra = b''
            info.comment = b''
            z.writestr(info, parts[name])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model-dir', type=Path, default=HERE.parent)
    p.add_argument('--stl', type=Path)
    p.add_argument('--blend', type=Path)
    p.add_argument('--appearance', type=Path, default=HERE/'appearance-original.json')
    p.add_argument('--bindings', type=Path, default=HERE/'face-materials.csv')
    p.add_argument('--output', type=Path, default=HERE/'cnu-wang-chen-library.3mf')
    a = p.parse_args()
    stl, blend = a.stl or a.model_dir/'model.stl', a.blend or a.model_dir/'scene.blend'
    if a.output.resolve() in {stl.resolve(), blend.resolve(), a.appearance.resolve(), a.bindings.resolve()}:
        raise ValueError('Refusing to overwrite an input')
    if a.output.is_symlink() or (a.output.exists() and any(a.output.samefile(p) for p in (stl, blend, a.appearance, a.bindings))):
        raise ValueError('Refusing output symlink or input hardlink overwrite')
    write_package(a.output, make_parts(*inputs(stl, blend, a.appearance, a.bindings)))
    print(json.dumps({'output':a.output.name,'bytes':a.output.stat().st_size,'sha256':sha(a.output.read_bytes()),'faces':65686,'vertices':32643,'color_claim':'quantized sRGB8 display only; exact original RGBA retained separately'}, indent=2))


if __name__ == '__main__':
    main()
