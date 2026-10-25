#!/usr/bin/env python3
"""Independent ZIP/XML and same-index binary32 validation of this pinned supplement.

Uses no exporter code and no third-party Python libraries. It validates this
specific immutable deliverable, not arbitrary 3MF files or physical printability.
"""
import argparse
from collections import Counter, defaultdict
import csv
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
CORE = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
REL = '{http://schemas.openxmlformats.org/package/2006/relationships}'
CT = '{http://schemas.openxmlformats.org/package/2006/content-types}'
EXPECTED_MEMBERS = ['[Content_Types].xml', '_rels/.rels', '3D/3dmodel.model']
PINS = {
    'stl': '353a5ce7fcd15a798f8bbf932e73d67b95ef856c60623cc3d7831f46dd609897',
    'blend': 'd63ad8d2dcf1c896dda145966e4bad84e9475634c3080755fe60251e0cd0189a',
    'appearance': 'da023d8310e2d5f73500cc35cd910ce87ca01ef266902f92e5bc0d4094e245d2',
    'bindings': 'acd713223dc352c9dedb7902273d28db5b58c0288dbd9308b6c3b389ec338f54',
    'xyz': 'cf80fd91ee40f3f89dc711404ef27731763ce3d265bafd26e1ad8e7fe354e85a',
    'indices': '7565653b6de1aed06d7785ddf83c5839d55a15977bde3d7073f41334e02ecb12',
}
COUNTS = [52416,451,4736,6612,1471]
PALETTE = ['#EDEDE8FF','#99A8ADFF','#A6B3B6FF','#9EB8BAFF','#CEBAA8FF']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(test, message):
    if not test:
        raise ValueError(message)


def parse_xml(raw):
    require(b'<!DOCTYPE' not in raw and b'<!ENTITY' not in raw, 'Disallowed XML entity/doctype')
    return ET.fromstring(raw)


