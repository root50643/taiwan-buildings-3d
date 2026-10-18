"""Read-only incremental fidelity audit; emits only into a separate review folder.

No geometry, slicing, ray sampling or physical manufacturing test is repeated.
"""
import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

COMMIT = '7cf0563a06858137f51751600348a35198c8f6f2'
OLD_COMMIT = '3a9a6041c5fde9ef2d6e9e96b02f24f025c8be5a'

def sha(b):
    return hashlib.sha256(b).hexdigest()

def substitutions(source, package):
    root = '${HISTORICAL_WORKSPACE_ROOT}'
    pairs = [
        (str(source / 'candidate').replace('\\', '/'), 'PACKAGE'),
        (str(package).replace('\\', '/'), 'PACKAGE'),
        (str(source).replace('\\', '/'), 'REVIEW_ROOT'),
        (root + '/2026-10-19/task/manufacturing-review/private', 'ORIGINAL_DIAGNOSTIC_GCODE_DIR'),
        (root + '/2026-10-18/task-4/manufacturing-tools/PrusaSlicer-2.9.6/PrusaSlicer-2.9.6', 'PRUSASLICER_2_9_6_DIR'),
        (root + '/2026-10-18/task/tool-libs', 'PYTHON_AUDIT_DEPS'),
        (root + '/2026-10-18/task-2/xizi-split-independent-review/gcode-audit/independent_gcode_audit.py', 'EARLIER_INDEPENDENT_AUDIT_PY'),
    ]
    result = {}
    for raw, role in pairs:
        for form in [raw, raw.replace('/', '\\')]:
            result[form] = role
            result[json.dumps(form, ensure_ascii=False)[1:-1]] = role
    return sorted(result.items(), key=lambda p: len(p[0]), reverse=True)

def normalize(text, mapping):
    counts = Counter()
    for old, role in mapping:
        n = text.count(old)
        if n:
            counts[role] += n
            text = text.replace(old, '${' + role + '}')
    return text, dict(counts)

def compare_json(a, b, mapping):
    counts = Counter()
    string_changes = []
    failures = []
    digest = hashlib.sha256()
    def walk(x, y, path):
        if type(x) is not type(y):
            failures.append({'path': path, 'reason': 'type changed'})
            return
        if isinstance(x, dict):
            if list(x) != list(y):
                failures.append({'path': path, 'reason': 'dictionary keys/order changed'})
            for k in x.keys() & y.keys():
                walk(x[k], y[k], path + '/' + k)
        elif isinstance(x, list):
            if len(x) != len(y):
                failures.append({'path': path, 'reason': 'list length changed'})
            for k, (xx, yy) in enumerate(zip(x, y)):
                walk(xx, yy, path + '/' + str(k))
        elif isinstance(x, str):
            counts['string'] += 1
            if x != y:
                normalized, _ = normalize(x, mapping)
                ok = normalized == y
                string_changes.append({'path': path, 'semantic_path_substitution_only': ok})
                if not ok:
                    failures.append({'path': path, 'reason': 'non-path string change'})
        else:
            name = type(x).__name__
            counts[name] += 1
            # JSON serialization distinguishes -0.0, 0.0 and int/float forms.
            token = json.dumps([name, x], allow_nan=False, separators=(',', ':'))
            if token != json.dumps([name, y], allow_nan=False, separators=(',', ':')):
                failures.append({'path': path, 'reason': 'numeric/bool/null changed'})
            digest.update((path + ':' + token + '\n').encode('utf8'))
    walk(a, b, '')
    return {'leaf_counts_by_type': dict(counts), 'numeric_boolean_null_leaf_count': sum(v for k, v in counts.items() if k != 'string'),
            'numeric_boolean_null_values_preserved': not failures,
            'structure_and_all_strings_preserved_except_semantic_paths': not failures,
            'changed_string_leaves': string_changes, 'failures': failures}

