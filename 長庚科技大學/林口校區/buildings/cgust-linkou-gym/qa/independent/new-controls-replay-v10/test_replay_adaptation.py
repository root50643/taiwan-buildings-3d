"""Check the narrow replay adaptation and builder lookup without replaying any archive."""
import argparse, ast, copy, hashlib, json, sys, types
from pathlib import Path
BASE_SHA = 'f79bc1aec6467e1fdeb78eb30ad801ef68e3ae77e5746fa9ccf7b34aa51267d3'
BUILDER_SHA = 'e4b23d35449c6321abbfea94e85f4d733ce58be65658255e1e5ba5065b33f637'

def need(value, message):
    if not value:
        raise ValueError(message)
def sha(data):
    return hashlib.sha256(data).hexdigest()
def apply_spans(base, manifest):
    need(sha(base) == BASE_SHA == manifest['base_sha256'], 'Base identity differs')
    source = base.decode()
    for span in manifest['spans']:
        need(source.count(span['old']) == 1, 'Nonunique exact adaptation span')
        source = source.replace(span['old'], span['new'])
    return source.encode()
def compare_source(expected, actual):
    need(expected == actual, 'Unexpected source delta')
    need(ast.dump(ast.parse(expected), include_attributes=False) ==
         ast.dump(ast.parse(actual), include_attributes=False), 'Unexpected AST delta')

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-source', type=Path, required=True)
    ap.add_argument('--candidate', type=Path, required=True)
    ap.add_argument('--spans', type=Path, required=True)
    ap.add_argument('--expected-spans-sha256', required=True)
    ap.add_argument('--builder-source', type=Path, required=True)
    args = ap.parse_args()
    raw = args.spans.read_bytes()
    need(sha(raw) == args.expected_spans_sha256, 'Adaptation manifest identity differs')
    manifest = json.loads(raw)
    source = args.candidate.read_bytes()
    expected = apply_spans(args.base_source.read_bytes(), manifest)
    compare_source(expected, source)
    module = types.ModuleType('audited_replay_module')
    module.__file__ = str(args.candidate)
    exec(compile(source, str(args.candidate), 'exec'), module.__dict__)
    builder = args.builder_source.read_bytes()
    need(sha(builder) == BUILDER_SHA == module.BUILDER_SHA, 'Builder source pin differs')
    results = []
    def case(name, operation, rejected=False):
        try:
            operation()
        except ValueError:
            need(rejected, 'Positive control rejected: ' + name)
            results.append({'case': name, 'expected': 'reject', 'observed': 'reject', 'passed': True})
        else:
            need(not rejected, 'Negative control accepted: ' + name)
            results.append({'case': name, 'expected': 'accept', 'observed': 'accept', 'passed': True})
    logical = 'author/qa/tools/build_controls_archive.py'
    canonical = 'qa/tools/build_controls_archive.py'
    row = {'restore_path': logical, 'canonical_public_path': canonical,
           'bytes': len(builder), 'sha256': BUILDER_SHA, 'mode': 'byte_exact'}
    mapping = {'files': [{key: row[key] for key in ('canonical_public_path', 'bytes', 'sha256')}],
               'copy_map': [row, {**row, 'restore_path': 'independent/tools/build_controls_archive.py'}]}
    def check_map(value, member=logical, data=builder):
        selected = module.resolve_builder_binding(value, member, data)
        need(selected['restore_path'] == member, 'Wrong logical builder selected')
    case('explicit_logical_builder_with_same_bytes_alias', lambda: check_map(mapping))
    case('missing_logical_builder', lambda: check_map(mapping, 'missing/build_controls_archive.py'), True)
    duplicate = copy.deepcopy(mapping); duplicate['copy_map'].append(copy.deepcopy(row))
    case('ambiguous_logical_builder', lambda: check_map(duplicate), True)
    for field, value in [('sha256', '0' * 64), ('bytes', len(builder) + 1),
                         ('bytes', True), ('mode', 'metadata_only_json_projection')]:
        changed = copy.deepcopy(mapping); changed['copy_map'][0][field] = value
        case('wrong_logical_' + field + '_' + str(value)[:6], lambda changed=changed: check_map(changed), True)
    missing = copy.deepcopy(mapping); missing['files'] = []
    case('missing_canonical_builder', lambda: check_map(missing), True)
    ambiguous = copy.deepcopy(mapping); ambiguous['files'].append(copy.deepcopy(ambiguous['files'][0]))
    case('ambiguous_canonical_builder', lambda: check_map(ambiguous), True)
    for field, value in [('sha256', '0' * 64), ('bytes', len(builder) + 1), ('bytes', True)]:
        changed = copy.deepcopy(mapping); changed['files'][0][field] = value
        case('wrong_canonical_' + field + '_' + str(value)[:6], lambda changed=changed: check_map(changed), True)
    case('wrong_actual_builder_bytes', lambda: check_map(mapping, data=builder + b'\n'), True)
    case('exact_source_and_ast_positive', lambda: compare_source(expected, source))
    for name, old, new in [
        ('verifier_pin_drift', module.VERIFIER_SHA.encode(), b'0' * 64),
        ('generic_limit_drift', b'LIMIT = 536870912', b'LIMIT = 1073741824'),
        ('csv_guard_removed', b"'.csv' not in row['restore_path'].lower()", b'True'),
        ('runtime_mode_check_removed', b"actual['optimization_level'] == level", b'True')]:
        need(source.count(old) >= 1, 'Mutation target absent')
        mutated = source.replace(old, new, 1)
        case(name, lambda mutated=mutated: compare_source(expected, mutated), True)
    case('runtime_need_not_stripped_by_optimization', lambda: module.need(False, 'Expected rejection'), True)
    report = {'schema': 'public-controls-replay-adaptation-check-v1', 'passed': True,
              'optimization_level': sys.flags.optimize, 'case_count': len(results), 'cases': results,
              'exact_source_and_ast_match_approved_spans': True, 'base_source_sha256': BASE_SHA,
              'candidate_source_sha256': sha(source), 'spans_sha256': sha(raw),
              'builder_source_sha256': sha(builder), 'test_source_sha256': sha(Path(__file__).read_bytes()),
              'actual_public_replay_executed': False, 'archive_constructed_or_opened': False,
              'generic_synthetic_suites_rerun': False, 'model_go': False, 'publication_go': False}
    print(json.dumps(report, indent=2) + '\n', end='')
if __name__ == '__main__':
    main()
