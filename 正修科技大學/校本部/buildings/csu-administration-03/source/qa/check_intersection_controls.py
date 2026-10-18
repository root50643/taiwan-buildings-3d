#!/usr/bin/env python3
"""Truth-labelled geometric controls and optimized-interpreter subprocess checks."""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import random
import struct
import subprocess
import sys

import check_original_intersections as checker


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def write_stl(path, triangles):
    data = bytearray(b'Exact intersection QA control'.ljust(80, b'\0'))
    data += struct.pack('<I', len(triangles))
    for t in triangles:
        values = tuple(float(x) for p in t for x in p)
        packed = struct.pack('<12fH', 0, 0, 0, *values, 0)
        require(struct.unpack('<12fH', packed)[3:12] == values,
                'Control would silently round during float32 serialization')
        data += packed
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def affine(p):
    x, y, z = p
    # Determinant 3, so an invertible oblique affine transform.
    return (x + 2 * y + 3, y + z - 5, x + z + 7)


def tiny_affine(p):
    x, y, z = p
    # Reversible permutation and exact power-of-two scale, without translation.
    return (2 * z, x / 2, y)


def map_triangles(triangles, transform):
    return tuple(tuple(transform(p) for p in t) for t in triangles)


def base_cases():
    a = ((0, 0, 0), (2, 0, 0), (0, 2, 0))
    s = 2.0 ** -120
    t = 2.0 ** -149
    cases = [
        ('disjoint_coplanar_bbox_overlap', (a, ((2, 2, 0), (1.25, 2, 0), (2, 1.25, 0))), True, 'disjoint', False),
        ('disjoint_noncoplanar_bbox_overlap', (a, ((1.5, 1.5, -1), (1.5, 1.5, 1), (1.5, 2, 0))), True, 'disjoint', False),
        ('shared_vertex_only', (a, ((0, 0, 0), (-1, 0, 1), (0, -1, 1))), True, 'allowed_shared_vertex', False),
        ('coplanar_shared_vertex_only', (a, ((0, 0, 0), (-1, 0, 0), (0, -1, 0))), True, 'allowed_shared_vertex', False),
        ('coplanar_shared_edge_only', (a, ((0, 0, 0), (2, 0, 0), (1, -1, 0))), True, 'allowed_shared_edge', False),
        ('noncoplanar_shared_edge_only', (a, ((0, 0, 0), (2, 0, 0), (1, 0, 1))), True, 'allowed_shared_edge', False),
        ('noncoplanar_crossing', (a, ((0.5, -0.5, -1), (0.5, 1.5, 1), (0.5, 1.5, -1))), False, 'noncoplanar_nonshared_segment_intersection', False),
        ('coplanar_positive_overlap', (a, ((0.25, 0.25, 0), (1.25, 0.25, 0), (0.25, 1.25, 0))), False, 'coplanar_positive_area_overlap', False),
        ('shared_vertex_but_crosses', (a, ((0, 0, 0), (1, 1, -1), (1, 1, 1))), False, 'noncoplanar_intersection_exceeds_shared_vertex', False),
        ('shared_edge_but_overlaps', (a, ((0, 0, 0), (2, 0, 0), (0.5, 0.5, 0))), False, 'coplanar_positive_area_overlap', False),
        ('shared_vertex_but_area_overlap', (a, ((0, 0, 0), (1, 0, 0), (0, 1, 0))), False, 'coplanar_positive_area_overlap', False),
        ('nonshared_point_on_interior', (a, ((0.5, 0.5, 0), (0.5, 0.5, 1), (1, 0.5, 1))), False, 'noncoplanar_nonshared_point_contact', False),
        ('coplanar_vertex_T_junction', (a, ((1, 0, 0), (1, -1, 0), (2, -1, 0))), False, 'coplanar_nonshared_point_contact', False),
        ('coplanar_partial_edge_contact', (a, ((0.5, 0, 0), (1.5, 0, 0), (1, -1, 0))), False, 'coplanar_nonshared_segment_intersection', False),
        ('duplicate_reversed_face', (a, tuple(reversed(a))), False, 'coplanar_positive_area_overlap', False),
        ('minimum_subnormal_plane_gap', (a, ((0, 0, t), (2, 0, t), (0, 2, t))), True, 'disjoint', True),
        ('extremely_skinny_area_overlap', (((0, 0, 0), (1, 0, 0), (0, s, 0)), ((0, 0, 0), (1, 0, 0), (0, s / 2, 0))), False, 'coplanar_positive_area_overlap', True),
        ('tiny_noncoplanar_crossing', (((0, 0, 0), (s, 0, 0), (0, s, 0)), ((s / 4, s / 4, -s), (s / 4, s / 4, s), (3 * s / 4, s / 4, 0))), False, 'noncoplanar_nonshared_segment_intersection', True),
        ('tiny_coplanar_near_disjoint', (((0, 0, 0), (4 * s, 0, 0), (0, 4 * s, 0)), ((2 * s, 3 * s, 0), (3 * s, 2 * s, 0), (4 * s, 4 * s, 0))), True, 'disjoint', True),
    ]
    return cases