def git_bindings(package, paths):
    repo = package.parents[3]
    prefix = package.relative_to(repo).as_posix() + '/qa/independent-support-review/'
    base = ['git', '--git-dir=' + str(repo / '.git')]
    tree = subprocess.run(base + ['ls-tree', '-rz', '--full-tree', COMMIT, '--', prefix], check=True, stdout=subprocess.PIPE).stdout
    entries = {}
    for record in tree.split(b'\0'):
        if record:
            meta, name = record.split(b'\t', 1)
            entries[name.decode('utf8')[len(prefix):]] = meta.split()[2].decode('ascii')
    names = sorted(paths)
    ids = [entries[n] for n in names]
    data = subprocess.run(base + ['cat-file', '--batch'], input=('\n'.join(ids) + '\n').encode('ascii'), check=True, stdout=subprocess.PIPE).stdout
    at = 0
    results = []
    for name, oid in zip(names, ids):
        stop = data.index(b'\n', at)
        header = data[at:stop].split()
        size = int(header[2])
        body = data[stop + 1:stop + 1 + size]
        at = stop + 1 + size + 1
        local = (package / 'qa/independent-support-review' / name).read_bytes()
        results.append({'path': name, 'git_blob': oid, 'bytes': size, 'sha256': sha(body), 'working_file_equals_fixed_commit': body == local})
    return {'commit': COMMIT, 'tree_file_count': len(entries), 'working_file_count': len(paths),
            'same_paths': set(entries) == set(paths), 'all_working_files_equal_fixed_commit': all(x['working_file_equals_fixed_commit'] for x in results), 'files': results}

