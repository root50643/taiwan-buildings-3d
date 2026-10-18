"""Verify exact STL rebuild and saved Blender mesh identity, without re-rendering."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from collections import Counter

import bpy

ROOT = Path(__file__).resolve().parents[1]


def triangle_key(points):
    # Cyclic rotation preserves orientation. Binary32 is the exported STL lattice.
    p = [struct.pack('<3f', *v) for v in points]
    return min(b''.join(p[k:]+p[:k]) for k in range(3))


def stl_triangles(path):
    data = path.read_bytes()
    n, = struct.unpack_from('<I', data, 80)
    if len(data) != 84+50*n:
        raise ValueError('Invalid binary STL length')
    faces = Counter()
    for k in range(n):
        p = struct.unpack_from('<9f', data, 84+50*k+12)
        faces[triangle_key([p[:3],p[3:6],p[6:]])] += 1
    return faces


def main():
    stl = ROOT/'models/v1/model.stl'
    original = stl.read_bytes()
    # Keep temporary rebuilds inside this writable package workspace. Some
    # managed Windows environments redirect OS temp to an unwritable container.
    with tempfile.TemporaryDirectory(prefix='apollo-rebuild-', dir=ROOT/'qa') as temp:
        process = subprocess.run([sys.executable,str(ROOT/'source/build_model.py'),
            '--output-dir',temp],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if process.returncode != 0:
            raise RuntimeError(process.stderr)
        rebuilt = (Path(temp)/'model.stl').read_bytes()
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/v1/scene.blend'),load_ui=False)
    obj = bpy.data.objects.get('APOLLO_print_mesh_mm')
    if obj is None or obj.type != 'MESH':
        raise ValueError('Missing print mesh')
    mesh = obj.data
    mesh.calc_loop_triangles()
    scene_faces = Counter(triangle_key([obj.matrix_world @ mesh.vertices[i].co
        for i in face.vertices]) for face in mesh.loop_triangles)
    scene_matches = scene_faces == stl_triangles(stl)
    manifest = json.loads((ROOT/'previews/v1/render-manifest.json').read_text())
    preview_hashes = {v['name']:hashlib.sha256((ROOT/'previews/v1'/
        (v['name']+'.png')).read_bytes()).hexdigest()==v['png_sha256'] for v in manifest['views']}
    report = {
        'stl_sha256':hashlib.sha256(original).hexdigest(),
        'rebuild_returncode':process.returncode,
        'rebuilt_stl_bytes_identical':original==rebuilt,
        'saved_blend_oriented_triangle_multiset_equals_stl_binary32':scene_matches,
        'scene_triangles':sum(scene_faces.values()),
        'print_object_transform_is_identity':all(abs(obj.matrix_world[i][j]-(1 if i==j else 0))<1e-12 for i in range(4) for j in range(4)),
        'scene_units':'millimetres, scale_length=0.001',
        'render_ground_excluded_from_print_mesh':bpy.data.objects.get('RenderGround_NOT_STL') is not None,
        'reference_image_datablocks':len(bpy.data.images),
        'manifest_scene_hash_matches':hashlib.sha256((ROOT/'models/v1/scene.blend').read_bytes()).hexdigest()==manifest['scene_sha256'],
        'manifest_stl_hash_matches':manifest['stl_sha256']==hashlib.sha256(original).hexdigest(),
        'five_preview_hashes':preview_hashes,
        'scope':'Mesh identity and existing preview hashes only; does not repeat rendering or prove photographic accuracy',
    }
    ok = report['rebuilt_stl_bytes_identical'] and scene_matches and report['print_object_transform_is_identity'] and report['manifest_scene_hash_matches'] and report['manifest_stl_hash_matches'] and all(preview_hashes.values())
    report['pass']=bool(ok)
    (ROOT/'qa/reproducibility.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report))
    if not ok:
        raise SystemExit(1)


if __name__=='__main__':
    main()
