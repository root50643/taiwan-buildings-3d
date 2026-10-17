"""Small synthetic controls; no original Blend/CSV read or scene/geometry work.

Run only in the shared CPU slot. Reports bind generator, helper, policy and
synthetic fixture hashes. All decoded spools are private and unnamed.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse
import hashlib
import json
import lzma
import os
import stat
import tempfile
import types
from unittest.mock import patch

HERE = Path(__file__).absolute().parent
CHECKER_SHA = '58e7025590eec9efc7f242552ac22c950fc8e41d41c5eb74051ee323c3a9e950'
CHECKER_BYTES = 12032


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check(condition, message):
    if not condition:
        raise ValueError(message)


def load_checker():
    # The test bootstrap cannot use the checker until its bytes are verified.
    # Walk directory FDs here too; never use a stat-then-path-read bootstrap.
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    directory_fd = os.open('/', flags)
    try:
        for component in HERE.parts[1:]:
            child_fd = os.open(component, flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = child_fd
        fd = os.open('check_wfu_privacy.py', os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                     dir_fd=directory_fd)
    finally:
        os.close(directory_fd)
    try:
        before = os.fstat(fd)
        check(stat.S_ISREG(before.st_mode) and before.st_size == CHECKER_BYTES,
              'Control target checker byte count/type differs')
        with os.fdopen(fd, 'rb') as stream:
            fd = None
            data = stream.read(CHECKER_BYTES + 1)
            after = os.fstat(stream.fileno())
    finally:
        if fd is not None:
            os.close(fd)
    check((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
          == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
          and len(data) == CHECKER_BYTES, 'Control target checker changed during read')
    check(digest(data) == CHECKER_SHA, 'Control target checker source differs')
    m = types.ModuleType('wfu_control_target')
    m.__file__ = str(HERE / 'check_wfu_privacy.py')
    exec(compile(data, m.__file__, 'exec'), m.__dict__)
    return m


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    check(args.out.parent.is_dir() and not args.out.exists() and not args.out.is_symlink(),
          'Fresh output required')
    target = load_checker()
    initial_source = target.source_snapshot(__file__)
    generic, primitive, policy = target.load_tools()
    cases = []

    def case(name, fn, error=None, binding=None):
        accepted = False
        actual_error = None
        try:
            fn()
            accepted = True
        except Exception as exc:
            actual_error = type(exc).__name__ + ': ' + str(exc)
        passed = accepted if error is None else (not accepted and error in actual_error)
        cases.append({'name': name, 'expected_accept': error is None, 'accepted': accepted,
                      'expected_error_substring': error, 'error': actual_error, 'passed': passed,
                      'fixture_binding': binding})

    def fixture(raw, encoded=None, changes=None):
        encoded = lzma.compress(raw, preset=0) if encoded is None else encoded
        profile = {'compressed_bytes': len(encoded), 'compressed_sha256': digest(encoded),
                   'decoded_bytes': len(raw), 'decoded_sha256': digest(raw),
                   'csv_data_rows': raw.count(b'\n') - 1}
        if changes:
            profile.update(changes)
        binding = {'raw_bytes': len(raw), 'raw_sha256': digest(raw),
                   'encoded_bytes': len(encoded), 'encoded_sha256': digest(encoded),
                   'profile': profile}
        return encoded, profile, binding

    def csv_case(name, raw, error=None, encoded=None, changes=None, chunk=31,
                 compressed_must_pass=False):
        encoded, profile, binding = fixture(raw, encoded, changes)
        binding['chunk_bytes'] = chunk
        if compressed_must_pass:
            case(name + '_compressed_buffer_safe',
                 lambda: primitive.scan_complete_plain_buffer(policy, encoded), binding=binding)
        case(name, lambda: primitive.bounded_xz_csv_privacy_scan(policy, encoded, profile, chunk),
             error, binding)

    raw = b'column\n' + b'0123456789,' * 512 + b'\n'
    csv_case('safe_complete_csv', raw)
    case('safe_plain_words', lambda: primitive.scan_complete_plain_buffer(
        policy, b'column,value\npublic,ordinary safe text\n'))
    markers = tuple(policy.PRIVATE_MARKERS) + (policy.TMP_MARKER,) + primitive.ADDITIONAL_PRIVATE_MARKERS
    credentials = (
        b'gh' + b'p_' + b'A' * 36,
        b'sk-' + b'proj-' + b'A' * 40,
        b'xox' + b'b-' + b'A' * 24,
        b'AK' + b'IA' + b'A' * 16,
        b'Authorization: ' + b'Bearer ' + b'A' * 24,
        b'password=' + b'"' + b'A' * 24 + b'"',
        b'-----BEGIN ' + b'RSA PRIVATE KEY-----',
    )
    for category, values, error in (('marker', markers, 'Private path marker'),
                                     ('credential', credentials, 'Credential-shaped content')):
        for index, token in enumerate(values):
            for position, chunk in (('cross_one_byte_output', 1), ('tail', 31)):
                body = (b'0' * 24 + b' ' + token + b' ' + b'0' * 1024
                        if chunk == 1 else b'0' * 1024 + b' ' + token)
                csv_case('%s_%02d_%s' % (category, index, position), b'column\n' + body + b'\n',
                         error, chunk=chunk, compressed_must_pass=True)
    encoded, profile, _ = fixture(raw)
    for name, change, error in (
        ('compressed_short', {'compressed_bytes': len(encoded)-1}, 'size/hash differs'),
        ('compressed_large', {'compressed_bytes': len(encoded)+1}, 'size/hash differs'),
        ('compressed_wrong_hash', {'compressed_sha256': '0'*64}, 'size/hash differs'),
        ('decoded_oversize', {'decoded_bytes': len(raw)-1}, 'exceeds exact byte bound'),
        ('decoded_short', {'decoded_bytes': len(raw)+1}, 'exact size/hash differs'),
        ('decoded_wrong_hash', {'decoded_sha256': '0'*64}, 'exact size/hash differs'),
        ('wrong_rows', {'csv_data_rows': 2}, 'data-row/line count differs'),
        ('zero_decoded_bound', {'decoded_bytes': 0}, 'Invalid exact decoded'),
        ('bool_decoded_bound', {'decoded_bytes': True}, 'Invalid exact decoded'),
        ('raised_decoded_bound', {'decoded_bytes': 194500310}, 'Invalid exact decoded'),
        ('negative_rows', {'csv_data_rows': -1}, 'Invalid exact decoded'),
        ('bool_rows', {'csv_data_rows': True}, 'Invalid exact decoded'),
    ):
        csv_case(name, raw, error, changes=change)
    csv_case('missing_final_newline', raw[:-1], 'data-row/line count differs')
    for name, bad, error in (
        ('trailing_garbage', encoded + b'garbage', 'Trailing'),
        ('trailing_zero_padding', encoded + b'\0'*4, 'Trailing'),
        ('extra_xz_stream', encoded + lzma.compress(b'', preset=0), 'Trailing'),
        ('truncated_xz', encoded[:-1], 'Incomplete single XZ'),
        ('corrupt_xz', b'bad' + encoded[3:], 'LZMAError'),
    ):
        csv_case(name, raw, error, encoded=bad)
    for bad in (0, -1, True, False, 4*1024*1024+1, 1.0, '31'):
        csv_case('invalid_chunk_' + repr(bad), raw, 'Invalid bounded streaming chunk size', chunk=bad)
    for index, token in enumerate((markers[0], credentials[1])):
        csv_case('compressed_plain_pattern_%d' % index, raw,
                 'Private path marker' if index == 0 else 'Credential-shaped content',
                 encoded=b'prefix ' + token)
    case('non_bytes_input_rejected', lambda: primitive.bounded_xz_csv_privacy_scan(
        policy, bytearray(encoded), profile), 'Compressed CSV input')
    case('production_rejects_synthetic_csv', lambda: target.scan_csv(
        encoded, generic, primitive, policy), 'Compressed CSV size/hash differs')
    for key, value in target.CSV_ITEMS:
        bad_profile = dict(target.CSV_ITEMS)
        bad_profile[key] = value + 1 if type(value) is int else '0'*64
        with patch.object(primitive, 'SCIENCE_CSV_PROFILE', bad_profile):
            case('production_profile_tamper_' + key, lambda: target.validate_policy(
                generic, primitive, policy), 'Exact fixed CSV profile differs')
    for key, bad, error in (
        ('MAX_BYTES', policy.MAX_BYTES+1, 'Unchanged generic'),
        ('PRIVATE_MARKERS', (), 'pattern coverage differs'),
        ('SECRET_PATTERNS', (), 'pattern coverage differs'),
        ('TMP_MARKER', b'not-the-marker', 'pattern coverage differs'),
    ):
        with patch.object(policy, key, bad):
            case('production_policy_tamper_' + key, lambda: target.validate_policy(
                generic, primitive, policy), error)
    with patch.object(primitive, 'BLEND', '0'*64):
        case('production_blend_candidate_param_tamper', lambda: target.validate_policy(
            generic, primitive, policy), 'Exact Blend candidate/field profile differs')
    for index, changed in enumerate(([(171625, *target.FIELDS[0][1:]), target.FIELDS[1]],
                                     [target.FIELDS[0], (231956, 1023, target.FIELDS[1][2])],
                                     [target.FIELDS[0], (231956, 1024, '0'*64)])):
        with patch.object(primitive, 'BLEND_FIELDS', changed):
            case('production_blend_field_param_tamper_%d' % index, lambda: target.validate_policy(
                generic, primitive, policy), 'Exact Blend candidate/field profile differs')

    # A separate module instance binds small synthetic field buffers, solely to
    # exercise unchanged mask semantics. This cannot alter production profiles.
    synthetic = target.load_exact_source('exact_privacy_primitives.py', target.PRIMITIVES_SHA)
    blob = bytearray(234000)
    effective_texts = (b'/' + b'home/agent', b'/' + b'tmp/')
    for (offset, _, _), effective in zip(target.FIELDS, effective_texts):
        blob[offset:offset+len(effective)] = effective
    tail_start = target.FIELDS[0][0] + len(effective_texts[0]) + 1
    blob[tail_start:tail_start+29] = b'X'*29
    blob = bytes(blob)

    def bind_synthetic(data):
        synthetic.BLEND = digest(data)
        synthetic.BLEND_FIELDS = [(offset, size, digest(data[offset:offset+size]))
                                  for offset, size, _ in target.FIELDS]

    def synthetic_scan(data):
        projection = synthetic.mask_exact_blend_defaults(data)
        synthetic.scan_complete_plain_buffer(policy, projection)
        check(tuple(map(len, effective_texts)) == (11, 5), 'Synthetic effective text lengths differ')
        for (offset, size, _), length in zip(target.FIELDS, map(len, effective_texts)):
            check(projection[offset+length:offset+size] == data[offset+length:offset+size],
                  'Synthetic NUL tail changed')

    bind_synthetic(blob)
    binding = {'synthetic_bytes': len(blob), 'synthetic_sha256': digest(blob),
               'not_original_blend_or_sdna_validation': True}
    case('synthetic_blend_mask_effective_strings_only', lambda: synthetic_scan(blob), binding=binding)
    case('production_rejects_synthetic_blend', lambda: target.scan_blend(
        blob, generic, primitive, policy), 'Exact original WFU Blend identity differs', binding)
    case('blend_wrong_candidate_hash', lambda: synthetic.mask_exact_blend_defaults(blob+b'x'),
         'Exact Blend privacy profile hash differs', binding)
    for name, offset in (('effective_buffer_changed', 171624), ('nul_tail_changed', 171624+20)):
        changed = bytearray(blob)
        changed[offset] ^= 1
        changed = bytes(changed)
        synthetic.BLEND = digest(changed)  # force the separate full-buffer guard
        case('blend_' + name, lambda: synthetic.mask_exact_blend_defaults(changed),
             'Exact SDNA full-buffer identity differs', binding)
        bind_synthetic(blob)
    synthetic.BLEND_FIELDS[0] = (171625, synthetic.BLEND_FIELDS[0][1], synthetic.BLEND_FIELDS[0][2])
    case('blend_wrong_offset', lambda: synthetic.mask_exact_blend_defaults(blob),
         'Exact SDNA full-buffer identity differs', binding)
    bind_synthetic(blob)
    changed = bytearray(blob)
    changed[171624] = ord('X')
    changed = bytes(changed)
    bind_synthetic(changed)
    case('blend_effective_string_changed_even_after_hash_rebinding',
         lambda: synthetic.mask_exact_blend_defaults(changed),
         'Exact SDNA full-buffer identity differs', binding)
    bind_synthetic(blob)
    duplicate = blob + b'/' + b'home/agent'
    synthetic.BLEND = digest(duplicate)
    case('blend_duplicate_default_elsewhere', lambda: synthetic.mask_exact_blend_defaults(duplicate),
         'Unexpected repeated generic path', binding)
    for index, token in enumerate((markers[0], target.WFU_MARKERS[0], credentials[1])):
        changed = bytearray(blob)
        at = 171624+100
        changed[at:at+len(token)] = token
        changed = bytes(changed)
        bind_synthetic(changed)
        case('blend_nul_tail_pattern_still_scanned_%d' % index, lambda: synthetic_scan(changed),
             'Credential-shaped content' if index == 2 else 'Private path marker',
             {'synthetic_bytes': len(changed), 'synthetic_sha256': digest(changed)})
    case('production_profile_unchanged_after_synthetic_controls',
         lambda: target.validate_policy(generic, primitive, policy))

    # Small, temporary filesystem fixtures only. These call the production
    # reader without weakening its checks or reading either original input.
    with tempfile.TemporaryDirectory(prefix='.small-filesystem-', dir=HERE) as temporary:
        work = Path(temporary)
        safe = b'public synthetic bytes\n'
        binding = {'synthetic_bytes': len(safe), 'synthetic_sha256': digest(safe)}
        (work / 'regular').write_bytes(safe)
        (work / 'parent').mkdir()
        (work / 'parent/regular').write_bytes(safe)
        (work / 'leaf-link').symlink_to('regular')
        (work / 'ancestor-link').symlink_to('parent', target_is_directory=True)
        os.mkfifo(work / 'fifo', mode=0o600)

        def read_fixture(relative, expected_hash=digest(safe), expected_bytes=len(safe), root=work):
            result = target.read_exact(root, relative, expected_hash, expected_bytes)
            check(result == safe, 'Synthetic regular content differs')

        case('filesystem_regular_positive', lambda: read_fixture('parent/regular'), binding=binding)
        case('filesystem_leaf_symlink_rejected', lambda: read_fixture('leaf-link'),
             'Too many levels of symbolic links', binding)
        case('filesystem_ancestor_symlink_rejected', lambda: read_fixture('ancestor-link/regular'),
             'NotADirectoryError', binding)
        case('filesystem_workspace_symlink_rejected',
             lambda: read_fixture('regular', root=work/'ancestor-link'), 'NotADirectoryError', binding)
        real_open = os.open

        def guarded_fifo_open(path, flags, *args, **kwargs):
            # Fail safely if a future regression drops O_NONBLOCK rather than
            # letting this negative test block forever in the kernel.
            if Path(path).name == 'fifo':
                check(flags & os.O_NONBLOCK and flags & os.O_NOFOLLOW
                      and kwargs.get('dir_fd') is not None,
                      'Control requires safe nonblocking descriptor-relative leaf open')
            return real_open(path, flags, *args, **kwargs)

        with patch.object(target.os, 'open', guarded_fifo_open):
            case('filesystem_fifo_rejected_without_blocking', lambda: read_fixture('fifo'),
                 'Exact source byte count/type differs', binding)
        case('filesystem_directory_leaf_rejected', lambda: read_fixture('parent'),
             'Exact source byte count/type differs', binding)
        case('filesystem_wrong_size_rejected', lambda: read_fixture('regular', expected_bytes=len(safe)+1),
             'Exact source byte count/type differs', binding)
        case('filesystem_wrong_hash_rejected', lambda: read_fixture('regular', expected_hash='0'*64),
             'Exact source size/hash differs', binding)
        case('filesystem_missing_leaf_rejected', lambda: read_fixture('missing'),
             'FileNotFoundError', binding)
        case('filesystem_relative_parent_rejected', lambda: read_fixture('../regular'),
             'Unsafe input relative path', binding)
        case('filesystem_workspace_parent_rejected', lambda: read_fixture('regular', root=work/'parent/..'),
             'Unsafe workspace path', binding)
        for invalid in (None, True, 0, -1, 512*1024*1024+1):
            case('filesystem_invalid_exact_bound_' + repr(invalid),
                 lambda: read_fixture('regular', expected_bytes=invalid), 'Invalid exact input byte bound')

        snapshot = target.source_snapshot(work / 'regular')
        case('filesystem_source_snapshot_unchanged_positive',
             lambda: target.require_source_unchanged(work / 'regular', snapshot))
        (work / 'regular').write_bytes(b'Y'*len(safe))
        case('filesystem_source_snapshot_change_rejected',
             lambda: target.require_source_unchanged(work / 'regular', snapshot),
             'Tool self source changed during execution')

        (work / 'swap').mkdir()
        (work / 'swap/regular').write_bytes(safe)
        (work / 'replacement').mkdir()
        (work / 'replacement/regular').write_bytes(b'wrong bytes\n')
        swapped = False

        def swap_opened_ancestor(path, flags, *args, **kwargs):
            nonlocal swapped
            fd = real_open(path, flags, *args, **kwargs)
            if path == 'swap' and kwargs.get('dir_fd') is not None:
                # The real kernel FD is already open before replacing its name.
                (work / 'swap').rename(work / 'pinned-original')
                (work / 'swap').symlink_to('replacement', target_is_directory=True)
                swapped = True
            return fd

        def read_after_swap():
            read_fixture('swap/regular')
            check(swapped, 'Deterministic ancestor replacement did not happen')

        with patch.object(target.os, 'open', swap_opened_ancestor):
            case('filesystem_ancestor_swap_cannot_redirect_open_fd', read_after_swap, binding=binding)
        case('filesystem_later_read_rejects_swapped_symlink', lambda: read_fixture('swap/regular'),
             'NotADirectoryError', binding)

        changing = work / 'changing'
        changing.write_bytes(safe)
        identity = changing.stat()
        real_fstat = os.fstat
        mutated = False

        def mutate_after_initial_fstat(fd):
            nonlocal mutated
            observed = real_fstat(fd)
            if not mutated and (observed.st_dev, observed.st_ino) == (identity.st_dev, identity.st_ino):
                mutated = True
                changing.write_bytes(b'X' * len(safe))
                os.utime(changing, ns=(observed.st_atime_ns, observed.st_mtime_ns + 1_000_000_000))
            return observed

        with patch.object(target.os, 'fstat', mutate_after_initial_fstat):
            case('filesystem_mutation_during_read_rejected', lambda: read_fixture('changing'),
                 'Source changed during read', binding)
        case('filesystem_mutation_injection_exercised',
             lambda: check(mutated, 'Deterministic source mutation did not happen'))
    report = {'passed': all(row['passed'] for row in cases), 'optimization_level': sys.flags.optimize,
              'case_count': len(cases), 'cases': cases, 'synthetic_only': True,
              'original_candidate_or_csv_read': False, 'geometry_or_render_run': False,
              'model_go': False, 'publication_go': False, 'checker_sha256': CHECKER_SHA,
              'test_source_sha256': initial_source['sha256'], 'test_source_bytes': initial_source['bytes'],
              'test_source_unchanged_during_execution': True, 'checker_source_bytes': CHECKER_BYTES,
              'primitive_sha256': target.PRIMITIVES_SHA, 'generic_sha256': target.GENERIC_SHA,
              'scope': 'Synthetic byte/pattern/bounds and small temporary filesystem controls only. Existing original-candidate SDNA controls are independently retained in provenance. These controls do not replace original-file scans or complete scene/API-resource checks.'}
    target.require_source_unchanged(__file__, initial_source)
    target.read_exact(HERE, 'check_wfu_privacy.py', CHECKER_SHA, CHECKER_BYTES)
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({k: report[k] for k in ('passed', 'optimization_level', 'case_count')}))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
