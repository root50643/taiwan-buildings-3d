"""Minimal exact CGUST state bridge controls, private fixtures in memory only.
Uses unchanged generic bytes; no Blender, render, geometry or large fixtures.
Run normal and optimized only under the shared CPU-0 heavyweight lock.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, hashlib, json, os, stat, types

CHECKER_NAME = 'check_scene_state_bridge_v10.py'
CHECKER_BYTES = 18218
CHECKER_SHA = 'a5b1714cf74d42c3fff80dc22b397afb458e88b29748bd116cc704f74be9ed24'

def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _read_regular_snapshot(workspace, relative, expected_bytes, maximum_bytes):
    """Shared FD-safe reader; optional discovered size is for self-code only."""
    require(type(relative) is str and relative and '\\' not in relative,
            'Invalid input relative path')
    parts = relative.split('/')
    require(all(part not in ('', '.', '..') for part in parts) and not relative.startswith('/'),
            'Unsafe input relative path')
    root = Path(workspace).absolute()
    require(root.anchor == '/' and all(p not in ('', '.', '..') for p in root.parts[1:]),
            'Unsafe workspace path')
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    directory_fd = os.open(root.anchor, directory_flags)
    try:
        # Every component is opened relative to the already pinned parent FD.
        # Renames or symlink swaps cannot redirect later opens through a new
        # pathname ancestor; no is_symlink/stat-then-open path race is used.
        for component in root.parts[1:] + tuple(parts[:-1]):
            child_fd = os.open(component, directory_flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = child_fd
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                     dir_fd=directory_fd)
    finally:
        os.close(directory_fd)
    try:
        # O_NONBLOCK prevents an untrusted FIFO from blocking at open. Reject
        # every nonregular leaf before fdopen/read, even if its size happens to fit.
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= maximum_bytes
                and (expected_bytes is None or before.st_size == expected_bytes),
                'Exact source byte count/type differs')
        with os.fdopen(fd, 'rb') as stream:
            fd = None  # stream now owns and closes this descriptor
            data = stream.read(before.st_size + 1)
            after = os.fstat(stream.fileno())
    finally:
        if fd is not None:
            os.close(fd)
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns),
            'Source changed during read')
    require(len(data) == before.st_size, 'Exact source byte count changed during read')
    return data


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workspace', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    require(os.sched_getaffinity(0) == {0}, 'CPU-0-only execution required')
    require(args.out.parent.is_dir() and not args.out.exists() and not args.out.is_symlink(),
            'Fresh control report required')
    here = Path(__file__).absolute().parent
    own = _read_regular_snapshot(here, Path(__file__).name, None, 256 * 1024)
    source = _read_regular_snapshot(here, CHECKER_NAME, CHECKER_BYTES, 256 * 1024)
    require(digest(source) == CHECKER_SHA, 'Exact bridge checker source differs')
    target = types.ModuleType('verified_exact_case_bridge')
    target.__file__ = str(here / CHECKER_NAME)
    exec(compile(source, target.__file__, 'exec'), target.__dict__)
    generic = target.load_generic(args.workspace)
    profile_before = json.dumps(target.ROWS, sort_keys=True)
    table = target.read_exact(args.workspace, target.TABLE_PATH, target.TABLE_SHA, target.TABLE_BYTES)
    raw = target.read_exact(args.workspace, target.PREFIXES['author'] + target.INPUT_FILES['author.original'],
                            target.ROWS['author.original']['sha256'], target.ROWS['author.original']['bytes'])
    cases = []

    def case(name, fn, expected=None, fixture=None):
        row = {'logical_case': name, 'expected': 'accept' if expected is None else 'reject'}
        try:
            result = fn()
            row.update(passed=expected is None, observed='accepted')
        except ValueError as exc:
            # Message is from audited fixed validators; input values are not echoed.
            row.update(passed=expected is not None and expected in str(exc), observed='rejected',
                       rejection=str(exc))
        if fixture is not None:
            row['reconstruction'] = fixture
        cases.append(row)

    def rebuilt_fixture(data, base_logical='synthetic_json', base=None, offset=None, replacement=None):
        if base is None:
            recipe = {'kind': 'hex_bytes', 'fixture_utf8_hex': data.hex()}
            first = bytes.fromhex(recipe['fixture_utf8_hex'])
            second = bytes(bytearray.fromhex(recipe['fixture_utf8_hex']))
        else:
            recipe = {'kind': 'replace_same_length', 'base_logical': base_logical,
                      'base_sha256': digest(base), 'offset': offset,
                      'replacement_bytes_hex': replacement.hex()}
            first = bytearray(base)
            first[offset:offset + len(replacement)] = replacement
            first = bytes(first)
            decoded = bytes.fromhex(recipe['replacement_bytes_hex'])
            second = base[:recipe['offset']] + decoded + base[recipe['offset'] + len(decoded):]
        require(first == data and second == data, 'Actual negative reconstruction differs')
        return {'recipe': recipe, 'fixture_bytes': len(first), 'fixture_sha256': digest(first),
                'actual_rebuilt_bytes': len(second), 'actual_rebuilt_sha256': digest(second),
                'actual_bitwise_equal': first == second, 'materialized_fixture_file': False}

    def positive_all():
        target.bind_table(table, generic)
        for logical, name in target.INPUT_FILES.items():
            row = target.ROWS[logical]
            domain = logical.split('.')[0]
            data = target.read_exact(args.workspace, target.PREFIXES[domain] + name,
                                     row['sha256'], row['bytes'])
            got = target.scan_state(data, logical, generic)
            require(got['masked_bytes'] == 5, 'Exact observed mask size differs')
            canonical = 'author.source_memory' if logical.endswith('.source_memory') else 'author.original'
            crow = target.ROWS[canonical]
            original = target.read_exact(args.workspace,
                target.PREFIXES['author'] + target.INPUT_FILES[canonical], crow['sha256'], crow['bytes'])
            require(data == original, 'Actual six-to-two canonical byte comparison differs')
        for domain, audit in target.AUDITS.items():
            data = target.read_exact(args.workspace, target.PREFIXES[domain] + 'source-scene-audit.json',
                                     audit['sha256'], audit['bytes'])
            target.validate_audit(data, domain, generic)
    case('exact_six_aliases_two_canonical_bytes_and_two_audits_positive', positive_all)
    altered = bytearray(raw); altered[0] = ord('['); altered = bytes(altered)
    evidence = rebuilt_fixture(altered, 'author.original', raw, 0, b'[')
    case('changed_original_state_identity_rejected', lambda: target.scan_state(altered, 'author.original', generic),
         'State identity differs', evidence)
    for name, key, wrong_value in [
        ('old_wfu_identity', 'sha256', '5a5392d71a92898c2f455c527fd4f1f9cebcaca44a811a809ebc179e417bec1a'),
        ('wrong_pointer', 'json_pointer', '/other/filepath'),
        ('wrong_type', 'exact_type', 'number'),
        ('wrong_encoded_span', 'encoded_json_string_offset', 108038),
        ('wrong_effective_range', 'marker_bytes', 6),
        ('bool_is_not_int', 'marker_occurrences', True)]:
        row = dict(target.ROWS['author.original']); row[key] = wrong_value
        case(name + '_pin_rejected', lambda row=row: target.pin_row('author.original', row),
             'Exact case row/type/range pin differs')
    case('unlisted_logical_alias_rejected', lambda: target.scan_state(raw, 'unbound.original', generic),
         'Unknown exact logical alias')
    bad_table = bytearray(table); bad_table[0] = ord('['); bad_table = bytes(bad_table)
    case('changed_exception_table_identity_rejected', lambda: target.bind_table(bad_table, generic),
         'Exact bridge table identity differs', rebuilt_fixture(bad_table, 'exact_exception_table', table, 0, b'['))
    independent = target.AUDITS['independent']
    qaudit = target.read_exact(args.workspace, target.PREFIXES['independent'] + 'source-scene-audit.json',
                              independent['sha256'], independent['bytes'])
    case('other_domain_audit_rejected', lambda: target.validate_audit(qaudit, 'author', generic),
         'Exact audit identity differs')

    # The following isolate unchanged primitive guards after an explicitly local
    # synthetic identity rebind. No production ROWS, aliases or table are changed.
    marker = bytes.fromhex('2f746d702f')
    literal = b'"' + marker + b'"'
    simple = b'{"render":{"filepath":' + literal + b'}}'
    fixtures = [
        ('typed_pointer_wrong', b'{"other":{"filepath":' + literal + b'}}', 'State typed pointer differs', False),
        ('typed_value_wrong', b'{"render":{"filepath":5}}', 'State typed pointer differs', False),
        ('duplicate_key', b'{"render":{"filepath":' + literal + b',"filepath":' + literal + b'}}', 'Duplicate JSON object key', False),
        ('duplicate_marker_outside', simple[:-1] + b',"outside":' + literal + b'}', 'State exact literal/offset differs', False),
        ('escaped_encoding', b'{"render":{"filepath":"\\u002ftmp/"}}', 'State exact literal/offset differs', False),
        ('value_tail_not_exempt', b'{"render":{"filepath":"' + marker + b'private-tail"}}', 'State typed pointer differs', False),
        ('outside_private_path', simple[:-1] + b',"outside":"' + bytes.fromhex('2f686f6d652f73796e746865746963') + b'"}', 'Private path marker', True),
        ('outside_credential', simple[:-1] + b',"outside":"' + b'gh' + b'p_' + b'A'*36 + b'"}', 'Credential-shaped content', True)]
    for name, data, expected, full_scan in fixtures:
        literal_start = data.find(literal)
        if literal_start < 0:
            literal_start = simple.index(literal)
        isolated_row = dict(target.ROWS['author.original'])
        isolated_row.update(bytes=len(data), sha256=digest(data),
            encoded_json_string_offset=literal_start, marker_offset=literal_start + 1)
        def validate(data=data, isolated_row=isolated_row, full_scan=full_scan):
            projected = target.state_projection(data, isolated_row, generic)
            if full_scan:
                target.scan_complete_plain_buffer(target.policy(generic), projected)
        case(name + '_isolated_primitive_rejected', validate, expected, rebuilt_fixture(data))

    require(json.dumps(target.ROWS, sort_keys=True) == profile_before, 'Production exact rows changed')
    target.read_exact(args.workspace, target.TABLE_PATH, target.TABLE_SHA, target.TABLE_BYTES)
    target.read_exact(args.workspace, target.GENERIC_PATH, target.GENERIC_SHA, target.GENERIC_BYTES)
    require(_read_regular_snapshot(here, CHECKER_NAME, CHECKER_BYTES, 256 * 1024) == source,
            'Bridge source changed during controls')
    require(_read_regular_snapshot(here, Path(__file__).name, len(own), 256 * 1024) == own,
            'Control source changed during controls')
    report = {'passed': all(row['passed'] for row in cases), 'case_count': len(cases),
        'optimization_level': sys.flags.optimize, 'source_set': 'author_and_independent',
        'logical_alias_count': 6, 'unique_identity_count': 2,
        'checker_source_sha256': CHECKER_SHA, 'checker_source_bytes': CHECKER_BYTES,
        'generator_source_sha256': digest(own), 'generator_source_bytes': len(own),
        'generic_source_sha256': target.GENERIC_SHA, 'generic_source_bytes': target.GENERIC_BYTES,
        'exception_table_sha256': target.TABLE_SHA, 'exception_table_bytes': target.TABLE_BYTES,
        'cases': cases, 'production_exact_rows_unchanged': True,
        'private_negative_fixtures_only_in_process_memory': True,
        'actual_rebuilt_bitwise_comparisons': True, 'generic_full_suites_rerun': False,
        'blender_or_render_executed': False, 'model_go': False, 'publication_go': False}
    with args.out.open('x', encoding='utf8') as stream:
        json.dump(report, stream, indent=2, allow_nan=False); stream.write('\n')
    print(json.dumps({'passed': report['passed'], 'case_count': len(cases), 'optimization_level': sys.flags.optimize}))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