def audit(source, package):
    integrated = package / 'qa/independent-support-review'
    manifest = json.loads((integrated / 'integration-source-manifest.json').read_text('utf8'))
    mapping = substitutions(source, package)
    records = []
    for record in manifest['files']:
        rel = record['path']
        a, b = (source / rel).read_bytes(), (integrated / rel).read_bytes()
        checks = {'path': rel, 'source_bytes': len(a), 'integrated_bytes': len(b), 'source_sha256': sha(a), 'integrated_sha256': sha(b),
                  'manifest_source_hash_and_size_match': sha(a) == record['source_sha256'] and len(a) == record['source_bytes'],
                  'manifest_integrated_hash_and_size_match': sha(b) == record['integrated_sha256'] and len(b) == record['integrated_bytes'],
                  'source_bytes_preserved_field_accurate': record['source_bytes_preserved'] == (a == b), 'byte_identical': a == b}
        if a != b:
            normalized, transformations = normalize(a.decode('utf8'), mapping)
            checks['only_explicit_semantic_path_substitutions'] = normalized.encode('utf8') == b
            checks['actual_transformations'] = transformations
            declared = {x['semantic_role']: x['occurrences'] for x in record['transformations']}
            checks['transformation_counts_match_manifest'] = transformations == declared
        if rel.endswith('.json'):
            checks['json'] = compare_json(json.loads(a), json.loads(b), mapping)
        if rel.endswith('.py'):
            ast.parse(b.decode('utf8'))
            checks['python_AST_parse_ok'] = True
        if rel.endswith('.npz'):
            with zipfile.ZipFile(integrated / rel) as z:
                checks['npz_crc_ok'] = z.testzip() is None
                checks['npz_members'] = z.namelist()
        records.append(checks)
    paths = sorted(p.relative_to(integrated).as_posix() for p in integrated.rglob('*') if p.is_file())
    selected = {r['path'] for r in manifest['files']}
    added = sorted(set(paths) - selected)
    old_qa = []
    for rel in ['qa/geometry-review-superseded-pre-freeze.json', 'qa/scene-review-superseded-coordinate-sort.json', 'qa/tool-failures.json', 'qa/README.md']:
        a, b = (source / 'candidate' / rel).read_bytes(), (package / rel).read_bytes()
        old_qa.append({'path': rel, 'sha256': sha(a), 'byte_identical': a == b})
    original = json.loads((integrated / 'slicing-support-audit/support-access-and-bridge.json').read_text('utf8'))
    corrected = json.loads((integrated / 'slicing-support-audit/REVIEW-ONLY-support-access-and-bridge.json').read_text('utf8'))
    summary = json.loads((integrated / 'review-summary.json').read_text('utf8'))
    whitespace = json.loads((package / 'qa/revision-whitespace-check.json').read_text('utf8'))
    delta = json.loads((package / 'qa/revision-delta-review.json').read_text('utf8'))
    npz_bindings = []
    for rel in ['main_body-selected-paths.npz', 'REVIEW-ONLY-main-short-axis-selected-paths.npz']:
        npz_bindings.append({'path': 'slicing-support-audit/' + rel, 'byte_identical_to_original_independent_review': (source / 'slicing-support-audit' / rel).read_bytes() == (integrated / 'slicing-support-audit' / rel).read_bytes()})
    support = {'old_segments': original['actual_support_segment_count'], 'old_unique_samples': original['unique_points'],
               'old_no_eight_direction_clear_count': original['no_eight_direction_clear_count'], 'new_segments': corrected['actual_support_segment_count'],
               'new_unique_samples': corrected['unique_points'], 'new_no_eight_direction_clear_count': corrected['no_eight_direction_clear_count'],
               'old_flag_list_length': len(original['no_eight_direction_points']), 'new_flag_list_length': len(corrected['no_eight_direction_points']),
               'old_and_new_580_coordinate_lists_equal': original['no_eight_direction_points'] == corrected['no_eight_direction_points'], 'npz_bindings': npz_bindings}
    git = git_bindings(package, paths)
    failures = []
    for r in records:
        for k, v in r.items():
            if isinstance(v, bool) and not v and k != 'byte_identical':
                failures.append({'path': r['path'], 'check': k})
        if 'json' in r and r['json']['failures']:
            failures.append({'path': r['path'], 'json_failures': r['json']['failures']})
    if not all(r['byte_identical'] for r in old_qa):
        failures.append({'check': 'historical_original_QA_changed'})
    if not git['same_paths'] or not git['all_working_files_equal_fixed_commit']:
        failures.append({'check': 'fixed_commit_binding'})
    return {'created_utc': datetime.now(timezone.utc).isoformat(), 'candidate_commit': COMMIT, 'old_evidence_candidate_commit': OLD_COMMIT,
            'scope': 'Fidelity and completeness of integrated historical evidence, semantic path substitutions, archived failure records and incremental-review limits only. No geometry, reslicing, numerical bridge recomputation, finite-ray execution or physical test.',
            'decision': 'GO_EVIDENCE_INTEGRATION_ONLY' if not failures else 'BLOCKED',
            'source_files_checked': len(records), 'integrated_total_files': len(paths), 'integration_added_files': added,
            'unchanged_source_files': sum(r['byte_identical'] for r in records), 'path_sanitized_source_files': sum(not r['byte_identical'] for r in records),
            'all_manifest_hash_and_size_claims_rechecked': all(r['manifest_source_hash_and_size_match'] and r['manifest_integrated_hash_and_size_match'] for r in records),
            'all_differences_only_explicit_path_substitutions': all(r.get('only_explicit_semantic_path_substitutions', True) for r in records),
            'all_JSON_structure_numeric_boolean_null_and_nonpath_strings_preserved': all(r.get('json', {}).get('structure_and_all_strings_preserved_except_semantic_paths', True) for r in records),
            'total_JSON_numeric_boolean_null_leaves_compared': sum(r.get('json', {}).get('numeric_boolean_null_leaf_count', 0) for r in records),
            'source_and_integrated_all_checks': records, 'historical_QA': old_qa, 'support_evidence_preserved': support,
            'historical_decision_preserved': {'as_delivered_main_slicing_process': summary['as_delivered_main_slicing_process'], 'unconditional_package_GO': summary['unconditional_package_GO'], 'decision': summary['decision']},
            'whitespace_record': {'exit_code': whitespace['exit_code'], 'raw_output_nonempty': bool(whitespace['raw_output']), 'raw_output_retained_sha256': sha(whitespace['raw_output'].encode('utf8')), 'disposition': whitespace['disposition'], 'original_inputs_or_thresholds_changed_to_hide_findings': whitespace['original_inputs_or_thresholds_changed_to_hide_findings']},
            'incremental_delta_review_limits': {k: delta[k] for k in ['pass', 'pass_scope', 'manufacturing_status', 'old_main_route_accepted', 'scope', 'limitations', 'blocking_findings']},
            'fixed_commit_binding': git, 'blocking_findings': failures,
            'not_performed': ['New slicing', 'Geometry/self-intersection computation', 'Bridge-coverage recomputation', 'Finite support-ray replay', 'Physical print/removal/fit/glue tests', 'Remote write/publication', 'Library download']}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = audit(args.source, args.package)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({k: result[k] for k in ['decision', 'source_files_checked', 'integrated_total_files', 'unchanged_source_files', 'path_sanitized_source_files', 'total_JSON_numeric_boolean_null_leaves_compared', 'blocking_findings']}, ensure_ascii=False))