def box():
    vertices = [(x, y, z) for z in (0, 1) for y in (0, 1) for x in (0, 1)]
    faces = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5),
             (0, 4, 5), (0, 5, 1), (2, 3, 7), (2, 7, 6),
             (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)]
    return tuple(tuple(vertices[i] for i in f) for f in faces)


def in_process_tests(cases):
    results = []
    permutations = list(itertools.permutations(range(3)))
    for name, original, expected_pass, expected_reason, tiny in cases:
        for transform_name, transform in [('identity', lambda p: p), ('oblique_or_tiny_reversible', tiny_affine if tiny else affine)]:
            transformed = map_triangles(original, transform)
            float_triangles = tuple(tuple(tuple(float(x) for x in p) for p in t) for t in transformed)
            # This verifier also runs on the exact dyadic values used by STL I/O.
            for triangle in float_triangles:
                for p in triangle:
                    require(struct.unpack('<3f', struct.pack('<3f', *p)) == p, f'{name}: transform rounded')
            integers, denominator, _ = checker.integer_lattice(float_triangles)
            for pa, pb in itertools.product(permutations, repeat=2):
                a = checker.Triangle(tuple(integers[0][k] for k in pa))
                b = checker.Triangle(tuple(integers[1][k] for k in pb))
                for swapped in (False, True):
                    reason, geometry = checker.classify_pair(b, a) if swapped else checker.classify_pair(a, b)
                    got_pass = reason.startswith(('disjoint_', 'allowed_'))
                    require(got_pass == expected_pass, f'{name}: wrong pass, {reason}')
                    require(reason.startswith(expected_reason), f'{name}: expected {expected_reason}, got {reason}')
                    require((geometry is not None) == (not reason.startswith('disjoint_')), f'{name}: missing intersection')
                    if geometry:
                        # Exact rational witnesses must lie on both planes.
                        for p in geometry['vertices_integer_lattice']:
                            require(checker.dot(a.n, p) == a.c and checker.dot(b.n, p) == b.c,
                                    f'{name}: witness does not lie on both planes')
                    results.append({'case': name, 'transform': transform_name,
                                    'vertex_orders': [pa, pb], 'pair_swapped': swapped,
                                    'expected_pass': expected_pass, 'actual_reason': reason})
    return results


