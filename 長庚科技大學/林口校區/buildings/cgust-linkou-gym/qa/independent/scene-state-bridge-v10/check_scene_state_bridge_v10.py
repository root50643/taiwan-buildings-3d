"""Exact CGUST v10 author and independent scene-state bridge.
Only six observed logical aliases and two exact original identities are accepted.
No original JSON is rewritten; only five exact effective bytes are projected in
memory. Generic privacy patterns remain intact. No Blender or geometry work.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, hashlib, json, os, re, stat, types

SCENE_SHA = '24405788a4c5bf2e88a2402089f5d7fc9bc6b360afa97cc316760bdf3e668a1b'
RENDER_SOURCE_SHA = 'cabfec873a72c95839be293b7c7adec8ba8bfb7637de9d88450e92b5d259c9d6'
RENDER_MANIFEST_SHA = '14c96f51669a14bea78e75a10f0da42bcede3b9b86f6e18901700636660d4c21'
SCENE_CHECKER_SHA = '5e5c7e80cc4c6bf7e7a803cb76f5c8337bab73405935e8f5a39b1859a6873996'
PREFIXES = {'author': 'cgust-linkou-gym-' + 'private-v1/qa/render-check/v10-author/source-scene/',
            'independent': 'cgust-linkou-gym-independent-qa/run-v10/source-scene-reproduction/'}
AUDITS = {'author': {'bytes': 1894, 'sha256': '286609afc475b540c09884386a702675c43c0d17bfb2b4af2756114ca9a2c701', 'generated_blend_sha256': 'f2d1dbf860049055add2080a7dc93a823ae986d14658be3c191981e071e48f3f'}, 'independent': {'bytes': 1894, 'sha256': '65b791f43a07fa921cbb7de83a353cbad9cbc7911fc7e8a9d40f5378e994c5aa', 'generated_blend_sha256': '0017b4e0e2648a671dbc8d908802c48dd1a8bf034ea699e7b09be572a1193c8d'}}
INPUT_FILES = {'author.original': 'original-scene-state.json', 'author.source_memory': 'source-constructed-memory-state.json', 'author.source_saved': 'source-scene-state.json', 'independent.original': 'original-scene-state.json', 'independent.source_memory': 'source-constructed-memory-state.json', 'independent.source_saved': 'source-scene-state.json'}
TABLE_PATH = 'cgust-linkou-gym-independent-qa/scene-state-bridge-v10/SOURCE-STATE-DEFAULT-EXCEPTIONS.json'
TABLE_BYTES = 7377
TABLE_SHA = 'c44d4f95d3bc8ab3e9408624ee3ed2873f92875481d0f87a7ef2e60f5e8b4a3f'
GENERIC_PATH = 'wfu-shengyou-independent-qa/public-privacy-v1/package_controls_v2.py'
GENERIC_BYTES = 47569
GENERIC_SHA = '1402e983241d78d19969380b45ce79b7cd3936207a4324710a17b094f5ac256c'
CASE_MARKERS = (b'cgust-linkou-gym-' + b'private-v1', b'cgust-linkou-gym-source-' + b'audit-private',
                b'wfu-shengyou-' + b'private-v1', b'wfu-shengyou-source-' + b'audit-private')
ROWS = {'author.original': {'bytes': 120264, 'sha256': '0e03d8ce76b8a040925bdf70d0a93b94f17c043000866f32cb33b8e2a1f694e7', 'json_pointer': '/render/filepath', 'exact_type': 'string', 'exact_value_utf8_hex': '2f746d702f', 'encoded_json_string_offset': 108037, 'encoded_json_string_bytes': 7, 'marker_offset': 108038, 'marker_bytes': 5, 'encoded_string_occurrences': 1, 'marker_occurrences': 1}, 'author.source_memory': {'bytes': 120263, 'sha256': '3c5ecbeb2109c40e0ba7662907d116725986d4e25d82a47ad3f0922ccde5ac73', 'json_pointer': '/render/filepath', 'exact_type': 'string', 'exact_value_utf8_hex': '2f746d702f', 'encoded_json_string_offset': 108037, 'encoded_json_string_bytes': 7, 'marker_offset': 108038, 'marker_bytes': 5, 'encoded_string_occurrences': 1, 'marker_occurrences': 1}, 'author.source_saved': {'bytes': 120264, 'sha256': '0e03d8ce76b8a040925bdf70d0a93b94f17c043000866f32cb33b8e2a1f694e7', 'json_pointer': '/render/filepath', 'exact_type': 'string', 'exact_value_utf8_hex': '2f746d702f', 'encoded_json_string_offset': 108037, 'encoded_json_string_bytes': 7, 'marker_offset': 108038, 'marker_bytes': 5, 'encoded_string_occurrences': 1, 'marker_occurrences': 1}, 'independent.original': {'bytes': 120264, 'sha256': '0e03d8ce76b8a040925bdf70d0a93b94f17c043000866f32cb33b8e2a1f694e7', 'json_pointer': '/render/filepath', 'exact_type': 'string', 'exact_value_utf8_hex': '2f746d702f', 'encoded_json_string_offset': 108037, 'encoded_json_string_bytes': 7, 'marker_offset': 108038, 'marker_bytes': 5, 'encoded_string_occurrences': 1, 'marker_occurrences': 1}, 'independent.source_memory': {'bytes': 120263, 'sha256': '3c5ecbeb2109c40e0ba7662907d116725986d4e25d82a47ad3f0922ccde5ac73', 'json_pointer': '/render/filepath', 'exact_type': 'string', 'exact_value_utf8_hex': '2f746d702f', 'encoded_json_string_offset': 108037, 'encoded_json_string_bytes': 7, 'marker_offset': 108038, 'marker_bytes': 5, 'encoded_string_occurrences': 1, 'marker_occurrences': 1}, 'independent.source_saved': {'bytes': 120264, 'sha256': '0e03d8ce76b8a040925bdf70d0a93b94f17c043000866f32cb33b8e2a1f694e7', 'json_pointer': '/render/filepath', 'exact_type': 'string', 'exact_value_utf8_hex': '2f746d702f', 'encoded_json_string_offset': 108037, 'encoded_json_string_bytes': 7, 'marker_offset': 108038, 'marker_bytes': 5, 'encoded_string_occurrences': 1, 'marker_occurrences': 1}}

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


def state_projection(data, row, generic):
    """Authenticate whole JSON and one original typed pointer, mask five bytes."""
    require(len(data) == row['bytes'] and digest(data) == row['sha256'], 'State identity differs')
    value = generic.load_json_bytes(data)
    marker = bytes.fromhex(row['exact_value_utf8_hex'])
    require(type(value) is dict and type(value.get('render')) is dict
            and type(value['render'].get('filepath')) is str
            and value['render']['filepath'].encode() == marker, 'State typed pointer differs')
    literal = b'"' + marker + b'"'
    offset = row['marker_offset']
    require(len(marker) == 5 and data[row['encoded_json_string_offset']:offset+5+1] == literal
            and data.count(literal) == 1 and data.count(marker) == 1, 'State exact literal/offset differs')
    result = bytearray(data)
    result[offset:offset+5] = b'_'*5
    return bytes(result)


def pin_row(logical, row):
    require(logical in ROWS and type(row) is dict and row == ROWS[logical]
            and all(type(row[key]) is type(value) for key, value in ROWS[logical].items()),
            'Exact case row/type/range pin differs')
    require(row['json_pointer'] == '/render/filepath' and row['exact_type'] == 'string'
            and row['exact_value_utf8_hex'] == '2f746d702f'
            and row['encoded_json_string_bytes'] == 7 and row['marker_bytes'] == 5
            and row['encoded_string_occurrences'] == row['marker_occurrences'] == 1,
            'Unsupported typed field scope')


def scan_state(data, logical, generic):
    require(logical in INPUT_FILES, 'Unknown exact logical alias')
    row = json.loads(json.dumps(ROWS[logical]))
    pin_row(logical, row)
    projected = state_projection(data, row, generic)
    start = row['marker_offset']
    raw_value = generic.load_json_bytes(data)['render']['filepath'].encode('utf8')
    length = len(raw_value)
    require(length == row['marker_bytes'] and projected[:start] == data[:start]
            and projected[start:start + length] == b'_' * length
            and projected[start + length:] == data[start + length:],
            'Projection changed bytes outside exact effective value')
    scan_complete_plain_buffer(policy(generic), projected)
    return {'logical_alias': logical, 'original_bytes': len(data), 'original_sha256': digest(data),
            'exact_typed_field': row, 'masked_bytes': length,
            'entire_other_original_bytes_scanned_unchanged': True,
            'projection_written': False, 'original_has_zero_paths_claimed': False}


def validate_audit(data, domain, generic):
    require(domain in AUDITS, 'Unknown exact audit domain')
    expected = AUDITS[domain]
    require(len(data) == expected['bytes'] and digest(data) == expected['sha256'],
            'Exact audit identity differs')
    value = generic.load_json_bytes(data)
    require(type(value) is dict and value.get('passed') is True
            and value.get('original_blend_sha256') == SCENE_SHA
            and value.get('source_sha256') == RENDER_SOURCE_SHA
            and value.get('manifest_sha256') == RENDER_MANIFEST_SHA
            and value.get('checker_sha256') == SCENE_CHECKER_SHA
            and value.get('generated_blend_sha256') == expected['generated_blend_sha256']
            and value.get('exact_scene_state_matches') is True
            and type(value.get('state_difference_count')) is int and value['state_difference_count'] == 0
            and value.get('state_differences') == []
            and value.get('source_construction_to_saved_reload_differences') ==
                ['/world/nodes/rna/is_runtime_data: value differs']
            and all(value.get(key) is True for key in ('source_unchanged', 'original_blend_unchanged',
                                                     'manifest_unchanged', 'all_nine_camera_definitions_match')),
            'Scene/source binding predicates differ')
    return {'logical_domain': domain, 'bytes': len(data), 'sha256': digest(data),
            'original_scene_sha256': SCENE_SHA, 'render_source_sha256': RENDER_SOURCE_SHA,
            'manifest_sha256': RENDER_MANIFEST_SHA, 'checker_sha256': SCENE_CHECKER_SHA,
            'saved_reload_state_equal': True, 'constructed_memory_equals_saved_claimed': False,
            'construction_to_saved_runtime_flag_difference_count': 1}


def bind_table(data, generic):
    require(len(data) == TABLE_BYTES and digest(data) == TABLE_SHA, 'Exact bridge table identity differs')
    value = generic.load_json_bytes(data)
    require(value['schema'] == 'cgust-source-state-exact-generic-default-scan-exceptions-v1'
            and value['original_blend_sha256'] == SCENE_SHA and len(value['files']) == 6,
            'Bridge table scope differs')
    by_logical = {}
    for entry in value['files']:
        domain = entry['source_root']
        require(domain in PREFIXES, 'Unknown table domain')
        name = entry['source_relative_path'].rsplit('/', 1)[-1]
        matches = [key for key, filename in INPUT_FILES.items()
                   if key.startswith(domain + '.') and filename == name]
        require(len(matches) == 1, 'Unbound table logical file')
        logical = matches[0]
        require(logical not in by_logical, 'Duplicate table alias')
        row = {key: entry[key] for key in ROWS[logical]}
        pin_row(logical, row)
        by_logical[logical] = entry
    require(set(by_logical) == set(INPUT_FILES), 'Table logical scope differs')
    return by_logical


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workspace', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    require(os.sched_getaffinity(0) == {0}, 'CPU-0-only execution required')
    require(args.out.parent.is_dir() and not args.out.exists() and not args.out.is_symlink(),
            'Fresh report required')
    initial = source_snapshot(__file__)
    generic = load_generic(args.workspace)
    table = bind_table(read_exact(args.workspace, TABLE_PATH, TABLE_SHA, TABLE_BYTES), generic)
    audit_bindings = []
    for domain, expected in AUDITS.items():
        data = read_exact(args.workspace, PREFIXES[domain] + 'source-scene-audit.json',
                          expected['sha256'], expected['bytes'])
        audit_bindings.append(validate_audit(data, domain, generic))
    checked = []
    for logical, name in INPUT_FILES.items():
        row = ROWS[logical]
        domain = logical.split('.')[0]
        relative = PREFIXES[domain] + name
        data = read_exact(args.workspace, relative, row['sha256'], row['bytes'])
        item = scan_state(data, logical, generic)
        item.update({key: table[logical][key] for key in ('source_root', 'source_relative_path',
                     'logical_public_path', 'canonical_public_path')})
        checked.append(item)
        read_exact(args.workspace, relative, row['sha256'], row['bytes'])
    for domain, expected in AUDITS.items():
        read_exact(args.workspace, PREFIXES[domain] + 'source-scene-audit.json',
                   expected['sha256'], expected['bytes'])
    read_exact(args.workspace, TABLE_PATH, TABLE_SHA, TABLE_BYTES)
    read_exact(args.workspace, GENERIC_PATH, GENERIC_SHA, GENERIC_BYTES)
    require_source_unchanged(__file__, initial)
    report = {'passed': True, 'completed': True, 'optimization_level': sys.flags.optimize,
        'source_sha256': initial['sha256'], 'source_bytes': initial['bytes'],
        'generic_sha256': GENERIC_SHA, 'source_set': 'author_and_independent', 'checked': checked,
        'logical_alias_count': 6, 'unique_identity_count': 2, 'audit_bindings': audit_bindings,
        'exception_table_sha256': TABLE_SHA, 'exception_table_bytes': TABLE_BYTES,
        'original_inputs_and_sources_unchanged': True, 'independent_Q_state_checked': True,
        'model_go': False, 'publication_go': False,
        'scope': 'Six exact original state JSON identities and one typed output-field bridge per identity; complete package scan and overall gates remain separate.'}
    with args.out.open('x', encoding='utf8') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'passed': True, 'source_set': 'author_and_independent', 'aliases': 6, 'unique_identities': 2}))


if __name__ == '__main__':
    main()
