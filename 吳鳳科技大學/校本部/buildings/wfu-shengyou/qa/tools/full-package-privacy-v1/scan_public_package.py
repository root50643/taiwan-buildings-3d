"""All-file bounded privacy scan; current WFU and inactive historical domains.
No extraction, geometry, rewriting, publication approval or persistent CSV copy.
Run only in the parent-owned shared CPU slot. Output must be outside public root.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, hashlib, json, os, stat, tempfile, types

HERE = Path(__file__).absolute().parent
TOOLS = {'package_controls_v2.py': {'bytes': 47569, 'sha256': '1402e983241d78d19969380b45ce79b7cd3936207a4324710a17b094f5ac256c'}, 'exact_privacy_primitives.py': {'bytes': 6783, 'sha256': '1b8f3d36243bdd1bc090bbf1dffa55e9f80d803bce73c2354efb7f466b15f6cd'}, 'check_wfu_privacy.py': {'bytes': 12032, 'sha256': '58e7025590eec9efc7f242552ac22c950fc8e41d41c5eb74051ee323c3a9e950'}, 'roster_primitives.py': {'bytes': 6313, 'sha256': '7211c544e258dd4855ca9747837845aa683d6c28c3939ea0b9a08cb271d69273'}, 'restore_scientific_layout.py': {'bytes': 8677, 'sha256': '60b9e1f3b6974e8884501e7f7a5b18446dea04a15886ed864ff7c2de2ab2581e'}, 'archive_verify.py': {'bytes': 10831, 'sha256': '1af27c8212057503323899b7a5f9f9171de42f78a28ff1e3e07f82d688e021fd'}}
HISTORY_METADATA = {'controls-index.json': {'bytes': 4364858, 'sha256': '157fbf951147405727eb557b167e6db16d9ce3a651012f1c87ee2a5975d0015e'}, 'controls-selection.json': {'bytes': 7688822, 'sha256': '51540622191aff2f431002198d7a69d2c3bee7747c4cebbb6060b4b954efb054'}, 'malformed-fixture-allowlist.json': {'bytes': 424474, 'sha256': '3c857b321d73d5ccdc5fe4b6143ac8995af05efa3d79e25f1e9a9e30160ab0ec'}, 'privacy-allowlist.json': {'bytes': 86755, 'sha256': '924b86a8649aea7702ec8db4461bfbe64934c1f748fab6372df712ce480fafbc'}, 'negative-archive-allowlist.json': {'bytes': 771008, 'sha256': '236657191ba7de94c7fe4e5fb8399ed34b2a491843420e329132933fda97f497'}, 'packaging-result.json': {'bytes': 11725077, 'sha256': 'f7ac5122332996e021b36cb7533a54084d0650f800204b71197c0555e5f51a43'}, 'replay-verification.json': {'bytes': 3866, 'sha256': '29d065ddf4742d08c4a43ccecc7475ce94972820fb7fd5006952b0b62027ed17'}}
STATE_EXCEPTIONS = {'bytes': 6935, 'sha256': '126fac9c7d8ff0e36c5922868c4ea3f48ece0423fa2c6c284dad258e749c8863'}
HISTORY_ARCHIVE = {'bytes': 59649412, 'sha256': 'e5c4465705d5e5299c5d9aa7fa7e99f5db44a61437990508ecee72d615e165b9'}
HISTORY_PATH = 'qa/controls-history/controls.tar.xz'
STATE_HASHES = {'5a5392d71a92898c2f455c527fd4f1f9cebcaca44a811a809ebc179e417bec1a': 167332, 'f284e231753dc964b6f71f3855616921313b8669922def0bd2496233d81c0e28': 167331}


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def bootstrap():
    """Authenticate the existing FD-safe reader before executing its bytes."""
    name = 'roster_primitives.py'
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    parent = os.open('/', flags)
    try:
        for part in HERE.parts[1:]:
            child = os.open(part, flags, dir_fd=parent)
            os.close(parent)
            parent = child
        fd = os.open(name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent)
    finally:
        os.close(parent)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        require(stat.S_ISREG(before.st_mode) and before.st_size == TOOLS[name]['bytes'], 'Reader source type/size differs')
        data = stream.read(before.st_size + 1)
        after = os.fstat(stream.fileno())
    require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)
            == (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
            and len(data) == TOOLS[name]['bytes'] and digest(data) == TOOLS[name]['sha256'],
            'Reader source changed or hash differs')
    module = types.ModuleType('verified_package_reader')
    exec(compile(data, str(HERE/name), 'exec'), module.__dict__)
    return module


def load_tools():
    p = bootstrap()
    modules = {}
    for name, row in TOOLS.items():
        data = p._read_regular_snapshot(HERE, name, row['bytes'], 256*1024)
        require(digest(data) == row['sha256'], 'Bound tool source differs: ' + name)
        module = types.ModuleType('verified_' + name[:-3])
        module.__file__ = str(HERE/name)
        exec(compile(data, module.__file__, 'exec'), module.__dict__)
        modules[name] = module
    return p, modules


def inventory(root):
    """Names only; every data read is separately FD-safe and identity-bound."""
    require(root.is_dir() and not root.is_symlink(), 'Unsafe public root')
    names = set()
    def fail(error):
        raise error
    for base, dirs, files in os.walk(root, followlinks=False, onerror=fail):
        for name in dirs + files:
            require(not (Path(base)/name).is_symlink(), 'Symlink in public inventory')
        for name in files:
            path = Path(base)/name
            require(stat.S_ISREG(path.stat().st_mode), 'Special file in public inventory')
            names.add(path.relative_to(root).as_posix())
    return names


def bind_state_exceptions(data, generic, canonical):
    require(len(data) == STATE_EXCEPTIONS['bytes'] and digest(data) == STATE_EXCEPTIONS['sha256'],
            'Exact state exception table differs')
    value = generic.load_json_bytes(data)
    require(value['schema'] == 'wfu-source-state-exact-generic-default-scan-exceptions-v1'
            and len(value['files']) == 6 and set(value['unique_sha256']) == set(STATE_HASHES),
            'State exception scope differs')
    unique = {}
    for row in value['files']:
        name = row['canonical_public_path']
        require(row['sha256'] in STATE_HASHES and row['bytes'] == STATE_HASHES[row['sha256']]
                and row['json_pointer'] == '/render/filepath' and row['exact_type'] == 'string'
                and row['exact_value_utf8_hex'] == '2f746d702f'
                and row['encoded_json_string_offset'] == 155195 and row['encoded_json_string_bytes'] == 7
                and row['marker_offset'] == 155196 and row['marker_bytes'] == 5
                and row['encoded_string_occurrences'] == 1, 'Exact state exception fields differ')
        require(name in canonical and all(canonical[name][k] == row[k] for k in ('bytes','sha256')),
                'Exact state missing/different in canonical map')
        if name in unique:
            require(unique[name]['sha256'] == row['sha256'], 'Conflicting canonical state exception')
        unique[name] = row
    require(len(unique) == 2, 'Exactly two canonical state identities required')
    return unique


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


def current_scanner(generic, primitive, checker, policy, selection, states):
    allowances = [dict(source_relative_path=name, kind='json_blender_render_default',
                       json_pointer='/render/filepath', bytes=row['bytes'], sha256=row['sha256'])
                  for name,row in states.items()]
    sources = types.SimpleNamespace(tracked={})
    class Current(generic.Scanner):
        def plain(self, data, context, top=False):
            if top and context == checker.BLEND_PATH:
                checker.scan_blend(data, generic, primitive, policy)
                data = primitive.mask_exact_blend_defaults(data)
                self.blend_seen = True
            # The original JSON exception gate verifies the pointer and that
            # no other string anywhere in this object contains its default.
            data = super().plain(data, context, top=top)
            if top and context in states:
                data = state_projection(data, states[context], generic)
                self.state_seen.add(context)
            primitive.scan_complete_plain_buffer(policy, data)
            return data
    scanner = Current(sources, selection, [], allowances, [])
    scanner.blend_seen = False
    scanner.state_seen = set()
    return scanner


def scan_history(read_file, generic, primitive, policy, verifier):
    """Only the original archive and its frozen proof-bound historical policy."""
    archive = read_file(HISTORY_PATH, HISTORY_ARCHIVE)
    require(len(archive) == HISTORY_ARCHIVE['bytes'] and digest(archive) == HISTORY_ARCHIVE['sha256'],
            'Historical domain requires the exact frozen archive')
    primitive.scan_complete_plain_buffer(policy, archive)
    raw = {name: read_file('qa/controls-history/'+name, row) for name,row in HISTORY_METADATA.items()}
    require(all(len(raw[name]) == row['bytes'] and digest(raw[name]) == row['sha256']
                for name,row in HISTORY_METADATA.items()), 'Frozen historical metadata identity differs')
    objects = {name: generic.load_json_bytes(data) for name,data in raw.items()}
    selection = objects['controls-selection.json']['files']
    privacy = objects['privacy-allowlist.json']['files']
    malformed = objects['malformed-fixture-allowlist.json']['files']
    negatives = objects['negative-archive-allowlist.json']['files']
    require(len(privacy) == 34 and len(malformed) == 188
            and all(r['kind'] == 'blend_generic_defaults' for r in privacy),
            'Frozen historical policy scope differs')
    # The unchanged original verifier accepts paths. Give it only private
    # unnamed regular spools of the already-authenticated archive/index bytes.
    # This writes no public file, extracts nothing, and never spools a CSV.
    with tempfile.TemporaryFile('w+b') as a, tempfile.TemporaryFile('w+b') as i:
        for stream, data in ((a,archive),(i,raw['controls-index.json'])):
            info = os.fstat(stream.fileno())
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 0 and not info.st_mode & 0o077,
                    'Private unnamed regular archive input spool required')
            require(stream.write(data) == len(data), 'Incomplete archive input spool')
            stream.flush()
            stream.seek(0)
        verified, tar, records = verifier.verify('/proc/self/fd/'+str(a.fileno()), '/proc/self/fd/'+str(i.fileno()))
    require(verified['members'] == 16730 and verified['archive_sha256'] == HISTORY_ARCHIVE['sha256']
            and verified['index_sha256'] == HISTORY_METADATA['controls-index.json']['sha256'],
            'Frozen historical archive verification differs')
    by_path = {name:(start,end) for name,start,end in records}
    selected = {row['source_relative_path']:row for row in selection}
    require(len(selected) == len(selection) and len({r['archive_path'] for r in selection}) == len(selection)
            and set(by_path) == {r['archive_path'] for r in selection} | {'ARCHIVE-SCOPE.json'},
            'Historical all-member/selection coverage differs')
    class MemorySources:
        def __init__(self):
            self.tracked = {}
        def read(self, logical, expected_sha256=None, expected_bytes=None):
            require(logical in selected, 'Unknown historical selected dependency')
            row = selected[logical]
            start,end = by_path[row['archive_path']]
            data = bytes(tar[start:end])
            require(len(data) == row['bytes'] and digest(data) == row['sha256']
                    and (expected_sha256 is None or expected_sha256 == row['sha256'])
                    and (expected_bytes is None or expected_bytes == row['bytes']),
                    'Historical member/dependency identity differs')
            self.tracked[logical] = (row['sha256'], row['bytes'])
            return data
    class Historical(generic.Scanner):
        def plain(self, data, context, top=False):
            projection = super().plain(data, context, top=top)
            primitive.scan_complete_plain_buffer(policy, projection)
            return projection
    sources = MemorySources()
    scanner = Historical(sources, selection, malformed, privacy, negatives)
    for row in selection:
        scanner.scan(row, sources.read(row['source_relative_path']))
    scanner.complete()
    start,end = by_path['ARCHIVE-SCOPE.json']
    scanner.plain(bytes(tar[start:end]), 'ARCHIVE-SCOPE.json')
    # Every header, name, link field, padding byte and terminator is scanned in
    # addition to every indexed member; no whole-tar default-path exemption.
    cursor = 0
    for name,start,end in records:
        primitive.scan_complete_plain_buffer(policy, bytes(tar[cursor:start]))
        cursor = end
    primitive.scan_complete_plain_buffer(policy, bytes(tar[cursor:]))
    require(digest(tar) == verified['tar_sha256'] and len(scanner.events) == 188
            and len(scanner.used_privacy) == 34, 'Historical decoded bytes/policy use drifted')
    return dict(verified, inactive_historical_tool_controls=True,
                every_indexed_member_and_framing_scanned=True, exact_blend_privacy_entries_used=34,
                exact_malformed_entries_used=188, exact_negative_archive_entries_used=len(scanner.used_negative_archives),
                no_new_historical_exceptions=True, applies_to_new_wfu=False,
                zero_exception_claimed=False, persistent_decoded_output_written=False)


def run(public_root, expected_map_sha, out):
    p, tools = load_tools()
    own = p._read_regular_snapshot(HERE, Path(__file__).name, None, 256*1024)
    root = Path(public_root).absolute()
    require(not out.absolute().is_relative_to(root), 'Report must be outside the scanned public tree')
    require(out.parent.is_dir() and not out.exists() and not out.is_symlink(), 'Fresh output required')
    generic = tools['package_controls_v2.py']; primitive = tools['exact_privacy_primitives.py']
    checker = tools['check_wfu_privacy.py']; restore = tools['restore_scientific_layout.py']
    policy = types.SimpleNamespace(MAX_BYTES=generic.MAX_BYTES, PRIVATE_MARKERS=generic.PRIVATE_MARKERS+checker.WFU_MARKERS,
                                   TMP_MARKER=generic.TMP_MARKER, SECRET_PATTERNS=generic.SECRET_PATTERNS)
    checker.validate_policy(generic, primitive, policy)
    names = inventory(root)
    tracked = {}
    def read_file(name, expected=None):
        p.safe_relative(name)
        require(name in names, 'Required file absent from public inventory: ' + name)
        data = p._read_regular_snapshot(root, name, None if expected is None else expected['bytes'], generic.MAX_BYTES)
        row = {'bytes':len(data),'sha256':digest(data)}
        require(expected is None or all(row[k] == expected[k] for k in row), 'Public exact identity differs: ' + name)
        require(name not in tracked or tracked[name] == row, 'Public bytes changed between reads: ' + name)
        tracked[name] = row
        return data
    map_data = read_file('qa/PUBLIC-COPY-MAP.json')
    require(digest(map_data) == expected_map_sha, 'Final canonical copy-map SHA differs')
    mapping = generic.load_json_bytes(map_data)
    canonical, aliases = restore.validated_map(mapping)
    require(set(canonical) <= names, 'Canonical public file missing')
    states = bind_state_exceptions(read_file('qa/SOURCE-STATE-DEFAULT-EXCEPTIONS.json',STATE_EXCEPTIONS),generic,canonical)
    require(checker.BLEND_PATH in canonical and canonical[checker.BLEND_PATH]['sha256'] == checker.BLEND_SHA,
            'Original Blend absent from canonical map')
    csv_profile = dict(checker.CSV_ITEMS)
    require(checker.CSV_PATH in canonical
            and canonical[checker.CSV_PATH]['sha256'] == csv_profile['compressed_sha256']
            and canonical[checker.CSV_PATH]['bytes'] == csv_profile['compressed_bytes'],
            'Exact canonical CSV absent')
    selection = [dict(source_relative_path=name, **{k:row[k] for k in ('bytes','sha256')}) for name,row in canonical.items()]
    scanner = current_scanner(generic,primitive,checker,policy,selection,states)
    def read_history_file(logical, expected):
        require(logical.startswith('qa/controls-history/'), 'Historical path outside exact domain')
        source = 'history/qa/controls/' + logical.removeprefix('qa/controls-history/')
        require(source in aliases and aliases[source]['mode'] == 'byte_exact'
                and all(aliases[source][k] == expected[k] for k in ('bytes','sha256')),
                'Historical logical copy-map binding differs')
        return read_file(aliases[source]['canonical_public_path'],expected)
    csv_report = history_report = None
    for name in sorted(names):
        # All names are checked too; path labels never receive data exceptions.
        primitive.scan_complete_plain_buffer(policy,name.encode())
        if name == HISTORY_PATH:
            history_report = scan_history(read_history_file,generic,primitive,policy,tools['archive_verify.py'])
            continue
        data = read_file(name,canonical.get(name))
        if name == checker.CSV_PATH:
            csv_report = checker.scan_csv(data,generic,primitive,policy)
        else:
            scanner.scan({'source_relative_path':name},data)
    scanner.complete()
    require(scanner.blend_seen and scanner.state_seen == set(states) and csv_report is not None
            and history_report is not None and set(tracked) == names, 'Whole-package privacy scope incomplete')
    require(inventory(root) == names, 'Public inventory changed during scan')
    for name,row in sorted(tracked.items()):
        read_file(name,row)
    require(inventory(root) == names, 'Public inventory changed during final identity check')
    require(p._read_regular_snapshot(HERE,Path(__file__).name,len(own),256*1024) == own, 'Scanner self source changed')
    for name,row in TOOLS.items():
        require(digest(p._read_regular_snapshot(HERE,name,row['bytes'],256*1024)) == row['sha256'], 'Tool source changed')
    result = {'passed':True,'completed':True,'optimization_level':sys.flags.optimize,
              'scanner_source_sha256':digest(own),'copy_map_sha256':digest(map_data),'public_file_count':len(names),
              'files':tracked,'all_public_files_and_names_scanned':True,'all_public_bytes_unchanged':True,
              'current_wfu':{'blend_effective_bytes':16,'exact_json_files':2,'masked_bytes_per_json':5,
                             'no_malformed_archive_exceptions':True,'csv':csv_report},
              'inactive_historical_controls':history_report,'source_bindings':TOOLS,
              'model_go':False,'publication_go':False,
              'scope':'Exact byte-pattern privacy scan only. Historical frozen exceptions remain confined to the original archive; no zero-exception or universal-secret-detection claim. Source/science/full-scene/publication gates remain separate.'}
    with out.open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2,ensure_ascii=False,allow_nan=False);stream.write('\n')
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--public-root',type=Path,required=True)
    ap.add_argument('--copy-map-sha256',required=True)
    ap.add_argument('--out',type=Path,required=True)
    a = ap.parse_args()
    r = run(a.public_root,a.copy_map_sha256,a.out)
    print(json.dumps({'passed':r['passed'],'files':r['public_file_count'],'optimization_level':r['optimization_level']}))
