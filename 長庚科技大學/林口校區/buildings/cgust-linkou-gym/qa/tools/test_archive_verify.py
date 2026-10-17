#!/usr/bin/env python3
"""Tiny synthetic controls only. Run with Python and Python -O in new --out dirs."""
import argparse
import copy
import hashlib
import importlib.util
import io
import json
import lzma
import os
from pathlib import Path
import stat
import subprocess
import sys
import tarfile


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def make_tar(entries):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w', format=tarfile.USTAR_FORMAT) as archive:
        for name, data in entries:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            info.uid = info.gid = info.mtime = 0
            info.uname = info.gname = ''
            archive.addfile(info, io.BytesIO(data))
    return stream.getvalue()


def repair_header(raw, offset=0):
    raw = bytearray(raw)
    raw[offset + 148:offset + 156] = b'        '
    checksum = sum(raw[offset:offset + 512])
    raw[offset + 148:offset + 156] = ('%06o\0 ' % checksum).encode('ascii')
    return bytes(raw)


def field(raw, start, width, value):
    changed = bytearray(raw)
    changed[start:start + width] = value.ljust(width, b'\0')
    return repair_header(changed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    root = Path(args.out)
    root.mkdir(parents=False, exist_ok=False)
    tool = Path(__file__).with_name('archive_verify.py')
    entries = [('alpha.txt', b'alpha\n'), ('nested/beta.bin', bytes(range(32))),
               ('nested/empty', b'')]
    original_tar = make_tar(entries)
    results = []

    def case(label, tar=original_tar, success=False, mutate_index=None,
             archive_transform=None, rewrite_hash=True, out_mode='new', raw_index=None):
        directory = root / label
        directory.mkdir()
        archive_bytes = lzma.compress(tar, format=lzma.FORMAT_XZ, preset=0)
        original_archive_hash = sha(archive_bytes)
        if archive_transform:
            archive_bytes = archive_transform(archive_bytes)
        index = {'format': 'original-stl-controls-ustar-xz-v1',
                 'archive_sha256': sha(archive_bytes) if rewrite_hash else original_archive_hash,
                 'tar_sha256': sha(tar),
                 'members': [{'path': name, 'bytes': len(data), 'sha256': sha(data)}
                             for name, data in entries]}
        if mutate_index:
            mutate_index(index)
        (directory / 'controls.tar.xz').write_bytes(archive_bytes)
        index_bytes = (json.dumps(index, sort_keys=True) + '\n').encode()
        if raw_index:
            index_bytes = raw_index(index_bytes)
        (directory / 'index.json').write_bytes(index_bytes)
        output = directory / 'extracted'
        target = None
        if out_mode == 'existing':
            output.mkdir()
            (output / 'sentinel').write_bytes(b'unchanged')
        elif out_mode == 'symlink':
            target = directory / 'target'
            target.mkdir()
            output.symlink_to('target', target_is_directory=True)
        elif out_mode == 'ancestor_symlink':
            target = directory / 'target'
            target.mkdir()
            (directory / 'linked').symlink_to('target', target_is_directory=True)
            output = directory / 'linked' / 'extracted'
        elif out_mode == 'untrusted_parent':
            directory.chmod(0o777)
        command = [sys.executable] + (['-O'] if sys.flags.optimize else []) + [
            str(tool), '--archive', str(directory / 'controls.tar.xz'),
            '--index', str(directory / 'index.json')]
        if out_mode != 'none':
            command += ['--out', str(output)]
        run = subprocess.run(command, capture_output=True, text=True, env={
            **os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONOPTIMIZE': ''})
        report = json.loads(run.stdout)
        check((run.returncode == 0) == success, label + ': unexpected exit ' + run.stdout)
        check(report.get('passed') is success, label + ': unexpected passed field')
        if success and out_mode == 'new':
            actual = sorted(p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file())
            check(actual == [name for name, _ in entries], label + ': extracted membership')
            for name, data in entries:
                path = output / name
                check(path.read_bytes() == data, label + ': extracted bytes')
                check(stat.S_IMODE(path.stat().st_mode) == 0o644, label + ': extracted mode')
                check(path.stat().st_mtime_ns == 0, label + ': extracted mtime')
        elif out_mode == 'existing':
            check(list(output.iterdir()) == [output / 'sentinel'] and
                  (output / 'sentinel').read_bytes() == b'unchanged', label + ': existing output changed')
        elif out_mode in ('symlink', 'ancestor_symlink'):
            check(not list(target.iterdir()), label + ': escaped through symlink')
        else:
            check(not output.exists(), label + ': output created before acceptance')
        record = {'case': label, 'expected_accept': success, 'returncode': run.returncode,
                  'report': report, 'passed': True}
        (directory / 'result.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
        results.append(record)

    case('valid_read_only', success=True, out_mode='none')
    case('valid_extract', success=True)
    case('existing_output', out_mode='existing')
    case('existing_output_symlink', out_mode='symlink')
    case('ancestor_symlink', out_mode='ancestor_symlink')
    case('untrusted_output_parent', out_mode='untrusted_parent')
    case('compressed_corruption', archive_transform=lambda b: b[:20] + bytes([b[20] ^ 1]) + b[21:])
    case('compressed_truncation', archive_transform=lambda b: b[:-8])
    case('extra_xz_stream', archive_transform=lambda b: b + lzma.compress(b'', preset=0))
    case('xz_trailing_zero_padding', archive_transform=lambda b: b + b'\0' * 4)
    case('xz_trailing_garbage', archive_transform=lambda b: b + b'garbage')
    case('wrong_archive_hash', mutate_index=lambda d: d.update(archive_sha256='0' * 64))
    case('wrong_tar_hash', mutate_index=lambda d: d.update(tar_sha256='0' * 64))
    case('wrong_member_hash', mutate_index=lambda d: d['members'][0].update(sha256='0' * 64))
    case('wrong_member_size', mutate_index=lambda d: d['members'][0].update(bytes=7))
    case('boolean_member_size', mutate_index=lambda d: d['members'][0].update(bytes=True))
    case('missing_tar_member', tar=make_tar(entries[:-1]))
    case('extra_tar_member', tar=make_tar(entries + [('z-extra', b'new')]))
    case('member_substitution', tar=make_tar([('alpha.txt', b'ALPHA\n')] + entries[1:]))
    case('duplicate_tar_member', tar=make_tar([entries[0], entries[0]] + entries[1:]))
    case('tar_member_order', tar=make_tar(list(reversed(entries))))
    case('index_missing_member', mutate_index=lambda d: d['members'].pop())
    case('index_extra_member', mutate_index=lambda d: d['members'].append(
        {'path': 'z-extra', 'bytes': 0, 'sha256': sha(b'')}))
    case('index_duplicate_member', mutate_index=lambda d: d['members'].insert(0, copy.deepcopy(d['members'][0])))
    case('index_unsorted', mutate_index=lambda d: d['members'].reverse())
    case('index_extra_field', mutate_index=lambda d: d.update(unexpected=True))
    case('index_duplicate_json_key', raw_index=lambda b: b.replace(b'"format":', b'"format":"ignored","format":', 1))
    for label, name in [('absolute', '/escape'), ('dotdot', '../escape'),
                        ('backslash', 'nested\\escape'), ('dot', 'nested/./escape'),
                        ('empty_component', 'nested//escape'), ('drive', 'C:/escape')]:
        case('unsafe_index_' + label, mutate_index=lambda d, n=name: d['members'][0].update(path=n))
        case('unsafe_tar_' + label, tar=field(original_tar, 0, 100, name.encode()))
    def prefix_collision(index):
        index['members'][1]['path'] = 'alpha.txt/child'
    case('index_prefix_collision', mutate_index=prefix_collision)
    for label, start, width, value in [
        ('mode', 100, 8, b'0000600\0'), ('uid', 108, 8, b'0000001\0'),
        ('gid', 116, 8, b'0000001\0'), ('mtime', 136, 12, b'00000000001\0'),
        ('uname', 265, 32, b'root'), ('gname', 297, 32, b'root'),
        ('devmajor', 329, 8, b'0000001\0'), ('reserved', 500, 12, b'x'),
        ('linkname', 157, 100, b'target'), ('magic', 257, 8, b'ustar  \0'),
        ('binary_size', 124, 12, b'\x80' + b'\0' * 10 + b'\x06')]:
        case('metadata_' + label, tar=field(original_tar, start, width, value))
    for label, flag in [('symlink', b'2'), ('hardlink', b'1'), ('directory', b'5'),
                        ('pax', b'x'), ('global_pax', b'g'), ('gnu_longname', b'L'),
                        ('nul_typeflag', b'\0')]:
        case('forbidden_type_' + label, tar=field(original_tar, 156, 1, flag))
    bad = bytearray(original_tar)
    bad[0] ^= 1
    case('header_checksum', tar=bytes(bad))
    bad = bytearray(original_tar)
    bad[512 + len(entries[0][1])] = 1
    case('member_padding', tar=bytes(bad))
    case('missing_tar_terminator', tar=original_tar[:2560])
    case('one_block_tar_terminator', tar=original_tar[:3072])
    case('non_block_tar_length', tar=original_tar[:-1])
    case('tar_trailing_nonzero', tar=original_tar + b'x' + b'\0' * 511)
    # Exercise the real streaming limit with a tiny ceiling, not a 512 MiB allocation.
    spec = importlib.util.spec_from_file_location('archive_verify_under_test', tool)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    check(module.MAX_TAR_BYTES == 512 * 1024 * 1024, 'production decompression limit')
    module.MAX_TAR_BYTES = 4096
    try:
        module.read_xz(root / 'valid_read_only' / 'controls.tar.xz')
    except ValueError as error:
        check('exceeds' in str(error), 'unexpected reduced-limit rejection')
        results.append({'case': 'streaming_decompression_limit_reduced', 'passed': True,
                        'expected_accept': False, 'error': str(error)})
    else:
        raise RuntimeError('reduced decompression limit not enforced')
    summary = {'tool': tool.name, 'tool_sha256': sha(tool.read_bytes()),
               'python_optimized': bool(sys.flags.optimize), 'passed': True,
               'case_count': len(results), 'cases': results}
    (root / 'results.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({key: value for key, value in summary.items() if key != 'cases'}, sort_keys=True))


if __name__ == '__main__':
    main()