def broad_phase_tests():
    random.seed(184337)
    results = []
    for trial in range(12):
        triangles = [checker.Triangle(tuple(tuple(random.randrange(-10, 11) for _ in range(3)) for _ in range(3))) for _ in range(35)]
        brute = {(i, j) for i in range(len(triangles)) for j in range(i + 1, len(triangles))
                 if all(triangles[i].lo[k] <= triangles[j].hi[k] and triangles[j].lo[k] <= triangles[i].hi[k] for k in range(3))}
        for axis in range(3):
            order = sorted(range(len(triangles)), key=lambda i: (triangles[i].lo[axis], i))
            actual = list(checker.bbox_candidates(triangles, axis, order))
            require(len(actual) == len(set(actual)), 'Duplicate broad-phase pair')
            require(set(actual) == brute, 'Broad phase omitted or added a closed-AABB candidate')
            results.append({'trial': trial, 'axis': axis, 'exact_pairs': len(brute), 'matches_bruteforce': True})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', required=True)
    args = parser.parse_args()
    out = Path(args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    report = {'passed': False, 'checker_sha256': hashlib.sha256(Path(checker.__file__).read_bytes()).hexdigest(),
              'controls_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'python': sys.version, 'optimization_level': sys.flags.optimize,
              'meaning': 'Truth-labelled controls test this intersection checker, not global model printability.'}
    try:
        cases = base_cases()
        report['predicate_cases'] = in_process_tests(cases)
        report['predicate_case_count'] = len(report['predicate_cases'])
        report['broad_phase_bruteforce_cases'] = broad_phase_tests()
        artifacts = []
        for name, triangles, expect_pass, reason, tiny in cases:
            file = out / f'{name}.stl'
            digest = write_stl(file, triangles)
            artifacts.append((name, file, digest, expect_pass, False))
        for name, triangles in [('normal_box', box()), ('oblique_box', map_triangles(box(), affine))]:
            file = out / f'{name}.stl'
            artifacts.append((name, file, write_stl(file, triangles), True, False))
        degenerate = out / 'degenerate_face.stl'
        artifacts.append(('degenerate_face', degenerate,
                          write_stl(degenerate, [((0, 0, 0), (1, 0, 0), (2, 0, 0))]), False, False))
        malformed = out / 'malformed_count.stl'
        malformed.write_bytes(b'Bad STL'.ljust(80, b'\0') + struct.pack('<I', 5))
        artifacts.append(('malformed_count', malformed, hashlib.sha256(malformed.read_bytes()).hexdigest(), False, True))
        nonfinite = out / 'nonfinite.stl'
        nonfinite.write_bytes(b'Bad float'.ljust(80, b'\0') + struct.pack('<I', 1) + struct.pack('<12fH', 0, 0, 0, float('nan'), 0, 0, 1, 0, 0, 0, 1, 0, 0))
        artifacts.append(('nonfinite', nonfinite, hashlib.sha256(nonfinite.read_bytes()).hexdigest(), False, True))
        executions = []
        checker_path = str(Path(checker.__file__).resolve())
        for name, file, digest, expected_pass, expected_error in artifacts:
            for flags, mode in [(['-B'], 'B'), (['-B', '-O'], 'B_O')]:
                report_path = out / f'{name}.{mode}.json'
                command = [sys.executable, *flags, checker_path, '--stl', str(file), '--expected-sha256', digest, '--out', str(report_path)]
                result = subprocess.run(command, capture_output=True, text=True)
                require(report_path.is_file(), f'{name}/{mode}: no report')
                data = json.loads(report_path.read_text())
                require(data['passed'] == expected_pass, f'{name}/{mode}: wrong pass state')
                expected_exit = 0 if expected_pass else 2 if expected_error else 1
                require(result.returncode == expected_exit, f'{name}/{mode}: expected exit {expected_exit}, got {result.returncode}: {result.stderr}')
                executions.append({'case': name, 'interpreter_flags': flags, 'stl_sha256': digest,
                                   'expected_pass': expected_pass, 'exit_code': result.returncode,
                                   'report': report_path.name, 'report_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest(),
                                   'stdout': checker.public_error_text(result.stdout, [str(out), checker_path, sys.executable]),
                                   'stderr': checker.public_error_text(result.stderr, [str(out), checker_path, sys.executable])})
        report['subprocess_executions'] = executions
        report['subprocess_execution_count'] = len(executions)
        report['passed'] = True
    except Exception as error:
        report['error_type'] = type(error).__name__
        report['error'] = checker.public_error_text(str(error), [str(out)])
    report_path = out / 'controls-summary.json'
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'passed': report['passed'], 'predicate_case_count': report.get('predicate_case_count'),
                      'subprocess_execution_count': report.get('subprocess_execution_count'),
                      'summary': report_path.name, 'error': report.get('error')}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
