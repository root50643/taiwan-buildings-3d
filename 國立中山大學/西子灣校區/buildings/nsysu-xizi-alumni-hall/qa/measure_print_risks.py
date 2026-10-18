"""Trace print risks to the unchanged binary32 STL and generic failed/pass report.

This supplement never changes a gate, STL or threshold.  It quantifies original
downward-facing facets, flat underside patches and flagged sampled layers.  It
does not simulate a bridge, slicer extrusion or a physical print.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import struct


def sub(a, b): return tuple(x-y for x, y in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def read_stl(path):
    data = path.read_bytes()
    n, = struct.unpack_from('<I', data, 80)
    if len(data) != 84 + 50*n:
        raise ValueError('Requires a binary STL with consistent record count')
    vertices, faces, index = [], [], {}
    for face_id in range(n):
        p = struct.unpack_from('<9f', data, 84+50*face_id+12)
        face = []
        for k in range(3):
            q = tuple(p[3*k:3*k+3])
            if not all(math.isfinite(x) for x in q):
                raise ValueError('Nonfinite STL coordinates')
            if q not in index:
                index[q] = len(vertices)
                vertices.append(q)
            face.append(index[q])
        faces.append(tuple(face))
    return data, vertices, faces


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mesh', type=Path)
    ap.add_argument('report', type=Path)
    ap.add_argument('--json', type=Path, required=True)
    args = ap.parse_args()
    if args.json.resolve() in (args.mesh.resolve(), args.report.resolve()):
        ap.error('Output must differ from all inputs')
    data, vertices, faces = read_stl(args.mesh)
    digest = hashlib.sha256(data).hexdigest()
    source = json.loads(args.report.read_text(encoding='utf-8'))
    if source.get('sha256') != digest:
        raise ValueError('Generic report SHA-256 differs from STL')
    bottom = min(p[2] for p in vertices)
    rational = [tuple(F(x) for x in p) for p in vertices]
    down, horizontal = [], []
    for face_id, face in enumerate(faces):
        pts = [vertices[i] for i in face]
        a, b, c = (rational[i] for i in face)
        n = cross(sub(b, a), sub(c, a))
        if n[2] >= 0 or all(p[2] == bottom for p in pts):
            continue
        xy2 = n[0]**2 + n[1]**2
        ratio = float(-n[2]) / math.sqrt(float(xy2)) if xy2 else math.inf
        dz = max(p[2] for p in (a, b, c)) - min(p[2] for p in (a, b, c))
        row = {
            'stl_record_face_index': face_id,
            'vertices_mm': pts,
            'unnormalized_normal_exact': [str(x) for x in n],
            'area_mm2': math.sqrt(sum(float(x*x) for x in n))/2,
            'xy_projected_area_mm2': float(-n[2])/2,
            'angle_from_vertical_deg': math.degrees(math.atan(ratio)),
            'exact_within_45_degrees': n[2]**2 <= xy2,
            'horizontal_underside': xy2 == 0,
            'z_span_mm_exact': str(dz),
        }
        # For an axis-aligned sloping plane, the outward run over this facet's
        # full Z span is rational.  This is a plane-slope diagnostic, not the
        # unsupported area of an extrusion path.
        if (n[0] == 0) != (n[1] == 0):
            run = abs(n[2]) / abs(n[1] if n[0] == 0 else n[0]) * dz
            row['axis_aligned_slope_run_over_full_z_span_mm_exact'] = str(run)
            row['axis_aligned_slope_outward_excess_over_45_mm_exact'] = str(run-dz)
            row['axis_aligned_slope_outward_excess_over_45_mm'] = float(run-dz)
        down.append(row)
        if xy2 == 0:
            horizontal.append(face_id)
    edge_faces = defaultdict(list)
    for fi in horizontal:
        face = faces[fi]
        for a, b in zip(face, face[1:] + face[:1]):
            edge_faces[tuple(sorted((a, b)))].append(fi)
    adjacency = defaultdict(set)
    for uses in edge_faces.values():
        for fi in uses:
            adjacency[fi].update(fj for fj in uses if fj != fi)
    remaining = set(horizontal)
    by_index = {r['stl_record_face_index']: r for r in down}
    patches = []
    while remaining:
        stack, member = [min(remaining)], []
        while stack:
            fi = stack.pop()
            if fi not in remaining:
                continue
            remaining.remove(fi)
            member.append(fi)
            stack.extend(adjacency[fi])
        pts = [vertices[vi] for fi in member for vi in faces[fi]]
        bounds = [[min(p[k] for p in pts), max(p[k] for p in pts)] for k in range(3)]
        patches.append({
            'face_indices': sorted(member),
            'area_mm2': sum(by_index[fi]['area_mm2'] for fi in member),
            'bounds_by_axis_mm': bounds,
            'xy_bounding_box_mm': [bounds[k][1]-bounds[k][0] for k in (0, 1)],
            'interpretation': 'Connected horizontal underside patch. Bounding box is not a verified unsupported bridge span; consult actual layer/support evidence.',
        })
    sections = source['sections']
    flagged = [r for r in sections['rows'] if r.get('outside_support_envelope_area_mm2', 0) > sections['support_area_reporting_tolerance_mm2']]
    result = {
        'scope': 'Original binary32 facet and existing sampled-layer risk quantification; no geometry repair or gate override.',
        'stl_sha256': digest,
        'generic_report_sha256': hashlib.sha256(args.report.read_bytes()).hexdigest(),
        'diagnostic_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'generic_report_passes_bounded_geometry_screen': source['passes_bounded_geometry_screen'],
        'support_threshold_mm2_unchanged': sections['support_area_reporting_tolerance_mm2'],
        'support_angle_from_vertical_deg_unchanged': sections['support_angle_from_vertical_deg'],
        'first_sampled_layer_assumed_plate_supported': sections['first_section_treated_as_build_plate_supported'],
        'actual_bottom_z_mm': bottom,
        'nonbase_downward_face_count': len(down),
        'nonbase_horizontal_underside_face_count': len(horizontal),
        'exact_over_45_degree_face_indices': [r['stl_record_face_index'] for r in down if not r['exact_within_45_degrees']],
        'maximum_downward_facet_angle_from_vertical_deg': max((r['angle_from_vertical_deg'] for r in down), default=None),
        'connected_horizontal_underside_patches': patches,
        'support_flagged_layer_count': len(flagged),
        'support_flagged_layers': flagged,
        'nonbase_downward_facets': down,
        'thin_feature_interpretation': 'Per-component 0.8 mm erosion is retained in generic report; surviving cores do not prove every-point minimum XY wall or Z relief thickness.',
        'remaining_print_checks': 'No target-printer slicing, bridge path, support removal, bed adhesion, material shrinkage, G-code inspection or physical print performed.',
        'does_not_override_generic_report_exit_status': True,
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('nonbase_downward_facets', 'support_flagged_layers')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
