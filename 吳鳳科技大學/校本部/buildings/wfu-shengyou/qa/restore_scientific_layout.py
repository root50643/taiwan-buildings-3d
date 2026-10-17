"""Verify canonical public bytes and restore their declared logical layout.

No archive extraction, decompression, geometry, privacy scan or network access.
The output is a new directory. Original private paths and omitted files cannot
be reconstructed. A metadata-only public projection remains a projection.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, copy, hashlib, json, os, re, stat, types

PRIMITIVES_SHA = '7211c544e258dd4855ca9747837845aa683d6c28c3939ea0b9a08cb271d69273'
_p = Path(__file__).absolute().with_name('roster_primitives.py')
_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_fd = os.open('/', _flags)
try:
    for _part in _p.parent.parts[1:]:
        _child = os.open(_part, _flags, dir_fd=_fd)
        os.close(_fd)
        _fd = _child
    _leaf = os.open(_p.name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=_fd)
finally:
    os.close(_fd)
with os.fdopen(_leaf, 'rb') as _stream:
    _before = os.fstat(_stream.fileno())
    if not stat.S_ISREG(_before.st_mode) or not 0 < _before.st_size <= 256 * 1024:
        raise ValueError('Invalid helper source size/type')
    _raw = _stream.read(_before.st_size + 1)
    _after = os.fstat(_stream.fileno())
if (_before.st_dev, _before.st_ino, _before.st_size, _before.st_mtime_ns, _before.st_ctime_ns) != (
        _after.st_dev, _after.st_ino, _after.st_size, _after.st_mtime_ns, _after.st_ctime_ns):
    raise ValueError('Helper source changed during read')
if hashlib.sha256(_raw).hexdigest() != PRIMITIVES_SHA:
    raise ValueError('Restore helper source identity differs')
_m = types.ModuleType('verified_roster_primitives')
exec(compile(_raw, str(_p), 'exec'), _m.__dict__)
require, parse, dump = _m.require, _m.parse, _m.dump
safe_relative, digest = _m.safe_relative, _m.digest
MAX_FILE_BYTES = 64 * 1024 * 1024


def read_exact(root, name, row):
    safe_relative(name)
    require(type(row.get('bytes')) is int and 0 <= row['bytes'] <= MAX_FILE_BYTES,
            'Invalid exact file byte count')
    require(type(row.get('sha256')) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']),
            'Invalid exact file digest')
    data = _m._read_regular_snapshot(root, name, row['bytes'], MAX_FILE_BYTES)
    require(len(data) == row['bytes'] and digest(data) == row['sha256'],
            'Canonical source identity differs')
    return data


def typed_equal(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(typed_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(typed_equal(x, y) for x, y in zip(a, b))
    return a == b


def pointer_parent(value, pointer):
    require(type(pointer) is str and pointer.startswith('/') and pointer != '/',
            'Nonempty JSON pointer required')
    tokens = pointer[1:].split('/')
    require(all(re.search(r'~(?![01])', t) is None for t in tokens), 'Invalid pointer escape')
    tokens = [t.replace('~1', '/').replace('~0', '~') for t in tokens]
    current = value
    for token in tokens[:-1]:
        if type(current) is list:
            require(re.fullmatch('0|[1-9][0-9]*', token) is not None, 'Invalid array pointer')
            current = current[int(token)]
        else:
            require(type(current) is dict and token in current, 'Unknown pointer member')
            current = current[token]
    key = tokens[-1]
    if type(current) is list:
        require(re.fullmatch('0|[1-9][0-9]*', key) is not None, 'Invalid array pointer')
        key = int(key)
        require(key < len(current), 'Array pointer out of range')
    else:
        require(type(current) is dict and key in current, 'Unknown final pointer member')
    return current, key


def project_json(data, changes):
    """Apply only exact approved string substitutions at enumerated pointers."""
    original = parse(data)
    result = copy.deepcopy(original)
    seen = set()
    for change in changes:
        require(set(change) == {'pointer', 'old', 'new'}, 'Unknown projection instruction')
        pointer, old, new = (change[k] for k in ('pointer', 'old', 'new'))
        require(pointer not in seen, 'Duplicate projection pointer')
        seen.add(pointer)
        require(type(old) is str and type(new) is str and old != new,
                'Projection only permits changed string path labels')
        parent, key = pointer_parent(result, pointer)
        require(type(parent[key]) is str and parent[key] == old, 'Projection source value drift')
        parent[key] = new
    # Reverse only the declared substitutions and require full typed deep equality.
    reversed_value = copy.deepcopy(result)
    for change in reversed(changes):
        parent, key = pointer_parent(reversed_value, change['pointer'])
        require(parent[key] == change['new'], 'Projection output value drift')
        parent[key] = change['old']
    require(typed_equal(original, reversed_value), 'Unexpected nonpath JSON change')
    return dump(result)


def validated_map(mapping):
    require(mapping.get('schema') == 'wfu-public-scientific-copy-map-v1', 'Wrong copy-map schema')
    require(mapping.get('status') == 'byte_bound_ready_for_publication_gate', 'Incomplete copy map')
    require(mapping.get('publication_go') is False, 'Copy map cannot grant publication GO')
    require(mapping.get('original_numerical_strict_passed') is False, 'Strict result was upgraded')
    files, targets = {}, {}
    for row in mapping['files']:
        name = safe_relative(row['canonical_public_path'])
        require(name not in files, 'Duplicate canonical destination')
        require(type(row['bytes']) is int and 0 <= row['bytes'] <= MAX_FILE_BYTES and
                type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']),
                'Invalid canonical descriptor')
        files[name] = row
    for row in mapping['copy_map']:
        target = safe_relative(row['restore_path'])
        name = safe_relative(row['canonical_public_path'])
        require(target not in targets and name in files, 'Duplicate or missing restore destination')
        require(type(row['bytes']) is int and row['bytes'] == files[name]['bytes'] and
                row['sha256'] == files[name]['sha256'], 'Restore identity differs from canonical')
        require(row['mode'] in ('byte_exact', 'metadata_only_json_projection'), 'Unknown restore mode')
        targets[target] = row
    names = sorted(targets)
    for i, name in enumerate(names[:-1]):
        require(not names[i + 1].startswith(name + '/'), 'File/directory restore collision')
    require(targets, 'Empty copy map')
    return files, targets


def restore(root, mapping, out):
    files, targets = validated_map(mapping)
    # Every canonical source is authenticated before any output directory exists.
    for name, row in sorted(files.items()):
        read_exact(root, name, row)
    _m.write_new_tree(out, [(target, lambda row=row: read_exact(
        root, row['canonical_public_path'], row)) for target, row in sorted(targets.items())])
    for target, row in sorted(targets.items()):
        read_exact(out, target, row)
    return {'passed': True, 'scope': 'Declared public logical layout only; private omissions are not restored.',
            'canonical_files_verified': len(files), 'logical_files_restored': len(targets),
            'byte_exact_files': sum(r['mode'] == 'byte_exact' for r in targets.values()),
            'public_projection_files': sum(r['mode'] != 'byte_exact' for r in targets.values()),
            'original_numerical_strict_passed': False, 'publication_go': False,
            'all_written_bytes_reauthenticated': True}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--public-root', type=Path, required=True)
    ap.add_argument('--copy-map', default='qa/PUBLIC-COPY-MAP.json')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    own = _m._read_regular_snapshot(Path(__file__).absolute().parent, Path(__file__).name, None, 256 * 1024)
    safe_relative(args.copy_map)
    raw = _m._read_regular_snapshot(args.public_root, args.copy_map, None, 16 * 1024 * 1024)
    result = restore(args.public_root, parse(raw), args.out)
    result['copy_map_sha256'] = digest(raw)
    after = _m._read_regular_snapshot(Path(__file__).absolute().parent, Path(__file__).name, len(own), 256 * 1024)
    require(after == own, 'Restore source changed during execution')
    result['restore_source_sha256'] = digest(own)
    print(dump(result).decode(), end='')


if __name__ == '__main__':
    main()
