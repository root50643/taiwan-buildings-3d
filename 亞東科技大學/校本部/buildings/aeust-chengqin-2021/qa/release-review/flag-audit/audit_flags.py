"""Independent audit of the fixed candidate's 20 flagged pairs.

Reads binary STL records directly with struct; does not use trimesh or import
the candidate classifier for the independent exact sidedness proof.
Candidate CLI reruns are reported separately from independent proof.
"""
from pathlib import Path
from fractions import Fraction as Q
import collections
import hashlib
import json
import os
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
CANDIDATE = Path(os.environ['CHENGQIN_PACKAGE']).resolve()
STL = CANDIDATE / 'models/v1/model.stl'
REPORT = CANDIDATE / 'qa/qa-report.json'
EXPECTED_STL = '4e73e7094c83de47c19bcc6121fee575c1360b285d597773d983a873f46b7f5a'
EXPECTED_REPORT = '9d7253369d81df71bdbdb40d4c0576d2452fe7eeed26d9bbf9e52c5933a94f23'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))

def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def dot(a, b):
    return sum(x*y for x, y in zip(a, b))

def plane_vertex_test(a, b):
    """Exact separation/plane-cut fact; no tolerance or normalized normals.

    If all nonzero vertex distances have one sign, triangle/plane intersection
    is precisely the convex hull of zero-distance vertices. Thus, for the
    present nonparallel pairs, matching zero sets that equal the real shared
    vertices independently prove edge/vertex-only contact. Cases that straddle
    a plane fail this conservative proof, rather than being rounded/waived.
    """
    normal = cross(sub(b[1], b[0]), sub(b[2], b[0]))
    if not any(normal):
        return {'degenerate': True, 'same_side': False, 'distances': []}, []
    distances = [dot(normal, sub(p, b[0])) for p in a]
    nonzero = [d for d in distances if d]
    same_side = bool(nonzero) and (all(d > 0 for d in nonzero) or all(d < 0 for d in nonzero))
    zero_vertices = [p for p, d in zip(a, distances) if d == 0]
    return {'degenerate': False, 'same_side': same_side,
            'distances': [str(d) for d in distances],
            'zero_vertex_count': len(zero_vertices)}, zero_vertices

def independent_pair(a, b):
    a, b = [tuple(tuple(Q(x) for x in p) for p in tri) for tri in (a, b)]
    shared = set(a).intersection(b)
    ta, za = plane_vertex_test(a, b)
    tb, zb = plane_vertex_test(b, a)
    na, nb = cross(sub(a[1], a[0]), sub(a[2], a[0])), cross(sub(b[1], b[0]), sub(b[2], b[0]))
    nonparallel = bool(any(cross(na, nb)))
    proven = (nonparallel and ta['same_side'] and tb['same_side']
              and len(shared) in (1, 2) and set(za) == set(zb) == shared)
    return {'proof_method': 'Exact binary-coordinate plane sidedness; zero-vertex hull equals actual shared-coordinate set in both triangles',
            'nonparallel_planes': nonparallel, 'shared_coordinate_count': len(shared),
            'a_vertices_against_b_plane': ta, 'b_vertices_against_a_plane': tb,
            'zero_hulls_equal_shared_topology': bool(set(za) == set(zb) == shared),
            'contact_only_on_shared_topology_proven': bool(proven),
            'classification': ('shared_vertex_only' if len(shared) == 1 else 'shared_edge_only') if proven else 'not_proven_by_this_test'}

def read_stl(path):
    data = path.read_bytes()
    count, = struct.unpack_from('<I', data, 80)
    assert len(data) == 84 + count * 50, 'Unexpected binary STL record length'
    triangles = []
    for i in range(count):
        record = struct.unpack_from('<12fH', data, 84+i*50)
        triangles.append([list(record[3+j*3:6+j*3]) for j in range(3)])
    return triangles

def run(args, stem):
    proc = subprocess.run([sys.executable, '-B', '-X', 'utf8'] + [str(x) for x in args], capture_output=True, text=True, encoding='utf-8')
    (ROOT / (stem+'.stdout.txt')).write_text(proc.stdout, encoding='utf-8')
    (ROOT / (stem+'.stderr.txt')).write_text(proc.stderr, encoding='utf-8')
    return {'exit_status': proc.returncode, 'stdout_file': stem+'.stdout.txt', 'stderr_file': stem+'.stderr.txt'}

