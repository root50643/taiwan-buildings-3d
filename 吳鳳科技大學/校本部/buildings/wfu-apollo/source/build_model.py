"""Original parametric APOLLO exterior. Units: mm. No reference imagery needed.

Run from any directory: python source/build_model.py [--output-dir PATH]
Requires numpy, trimesh and manifold3d; see requirements.txt.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import trimesh
import manifold3d
from importlib.metadata import version

ROOT = Path(__file__).resolve().parents[1]


def box(extents, center):
    mesh = trimesh.creation.box(extents)
    mesh.apply_translation(center)
    return mesh


def prism_x(x0, x1, yz):
    """Extrude a convex YZ polygon along X and orient faces outward."""
    n = len(yz)
    vertices = [[x, y, z] for x in (x0, x1) for y, z in yz]
    faces = []
    for k in range(1, n-1):
        faces.extend([[0, k+1, k], [n, n+k, n+k+1]])
    for k in range(n):
        j = (k+1) % n
        faces.extend([[k, j, n+j], [k, n+j, n+k]])
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    mesh.fix_normals()
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def recess(xc, width, bottom, top, depth, wall_y):
    # A 45 degree top chamfer bounds the recess's overhead projection.
    yz = [(wall_y-2, bottom), (wall_y+depth, bottom),
          (wall_y+depth, top-depth), (wall_y, top), (wall_y-2, top)]
    return prism_x(xc-width/2, xc+width/2, yz)


def build(params):
    m = params['model_mm']
    length, width = m['body_length'], m['body_width']
    base_z, eave = m['base_thickness'], m['body_eave_z']
    base = box([m['base_length'], m['base_width'], base_z], [0, 0, base_z/2])
    wall = box([length, width, eave-base_z], [0, 0, (eave+base_z)/2])
    half = width/2
    projection = m['eave_projection']
    roof = prism_x(-length/2, length/2, [
        (-half, eave-m['eave_bevel_rise']),
        (half, eave-m['eave_bevel_rise']),
        (half+projection, eave),
        (0, m['ridge_z']),
        (-half-projection, eave),
    ])
    solid = trimesh.boolean.union([base, wall, roof], engine='manifold')
    scale = length / params['plan_metres']['length']
    cutters = []
    for k in range(10):
        xc = -length/2 + (3+6*k)*scale
        cutters.append(recess(xc, 13.5, 24.0, 28.2, m['window_recess'], -half))
    for xc in [-length/2+3*scale, -length/2+21*scale]:
        cutters.append(recess(xc, 12.5, 7.5, 16.5, m['window_recess'], -half))
    cutters.append(recess(-length/2+12*scale, 17.0, base_z, 18.0, m['door_recess'], -half))
    model = trimesh.boolean.difference([solid]+cutters, engine='manifold')
    model.remove_unreferenced_vertices()
    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, default=ROOT/'models/v1')
    args = parser.parse_args()
    params = json.loads((ROOT/'parameters.json').read_text(encoding='utf8'))
    mesh = build(params)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = args.output_dir/'model.stl'
    path.write_bytes(trimesh.exchange.stl.export_stl(mesh))
    # Reopen the exact exported binary32 mesh, rather than certifying in-memory CSG.
    exported = trimesh.load_mesh(path, process=True)
    report = {
        'stl_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'parameters_sha256':hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest(),
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'vertices':len(exported.vertices), 'triangles':len(exported.faces),
        'bounds_mm':exported.bounds.tolist(), 'extents_mm':exported.extents.tolist(),
        'watertight':bool(exported.is_watertight),
        'winding_consistent':bool(exported.is_winding_consistent),
        'positive_volume_mm3':float(exported.volume),
        'components':len(exported.split(only_watertight=False)),
        'python':platform.python_version(),
        'packages':{n:version(n) for n in ['numpy','trimesh','manifold3d']},
        'repair_after_export':'none; process=True only merges identical STL triangle vertices',
    }
    (args.output_dir/'build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report))
    if not (report['watertight'] and report['winding_consistent'] and report['components']==1 and report['positive_volume_mm3']>0):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
