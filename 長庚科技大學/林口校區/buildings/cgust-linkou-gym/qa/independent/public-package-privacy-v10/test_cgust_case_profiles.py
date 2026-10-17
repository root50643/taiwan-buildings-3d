"""Small current-case pin/policy controls; no scene, archive or CSV is read."""
from pathlib import Path
import argparse
import copy
import json
import os
import sys
import types
from test_public_package import load_entry


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    m = load_entry()
    p, tools = m.load_tools()
    g = tools['package_controls_v2.py']
    primitive = tools['exact_privacy_primitives.py']
    c = tools['check_cgust_privacy.py']
    policy = types.SimpleNamespace(MAX_BYTES=g.MAX_BYTES,
        PRIVATE_MARKERS=g.PRIVATE_MARKERS+c.CGUST_MARKERS,
        TMP_MARKER=g.TMP_MARKER, SECRET_PATTERNS=g.SECRET_PATTERNS)
    m.require(sorted(os.sched_getaffinity(0)) == [0], 'Caller must use CPU0 under shared lock')
    m.require(args.out.parent.is_dir() and not args.out.exists(), 'Fresh output required')
    own = Path(__file__).read_bytes()
    cases = []

    def case(name, accepted, function, reason=None):
        error = None
        try:
            function()
        except (ValueError, RuntimeError, KeyError, TypeError) as exc:
            error = str(exc)
        passed = (error is None) is accepted and (reason is None or (error is not None and reason in error))
        cases.append({'name': name, 'expected_accept': accepted, 'accepted': error is None,
                      'error': error, 'expected_error_substring': reason, 'passed': passed})

    def mutate(module, key, value):
        fake = types.SimpleNamespace(**vars(module))
        setattr(fake, key, value)
        return fake

    case('current_exact_policy', True, lambda: c.validate_policy(g, primitive, policy))
    for index in range(len(c.CGUST_MARKERS)):
        case('retained_and_current_marker_' + str(index), False,
             lambda i=index: primitive.scan_complete_plain_buffer(policy, c.CGUST_MARKERS[i]),
             'Private path marker')
    case('old_blend_identity_not_inherited', False, lambda: c.validate_policy(g,
        mutate(primitive, 'BLEND', '70d8914cefaaceac8572d00c6cfba52b5abbedd18c810175f2deedb47ed2c429'), policy),
        'Exact Blend candidate/field profile differs')
    oldcsv = {'compressed_bytes': 19156984,
              'compressed_sha256': '80cf38d8255e789755e316a24638872db0fb913f2d37795edd3c81349551f550',
              'decoded_bytes': 194500309,
              'decoded_sha256': '6408a97da82dc7a1e226225637a415d6cd8ecaecfb962e51454f52bc3067f2b6',
              'csv_data_rows': 209460}
    case('old_csv_profile_not_inherited', False,
         lambda: c.validate_policy(g, mutate(primitive, 'SCIENCE_CSV_PROFILE', oldcsv), policy),
         'Exact fixed CSV profile differs')
    for key, value in c.CSV_ITEMS:
        changed = dict(c.CSV_ITEMS)
        changed[key] = value + 1 if type(value) is int else '0' * 64
        case('reject_changed_csv_' + key, False,
             lambda d=changed: c.validate_policy(g, mutate(primitive, 'SCIENCE_CSV_PROFILE', d), policy),
             'Exact fixed CSV profile differs')
    changed = dict(c.CSV_ITEMS, csv_data_rows=51760.0)
    case('reject_float_row_count', False,
         lambda: c.validate_policy(g, mutate(primitive, 'SCIENCE_CSV_PROFILE', changed), policy),
         'Exact fixed CSV profile differs')
    fields = list(primitive.BLEND_FIELDS)
    fields[0] = (fields[0][0]+1, fields[0][1], fields[0][2])
    case('reject_shifted_sdna_field', False,
         lambda: c.validate_policy(g, mutate(primitive, 'BLEND_FIELDS', fields), policy),
         'Exact Blend candidate/field profile differs')
    case('reject_dropped_case_marker', False,
         lambda: c.validate_policy(g, primitive, mutate(policy, 'PRIVATE_MARKERS', policy.PRIVATE_MARKERS[:-1])),
         'Original privacy pattern coverage differs')
    case('reject_expanded_generic_byte_bound', False,
         lambda: c.validate_policy(g, primitive, mutate(policy, 'MAX_BYTES', g.MAX_BYTES+1)),
         'Unchanged generic MAX_BYTES required')
    case('reject_foreign_scene_before_projection', False,
         lambda: c.scan_blend(b'BLENDER-v403', g, primitive, policy),
         'Exact original CGUST Blend identity differs')
    case('reject_foreign_csv_before_decode', False,
         lambda: c.scan_csv(b'foreign', g, primitive, policy),
         'Compressed CSV size/hash differs before streaming')
    m.require(Path(__file__).read_bytes() == own, 'Control source changed')
    report = {'passed': all(r['passed'] for r in cases), 'optimization_level': sys.flags.optimize,
              'cpu_affinity': sorted(os.sched_getaffinity(0)), 'case_count': len(cases), 'cases': cases,
              'source_sha256': m.digest(own), 'scanner_source_sha256': m.digest(Path(m.__file__).read_bytes()),
              'bound_sources': m.TOOLS, 'scene_csv_and_historical_archive_read': False,
              'scope': 'Current fixed identity and added-marker controls only; unchanged generic controls are retained by hash. Actual package scan remains required.'}
    with args.out.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'passed': report['passed'], 'case_count': len(cases), 'optimization_level': sys.flags.optimize}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
