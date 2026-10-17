#!/usr/bin/env python3
"""Exact pairwise contacts on unmodified binary-STL float32 triangles.

No repair, weld, coordinate rounding, epsilon, tiny-face filtering, or adjacency
pair exclusion. Broad phase uses closed AABBs on an exactly reversible dyadic
integer lattice. Narrow phase uses Python integers and fractions.Fraction only.
This check addresses triangle intersections, not solid validity or printability.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import gzip
import heapq
import json
from pathlib import Path
import platform
import struct
import sys
import time


class QAError(RuntimeError):
    pass


def require(condition, message):
    # Deliberately not an assert: active under python -O.
    if not condition:
        raise QAError(message)


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def orient2(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def interpolate(a, b, t):
    return tuple(x + t * (y - x) for x, y in zip(a, b))


def ratio_text(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f'{value.numerator}/{value.denominator}'


def load_original_stl(path):
    raw = Path(path).read_bytes()
    require(len(raw) >= 84, 'Binary STL is shorter than its 84-byte header')
    count = struct.unpack_from('<I', raw, 80)[0]
    require(count > 0, 'Binary STL contains no triangles')
    require(len(raw) == 84 + 50 * count, 'Binary STL count/length mismatch')
    triangles = []
    import math
    for i in range(count):
        values = struct.unpack_from('<12fH', raw, 84 + i * 50)
        require(all(math.isfinite(x) for x in values[:12]),
                f'Nonfinite original STL value in face {i}')
        triangles.append(tuple(tuple(values[3 + 3 * j:6 + 3 * j]) for j in range(3)))
    return raw, triangles


def integer_lattice(triangles):
    # Every finite binary32 coordinate is a dyadic rational. A common power-of-two
    # denominator gives lossless integer predicates, even for subnormal values.
    denominator = max(x.as_integer_ratio()[1] for t in triangles for p in t for x in p)
    require(denominator > 0 and denominator & (denominator - 1) == 0,
            'Coordinate denominator is not dyadic')
    integer_triangles = []
    checked = 0
    for t in triangles:
        points = []
        for p in t:
            q = []
            for x in p:
                numerator, local_denominator = x.as_integer_ratio()
                require(denominator % local_denominator == 0, 'Incompatible coordinate denominator')
                integer = numerator * (denominator // local_denominator)
                require(Fraction(integer, denominator) == Fraction.from_float(x),
                        'Original-coordinate exact round-trip failed')
                q.append(integer)
                checked += 1
            points.append(tuple(q))
        integer_triangles.append(tuple(points))
    return integer_triangles, denominator, checked


class Triangle:
    def __init__(self, points):
        self.p = points
        self.n = cross(sub(points[1], points[0]), sub(points[2], points[0]))
        self.c = dot(self.n, points[0])
        self.lo = tuple(min(p[a] for p in points) for a in range(3))
        self.hi = tuple(max(p[a] for p in points) for a in range(3))


def choose_sweep_axis(triangles):
    costs = []
    orders = []
    for axis in range(3):
        order = sorted(range(len(triangles)), key=lambda i: (triangles[i].lo[axis], i))
        active_max = []
        cost = 0
        for i in order:
            low = triangles[i].lo[axis]
            while active_max and active_max[0] < low:
                heapq.heappop(active_max)
            cost += len(active_max)
            heapq.heappush(active_max, triangles[i].hi[axis])
        costs.append(cost)
        orders.append(order)
    axis = min(range(3), key=lambda a: costs[a])
    return axis, orders[axis], costs


def bbox_candidates(triangles, axis, order):
    # Sweep maintains precisely those prior closed AABBs with max >= current min.
    # Test the two other integer intervals with inclusive comparisons. Thus every
    # intersecting closed AABB pair occurs exactly once, including shared points.
    other = [a for a in range(3) if a != axis]
    u, v = other
    active = {}
    expirations = []
    for j in order:
        b = triangles[j]
        while expirations and expirations[0][0] < b.lo[axis]:
            _, old = heapq.heappop(expirations)
            del active[old]
        for i, a in active.items():
            if a.lo[u] <= b.hi[u] and b.lo[u] <= a.hi[u] and a.lo[v] <= b.hi[v] and b.lo[v] <= a.hi[v]:
                yield (i, j) if i < j else (j, i)
        active[j] = b
        heapq.heappush(expirations, (b.hi[axis], j))


def clean_polygon(points):
    result = []
    for p in points:
        if not result or p != result[-1]:
            result.append(p)
    if len(result) > 1 and result[0] == result[-1]:
        result.pop()
    return result


def coplanar_polygon(a, b, drop):
    axes = [i for i in range(3) if i != drop]
    project = lambda p: (p[axes[0]], p[axes[1]])
    polygon = [project(p) for p in a.p]
    clipping = [project(p) for p in b.p]
    orientation = orient2(*clipping)
    require(orientation != 0, 'Nondegenerate triangle collapsed in coplanar projection')
    sign = 1 if orientation > 0 else -1
    for k in range(3):
        if not polygon:
            break
        edge_start, edge_end = clipping[k], clipping[(k + 1) % 3]
        previous = polygon[-1]
        d_previous = sign * orient2(edge_start, edge_end, previous)
        output = []
        for current in polygon:
            d_current = sign * orient2(edge_start, edge_end, current)
            if (d_current >= 0) != (d_previous >= 0):
                t = Fraction(d_previous, d_previous - d_current)
                output.append(interpolate(previous, current, t))
            if d_current >= 0:
                output.append(current)
            previous, d_previous = current, d_current
        polygon = clean_polygon(output)
    return polygon, axes


def plane_slice(triangle, signed_distances):
    points = []
    for i, d in enumerate(signed_distances):
        if d == 0:
            points.append(triangle.p[i])
    for i in range(3):
        j = (i + 1) % 3
        di, dj = signed_distances[i], signed_distances[j]
        if (di < 0 < dj) or (dj < 0 < di):
            points.append(interpolate(triangle.p[i], triangle.p[j], Fraction(di, di - dj)))
    points = list(dict.fromkeys(points))
    require(0 < len(points) <= 2, f'Unexpected noncoplanar plane slice: {len(points)} points')
    return points


def compare_contact(shared, points, kind):
    # All narrow-phase geometry has already been computed. Adjacency alone never
    # skips a pair, including pairs with one or two identical original vertices.
    endpoints = sorted(set(points))
    require(1 <= len(endpoints) <= 2, 'Invalid zero/one-dimensional intersection')
    if len(shared) == 1 and endpoints == shared:
        return 'allowed_shared_vertex', {'dimension': 0, 'vertices_integer_lattice': endpoints}
    if len(shared) == 2 and endpoints == shared:
        return 'allowed_shared_edge', {'dimension': 1, 'vertices_integer_lattice': endpoints}
    if shared:
        reason = f'{kind}_intersection_exceeds_shared_' + ('vertex' if len(shared) == 1 else 'edge')
    else:
        reason = f'{kind}_nonshared_' + ('point_contact' if len(endpoints) == 1 else 'segment_intersection')
    return reason, {'dimension': len(endpoints) - 1, 'vertices_integer_lattice': endpoints}


def classify_pair(a, b):
    da = [dot(b.n, p) - b.c for p in a.p]
    if min(da) > 0 or max(da) < 0:
        return 'disjoint_plane_separated', None
    db = [dot(a.n, p) - a.c for p in b.p]
    if min(db) > 0 or max(db) < 0:
        return 'disjoint_plane_separated', None
    shared = sorted(set(a.p).intersection(b.p))
    direction = cross(a.n, b.n)
    if direction == (0, 0, 0):
        require(all(d == 0 for d in da) and all(d == 0 for d in db),
                'Parallel-plane separation predicate inconsistency')
        drop = max(range(3), key=lambda k: abs(a.n[k]))
        polygon, axes = coplanar_polygon(a, b, drop)
        if not polygon:
            return 'disjoint_coplanar', None
        twice_area = abs(sum(polygon[i][0] * polygon[(i + 1) % len(polygon)][1]
                             - polygon[(i + 1) % len(polygon)][0] * polygon[i][1]
                             for i in range(len(polygon))))
        lifted = []
        for p in polygon:
            q = [None, None, None]
            q[axes[0]], q[axes[1]] = p
            q[drop] = Fraction(a.c - a.n[axes[0]] * p[0] - a.n[axes[1]] * p[1], a.n[drop])
            lifted.append(tuple(q))
        if twice_area > 0:
            return 'coplanar_positive_area_overlap', {
                'dimension': 2, 'vertices_integer_lattice': lifted,
                'projection_dropped_axis': drop,
                'twice_projected_area_integer_lattice': twice_area}
        endpoints = sorted(set(lifted))
        endpoints = [endpoints[0]] if len(endpoints) == 1 else [endpoints[0], endpoints[-1]]
        return compare_contact(shared, endpoints, 'coplanar')
    slice_a, slice_b = plane_slice(a, da), plane_slice(b, db)
    axis = max(range(3), key=lambda k: abs(direction[k]))
    lower = max(min(p[axis] for p in slice_a), min(p[axis] for p in slice_b))
    upper = min(max(p[axis] for p in slice_a), max(p[axis] for p in slice_b))
    if lower > upper:
        return 'disjoint_noncoplanar', None
    def point_at(position):
        if len(slice_a) == 1:
            require(slice_a[0][axis] == position, 'Singleton line coordinate mismatch')
            return slice_a[0]
        start, end = slice_a
        require(end[axis] != start[axis], 'Nonzero intersection direction collapsed')
        return interpolate(start, end, Fraction(position - start[axis], end[axis] - start[axis]))
    points = [point_at(lower)] if lower == upper else [point_at(lower), point_at(upper)]
    return compare_contact(shared, points, 'noncoplanar')


def world_geometry(geometry, denominator):
    output = {k: v for k, v in geometry.items() if k != 'vertices_integer_lattice'}
    points = [[Fraction(x, denominator) for x in p] for p in geometry['vertices_integer_lattice']]
    output['vertices_exact_original_units'] = [[ratio_text(x) for x in p] for p in points]
    output['vertices_approx_original_units'] = [[float(x) for x in p] for p in points]
    if 'twice_projected_area_integer_lattice' in output:
        output['twice_projected_area_original_units_squared_exact'] = ratio_text(
            Fraction(output.pop('twice_projected_area_integer_lattice'), denominator * denominator))
    return output


SCOPE = [
    'Checks every unordered original-triangle pair whose closed exact AABBs overlap.',
    'No repair, welding, coordinate rounding, dropped faces, epsilon, tiny-face filter, or adjacency exclusions.',
    'Allows only empty intersection, exactly one shared original vertex, or exactly the full edge between two shared original vertices.',
    'Rejects coplanar positive-area overlap, crossing segments, nonshared point/segment contacts, and intersections exceeding shared vertices or edges.',
    'Binary STL stores no connectivity: exact coordinate equality defines a geometrically shared vertex; signed zero has the same geometric value.',
    'This geometric pair check does not establish manifoldness, orientation, watertightness, minimum wall thickness, connectedness, mechanical strength, or slicer/printer suitability.',
    'No global printability guarantee; combine with separate topology, dimensional, material, and slicer checks.',
]


def check_file(stl, expected_hash=None, progress=False, contacts_output=None):
    started = time.time()
    raw, original = load_original_stl(stl)
    digest = hashlib.sha256(raw).hexdigest()
    if expected_hash is not None:
        require(digest == expected_hash, f'STL SHA256 mismatch: {digest}')
    points, denominator, checked = integer_lattice(original)
    triangles = [Triangle(p) for p in points]
    report = {
        'checker': 'exact_original_triangle_intersections_v1',
        'passed': False, 'strict_passed': False, 'completed': False,
        'stl_path': Path(stl).name, 'stl_sha256': digest,
        'original_face_count': len(original), 'face_index_base': 0,
        'total_unordered_original_face_pairs': len(original) * (len(original) - 1) // 2,
        'tools': {'python': sys.version, 'platform': platform.platform(),
                  'arithmetic': 'unbounded Python int and fractions.Fraction',
                  'external_geometry_dependencies': [],
                  'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  'optimization_level': sys.flags.optimize},
        'lattice': {'denominator': str(denominator),
                    'denominator_power_of_two': denominator.bit_length() - 1,
                    'exact_coordinate_round_trips_checked': checked,
                    'all_original_coordinates_round_trip_exactly': True,
                    'maximum_coordinate_integer_bits': max(abs(x).bit_length() for t in points for p in t for x in p)},
        'scope_and_limitations': SCOPE,
        'degenerate_original_faces': [], 'bad_pairs': [],
    }
    report['degenerate_original_faces'] = [
        {'face_index': i, 'original_vertices': original[i]}
        for i, t in enumerate(triangles) if t.n == (0, 0, 0)]
    if report['degenerate_original_faces']:
        report['failure_reason'] = 'Exact zero-area original triangles; pair classification is not attempted for degenerate input.'
        report['elapsed_seconds'] = time.time() - started
        return report
    axis, order, costs = choose_sweep_axis(triangles)
    report['broad_phase'] = {'method': 'exact integer closed-AABB sweep, each unordered pair once',
                             'sweep_axis': axis, 'axis_active_pair_costs': costs,
                             'all_bbox_overlapping_pairs_completed': False}
    counters = Counter()
    candidates = 0
    candidate_digest = hashlib.sha256()
    contacts = 0
    handle = None
    raw_handle = None
    if contacts_output is not None:
        Path(contacts_output).parent.mkdir(parents=True, exist_ok=True)
        raw_handle = Path(contacts_output).open('wb')
        handle = gzip.GzipFile(filename='', fileobj=raw_handle, mode='wb', mtime=0)
    try:
        for i, j in bbox_candidates(triangles, axis, order):
            candidates += 1
            candidate_digest.update(struct.pack('<II', i, j))
            reason, geometry = classify_pair(triangles[i], triangles[j])
            counters[reason] += 1
            if geometry is not None:
                contacts += 1
                entry = {
                    'face_indices': [i, j], 'reason': reason,
                    'shared_original_vertex_count': len(set(original[i]).intersection(original[j])),
                    'intersection': world_geometry(geometry, denominator)}
                if handle is not None:
                    handle.write((json.dumps(entry, separators=(',', ':'), allow_nan=False) + '\n').encode())
                if not reason.startswith('allowed_'):
                    report['bad_pairs'].append(dict(entry,
                        original_vertices=[original[i], original[j]],
                        shared_original_vertices=[list(p) for p in sorted(set(original[i]).intersection(original[j]))]))
            if progress and candidates % 50000 == 0:
                print(f'{candidates} exact candidates; {len(report["bad_pairs"])} bad pairs', file=sys.stderr, flush=True)
    finally:
        if handle is not None:
            handle.close()
        if raw_handle is not None:
            raw_handle.close()
    report['actual_intersection_pair_count'] = contacts
    if contacts_output is not None:
        report['all_actual_intersections'] = {
            'format': 'gzip JSON Lines; one exact intersection per line',
            'path': Path(contacts_output).name,
            'sha256': hashlib.sha256(Path(contacts_output).read_bytes()).hexdigest(),
            'record_count': contacts}
    report['broad_phase'].update({'candidate_pairs_checked': candidates,
                                  'candidate_sequence_sha256': candidate_digest.hexdigest(),
                                  'all_bbox_overlapping_pairs_completed': True})
    report['classification_counts'] = dict(sorted(counters.items()))
    report['bad_pair_count'] = len(report['bad_pairs'])
    final_stl_digest = hashlib.sha256(Path(stl).read_bytes()).hexdigest()
    require(final_stl_digest == digest, 'Input STL changed during verification')
    report['stl_sha256_after_check'] = final_stl_digest
    report['input_unchanged_during_check'] = True
    report['completed'] = True
    report['passed'] = not report['bad_pairs']
    report['strict_passed'] = report['passed']
    report['elapsed_seconds'] = time.time() - started
    return report


def public_error_text(message, paths):
    replacements = {str(Path(path).resolve()): Path(path).name for path in paths}
    replacements[str(Path(__file__).resolve().parent)] = '[checker-dir]'
    replacements[str(Path.cwd())] = '[workdir]'
    for private, public in sorted(replacements.items(), key=lambda item: -len(item[0])):
        message = message.replace(private, public)
    return message


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stl', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--expected-sha256')
    parser.add_argument('--progress', action='store_true')
    args = parser.parse_args()
    exit_code = 2
    try:
        report = check_file(args.stl, args.expected_sha256, args.progress, str(args.out) + '.contacts.jsonl.gz')
        exit_code = 0 if report['passed'] else 1
    except Exception as error:
        source = Path(args.stl)
        report = {'checker': 'exact_original_triangle_intersections_v1',
                  'passed': False, 'strict_passed': False, 'completed': False,
                  'error_type': type(error).__name__, 'error': public_error_text(str(error), [args.stl, args.out]),
                  'stl_sha256': hashlib.sha256(source.read_bytes()).hexdigest() if source.is_file() else None,
                  'checker_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  'scope_and_limitations': SCOPE}
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'passed': report['passed'], 'completed': report['completed'],
                      'bad_pair_count': report.get('bad_pair_count'),
                      'report': output.name, 'error': report.get('error')}))
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
