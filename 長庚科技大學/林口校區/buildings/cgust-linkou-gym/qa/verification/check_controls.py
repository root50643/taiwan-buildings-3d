"""Generic positive/negative fixtures, checked under Python -B and Python -B -O."""
from pathlib import Path
import argparse
import json
import struct
import subprocess
import sys
import numpy as np
from manifold3d import Manifold, OpType
from qa_common import require, sha256, write_json, checker_inventory

ROOT = Path(__file__).resolve().parent


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1-x0, y1-y0, z1-z0)).translate((x0, y0, z0))


def union(parts):
    result = Manifold.batch_boolean(parts, OpType.Add)
    require(str(result.status()).endswith('NoError'), f'Fixture CSG construction failed: {result.status()}')
    return result


def encode(triangles):
    triangles = np.asarray(triangles, dtype=np.float32)
    data = bytearray(b'Generic original-STL QA control fixture'.ljust(80, b'\0'))
    data.extend(struct.pack('<I', len(triangles)))
    for triangle in triangles:
        normal = np.cross(triangle[1].astype(float)-triangle[0], triangle[2].astype(float)-triangle[0])
        require(np.linalg.norm(normal) > 0, 'Control generator made a zero-area triangle')
        normal /= np.linalg.norm(normal)
        data.extend(struct.pack('<12fH', *normal, *triangle.ravel(), 0))
    return bytes(data)


def triangles_of(solid):
    mesh = solid.to_mesh()
    vertices = np.asarray(mesh.vert_properties[:, :3], dtype=np.float32)
    return vertices[np.asarray(mesh.tri_verts, dtype=np.int64)]


def fixture_cases():
    normal = triangles_of(box(0, 30, 0, 20, 0, 10))
    reversed_face = normal.copy()
    reversed_face[0] = reversed_face[0, [0, 2, 1]]
    # Re-encode normals for reversed faces, so winding/volume gates must reject
    # independently of the saved-normal agreement check.
    inverted = normal[:, [0, 2, 1]].copy()
    separate = np.concatenate([normal, triangles_of(box(35, 45, 0, 10, 0, 10))])
    inner = np.concatenate([normal, triangles_of(box(5, 10, 5, 10, 2, 5))[:, [0, 2, 1]]])
    point_touch = np.concatenate([triangles_of(box(0, 10, 0, 10, 0, 10)),
                                  triangles_of(box(10, 20, 10, 20, 10, 20))])
    narrow = triangles_of(union([box(0,10,0,10,0,3), box(14,24,0,10,0,3), box(9,15,4.7,5.3,0,3)]))
    tiny = triangles_of(union([box(0,35,0,25,0,1), box(0,20,0,20,0,5), box(29,29.6,10,10.6,0,5)]))
    thin = triangles_of(box(0, 30, 0, 20, 0, 0.6))
    raw_check = 'check_raw_mesh.py'
    slice_check = 'check_sections.py'
    dense_check = 'check_dense_surface.py'
    cases = [
        ('normal_box', encode(normal), [(raw_check, True, None), (slice_check, True, None), (dense_check, True, None)]),
        ('missing_original_triangle', encode(normal[1:]), [(raw_check, False, 'exact_coordinate_edges_two_faces')]),
        ('duplicate_original_triangle', encode(np.concatenate([normal, normal[:1]])), [(raw_check, False, 'exact_coordinate_edges_two_faces')]),
        ('one_reversed_face', encode(reversed_face), [(raw_check, False, 'exact_coordinate_consistent_winding')]),
        ('all_faces_inverted', encode(inverted), [(raw_check, False, 'positive_signed_volume')]),
        ('separate_closed_shell', encode(separate), [(raw_check, False, 'single_surface_no_internal_shell')]),
        ('internal_closed_shell', encode(inner), [(raw_check, False, 'single_surface_no_internal_shell')]),
        ('vertex_only_touching_shells', encode(point_touch), [(raw_check, False, 'exact_coordinate_vertex_links_single_cycles')]),
        ('narrow_0p6mm_root', encode(narrow), [(slice_check, False, 'no_original_polygon_splits_after_erosion_or_opening'),
                                             (dense_check, False, 'all_first_original_chords_ge_0p8mm')]),
        ('tiny_original_polygon', encode(tiny), [(slice_check, False, 'all_original_polygons_survive_erosion_and_opening')]),
        ('thin_0p6mm_slab', encode(thin), [(dense_check, False, 'all_first_original_chords_ge_0p8mm')]),
        ('truncated_binary_record', encode(normal)[:-1], [(raw_check, False, 'completed_without_error')]),
    ]
    return cases