def main():
    before = {str(p.relative_to(CANDIDATE)): sha(p) for p in CANDIDATE.rglob('*') if p.is_file()}
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    flags = report['self_intersections']['unexpected_contacts_or_intersections']
    tris = read_stl(STL)
    checks = {
        'stl_sha_matches_fixed_input': sha(STL) == EXPECTED_STL,
        'report_sha_matches_original': sha(REPORT) == EXPECTED_REPORT,
        'report_references_actual_stl': report['sha256'] == sha(STL),
        'original_float_self_screen_still_false': report['self_intersections']['passes_numerical_pair_screen'] is False,
        'original_overall_screen_still_false': report.get('passes_bounded_geometry_screen') is False,
        'exactly_20_unique_original_flags': len(flags) == len({tuple(sorted(f['faces'])) for f in flags}) == 20,
        'binary_stl_face_count_2936': len(tris) == 2936,
    }
    audit_pairs = []
    for flag in flags:
        i, j = flag['faces']
        proof = independent_pair(tris[i], tris[j])
        audit_pairs.append({'original_flag': flag, 'actual_raw_binary_stl_triangles_mm': [tris[i], tris[j]], 'independent_proof': proof})
    checks['independent_exact_sidedness_proves_all_original_flags'] = all(p['independent_proof']['contact_only_on_shared_topology_proven'] for p in audit_pairs)
    preserved = {}
    for name in ('diagnosis.json', 'diagnosis-verified.json'):
        dpath = CANDIDATE / 'qa/flag-diagnosis' / name
        d = json.loads(dpath.read_text(encoding='utf-8'))
        rows = d['pairs']
        row_checks = []
        for index, (flag, independent) in enumerate(zip(flags, audit_pairs)):
            row = rows[index]
            actual = independent['actual_raw_binary_stl_triangles_mm']
            shared = set(map(tuple, actual[0])).intersection(map(tuple, actual[1]))
            row_checks.append({
                'faces': flag['faces'],
                'entire_original_flag_unchanged': row['original_flag'] == flag,
                'actual_stl_triangles_equal': row['triangles_mm'] == actual,
                'actual_shared_coordinates_equal': set(map(tuple, row['shared_coordinates_mm'])) == shared,
                'independent_classification_equal': row['exact']['classification'] == independent['independent_proof']['classification'],
            })
        summary = {
            'file_sha256': sha(dpath), 'stl_binding_exact': d['input_sha256'] == sha(STL),
            'original_report_binding_exact': d['report_sha256'] == sha(REPORT),
            'row_count_exactly_20': len(rows) == len(flags) == 20,
            'row_checks': row_checks,
        }
        summary['all_record_provenance_checks_passed'] = (summary['stl_binding_exact'] and summary['original_report_binding_exact'] and summary['row_count_exactly_20']
            and all(all(v for k,v in r.items() if k != 'faces') for r in row_checks))
        preserved[name] = summary
    checks['both_original_and_guarded_diagnoses_preserve_actual_flags_and_coordinates'] = all(d['all_record_provenance_checks_passed'] for d in preserved.values())
    # Negative controls for the independent proof are deliberately outside its
    # acceptance domain: genuine crossing, shared-edge coplanar overlap, and
    # near-parallel contact extending beyond allowed shared topology.
    a = [(0.,0.,0.),(2.,0.,0.),(0.,2.,0.)]
    test_cases = {
        'shared_edge': (a, [(0.,0.,0.),(2.,0.,0.),(0.,0.,2.)], True),
        'shared_vertex': (a, [(0.,0.,0.),(-1.,0.,1.),(0.,-1.,1.)], True),
        'proper_crossing': (a, [(.5,.5,-1.),(.5,.5,1.),(1.5,.5,0.)], False),
        'coplanar_overlap_not_waived': (a, [(0.,0.,0.),(2.,0.,0.),(1.,1.,0.)], False),
        'near_coplanar_shared_edge': (a, [(0.,0.,0.),(2.,0.,0.),(0.,-2.,2**-22)], True),
        'near_coplanar_crossing_not_waived': (a, [(0.,0.,0.),(.5,.5,2**-24),(1.,1.,-2**-24)], False),
    }
    independent_controls = {}
    for name, (ta, tb, expected) in test_cases.items():
        actual = independent_pair(ta, tb)
        independent_controls[name] = {'expected_proven': expected, 'actual_proof': actual, 'expectation_passed': actual['contact_only_on_shared_topology_proven'] is expected}
    checks['independent_sidedness_controls_passed'] = all(c['expectation_passed'] for c in independent_controls.values())
    # Execute delivered tools unchanged into this new review output directory.
    rerun = run([CANDIDATE/'qa/flag_diagnosis.py', STL, REPORT, '--json', ROOT/'rerun-diagnosis.json'], 'rerun-diagnosis')
    cli_controls = run([CANDIDATE/'qa/run_diagnosis_controls.py', '--json', ROOT/'rerun-controls.json'], 'rerun-controls')
    rerun_doc = json.loads((ROOT/'rerun-diagnosis.json').read_text(encoding='utf-8'))
    rerun_controls = json.loads((ROOT/'rerun-controls.json').read_text(encoding='utf-8'))
    candidate_guarded = json.loads((CANDIDATE/'qa/flag-diagnosis/diagnosis-verified.json').read_text(encoding='utf-8'))
    checks['guarded_report_binds_delivered_diagnostic_script'] = candidate_guarded['diagnostic_script_sha256'] == sha(CANDIDATE/'qa/flag_diagnosis.py')
    checks['rerun_diagnosis_binds_unchanged_original_report'] = rerun_doc['report_sha256'] == sha(REPORT) and rerun_doc['generic_report_unchanged']
    checks['unchanged_delivered_diagnosis_cli_exit0'] = rerun['exit_status'] == 0
    checks['rerun_pairs_equal_candidate_guarded_pairs'] = rerun_doc['pairs'] == candidate_guarded['pairs']
    checks['rerun_all_20_flags_covered_once'] = rerun_doc['all_flags_covered_once'] and rerun_doc['diagnosed_pair_count'] == 20
    checks['candidate_8_classifier_and_7_cli_controls_passed'] = (cli_controls['exit_status'] == 0 and rerun_controls['all_control_expectations_passed']
        and len(rerun_controls['controls']) == 8 and len(rerun_controls['cli_guard_controls']) == 7)
    # Add invalid pair shapes/types, same-face, negative index and changed STL
    # probes through the delivered real CLI, each requiring nonzero rejection.
    extras = {
        'same_face': [{'faces':[1547,1547]}],
        'negative_index': [{'faces':[-1,1561]}],
        'bool_index': [{'faces':[True,1561]}],
        'noninteger_index': [{'faces':[1547.0,1561]}],
        'pair_length_three': [{'faces':[1547,1561,1560]}],
        'malformed_flag': ['not-a-flag'],
    }
    extra_results = {}
    for name, altered_flags in extras.items():
        input_path = ROOT/(name+'.input.json')
        source = dict(report)
        source['self_intersections'] = dict(source['self_intersections'])
        source['self_intersections']['unexpected_contacts_or_intersections'] = altered_flags
        input_path.write_text(json.dumps(source, indent=2), encoding='utf-8')
        out = ROOT/(name+'.result.json')
        run_result = run([CANDIDATE/'qa/flag_diagnosis.py', STL, input_path, '--json', out], name)
        result = json.loads(out.read_text(encoding='utf-8'))
        run_result.update({'guard_errors': result['guard_errors'], 'diagnosed_pair_count': result['diagnosed_pair_count'],
                           'passes_flag_diagnosis': result['passes_flag_diagnosis'],
                           'expectation_passed': run_result['exit_status'] == 1 and 'invalid_flag_face_pair' in result['guard_errors']
                               and result['diagnosed_pair_count'] == 0 and result['passes_flag_diagnosis'] is False})
        extra_results[name] = run_result
    checks['six_extra_actual_cli_invalid_pair_guards_passed'] = all(x['expectation_passed'] for x in extra_results.values())
    after = {str(p.relative_to(CANDIDATE)): sha(p) for p in CANDIDATE.rglob('*') if p.is_file()}
    checks['all_candidate_files_unchanged_during_audit'] = before == after
    result = {'candidate_commit': '4116148c135d8a67a444ce8bf33fb64aba3e06a3', 'scope': 'Flag provenance, exact interpretation and guarded diagnosis only. No whole-mesh exact certificate, slicer or physical print.',
        'stl_sha256': sha(STL), 'original_float_report_sha256': sha(REPORT),
        'diagnostic_script_sha256': sha(CANDIDATE/'qa/flag_diagnosis.py'),
        'auditor_script_sha256': sha(Path(__file__)), 'checks': checks,
        'independent_classification_counts': dict(collections.Counter(p['independent_proof']['classification'] for p in audit_pairs)),
        'independent_pair_proofs': audit_pairs, 'preserved_candidate_diagnoses': preserved,
        'independent_controls': independent_controls, 'delivered_cli_rerun': rerun, 'delivered_control_rerun': cli_controls,
        'extra_cli_guards': extra_results, 'candidate_files_sha256': before}
    result['all_checks_passed'] = all(checks.values())
    (ROOT/'flag-audit-results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'all_checks_passed': result['all_checks_passed'], 'checks': checks, 'classifications': result['independent_classification_counts']}, indent=2))
    raise SystemExit(0 if result['all_checks_passed'] else 1)

if __name__ == '__main__':
    main()
