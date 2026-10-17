"""One exact CGUST v10 SDNA/byte-pattern entry. No scene/API or publication GO.
Historical generic source is referenced and SHA-bound, never copied. All inputs
are read-only; only a fresh JSON report is written. No arbitrary case allowance.
Source is prepared, and must be frozen/reviewed before scheduled controls/run.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, hashlib, json, os, re, stat, types

BLEND_PATH = 'cgust-linkou-gym-' + 'private-v1/models/v10/scene.blend'
BLEND_LOGICAL_PATH = 'models/v10/scene.blend'
BLEND_BYTES = 883140
BLEND_SHA = '24405788a4c5bf2e88a2402089f5d7fc9bc6b360afa97cc316760bdf3e668a1b'
GENERIC_PATH = 'wfu-shengyou-independent-qa/public-privacy-v1/package_controls_v2.py'
GENERIC_BYTES = 47569
GENERIC_SHA = '1402e983241d78d19969380b45ce79b7cd3936207a4324710a17b094f5ac256c'
CASE_MARKERS = (b'cgust-linkou-gym-' + b'private-v1', b'cgust-linkou-gym-source-' + b'audit-private',
                b'wfu-shengyou-' + b'private-v1', b'wfu-shengyou-source-' + b'audit-private')
EFFECTIVE = (b'/' + b'home/agent', b'/' + b'tmp/')
PROFILE = {'blend_sha256': '24405788a4c5bf2e88a2402089f5d7fc9bc6b360afa97cc316760bdf3e668a1b', 'version': '403', 'pointer_bytes': 8, 'byte_order': 'little', 'field_findings': [{'classification': 'generic_file_browser_home', 'block_code': 'DATA', 'struct': 'FileSelectParams', 'field': 'dir[1090]', 'field_buffer_bytes': 1090, 'field_buffer_sha256': '2d1dc02e846e766c501535dfda01be83adbdea6d8e03a42e4e5df5377da744d1', 'field_type': 'char', 'field_absolute_byte_offset': 171624, 'marker_absolute_byte_offset': 171624, 'marker_offset_in_field': 0, 'after_first_nul_nonzero_bytes': 29}, {'classification': 'generic_unrendered_output_default', 'block_code': 'SC\x00\x00', 'struct': 'Scene', 'field': 'r.pic[1024]', 'field_buffer_bytes': 1024, 'field_buffer_sha256': 'a27bf0cff013ac91d264ac7f6b87fe91b392cee0ed657588929e56c4f0b4d07d', 'field_type': 'char', 'field_absolute_byte_offset': 231956, 'marker_absolute_byte_offset': 231956, 'marker_offset_in_field': 0, 'after_first_nul_nonzero_bytes': 0}]}

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


ADDITIONAL_PRIVATE_MARKERS = (b'/' + b'home/', b'/' + b'root/', b'/' + b'private/var/',
                              b'GH_CONFIG_' + b'DIR', b'file:' + b'//', b'C:' + b'\\Users\\')


ADDITIONAL_SECRET_PATTERNS = (
    re.compile(rb'(?<![A-Za-z0-9_])(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})(?![A-Za-z0-9_])'),
    re.compile(rb'(?i)(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*["\x27][A-Za-z0-9_+/=-]{20,}["\x27]'))


def scan_complete_plain_buffer(module, buffer):
    """Full bytes/mmap search; never use membership iteration on an mmap."""
    markers = tuple(module.PRIVATE_MARKERS) + (module.TMP_MARKER,) + ADDITIONAL_PRIVATE_MARKERS
    require(all(buffer.find(marker) < 0 for marker in markers),
            'Private path marker in exact CSV complete buffer')
    patterns = tuple(module.SECRET_PATTERNS) + ADDITIONAL_SECRET_PATTERNS
    require(all(pattern.search(buffer) is None for pattern in patterns),
            'Credential-shaped content in exact CSV complete buffer')


def load_generic(workspace):
    data = read_exact(workspace, GENERIC_PATH, GENERIC_SHA, GENERIC_BYTES)
    module = types.ModuleType('verified_unchanged_generic_privacy')
    module.__file__ = str(Path(workspace) / GENERIC_PATH)
    exec(compile(data, module.__file__, 'exec'), module.__dict__)
    return module


def policy(generic):
    require(generic.MAX_BYTES == 512 * 1024 * 1024, 'Generic byte bound differs')
    return types.SimpleNamespace(MAX_BYTES=generic.MAX_BYTES,
        PRIVATE_MARKERS=generic.PRIVATE_MARKERS + CASE_MARKERS,
        TMP_MARKER=generic.TMP_MARKER, SECRET_PATTERNS=generic.SECRET_PATTERNS)


def allowance():
    # Fresh objects for the immutable case identity, never caller-provided data.
    return {'kind': 'blend_generic_defaults', 'sha256': BLEND_SHA,
            'bytes': BLEND_BYTES, 'sdna_profile': json.loads(json.dumps(PROFILE))}


def scan_blend(data, generic):
    require(type(data) is bytes and len(data) == BLEND_BYTES and digest(data) == BLEND_SHA,
            'Exact CGUST v10 candidate identity differs')
    require(PROFILE['blend_sha256'] == BLEND_SHA, 'Internal profile identity differs')
    projected = generic.blend_generic_default_projection(data, allowance())
    cursor = 0
    total = 0
    for field, effective in zip(PROFILE['field_findings'], EFFECTIVE):
        start = field['field_absolute_byte_offset']
        size = field['field_buffer_bytes']
        raw = data[start:start + size]
        require(len(raw) == size and digest(raw) == field['field_buffer_sha256']
                and raw.partition(b'\0')[0] == effective and data.count(effective) == 1,
                'Exact complete field/effective multiplicity differs')
        effective_length = len(raw.partition(b'\0')[0])
        require(projected[cursor:start] == data[cursor:start]
                and projected[start:start + effective_length] == b' ' * effective_length,
                'Projection changed bytes outside exact effective strings')
        cursor = start + effective_length
        total += effective_length
    require(projected[cursor:] == data[cursor:] and total == sum(len(x) for x in EFFECTIVE),
            'Projection tail or exact effective extent differs')
    scan_complete_plain_buffer(policy(generic), projected)
    return {'original_bytes': len(data), 'original_sha256': digest(data),
            'source_logical_path': BLEND_LOGICAL_PATH,
            'exact_profile': json.loads(json.dumps(PROFILE)), 'masked_effective_bytes': total,
            'entire_projection_scanned_including_all_nul_tails': True,
            'all_other_original_bytes_unchanged': True, 'projection_written': False,
            'original_has_zero_paths_claimed': False}


def main():
    initial = source_snapshot(__file__)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(args.out.parent.is_dir() and not args.out.exists() and not args.out.is_symlink(),
            'Fresh report required')
    generic = load_generic(args.workspace)
    data = read_exact(args.workspace, BLEND_PATH, BLEND_SHA, BLEND_BYTES)
    checked = scan_blend(data, generic)
    read_exact(args.workspace, BLEND_PATH, BLEND_SHA, BLEND_BYTES)
    read_exact(args.workspace, GENERIC_PATH, GENERIC_SHA, GENERIC_BYTES)
    require_source_unchanged(__file__, initial)
    report = {'passed': True, 'completed': True, 'optimization_level': sys.flags.optimize,
        'checker_source_sha256': initial['sha256'], 'checker_source_bytes': initial['bytes'],
        'generic_source_sha256': GENERIC_SHA, 'generic_source_bytes': GENERIC_BYTES,
        'original_scene_and_tool_bytes_unchanged': True, 'checked': checked,
        'scene_api_resources_checked': False, 'model_go': False, 'publication_go': False,
        'scope': 'One exact original scene SDNA and complete byte-pattern projection only; source/scene API, render and publication gates remain separate.'}
    with args.out.open('x', encoding='utf8') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'passed': True, 'checked': BLEND_LOGICAL_PATH,
                      'model_go': False, 'publication_go': False}))


if __name__ == '__main__':
    main()