def inspect(out):
    rows = []
    report_names = {'check_raw_mesh.py': 'raw-mesh-check.json', 'check_sections.py': 'section-check.json',
                    'check_dense_surface.py': 'dense-check.json'}
    cases = fixture_cases()
    for mode, flags in [('python_B', ['-B']), ('python_B_O', ['-B', '-O'])]:
        for name, data, checks in cases:
            case_root = out / mode / name
            case_root.mkdir(parents=True, exist_ok=True)
            fixture = case_root / 'fixture.stl'
            fixture.write_bytes(data)
            for checker, expected_pass, expected_false in checks:
                result_root = case_root / Path(checker).stem
                command = [sys.executable, *flags, str(ROOT / checker), '--stl', str(fixture), '--out', str(result_root)]
                process = subprocess.run(command, capture_output=True, text=True)
                result_root.mkdir(parents=True, exist_ok=True)
                (result_root / 'stdout.txt').write_text(process.stdout)
                (result_root / 'stderr.txt').write_text(process.stderr)
                report_path = result_root / report_names[checker]
                report = json.loads(report_path.read_text()) if report_path.exists() else {}
                observed_pass = process.returncode == 0 and report.get('passed') is True and report.get('strict_passed') is True
                observed_fail = process.returncode != 0 and report.get('passed') is False and report.get('strict_passed') is False
                expected_check_failed = expected_false is None or report.get('checks', {}).get(expected_false) is False
                verified = observed_pass if expected_pass else observed_fail and expected_check_failed
                rows.append({'mode': mode, 'fixture': name, 'checker': checker,
                             'expected_pass': expected_pass, 'expected_false_check': expected_false,
                             'returncode': process.returncode, 'expectation_verified': verified,
                             'fixture_sha256': sha256(fixture),
                             'report_file': str(report_path.relative_to(out)),
                             'report_sha256': sha256(report_path) if report_path.exists() else None,
                             'actual_false_checks': [key for key, value in report.get('checks', {}).items() if value is False]})
                print(f'{mode} {name} {checker}: expected {expected_pass}, verified {verified}', flush=True)
    checks = {'positive_box_passes_all_gates_both_modes': all(row['expectation_verified'] for row in rows if row['expected_pass']),
              'all_negative_controls_rejected_for_expected_reason_both_modes': all(row['expectation_verified'] for row in rows if not row['expected_pass']),
              'all_controls_have_reports': all(row['report_sha256'] is not None for row in rows),
              'both_python_modes_tested': {row['mode'] for row in rows} == {'python_B', 'python_B_O'}}
    return {'passed': all(checks.values()), 'strict_passed': all(checks.values()), 'checks': checks,
            'control_runs': len(rows), 'fixtures': len(cases), 'controls': rows,
            'checker_sources_sha256': checker_inventory(),
            'method': 'Independent generic synthetic fixtures only; no imports from a model builder. The real model is never edited. Normal box must pass, and each deliberately invalid case must return nonzero with its expected false check. No Python assert statements are used for acceptance; all cases run in ordinary -B and optimized -B -O modes.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    try:
        report = inspect(args.out)
    except Exception as error:
        report = {'passed': False, 'strict_passed': False, 'checks': {'control_runner_completed': False},
                  'error_type': type(error).__name__, 'error': str(error), 'checker_sources_sha256': checker_inventory()}
    write_json(args.out / 'control-check.json', report)
    print({'passed': report['passed'], 'report': str(args.out / 'control-check.json'), 'error': report.get('error')})
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
