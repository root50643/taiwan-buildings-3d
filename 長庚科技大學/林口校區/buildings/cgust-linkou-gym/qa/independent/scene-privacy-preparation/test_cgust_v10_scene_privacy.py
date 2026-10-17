"""Minimal CGUST v10 identity/profile/scope controls; no Blender or fixture files.
Negatives exist only in private process memory. Public report contains logical
keys, deterministic hex recipes and actual second-reconstruction byte equality.
Run under the parent's shared CPU-0 lock; unchanged generic suites are not rerun.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, hashlib, json, os, stat, types

CHECKER_NAME = 'check_cgust_v10_scene_privacy.py'
CHECKER_BYTES = 10988
CHECKER_SHA = '854e1868de71bb82c93d27f637dd70c68d3eb1293d1c5eeb6e3177476cddb045'

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
    require(args.out.parent.is_dir() and not args.out.exists() and not args.out.is_symlink(),
            'Fresh report required')
    require(os.sched_getaffinity(0) == {0}, 'CPU-0-only execution required')
    here = Path(__file__).absolute().parent
    own = _read_regular_snapshot(here, Path(__file__).name, None, 256 * 1024)
    source = _read_regular_snapshot(here, CHECKER_NAME, CHECKER_BYTES, 256 * 1024)
    require(digest(source) == CHECKER_SHA, 'Frozen checker source differs')
    target = types.ModuleType('verified_cgust_v10_case')
    target.__file__ = str(here / CHECKER_NAME)
    exec(compile(source, target.__file__, 'exec'), target.__dict__)
    generic = target.load_generic(args.workspace)
    raw = target.read_exact(args.workspace, target.BLEND_PATH, target.BLEND_SHA, target.BLEND_BYTES)
    profile_before = json.dumps(target.PROFILE, sort_keys=True)
    projection = generic.blend_generic_default_projection(raw, target.allowance())
    cases = []

    def case(name, action, expected_error=None, fixture=None):
        value = None
        error = None
        try:
            value = action()
        except Exception as exc:
            error = type(exc).__name__ + ': ' + str(exc)
        passed = error is None if expected_error is None else error is not None and expected_error in error
        cases.append({'logical_case': name, 'expected_accept': expected_error is None,
                      'accepted': error is None, 'passed': bool(passed),
                      'expected_error_substring': expected_error, 'actual_error': error,
                      'fixture': fixture})
        return value

    def patched(base, name, offset, payload):
        require(0 <= offset <= len(base) - len(payload), 'Fixture range invalid')
        require(base[offset:offset + len(payload)] == b'\0' * len(payload), 'Fixture original region not zero')
        recipe = {'logical_base': name, 'base_bytes': len(base), 'base_sha256': digest(base),
                  'mutation': 'replace_equal_length', 'offset': offset,
                  'original_bytes_hex': base[offset:offset + len(payload)].hex(),
                  'replacement_bytes_hex': payload.hex()}
        first = bytearray(base)
        first[offset:offset + len(payload)] = payload
        first = bytes(first)
        # A separate reconstruction path executes the public recipe, rather
        # than trusting the first buffer's asserted hash.
        decoded = bytes.fromhex(recipe['replacement_bytes_hex'])
        second = base[:recipe['offset']] + decoded + base[recipe['offset'] + len(decoded):]
        require(first == second, 'Actual negative reconstruction differs')
        return first, {'recipe': recipe, 'fixture_bytes': len(first),
                       'fixture_sha256': digest(first), 'actual_rebuilt_bytes': len(second),
                       'actual_rebuilt_sha256': digest(second), 'actual_bitwise_equal': first == second,
                       'materialized_fixture_file': False}

    result = case('exact_v10_candidate_positive', lambda: target.scan_blend(raw, generic))
    if result is not None:
        require(result['masked_effective_bytes'] == sum(len(raw[r['field_absolute_byte_offset']:
            r['field_absolute_byte_offset'] + r['field_buffer_bytes']].partition(b'\0')[0])
            for r in target.PROFILE['field_findings']), 'Mask length not original-buffer derived')
        require(result['masked_effective_bytes'] == 16, 'Observed mask length differs')
    for label, old in [('old_wfu', '70d8914cefaaceac8572d00c6cfba52b5abbedd18c810175f2deedb47ed2c429'),
                       ('old_cgust_v8', 'c7ab626e4cbc30e32f6a8beda579aa126cf928e877e92b3a09d60ec6a1313f59')]:
        wrong = target.allowance()
        wrong['sha256'] = old
        case(label + '_identity_rejected',
             lambda wrong=wrong: generic.blend_generic_default_projection(raw, wrong),
             'Exact Blend privacy allowance identity differs')
    for label, key, value in [('struct', 'struct', 'Scene'), ('field', 'field', 'filename[256]'),
            ('type', 'field_type', 'void'), ('offset', 'field_absolute_byte_offset', 171625),
            ('range', 'field_buffer_bytes', 1091), ('buffer_hash', 'field_buffer_sha256', '0' * 64)]:
        wrong = target.allowance()
        wrong['sdna_profile']['field_findings'][0][key] = value
        case('wrong_' + label + '_pin_rejected',
             lambda wrong=wrong: generic.blend_generic_default_projection(raw, wrong),
             'Exact Blend SDNA profile differs')
    tail_offset = target.PROFILE['field_findings'][0]['field_absolute_byte_offset'] + 64
    tail_mutant, tail_recipe = patched(raw, 'original_scene', tail_offset, b'X')
    case('changed_original_candidate_rejected', lambda: target.scan_blend(tail_mutant, generic),
         'Exact CGUST v10 candidate identity differs', tail_recipe)
    isolated = target.allowance()
    isolated['sha256'] = digest(tail_mutant)
    isolated['sdna_profile']['blend_sha256'] = digest(tail_mutant)
    case('nul_tail_full_buffer_hash_rejected_even_after_isolated_identity_rebind',
         lambda: generic.blend_generic_default_projection(tail_mutant, isolated),
         'Generic-default full buffer hash differs', tail_recipe)

    for label, payload in [('new_case_marker', target.CASE_MARKERS[0]),
                           ('outside_generic_output', target.EFFECTIVE[1])]:
        mutant, fixture = patched(raw, 'original_scene', 171560, payload)
        isolated = target.allowance()
        isolated['sha256'] = digest(mutant)
        isolated['sdna_profile']['blend_sha256'] = digest(mutant)
        def full_scan(mutant=mutant, isolated=isolated):
            projected = generic.blend_generic_default_projection(mutant, isolated)
            target.scan_complete_plain_buffer(target.policy(generic), projected)
        case(label + '_outside_allowed_fields_rejected', full_scan,
             'Private path marker in exact CSV complete buffer', fixture)
    tail_payload = b'/' + b'workspace/' + b'synthetic-control'
    tail_projection, fixture = patched(projection, 'exact_effective_string_projection', tail_offset, tail_payload)
    case('private_nul_tail_bytes_are_scanned',
         lambda: target.scan_complete_plain_buffer(target.policy(generic), tail_projection),
         'Private path marker in exact CSV complete buffer', fixture)
    overmasked = bytearray(projection)
    field = target.PROFILE['field_findings'][0]
    start = field['field_absolute_byte_offset']
    overmasked[start:start + field['field_buffer_bytes']] = b' ' * field['field_buffer_bytes']
    fake_generic = types.SimpleNamespace(**vars(generic))
    fake_generic.blend_generic_default_projection = lambda data, allow: bytes(overmasked)
    case('whole_field_overmask_rejected', lambda: target.scan_blend(raw, fake_generic),
         'Projection changed bytes outside exact effective strings')
    require(json.dumps(target.PROFILE, sort_keys=True) == profile_before, 'Production profile mutated')
    target.read_exact(args.workspace, target.BLEND_PATH, target.BLEND_SHA, target.BLEND_BYTES)
    target.read_exact(args.workspace, target.GENERIC_PATH, target.GENERIC_SHA, target.GENERIC_BYTES)
    require(_read_regular_snapshot(here, CHECKER_NAME, CHECKER_BYTES, 256 * 1024) == source,
            'Checker source changed during controls')
    require(_read_regular_snapshot(here, Path(__file__).name, len(own), 256 * 1024) == own,
            'Control source changed during controls')
    report = {'passed': all(row['passed'] for row in cases), 'case_count': len(cases),
        'optimization_level': sys.flags.optimize, 'logical_input': target.BLEND_LOGICAL_PATH,
        'candidate_sha256': target.BLEND_SHA, 'candidate_bytes': target.BLEND_BYTES,
        'checker_source_sha256': CHECKER_SHA, 'checker_source_bytes': CHECKER_BYTES,
        'generator_source_sha256': digest(own), 'generator_source_bytes': len(own),
        'generic_source_sha256': target.GENERIC_SHA, 'generic_source_bytes': target.GENERIC_BYTES,
        'cases': cases, 'production_profile_unchanged': True,
        'original_scene_and_tool_sources_unchanged': True, 'in_memory_negative_fixtures_only': True,
        'actual_negative_reconstruction_bitwise_comparisons': True,
        'generic_162_case_and_24_case_suites_rerun': False, 'blender_or_render_executed': False,
        'scene_api_resources_checked': False, 'model_go': False, 'publication_go': False}
    with args.out.open('x', encoding='utf8') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'passed': report['passed'], 'case_count': len(cases),
                      'optimization_level': sys.flags.optimize}))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
