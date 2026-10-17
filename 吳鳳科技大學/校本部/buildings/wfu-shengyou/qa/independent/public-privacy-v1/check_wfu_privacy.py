"""Read-only exact WFU byte/pattern checks; never a publication/science gate.

Source bytes are authenticated and compiled in memory, ignoring stale pyc files.
Inputs are opened read-only. The only persistent output is a fresh JSON report.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse
import hashlib
import json
import os
import stat
import types

HERE = Path(__file__).absolute().parent
GENERIC_SHA = '1402e983241d78d19969380b45ce79b7cd3936207a4324710a17b094f5ac256c'
PRIMITIVES_SHA = '1b8f3d36243bdd1bc090bbf1dffa55e9f80d803bce73c2354efb7f466b15f6cd'
BLEND_SHA = '70d8914cefaaceac8572d00c6cfba52b5abbedd18c810175f2deedb47ed2c429'
BLEND_BYTES = 1827468
BLEND_PATH = 'models/v13/scene.blend'
CSV_PATH = 'qa/v12-full/normal/standard/dense/dense-original.csv.xz'
CSV_ITEMS = (
    ('compressed_bytes', 19156984),
    ('compressed_sha256', '80cf38d8255e789755e316a24638872db0fb913f2d37795edd3c81349551f550'),
    ('decoded_bytes', 194500309),
    ('decoded_sha256', '6408a97da82dc7a1e226225637a415d6cd8ecaecfb962e51454f52bc3067f2b6'),
    ('csv_data_rows', 209460),
)
FIELDS = (
    (171624, 1090, '2d1dc02e846e766c501535dfda01be83adbdea6d8e03a42e4e5df5377da744d1'),
    (231956, 1024, 'a27bf0cff013ac91d264ac7f6b87fe91b392cee0ed657588929e56c4f0b4d07d'),
)
WFU_MARKERS = (b'wfu-shengyou-' + b'private-v1', b'wfu-shengyou-source-' + b'audit-private')
SCOPE = ('Two exact original-file identities and complete byte/pattern privacy checks only. '
         'Known complete Blend buffers retain all NUL-tail bytes. This does not assert '
         'zero paths in the original Blend or inspect scene/API resources. Full scene '
         'resource inspection, numerical CSV predicates, source review, model approval '
         'and publication approval remain independent requirements.')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_exact_source(name, expected):
    path = HERE / name
    sizes = {'package_controls_v2.py': 47569, 'exact_privacy_primitives.py': 6783}
    require(name in sizes, 'Unknown fixed tool source')
    data = read_exact(HERE, name, expected, sizes[name])
    module = types.ModuleType('wfu_verified_' + path.stem)
    module.__file__ = str(path)
    exec(compile(data, str(path), 'exec'), module.__dict__)
    return module


def load_tools():
    generic = load_exact_source('package_controls_v2.py', GENERIC_SHA)
    primitive = load_exact_source('exact_privacy_primitives.py', PRIMITIVES_SHA)
    # Only add WFU directory markers; never mutate the original generic module.
    policy = types.SimpleNamespace(MAX_BYTES=generic.MAX_BYTES,
        PRIVATE_MARKERS=generic.PRIVATE_MARKERS + WFU_MARKERS,
        TMP_MARKER=generic.TMP_MARKER, SECRET_PATTERNS=generic.SECRET_PATTERNS)
    validate_policy(generic, primitive, policy)
    return generic, primitive, policy


def validate_policy(generic, primitive, policy):
    require(type(generic.MAX_BYTES) is int and generic.MAX_BYTES == 512 * 1024 * 1024
            and type(policy.MAX_BYTES) is int and policy.MAX_BYTES == generic.MAX_BYTES,
            'Unchanged generic MAX_BYTES required')
    require(policy.PRIVATE_MARKERS == generic.PRIVATE_MARKERS + WFU_MARKERS
            and policy.TMP_MARKER == generic.TMP_MARKER
            and policy.SECRET_PATTERNS == generic.SECRET_PATTERNS,
            'Original privacy pattern coverage differs')
    require(primitive.BLEND == BLEND_SHA and tuple(primitive.BLEND_FIELDS) == FIELDS,
            'Exact Blend candidate/field profile differs')
    p = primitive.SCIENCE_CSV_PROFILE
    require(type(p) is dict and p == dict(CSV_ITEMS)
            and all(type(p[key]) is type(value) for key, value in CSV_ITEMS),
            'Exact fixed CSV profile differs')


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


def read_exact(workspace, relative, expected_sha, expected_bytes):
    """Production input/tool reader always requires exact size and SHA256."""
    require(type(expected_bytes) is int and 0 < expected_bytes <= 512 * 1024 * 1024,
            'Invalid exact input byte bound')
    data = _read_regular_snapshot(workspace, relative, expected_bytes, 512 * 1024 * 1024)
    require(len(data) == expected_bytes and digest(data) == expected_sha,
            'Exact source size/hash differs')
    return data


def source_snapshot(path):
    """Bounded, FD-safe self-code identity at startup and before result output."""
    path = Path(path).absolute()
    data = _read_regular_snapshot(path.parent, path.name, None, 256 * 1024)
    return {'bytes': len(data), 'sha256': digest(data)}


def require_source_unchanged(path, initial):
    require(source_snapshot(path) == initial, 'Tool self source changed during execution')


def scan_blend(data, generic, primitive, policy):
    validate_policy(generic, primitive, policy)
    require(type(data) is bytes and len(data) == BLEND_BYTES and digest(data) == BLEND_SHA,
            'Exact original WFU Blend identity differs')
    projection = primitive.mask_exact_blend_defaults(data)
    # Authenticate both full buffers first; mask only their effective strings.
    # NUL terminators, all NUL tails and all other bytes are identical and scanned.
    lengths = tuple(len(data[offset:offset + size].split(b'\0', 1)[0])
                    for offset, size, _ in FIELDS)
    cursor = 0
    for (offset, size, h), text_length in zip(FIELDS, lengths):
        require(projection[cursor:offset] == data[cursor:offset],
                'Projection changed bytes outside exact effective text')
        require(projection[offset:offset + text_length] == b'_' * text_length,
                'Projection effective mask differs')
        cursor = offset + text_length
    require(projection[cursor:] == data[cursor:], 'Projection changed final untouched bytes')
    primitive.scan_complete_plain_buffer(policy, projection)
    return {'source_path': BLEND_PATH, 'bytes': len(data), 'sha256': digest(data),
            'complete_projection_buffer_scanned': True, 'masked_effective_bytes': sum(lengths),
            'complete_known_buffers_bound': [
                {'offset': offset, 'bytes': size, 'sha256': h,
                 'after_first_nul_nonzero_bytes': sum(x != 0 for x in data[offset:offset+size].split(b'\0', 1)[1])}
                for offset, size, h in FIELDS],
            'all_other_bytes_including_nul_tails_scanned_unchanged': True,
            'projection_written_or_published': False,
            'original_blend_zero_paths_claimed': False, 'scene_api_resources_checked': False}


def scan_csv(data, generic, primitive, policy, chunk_bytes=1024 * 1024):
    validate_policy(generic, primitive, policy)
    # There is no caller-supplied profile or allowlist in this production entry.
    result = primitive.bounded_xz_csv_privacy_scan(policy, data, dict(CSV_ITEMS), chunk_bytes)
    return dict(result, source_path=CSV_PATH, decoded_newline_count=209461,
                exact_decoded_bound_bytes=194500309)


def main():
    initial_source = source_snapshot(__file__)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=Path.cwd())
    parser.add_argument('--only', choices=('all', 'blend', 'csv'), default='all')
    parser.add_argument('--out', type=Path, required=True, help='Fresh JSON path; parent must already exist')
    args = parser.parse_args()
    require(args.out.parent.is_dir() and not args.out.exists() and not args.out.is_symlink(),
            'Fresh output required')
    generic, primitive, policy = load_tools()
    checks = {}
    if args.only in ('all', 'blend'):
        data = read_exact(args.workspace, BLEND_PATH, BLEND_SHA, BLEND_BYTES)
        checks['blend'] = scan_blend(data, generic, primitive, policy)
        del data
    if args.only in ('all', 'csv'):
        p = dict(CSV_ITEMS)
        data = read_exact(args.workspace, CSV_PATH, p['compressed_sha256'], p['compressed_bytes'])
        checks['csv'] = scan_csv(data, generic, primitive, policy)
        del data
    # Input was read-only. After scanning, re-read exact compressed/original inputs
    # to establish that the source paths still contain their authenticated bytes.
    for relative, h, size in ((BLEND_PATH, BLEND_SHA, BLEND_BYTES),
                             (CSV_PATH, dict(CSV_ITEMS)['compressed_sha256'], dict(CSV_ITEMS)['compressed_bytes'])):
        if (relative == BLEND_PATH and 'blend' in checks) or (relative == CSV_PATH and 'csv' in checks):
            read_exact(args.workspace, relative, h, size)
    result = {'passed': True, 'completed': True, 'optimization_level': sys.flags.optimize,
              'checked': checks, 'original_input_bytes_unchanged': True,
              'generic_MAX_BYTES': generic.MAX_BYTES, 'generic_source_sha256': GENERIC_SHA,
              'primitive_source_sha256': PRIMITIVES_SHA, 'checker_source_sha256': initial_source['sha256'],
              'checker_source_bytes': initial_source['bytes'], 'checker_source_unchanged_during_execution': True,
              'all_original_patterns_plus_common_and_wfu_markers': True,
              'model_go': False, 'publication_go': False, 'scope': SCOPE,
              'author_independent_normal_optimized_copy_map_checked': False}
    require_source_unchanged(__file__, initial_source)
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'passed': True, 'checked': sorted(checks), 'report': str(args.out)}))


if __name__ == '__main__':
    main()
