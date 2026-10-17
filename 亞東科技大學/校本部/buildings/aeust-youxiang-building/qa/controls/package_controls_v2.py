"""Exact-byte public control packager with individually bound negative fixtures.

Explicit file selection only; no glob expansion. Producer files remain read-only.
Compressed negative fixtures are opaque scientific test INPUTS, never successful
science archives. Their bytes, generator, expected-failure report and (for wrapper
mutations) local failure summary are all independently bound before exception use.
Nested containers are inspected in memory only; only the final outer archive is
extracted, by the unchanged strict archive verifier into a new private directory.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import io
import json
import lzma
import math
import os
import re
import stat
import struct
import tarfile
import tempfile
import types
import zipfile
import zlib

MAX_BYTES = 512 * 1024 * 1024
MAX_NESTING = 8
MAX_MEMBERS = 50000
TMP_MARKER = b'/' + b'tmp/'
PRIVATE_MARKERS = (
    b'/' + b'workspace/', b'/' + b'home/', b'/' + b'Users/',
    b'aeust-youxiang-' + b'private-v1',
    b'aeust-youxiang-source-' + b'audit-private',
)
SECRET_PATTERNS = (
    re.compile(rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b'),
    re.compile(rb'(?i)authorization\s*[:=]\s*[\"\x27]?bearer\s+[A-Za-z0-9_./+=-]{12,}'),
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    re.compile(rb'\bxox[baprs]-[A-Za-z0-9-]{15,}\b'),
)
ARCHIVE_CASES = {
    'compressed_corruption', 'compressed_truncation', 'extra_xz_stream',
    'xz_trailing_garbage', 'xz_trailing_zero_padding',
}

def require(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, 'Duplicate JSON object key')
        obj[key] = value
    return obj


def load_json_bytes(data):
    def finite_float(value):
        result = float(value)
        require(math.isfinite(result), 'Nonfinite JSON float')
        return result
    return json.loads(data.decode('utf-8'), object_pairs_hook=unique_object,
                      parse_float=finite_float,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def dump(data):
    return (json.dumps(data, indent=2, allow_nan=False) + '\n').encode()


def safe_relative(value):
    require(isinstance(value, str) and value and '\\' not in value,
            'Invalid relative path text')
    p = PurePosixPath(value)
    require(not p.is_absolute() and not re.match(r'^[A-Za-z]:', value)
            and p.as_posix() == value
            and all(part not in ('', '.', '..') for part in value.split('/'))
            and all(ord(c) >= 32 and ord(c) != 127 for c in value)
            and len(value.encode()) <= 256, 'Unsafe relative path')
    return value


def ordinary_path(root, relative):
    safe_relative(relative)
    p = root
    require(p.is_dir() and not p.is_symlink(), 'Source root must be a regular directory')
    for component in PurePosixPath(relative).parts:
        p = p / component
        require(not p.is_symlink(), 'Symlink in source path')
    require(p.is_file() and stat.S_ISREG(p.stat().st_mode), 'Missing/nonregular source')
    return p


class Sources:
    def __init__(self, roots, relocations=None):
        self.roots = roots
        self.relocations = relocations or {}
        self.tracked = {}

    def read(self, logical, expected_sha256=None, expected_bytes=None):
        safe_relative(logical)
        label, slash, relative = logical.partition('/')
        require(slash and label in self.roots, 'Unresolved logical source root')
        if self.relocations:
            require(logical in self.relocations, 'Logical source absent from replay map: ' + logical)
            mapped = self.relocations[logical]
            relative = safe_relative(mapped['archive_path'])
            require(expected_sha256 is None or mapped['sha256'] == expected_sha256,
                    'Replay-map source hash differs')
            require(expected_bytes is None or mapped['bytes'] == expected_bytes,
                    'Replay-map source byte count differs')
        p = ordinary_path(self.roots[label], relative)
        require(p.stat().st_size <= MAX_BYTES, 'Source byte safety limit exceeded')
        data = p.read_bytes()
        if expected_sha256 is not None:
            require(isinstance(expected_sha256, str) and re.fullmatch(r'[a-f0-9]{64}', expected_sha256)
                    and digest(data) == expected_sha256, 'Bound source SHA256 differs: ' + logical)
        if expected_bytes is not None:
            require(type(expected_bytes) is int and len(data) == expected_bytes,
                    'Bound source byte count differs: ' + logical)
        binding = (digest(data), len(data))
        require(logical not in self.tracked or self.tracked[logical] == binding,
                'Source changed between reads: ' + logical)
        self.tracked[logical] = binding
        return data

    def unchanged(self):
        initial = dict(self.tracked)
        for logical, (h, n) in initial.items():
            self.read(logical, h, n)
        return True


def decode_prefix(data, kind, budget):
    require(kind in ('xz', 'gzip'), 'Unsupported compression format')
    decoder = (lzma.LZMADecompressor(format=lzma.FORMAT_XZ, memlimit=MAX_BYTES)
               if kind == 'xz' else zlib.decompressobj(31))
    pieces = []
    decoded_count = 0
    anomaly = None
    tail = b''
    # This matches the preparation allowlist's recoverable-prefix method.
    for start in range(0, len(data), 64):
        chunk = data[start:start + 64]
        try:
            maximum = min(MAX_BYTES, budget[0]) + 1
            part = (decoder.decompress(chunk, max_length=maximum) if kind == 'xz'
                    else decoder.decompress(chunk, maximum))
            require(len(part) <= budget[0] and decoded_count + len(part) <= MAX_BYTES,
                    'Decoded byte safety limit exceeded')
            budget[0] -= len(part)
            decoded_count += len(part)
            pieces.append(part)
        except (lzma.LZMAError, zlib.error, EOFError) as error:
            anomaly = {'kind': 'decode_error', 'error': type(error).__name__ + ': ' + str(error)}
            break
        if decoder.eof:
            tail = decoder.unused_data + data[start + 64:]
            if tail:
                anomaly = {'kind': 'trailing_bytes', 'trailing_bytes': len(tail),
                           'trailing_sha256': digest(tail)}
            return b''.join(pieces), tail, anomaly
    if anomaly is None:
        anomaly = {'kind': 'incomplete_stream'}
    return b''.join(pieces), tail, anomaly


BLEND_DEFAULT_FIELDS = (
    {'struct': 'FileSelectParams', 'field': 'dir[1090]', 'block_code': 'DATA',
     'field_buffer_bytes': 1090,
     'field_buffer_sha256': '2d1dc02e846e766c501535dfda01be83adbdea6d8e03a42e4e5df5377da744d1',
     'classification': 'generic_file_browser_home', 'effective': b'/' + b'home/agent'},
    {'struct': 'Scene', 'field': 'r.pic[1024]', 'block_code': 'SC\0\0',
     'field_buffer_bytes': 1024,
     'field_buffer_sha256': 'a27bf0cff013ac91d264ac7f6b87fe91b392cee0ed657588929e56c4f0b4d07d',
     'classification': 'generic_unrendered_output_default', 'effective': b'/' + b'tmp/'},
)


def blend_sdna_defaults(data):
    """Resolve two known non-pointer char buffers from bounded SDNA, read-only.

    Offsets come from the file's actual blocks and checked struct layouts, never
    from the caller's allowance. This supports only the reviewed 403/64-bit/LE
    format. All other bytes, including each full buffer's NUL tail, stay intact.
    """
    require(len(data) <= MAX_BYTES and data[:12] == b'BLENDER-v403',
            'Unsupported Blend header for exact generic defaults')
    blocks = []
    offset = 12
    ended = False
    while offset + 24 <= len(data):
        code, size, address, sdna, count = struct.unpack_from('<4sIQII', data, offset)
        begin = offset + 24
        require(size <= MAX_BYTES and begin + size <= len(data), 'Invalid Blend block bounds')
        if code == b'ENDB':
            require(size == 0 and begin == len(data), 'Invalid Blend end block or trailing data')
            ended = True
            break
        blocks.append((code, begin, size, sdna, count))
        require(len(blocks) <= MAX_MEMBERS, 'Blend block count limit exceeded')
        offset = begin + size
    require(ended, 'Missing Blend end block')
    dna_blocks = [row for row in blocks if row[0] == b'DNA1']
    require(len(dna_blocks) == 1, 'Missing or duplicate Blend SDNA')
    _, begin, size, _, _ = dna_blocks[0]
    dna = data[begin:begin + size]
    at = 0

    def take(n):
        nonlocal at
        require(type(n) is int and 0 <= n <= len(dna) - at, 'Invalid SDNA bounds')
        result = dna[at:at + n]
        at += n
        return result

    def tag(value):
        require(take(len(value)) == value, 'Invalid SDNA tag')

    def number():
        return struct.unpack('<I', take(4))[0]

    def strings(count):
        require(0 <= count <= MAX_MEMBERS, 'SDNA string count limit exceeded')
        result = []
        for _ in range(count):
            end = dna.find(b'\0', at)
            require(end >= at, 'Unterminated SDNA string')
            raw = take(end - at + 1)[:-1]
            require(len(raw) <= 1024 and raw and all(32 <= x < 127 for x in raw),
                    'Invalid SDNA name')
            result.append(raw.decode('ascii'))
        take((-at) % 4)
        return result

    tag(b'SDNANAME')
    names = strings(number())
    tag(b'TYPE')
    types = strings(number())
    require(len(set(types)) == len(types), 'Duplicate SDNA type')
    tag(b'TLEN')
    lengths = list(struct.unpack('<' + str(len(types)) + 'H', take(2 * len(types))))
    take((-at) % 4)
    tag(b'STRC')
    struct_count = number()
    require(struct_count <= MAX_MEMBERS, 'SDNA struct count limit exceeded')
    structs = []
    by_type = {}
    for _ in range(struct_count):
        type_id, count = struct.unpack('<HH', take(4))
        require(type_id < len(types) and type_id not in by_type and count <= MAX_MEMBERS,
                'Invalid SDNA struct identity')
        fields = []
        for _ in range(count):
            field_type, field_name = struct.unpack('<HH', take(4))
            require(field_type < len(types) and field_name < len(names), 'Invalid SDNA field index')
            fields.append((field_type, names[field_name]))
        require(len({name for _, name in fields}) == len(fields), 'Duplicate SDNA field')
        by_type[type_id] = fields
        structs.append(type_id)
    require(at == len(dna), 'Unexpected SDNA trailing data')
    cache = {}
    active = set()

    def layout(type_id):
        if type_id in cache:
            return cache[type_id]
        if type_id not in by_type:
            alignment = min(lengths[type_id], 8) if lengths[type_id] else 1
            require(alignment in (1, 2, 4, 8), 'Unsupported primitive SDNA alignment')
            return alignment, []
        require(type_id not in active and len(active) < 64, 'Cyclic or excessive SDNA layout')
        active.add(type_id)
        position = 0
        maximum_alignment = 1
        result = []
        for field_type, name in by_type[type_id]:
            pointer = '*' in name
            alignment = 8 if pointer else layout(field_type)[0]
            width = 8 if pointer else lengths[field_type]
            for dimension in re.findall(r'\[(\d+)\]', name):
                width *= int(dimension)
                require(width <= MAX_BYTES, 'SDNA array byte limit exceeded')
            position = (position + alignment - 1) // alignment * alignment
            result.append({'type': field_type, 'name': name, 'offset': position, 'bytes': width})
            position += width
            maximum_alignment = max(maximum_alignment, alignment)
        total = (position + maximum_alignment - 1) // maximum_alignment * maximum_alignment
        require(total == lengths[type_id], 'SDNA computed struct size differs')
        active.remove(type_id)
        cache[type_id] = maximum_alignment, result
        return cache[type_id]

    findings = []
    spans = []
    for expected in BLEND_DEFAULT_FIELDS:
        candidates = []
        for code, block_start, block_bytes, sdna, count in blocks:
            if code.decode('ascii', 'replace') != expected['block_code']:
                continue
            require(sdna < len(structs), 'Invalid Blend block SDNA index')
            root_type = structs[sdna]
            if types[root_type] != expected['struct']:
                continue
            require(0 < count <= MAX_MEMBERS and lengths[root_type] > 0
                    and count * lengths[root_type] <= block_bytes, 'Invalid Blend struct count or bounds')
            for instance in range(count):
                type_id = root_type
                field_offset = 0
                parts = expected['field'].split('.')
                for index, part in enumerate(parts):
                    matches = [field for field in layout(type_id)[1] if field['name'] == part]
                    require(len(matches) == 1, 'Required SDNA field absent or ambiguous')
                    field = matches[0]
                    require('*' not in field['name'], 'Pointer cannot authorize a generic default')
                    field_offset += field['offset']
                    type_id = field['type']
                    if index < len(parts) - 1:
                        require(type_id in by_type and '[' not in field['name'],
                                'Unsupported nested generic-default field')
                require(types[type_id] == 'char' and field['bytes'] == expected['field_buffer_bytes'],
                        'Generic-default SDNA field type or size differs')
                start = block_start + instance * lengths[root_type] + field_offset
                require(start + field['bytes'] <= block_start + block_bytes,
                        'Generic-default field exceeds block')
                candidates.append((start, data[start:start + field['bytes']]))
        require(len(candidates) == 1, 'Generic-default SDNA field multiplicity differs')
        start, raw = candidates[0]
        require(digest(raw) == expected['field_buffer_sha256'], 'Generic-default full buffer hash differs')
        effective, separator, tail = raw.partition(b'\0')
        require(separator and effective == expected['effective'], 'Generic-default effective value differs')
        findings.append({key: expected[key] for key in ['classification', 'block_code', 'struct', 'field',
                                                       'field_buffer_bytes', 'field_buffer_sha256']})
        findings[-1].update(field_type='char', field_absolute_byte_offset=start,
                            marker_absolute_byte_offset=start, marker_offset_in_field=0,
                            after_first_nul_nonzero_bytes=sum(value != 0 for value in tail))
        spans.append((start, len(effective)))
    return {'blend_sha256': digest(data), 'version': '403', 'pointer_bytes': 8,
            'byte_order': 'little', 'field_findings': findings}, spans


def blend_generic_default_projection(data, allowance):
    require(allowance.get('kind') == 'blend_generic_defaults'
            and allowance.get('sha256') == digest(data) and allowance.get('bytes') == len(data),
            'Exact Blend privacy allowance identity differs')
    profile, spans = blend_sdna_defaults(data)
    require(allowance.get('sdna_profile') == profile, 'Exact Blend SDNA profile differs')
    projected = bytearray(data)
    for start, length in spans:
        projected[start:start + length] = b' ' * length
    require(len(projected) == len(data), 'Blend scan projection size differs')
    return bytes(projected)


class Scanner:
    def __init__(self, sources, selection, malformed, privacy, negative_archives=None):
        self.sources = sources
        self.selected = {r['source_relative_path']: r for r in selection}
        self.malformed = {}
        for row in malformed:
            name = safe_relative(row['source_relative_path'])
            require(name not in self.malformed, 'Duplicate malformed allowlist path')
            require(name in self.selected, 'Malformed allowlist path is not selected')
            self.malformed[name] = row
        self.negative_archives = {}
        for row in list(negative_archives or []) + [r for r in malformed
                if isinstance(r.get('proof'), dict) and r['proof'].get('proof_kind') == 'archive_verifier_expected_failure']:
            name = safe_relative(row['source_relative_path'])
            require(name in self.selected, 'Negative archive allowlist path is not selected')
            if name in self.negative_archives:
                old = self.negative_archives[name]
                require(old['sha256'] == row['sha256'] and old['bytes'] == row['bytes']
                        and old['proof'] == row['proof'], 'Conflicting negative archive binding')
            self.negative_archives[name] = row
        self.used_negative_archives = set()
        self.privacy = {}
        for row in privacy:
            name = safe_relative(row['source_relative_path'])
            require(name not in self.privacy and name in self.selected,
                    'Duplicate/unselected privacy allowance')
            require((row.get('kind') == 'json_blender_render_default'
                     and row.get('json_pointer') == '/render/filepath')
                    or (row.get('kind') == 'blend_generic_defaults'
                        and isinstance(row.get('sdna_profile'), dict)),
                    'Unsupported or broad privacy allowance')
            self.privacy[name] = row
        self.used_malformed = set()
        self.used_privacy = set()
        self.events = []

    def selected_bytes(self, name, expected_sha256=None, expected_bytes=None):
        # A readable private source root is never sufficient proof of public
        # replayability. Every dependency must have its own exact selected copy.
        require(name in self.selected, 'Required dependency absent from selection: ' + name)
        row = self.selected[name]
        require(expected_sha256 is None or row['sha256'] == expected_sha256,
                'Selected dependency SHA256 differs: ' + name)
        require(expected_bytes is None or row['bytes'] == expected_bytes,
                'Selected dependency byte count differs: ' + name)
        return self.sources.read(name, row['sha256'], row['bytes'])

    def selected_json(self, name):
        return load_json_bytes(self.selected_bytes(name))

    def selected_dependency_closure(self):
        # This also catches future source reads that bypass selected_bytes.
        # Check all tracked dependencies, not just the known proof field names.
        for name, (source_hash, source_bytes) in self.sources.tracked.items():
            row = self.selected.get(name)
            require(row is not None, 'Tracked dependency absent from selection: ' + name)
            require(row['sha256'] == source_hash and row['bytes'] == source_bytes,
                    'Tracked dependency binding differs from selection: ' + name)

    def fixture_proof(self, name, data, anomaly, decoded, tail):
        require(name in self.malformed, 'Unapproved malformed compressed payload: ' + name)
        row = self.malformed[name]
        require(row.get('sha256') == digest(data) and row.get('bytes') == len(data),
                'Malformed fixture raw identity differs')
        require(isinstance(row.get('anomaly'), list) and len(row['anomaly']) == 1
                and row['anomaly'][0].get('kind') == anomaly['kind'],
                'Malformed fixture anomaly kind differs')
        expected = row['anomaly'][0]
        if anomaly['kind'] == 'trailing_bytes':
            require(expected.get('trailing_bytes') == len(tail)
                    and expected.get('trailing_sha256') == digest(tail),
                    'Malformed fixture trailing bytes differ')
        proof = row.get('proof')
        require(isinstance(proof, dict), 'Missing expected-failure proof')
        result_data = self.selected_bytes(proof['result_path'], proof['result_sha256'])
        report = load_json_bytes(result_data)
        # Selected reports are individually verified too, never replaced by a
        # private aggregate pointer that will be absent from the public archive.
        require(proof['result_path'] in self.selected, 'Expected-failure result absent from selection')
        sr = self.selected[proof['result_path']]
        require(sr['sha256'] == digest(result_data) and sr['bytes'] == len(result_data),
                'Selected expected-failure result binding differs')
        self.selected_bytes(proof['generator_path'], proof['generator_sha256'])
        case = proof.get('expected_rejection_case')
        kind = proof.get('proof_kind')
        if kind == 'archive_verifier_expected_failure':
            require(case in ARCHIVE_CASES and report.get('case') == case
                    and report.get('expected_accept') is False and report.get('passed') is True
                    and type(report.get('returncode')) is int and report['returncode'] == 1
                    and report.get('report', {}).get('passed') is False
                    and report['report'].get('error') == proof.get('expected_rejection_error'),
                    'Archive expected-rejection semantics differ')
            expected_kind = {'compressed_corruption': 'decode_error',
                             'compressed_truncation': 'incomplete_stream'}.get(case, 'trailing_bytes')
            require(anomaly['kind'] == expected_kind, 'Archive failure class differs')
            if case == 'xz_trailing_zero_padding':
                require(tail == b'\0' * 4, 'Zero-padding fixture tail differs')
            elif case == 'xz_trailing_garbage':
                require(tail == b'garbage', 'Garbage fixture tail differs')
            elif case == 'extra_xz_stream':
                extra, rest, failure = decode_prefix(tail, 'xz', [MAX_BYTES])
                require(extra == b'' and rest == b'' and failure is None,
                        'Extra-stream fixture is not one exact empty XZ stream')
        elif kind == 'wrapper_expected_failure':
            require(case in ('compressed_hash_mismatch', 'late_input_mutation')
                    and report.get('passed') is True, 'Wrapper proof scope differs')
            matches = [r for r in report.get('cases', []) if r.get('test') == case]
            require(len(matches) == 1, 'Missing/duplicate wrapper rejection case')
            r = matches[0]
            require(r.get('passed') is True and type(r.get('exit_code')) is int
                    and r['exit_code'] == 1 and r.get('completed') is False
                    and r.get('error') == proof.get('expected_rejection_error'),
                    'Wrapper expected-rejection semantics differ')
            local_data = self.selected_bytes(proof['local_result_path'], proof['local_result_sha256'])
            local = load_json_bytes(local_data)
            require(proof['local_result_path'] in self.selected, 'Local failure report absent from selection')
            local_row = self.selected[proof['local_result_path']]
            require(local_row['sha256'] == digest(local_data) and local_row['bytes'] == len(local_data)
                    and local.get('completed') is False
                    and local.get('all_selected_rays_exactly_classified') is False
                    and local.get('all_selected_first_chords_ge_0p8mm') is False,
                    'Local wrapper failure binding/semantics differ')
            require(anomaly['kind'] == 'trailing_bytes'
                    and tail == (b'x' if case == 'compressed_hash_mismatch' else b'late-mutation'),
                    'Wrapper mutation tail differs')
        elif kind == 'packager_expected_failure':
            require(case == 'unapproved_bad_compression' and data == b'not xz'
                    and decoded == b'' and report.get('passed') is True,
                    'Packager malformed-fixture scope differs')
            matches = [r for r in report.get('cases', []) if r.get('case') == case]
            require(len(matches) == 1, 'Missing/duplicate packager rejection case')
            r = matches[0]
            require(r.get('passed') is True and r.get('expected_accept') is False
                    and type(r.get('returncode')) is int and r['returncode'] == 1
                    and r.get('expected_rejection_reason') == proof.get('expected_rejection_error'),
                    'Packager expected-rejection semantics differ')
        else:
            raise ValueError('Unknown expected-failure proof kind')
        self.used_malformed.add(name)
        self.events.append({'source_relative_path': name, 'sha256': digest(data), 'bytes': len(data),
                            'case': case, 'result_sha256': proof['result_sha256'],
                            'generator_sha256': proof['generator_sha256'],
                            'treatment': 'opaque_original_negative_fixture_bytes',
                            'decoded_prefix_bytes': len(decoded), 'decoded_prefix_sha256': digest(decoded),
                            'trailing_bytes': len(tail), 'trailing_sha256': digest(tail)})

    def plain(self, data, context, top=False):
        if top and context in self.privacy and self.privacy[context]['kind'] == 'blend_generic_defaults':
            data = blend_generic_default_projection(data, self.privacy[context])
            self.used_privacy.add(context)
        require(not any(marker in data for marker in PRIVATE_MARKERS),
                'Private path marker in public payload: ' + context)
        require(not any(pattern.search(data) for pattern in SECRET_PATTERNS),
                'Credential-shaped content in public payload: ' + context)
        if TMP_MARKER in data:
            require(top and context in self.privacy
                    and self.privacy[context]['kind'] == 'json_blender_render_default',
                    'Unreviewed temporary path in public payload: ' + context)
            row = self.privacy[context]
            require(row.get('sha256') == digest(data) and row.get('bytes') == len(data),
                    'Exact privacy allowance identity differs')
            obj = load_json_bytes(data)
            require(isinstance(obj, dict) and isinstance(obj.get('render'), dict)
                    and obj['render'].get('filepath') == TMP_MARKER.decode(),
                    'Known Blender render default field differs')
            def count(v, pointer=''):
                if isinstance(v, dict):
                    return sum(count(x, pointer + '/' + str(k)) for k, x in v.items())
                if isinstance(v, list):
                    return sum(count(x, pointer + '/' + str(i)) for i, x in enumerate(v))
                if isinstance(v, str) and TMP_MARKER.decode() in v:
                    require(pointer == '/render/filepath' and v == TMP_MARKER.decode(),
                            'Temporary path outside exact Blender default')
                    return 1
                return 0
            require(count(obj) == 1, 'Ambiguous temporary-path allowance')
            self.used_privacy.add(context)
        # Public verifier subclasses use this same validated in-memory projection
        # for additional path/credential scans. The original blob is never edited.
        return data

    def negative_tar_report(self, logical, data):
        # No generic sibling-report fallback: every structural-tar exception
        # requires this exact raw file identity and its exact frozen case proof.
        if logical not in self.negative_archives:
            return False
        row = self.negative_archives[logical]
        require(row['sha256'] == digest(data) and row['bytes'] == len(data),
                'Negative inner archive raw identity differs')
        proof = row['proof']
        require(proof.get('proof_kind') == 'archive_verifier_expected_failure'
                and proof.get('expected_rejection_case') == PurePosixPath(logical).parent.name,
                'Negative inner archive case/path binding differs')
        result = self.selected_bytes(proof['result_path'], proof['result_sha256'])
        selected = self.selected.get(proof['result_path'])
        require(selected and selected['sha256'] == digest(result) and selected['bytes'] == len(result),
                'Negative inner archive result absent or changed in selection')
        report = load_json_bytes(result)
        self.selected_bytes(proof['generator_path'], proof['generator_sha256'])
        require(proof['generator_path'] in self.selected
                and self.selected[proof['generator_path']]['sha256'] == proof['generator_sha256'],
                'Negative inner archive generator absent or changed in selection')
        require(report.get('case') == proof['expected_rejection_case']
                and report.get('expected_accept') is False and report.get('passed') is True
                and type(report.get('returncode')) is int and report['returncode'] == 1
                and report.get('report', {}).get('passed') is False
                and report['report'].get('error') == proof.get('expected_rejection_error'),
                'Negative inner archive rejection semantics differ')
        self.used_negative_archives.add(logical)
        return True

    def walk(self, data, name, logical, budget, depth=0, top=False, negative_tar=False):
        require(depth <= MAX_NESTING and len(data) <= MAX_BYTES, 'Nested container safety limit exceeded')
        self.plain(data, logical, top=top)
        is_xz = name.endswith('.xz') or data.startswith(b'\xfd7zXZ\0')
        is_gzip = name.endswith('.gz') or data.startswith(b'\x1f\x8b')
        if is_xz or is_gzip:
            kind = 'xz' if is_xz else 'gzip'
            decoded, tail, anomaly = decode_prefix(data, kind, budget)
            if anomaly is not None:
                require(top, 'Unapproved malformed nested compressed payload')
                self.fixture_proof(logical, data, anomaly, decoded, tail)
            else:
                require(logical not in self.malformed or not top,
                        'Allowlisted malformed fixture unexpectedly decodes normally')
            self.plain(tail, logical + '#unused-tail')
            # The exact extra-stream fixture has already been decoded and checked
            # to be an empty stream by fixture_proof; arbitrary tails never pass.
            inner_name = name[:-3] if name.endswith(('.xz', '.gz')) else 'decoded'
            if decoded:
                self.walk(decoded, inner_name, logical + '#decoded', budget, depth + 1,
                          negative_tar=negative_tar or self.negative_tar_report(logical, data))
            return
        if name.endswith('.tar') or (len(data) >= 265 and data[257:262] == b'ustar'):
            # Deliberately do not ask tarfile to interpret PAX, GNU long names,
            # hardlinks, or special headers. Some exact negative fixtures mutate
            # those flags while keeping ordinary payload bytes. Scan bounded raw
            # header/payload regions; never resolve or materialize a member.
            position = 0
            count = 0
            require(len(data) % 512 == 0 or negative_tar,
                    'Unapproved malformed nested tar: block alignment')
            while position + 512 <= len(data):
                header = data[position:position + 512]
                if not any(header):
                    require((len(data) - position >= 1024 and not any(data[position:])) or negative_tar,
                            'Unapproved malformed nested tar: terminator or trailing data')
                    return
                count += 1
                require(count <= MAX_MEMBERS, 'Nested tar member-count limit exceeded')
                name_bytes = header[:100].split(b'\0', 1)[0]
                prefix = header[345:500].split(b'\0', 1)[0]
                child_name = ((prefix + b'/' if prefix else b'') + name_bytes).decode('utf-8', 'surrogateescape')
                self.plain(name_bytes, logical + '#tar-name')
                self.plain(prefix, logical + '#tar-prefix')
                self.plain(header[157:257], logical + '#tar-link')
                size_field = header[124:136]
                value = size_field.strip(b'\0 ')
                if value and all(c in b'01234567' for c in value):
                    size = int(value, 8)
                elif size_field[0] & 0x80 and negative_tar:
                    size = int.from_bytes(size_field, 'big') & ((1 << 95) - 1)
                else:
                    require(negative_tar, 'Unapproved malformed nested tar: size field')
                    return
                checksum_field = header[148:156].strip(b'\0 ')
                valid_checksum = (bool(checksum_field)
                                  and all(c in b'01234567' for c in checksum_field)
                                  and int(checksum_field, 8) == sum(header[:148]) + 256 + sum(header[156:]))
                require(valid_checksum or negative_tar,
                        'Unapproved malformed nested tar: checksum')
                require(size <= budget[0], 'Nested tar byte limit exceeded')
                begin = position + 512
                end = begin + size
                if end > len(data):
                    require(negative_tar, 'Unapproved malformed nested tar: truncated payload')
                    return
                next_position = begin + ((size + 511) // 512) * 512
                require((next_position <= len(data) and not any(data[end:next_position])) or negative_tar,
                        'Unapproved malformed nested tar: member padding')
                child = data[begin:end]
                budget[0] -= len(child)
                if child:
                    self.walk(child, child_name, logical + '#tar/' + child_name,
                              budget, depth + 1)
                position = next_position
            require(negative_tar, 'Unapproved malformed nested tar: missing terminator')
            return
        if name.endswith('.zip') or data.startswith((b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08')):
            try:
                with zipfile.ZipFile(io.BytesIO(data), 'r') as archive:
                    infos = archive.infolist()
                    require(len(infos) <= MAX_MEMBERS, 'Nested zip member-count limit exceeded')
                    for member in infos:
                        self.plain(member.filename.encode('utf-8'), logical + '#zip-name')
                        require(not member.flag_bits & 1, 'Encrypted nested zip unsupported')
                        require(0 <= member.file_size <= budget[0], 'Nested zip byte limit exceeded')
                        require(not member.is_dir() or member.file_size == 0,
                                'Nested zip directory contains payload')
                        with archive.open(member, 'r') as stream:
                            child = stream.read(member.file_size + 1)
                        require(len(child) == member.file_size, 'Nested zip byte count differs')
                        budget[0] -= len(child)
                        self.walk(child, member.filename, logical + '#zip/' + member.filename,
                                  budget, depth + 1)
            except (zipfile.BadZipFile, RuntimeError, NotImplementedError) as error:
                raise ValueError('Invalid/unsupported nested zip: ' + type(error).__name__) from error

    def scan(self, row, data):
        name = row['source_relative_path']
        self.walk(data, PurePosixPath(name).name, name, [MAX_BYTES], top=True,
                  negative_tar=self.negative_tar_report(name, data))

    def complete(self):
        self.selected_dependency_closure()
        require(self.used_malformed == set(self.malformed), 'Unused malformed allowlist entry')
        require(self.used_privacy == set(self.privacy), 'Unused exact privacy allowance')
        require(self.used_negative_archives == set(self.negative_archives), 'Unused negative archive allowance')


def load_tool(path, module_name, expected_sha256):
    require(path.is_file() and not path.is_symlink(), 'Missing archive tool')
    data = path.read_bytes()
    require(digest(data) == expected_sha256, 'Archive tool source changed before exact-byte load')
    # Never consult timestamp/size-valid bytecode caches: disabling bytecode
    # writes alone does not prevent Python's ordinary import loader reading them.
    module = types.ModuleType(module_name)
    module.__file__ = str(path)
    module.__package__ = ''
    exec(compile(data, str(path), 'exec'), module.__dict__)
    return module


def package(selection_path, output, tooling, roots, malformed_path=None, privacy_path=None, replay_map_path=None, negative_archive_path=None):
    require(not output.exists() and not output.is_symlink(), 'Fresh output required')
    own_source_hash = digest(Path(__file__).read_bytes())
    selection_bytes = selection_path.read_bytes()
    selection = load_json_bytes(selection_bytes)
    require(selection.get('passed') is True and isinstance(selection.get('files'), list)
            and selection['files'], 'Explicit passed file selection required')
    require(selection.get('model_go', False) is False, 'Control archive must not claim model GO')
    files = selection['files']
    logical_names = [safe_relative(row['source_relative_path']) for row in files]
    targets = [safe_relative(row['archive_path']) for row in files]
    require(len(set(logical_names)) == len(logical_names), 'Duplicate logical source selection')
    require(len(set(targets)) == len(targets), 'Archive destination collision')
    require('ARCHIVE-SCOPE.json' not in targets, 'Reserved archive metadata destination')
    for target in targets:
        require(not any(target.startswith(other + '/') for other in targets),
                'Archive file/directory prefix collision')
    for row in files:
        require(row.get('transformation', 'identity') == 'identity', 'Only identity source copies allowed')
    malformed_bytes = malformed_path.read_bytes() if malformed_path else dump({'files': []})
    privacy_bytes = privacy_path.read_bytes() if privacy_path else dump({'files': []})
    negative_archive_bytes = negative_archive_path.read_bytes() if negative_archive_path else dump({'files': []})
    negative_archives = load_json_bytes(negative_archive_bytes)
    require(isinstance(negative_archives.get('files'), list), 'Negative archive allowlist schema differs')
    malformed = load_json_bytes(malformed_bytes)
    privacy = load_json_bytes(privacy_bytes)
    require(isinstance(malformed.get('files'), list) and isinstance(privacy.get('files'), list),
            'Malformed/privacy allowlist schema differs')
    replay_map_bytes = replay_map_path.read_bytes() if replay_map_path else None
    relocations = {}
    if replay_map_bytes is not None:
        replay_map = load_json_bytes(replay_map_bytes)
        records = replay_map.get('copies', replay_map.get('files'))
        require(isinstance(records, list), 'Replay-map schema differs')
        for record in records:
            key = safe_relative(record['source_relative_path'])
            require(key not in relocations, 'Duplicate replay-map source')
            safe_relative(record['archive_path'])
            relocations[key] = record
    sources = Sources(roots, relocations)
    scanner = Scanner(sources, files, malformed['files'], privacy['files'], negative_archives['files'])
    verifier_path = tooling / 'tools/archive_verify.py'
    builder_path = tooling / 'tools/build_controls_archive.py'
    tool_hashes = {p.name: digest(p.read_bytes()) for p in [verifier_path, builder_path]}
    verifier = load_tool(verifier_path, 'controls_v2_original_archive_verify', tool_hashes[verifier_path.name])
    builder = load_tool(builder_path, 'controls_v2_original_archive_builder', tool_hashes[builder_path.name])
    require(verifier.FORMAT == builder.FORMAT, 'Archive tool profile mismatch')
    output.mkdir(parents=True, exist_ok=False)
    copies = []
    with tempfile.TemporaryDirectory(dir=output, prefix='private-build-') as tmp:
        work = Path(tmp)
        stage = work / 'stage'
        stage.mkdir(mode=0o700)
        for row in sorted(files, key=lambda r: r['archive_path']):
            data = sources.read(row['source_relative_path'], row['sha256'], row['bytes'])
            scanner.scan(row, data)
            target = stage / row['archive_path']
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(data)
            require(digest(target.read_bytes()) == row['sha256'], 'Identity copy changed')
            copies.append({k: row[k] for k in ['source_relative_path', 'archive_path', 'bytes', 'sha256']})
        scanner.complete()
        scope = {'format': builder.FORMAT,
                 'scope': selection.get('scope', 'Exact original synthetic controls only; no model GO.'),
                 'selection_sha256': digest(selection_bytes),
                 'malformed_allowlist_sha256': digest(malformed_bytes),
                 'privacy_allowlist_sha256': digest(privacy_bytes),
                 'negative_archive_allowlist_sha256': digest(negative_archive_bytes),
                 'replay': selection.get('replay', {}), 'copies': copies,
                 'intentional_negative_fixtures': scanner.events,
                 'policy': 'Original bytes only; malformed control inputs remain opaque files. Nested containers are never extracted. No successful science verdict is inferred from a negative fixture.'}
        scope_bytes = dump(scope)
        scanner.plain(scope_bytes, 'ARCHIVE-SCOPE.json')
        (stage / 'ARCHIVE-SCOPE.json').write_bytes(scope_bytes)
        members = [{'path': p.relative_to(stage).as_posix(), 'bytes': p.stat().st_size,
                    'sha256': digest(p.read_bytes())}
                   for p in stage.rglob('*') if p.is_file()]
        members.sort(key=lambda row: row['path'])
        raw, compressed = builder.make_archive(stage, members)
        archive = work / 'controls.tar.xz'
        index_path = work / 'controls-index.json'
        archive.write_bytes(compressed)
        index = {'format': builder.FORMAT, 'archive_sha256': digest(compressed),
                 'tar_sha256': digest(raw), 'members': members}
        index_path.write_bytes(dump(index))
        verified, verified_tar, records = verifier.verify(archive, index_path)
        extracted = work / 'safe-extracted'
        verifier.extract_new(extracted, verified_tar, records)
        actual_paths = sorted(p.relative_to(extracted).as_posix()
                              for p in extracted.rglob('*') if p.is_file() or p.is_symlink())
        require(actual_paths == [m['path'] for m in members], 'Extracted all-member path inventory differs')
        for row in members:
            p = ordinary_path(extracted, row['path'])
            require(p.stat().st_size == row['bytes'] and digest(p.read_bytes()) == row['sha256'],
                    'Extracted member content differs')
        raw2, compressed2 = builder.make_archive(extracted, members)
        require(raw2 == raw and compressed2 == compressed, 'Safe-extract deterministic rebuild differs')
        sources.unchanged()
        scanner.selected_dependency_closure()
        copied = {row['source_relative_path']: (row['sha256'], row['bytes']) for row in copies}
        require(all(copied.get(name) == binding for name, binding in sources.tracked.items()),
                'Tracked dependency absent or changed in archive copies')
        require(digest(Path(__file__).read_bytes()) == own_source_hash, 'Packager source changed')
        require(selection_path.read_bytes() == selection_bytes, 'Selection changed during packaging')
        if malformed_path:
            require(malformed_path.read_bytes() == malformed_bytes, 'Malformed allowlist changed')
        if privacy_path:
            require(privacy_path.read_bytes() == privacy_bytes, 'Privacy allowlist changed')
        if replay_map_path:
            require(replay_map_path.read_bytes() == replay_map_bytes, 'Replay map changed')
        if negative_archive_path:
            require(negative_archive_path.read_bytes() == negative_archive_bytes, 'Negative archive allowlist changed')
        require(all(digest(p.read_bytes()) == tool_hashes[p.name] for p in [verifier_path, builder_path]),
                'Archive verifier/builder source changed')
        (output / 'controls.tar.xz').write_bytes(compressed)
        (output / 'controls-index.json').write_bytes(index_path.read_bytes())
    result = {'passed': True, 'model_go': False, 'source_sha256': own_source_hash,
              'selection_sha256': digest(selection_bytes), 'archive_sha256': digest(compressed),
              'index_sha256': digest((output / 'controls-index.json').read_bytes()),
              'archive_tool_sources_sha256': tool_hashes, 'members': len(members),
              'copy_count': len(copies), 'all_selected_inputs_accounted': len(copies) == len(files), 'sources_unchanged': True,
              'all_tracked_dependencies_selected_and_copied': True,
              'safe_extract_all_member_hashes_verified': True, 'bitwise_rebuild_verified': True,
              'malformed_fixture_count': len(scanner.events), 'copies': copies,
              'intentional_negative_fixtures': scanner.events,
              'proof_and_source_bindings': [{'source_relative_path': p, 'sha256': h, 'bytes': n}
                                            for p, (h, n) in sorted(sources.tracked.items())]}
    (output / 'packaging-result.json').write_bytes(dump(result))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selection', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--tooling', type=Path, required=True)
    parser.add_argument('--source-root', action='append', default=[], metavar='LABEL=PATH')
    parser.add_argument('--malformed-allowlist', type=Path)
    parser.add_argument('--privacy-allowlist', type=Path)
    parser.add_argument('--replay-map', type=Path)
    parser.add_argument('--negative-archive-allowlist', type=Path)
    args = parser.parse_args()
    roots = {}
    for value in args.source_root:
        label, sep, path = value.partition('=')
        require(sep and '/' not in label and safe_relative(label) and label not in roots,
                'Invalid/duplicate logical source root')
        original = Path(path)
        require(original.is_dir() and not original.is_symlink(), 'Invalid source root directory')
        roots[label] = original.resolve()
    require(roots, 'At least one logical source root required')
    result = package(args.selection, args.out, args.tooling, roots,
                     args.malformed_allowlist, args.privacy_allowlist, args.replay_map, args.negative_archive_allowlist)
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ['copies', 'intentional_negative_fixtures', 'proof_and_source_bindings']}))


if __name__ == '__main__':
    main()