def topology(vertices, triangles):
    edges = defaultdict(list)
    volume_terms = []
    degenerate = 0
    for fi, (i,j,k) in enumerate(triangles):
        a,b,c = vertices[i],vertices[j],vertices[k]
        u = [b[n]-a[n] for n in range(3)]; v = [c[n]-a[n] for n in range(3)]
        cross = [u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        degenerate += math.sqrt(sum(x*x for x in cross)) <= 1e-9
        volume_terms.append((a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6)
        for p,q in ((i,j),(j,k),(k,i)):
            edges[min(p,q),max(p,q)].append((fi,1 if p<q else -1))
    require(not degenerate, 'Degenerate face')
    require(len(edges)==98529, 'Edge count mismatch')
    require(all(len(e)==2 and e[0][1]+e[1][1]==0 for e in edges.values()), 'Unpaired/inconsistently oriented edge')
    adjacency = [[] for _ in triangles]
    for ((i,_),(j,_)) in edges.values():
        adjacency[i].append(j); adjacency[j].append(i)
    seen = set(); components = 0
    for start in range(len(triangles)):
        if start in seen: continue
        components += 1; stack = [start]; seen.add(start)
        while stack:
            for n in adjacency[stack.pop()]:
                if n not in seen: seen.add(n); stack.append(n)
    require(components==1, 'Disconnected triangle components')
    volume = math.fsum(volume_terms)
    require(volume>0, 'Nonpositive signed volume')
    return {'edges':len(edges),'all_edges_two_opposite_incidences':True,'triangle_components':components,
            'degenerate_faces_at_double_area_le_1e-9':degenerate,'signed_volume_mm3':volume,
            'bounds_mm':[[min(v[a] for v in vertices) for a in range(3)],[max(v[a] for v in vertices) for a in range(3)]],
            'not_tested':'No new self-intersection, minimum-wall, slicer, supports or physical-print certification.'}


def validate(model, stl, blend, appearance, bindings):
    raw = {}
    for label,path in [('stl',stl),('blend',blend),('appearance',appearance),('bindings',bindings)]:
        raw[label] = Path(path).read_bytes()
        require(sha(raw[label]) == PINS[label], 'Pinned '+label+' hash mismatch')
    a = json.loads(raw['appearance'])
    with Path(bindings).open(newline='') as f: rows = list(csv.DictReader(f))
    require(len(rows)==65686, 'Binding length mismatch')
    require(all(int(r['original_stl_face_index'])==i and int(r['existing_blend_polygon_index'])==i for i,r in enumerate(rows)), 'Binding source order mismatch')
    stored = [int(r['existing_blend_material_index']) for r in rows]
    require(sha(bytes(stored))==PINS['indices'], 'Binding stream mismatch')
    require(len(raw['stl'])==84+65686*50 and struct.unpack_from('<I',raw['stl'],80)[0]==65686, 'STL record layout mismatch')
    original = b''.join(raw['stl'][96+50*i:132+50*i] for i in range(65686))
    require(sha(original)==PINS['xyz'], 'Original ordered geometry mismatch')
    with zipfile.ZipFile(model) as z:
        require(z.namelist()==EXPECTED_MEMBERS, 'Package member allowlist/order/uniqueness mismatch')
        require(not z.comment, 'Unexpected ZIP comment')
        for info in z.infolist():
            require(info.compress_type==zipfile.ZIP_STORED and info.date_time==(1980,1,1,0,0,0), 'Noncanonical ZIP settings')
            require(info.create_system==3 and info.external_attr==0o100644<<16 and not info.extra and not info.comment, 'Noncanonical ZIP metadata')
            require(info.flag_bits==0, 'Unexpected ZIP flags')
        require(z.testzip() is None, 'ZIP CRC mismatch')
        parts = {name:z.read(name) for name in EXPECTED_MEMBERS}
    rel = parse_xml(parts['_rels/.rels'])
    require(rel.tag==REL+'Relationships' and len(rel)==1, 'Relationship structure mismatch')
    require(rel[0].tag==REL+'Relationship' and rel[0].attrib=={'Id':'rel0','Type':'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel','Target':'/3D/3dmodel.model'}, 'Invalid package start relationship')
    ct = parse_xml(parts['[Content_Types].xml'])
    require(ct.tag==CT+'Types' and len(ct)==2 and all(n.tag==CT+'Default' for n in ct), 'Content types structure mismatch')
    require([n.attrib for n in ct]==[{'Extension':'rels','ContentType':'application/vnd.openxmlformats-package.relationships+xml'},{'Extension':'model','ContentType':'application/vnd.ms-package.3dmanufacturing-3dmodel+xml'}], 'Content type mapping mismatch')
    root = parse_xml(parts['3D/3dmodel.model'])
    require(root.tag==CORE+'model' and root.attrib=={'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'zh-TW'}, 'Model unit/attributes mismatch')
    require([n.tag for n in root]==[CORE+'metadata']*3+[CORE+'resources',CORE+'build'], 'Unexpected model children/hidden geometry')
    metadata = root[:3]
    require([n.get('name') for n in metadata]==['Title','Description','tb:appearance-original'], 'Metadata identity mismatch')
    require(metadata[2].attrib=={'name':'tb:appearance-original','preserve':'1'} and json.loads(metadata[2].text)==a, 'Exact appearance metadata mismatch')
    require(b'xmlns:tb="https://github.com/root50643/taiwan-buildings-3d/ns/interchange/1"' in parts['3D/3dmodel.model'], 'Custom metadata namespace missing')
    resources = root.find(CORE+'resources')
    require(len(resources)==2 and [n.tag for n in resources]==[CORE+'basematerials',CORE+'object'], 'Unexpected resources/hidden geometry')
    group, obj = resources
    require(group.attrib=={'id':'1'} and len(group)==5, 'Base-material group mismatch')
    for i, (m, expected) in enumerate(zip(group,a['materials'])):
        require(m.tag==CORE+'base' and len(m)==0, 'Base-material shape mismatch')
        require(m.attrib=={'name':expected['name'],'displaycolor':PALETTE[i]}, 'Material color/name mismatch')
        rgba = struct.unpack('<4f', bytes.fromhex(expected['rgba_le_f32_hex']))
        require([Decimal(x) for x in expected['rgba_exact_decimal']]==[Decimal.from_float(x) for x in rgba], 'Exact RGBA bytes/decimal mismatch')
        conv = [12.92*x if x<=.0031308 else 1.055*x**(1/2.4)-.055 for x in rgba[:3]]+[rgba[3]]
        require('#'+''.join('%02X'%int(math.floor(x*255+.5)) for x in conv)==PALETTE[i], 'Linear-to-sRGB encoding mismatch')
    require(obj.attrib=={'id':'2','type':'model','name':'CNU_Wang_Chen_Library','pid':'1','pindex':'0'} and len(obj)==1 and obj[0].tag==CORE+'mesh', 'Object/default fallback mismatch')
    mesh = obj[0]
    require(len(mesh)==2 and [n.tag for n in mesh]==[CORE+'vertices',CORE+'triangles'], 'Mesh structure mismatch')
    vn, tn = mesh
    require(len(vn)==32643 and len(tn)==65686, 'Mesh size mismatch')
    vertices, words = [], []
    for v in vn:
        require(v.tag==CORE+'vertex' and set(v.attrib)=={'x','y','z'} and not len(v), 'Vertex structure mismatch')
        decimals = [v.get(k) for k in ('x','y','z')]
        require(all(re.fullmatch(r'-?\d+(?:\.\d+)?', d) for d in decimals), 'Nonfinite/nondecimal/exponent coordinate')
        xyz = [float(d) for d in decimals]; word = struct.pack('<3f',*xyz)
        f32 = struct.unpack('<3f', word)
        require(all(Decimal(d)==Decimal.from_float(f) for d,f in zip(decimals,f32)), 'Coordinate is not exact float32 decimal')
        vertices.append(f32); words.append(word)
    require(len(set(words))==len(words), 'Duplicate exact-bit vertex')
    triangles, indices, expanded, referenced = [], [], bytearray(), set()
    for fi,t in enumerate(tn):
        require(t.tag==CORE+'triangle' and set(t.attrib)=={'v1','v2','v3','pid','p1','p2','p3'} and not len(t), 'Triangle structure mismatch')
        ids = [int(t.get(k)) for k in ('v1','v2','v3')]
        require(len(set(ids))==3 and all(0<=i<len(words) for i in ids), 'Illegal vertex indices')
        require(t.get('pid')=='1', 'Invalid property resource')
        props = [int(t.get(k)) for k in ('p1','p2','p3')]
        require(props[0]==props[1]==props[2] and 0<=props[0]<5, 'Invalid material index/gradient')
        require(props[0]==stored[fi], 'Same-index material assignment mismatch')
        actual = b''.join(words[i] for i in ids)
        require(actual==original[fi*36:(fi+1)*36], 'Same-index triangle/corner/winding mismatch')
        expanded.extend(actual); indices.append(props[0]); triangles.append(ids); referenced.update(ids)
    require(len(referenced)==len(vertices), 'Unreferenced vertices')
    require(sha(expanded)==PINS['xyz'] and sha(bytes(indices))==PINS['indices'], 'Expanded stream mismatch')
    require([indices.count(i) for i in range(5)]==COUNTS, 'Material count mismatch')
    build = root.find(CORE+'build')
    require(not build.attrib and len(build)==1 and build[0].tag==CORE+'item' and build[0].attrib=={'objectid':'2'} and not len(build[0]), 'Nonidentity/multiple build item')
    return {'status':'PASS','model_sha256':sha(Path(model).read_bytes()),'faces':65686,'vertices':32643,
            'same_index_same_corner_float32':True,'exact_nonexponent_decimal_coordinates':True,
            'material_counts':COUNTS,'display_rgba8':PALETTE,'exact_original_rgba_record':True,
            'original_blend_byte_unchanged':True,'ordered_xyz_f32_sha256':sha(expanded),'face_material_index_u8_sha256':sha(bytes(indices)),
            'package_member_hashes':{n:sha(parts[n]) for n in EXPECTED_MEMBERS},'geometry':topology(vertices,triangles),
            'scope':'Existing preview-contrast interchange only; source-corrected approved faces 0; standard sRGB8 display is quantized.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',type=Path,default=HERE/'cnu-wang-chen-library.3mf')
    p.add_argument('--model-dir',type=Path,default=HERE.parent)
    p.add_argument('--stl',type=Path);p.add_argument('--blend',type=Path)
    p.add_argument('--appearance',type=Path,default=HERE/'appearance-original.json')
    p.add_argument('--bindings',type=Path,default=HERE/'face-materials.csv')
    p.add_argument('--report',type=Path)
    a=p.parse_args();r=validate(a.model,a.stl or a.model_dir/'model.stl',a.blend or a.model_dir/'scene.blend',a.appearance,a.bindings)
    text=json.dumps(r,indent=2)+'\n'
    if a.report:a.report.write_text(text)
    print(text,end='')


if __name__=='__main__':main()
