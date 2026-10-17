"""Exact-byte helper excerpts. Provenance records every copied source span.

Only fixed WFU candidate/profile constants differ from the original case values.
No AEUST publication or scientific gate is inherited or asserted here.
"""
import hashlib
import os
import re
import stat

BLEND = '70d8914cefaaceac8572d00c6cfba52b5abbedd18c810175f2deedb47ed2c429'
SCIENCE_CSV_PROFILE = {
    'compressed_bytes': 19156984,
    'compressed_sha256': '80cf38d8255e789755e316a24638872db0fb913f2d37795edd3c81349551f550',
    'decoded_bytes': 194500309,
    'decoded_sha256': '6408a97da82dc7a1e226225637a415d6cd8ecaecfb962e51454f52bc3067f2b6',
    'csv_data_rows': 209460}

ADDITIONAL_PRIVATE_MARKERS = (b'/' + b'home/', b'/' + b'root/', b'/' + b'private/var/',
                              b'GH_CONFIG_' + b'DIR', b'file:' + b'//', b'C:' + b'\\Users\\')


ADDITIONAL_SECRET_PATTERNS = (
    re.compile(rb'(?<![A-Za-z0-9_])(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})(?![A-Za-z0-9_])'),
    re.compile(rb'(?i)(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*["\x27][A-Za-z0-9_+/=-]{20,}["\x27]'))


BLEND_FIELDS = [(171624, 1090, '2d1dc02e846e766c501535dfda01be83adbdea6d8e03a42e4e5df5377da744d1'),
                (231956, 1024, 'a27bf0cff013ac91d264ac7f6b87fe91b392cee0ed657588929e56c4f0b4d07d')]


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def scan_complete_plain_buffer(module, buffer):
    """Full bytes/mmap search; never use membership iteration on an mmap."""
    markers = tuple(module.PRIVATE_MARKERS) + (module.TMP_MARKER,) + ADDITIONAL_PRIVATE_MARKERS
    require(all(buffer.find(marker) < 0 for marker in markers),
            'Private path marker in exact CSV complete buffer')
    patterns = tuple(module.SECRET_PATTERNS) + ADDITIONAL_SECRET_PATTERNS
    require(all(pattern.search(buffer) is None for pattern in patterns),
            'Credential-shaped content in exact CSV complete buffer')


def bounded_xz_csv_privacy_scan(module, data, profile, chunk_bytes=1024 * 1024):
    """Pure bounded streaming primitive; production caller pins the four inputs.

    A private unnamed temporary spool is removed on success or failure. mmap is
    read-only and scans the entire decoded stream with every original pattern.
    No scientific values are interpreted, rewritten, or exempted here.
    """
    import lzma
    import mmap
    import tempfile
    require(type(data) is bytes and len(data) <= module.MAX_BYTES,
            'Compressed CSV input exceeds unchanged generic bound')
    require(type(chunk_bytes) is int and 1 <= chunk_bytes <= 4 * 1024 * 1024,
            'Invalid bounded streaming chunk size')
    require(type(profile.get('decoded_bytes')) is int
            and 0 < profile['decoded_bytes'] <= SCIENCE_CSV_PROFILE['decoded_bytes']
            and type(profile.get('csv_data_rows')) is int and profile['csv_data_rows'] >= 0,
            'Invalid exact decoded CSV bounds')
    require(len(data) == profile['compressed_bytes'] and digest(data) == profile['compressed_sha256'],
            'Compressed CSV size/hash differs before streaming')
    scan_complete_plain_buffer(module, data)
    decoder = lzma.LZMADecompressor(format=lzma.FORMAT_XZ, memlimit=module.MAX_BYTES)
    decoded_hash = hashlib.sha256()
    total = newlines = 0
    last = b''
    with tempfile.TemporaryFile(mode='w+b') as spool:
        info = os.fstat(spool.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_mode & 0o077 == 0 and info.st_nlink == 0,
                'Private unlinked regular temporary scan spool required')
        for start in range(0, len(data), chunk_bytes):
            require(not decoder.eof, 'Trailing data after the single XZ stream')
            incoming = data[start:start + chunk_bytes]
            while True:
                part = decoder.decompress(incoming, max_length=min(chunk_bytes, profile['decoded_bytes'] - total + 1))
                incoming = b''
                require(total + len(part) <= profile['decoded_bytes'], 'Decoded CSV exceeds exact byte bound')
                if part:
                    total += len(part)
                    decoded_hash.update(part)
                    newlines += part.count(b'\n')
                    last = part[-1:]
                    require(spool.write(part) == len(part), 'Incomplete temporary CSV write')
                if decoder.eof:
                    require(not decoder.unused_data and start + chunk_bytes >= len(data),
                            'Trailing data or extra stream after the single XZ stream')
                    break
                if decoder.needs_input:
                    break
                require(part, 'XZ decoder made no bounded progress')
        require(decoder.eof and not decoder.unused_data, 'Incomplete single XZ stream')
        require(total == profile['decoded_bytes'] and decoded_hash.hexdigest() == profile['decoded_sha256'],
                'Decoded CSV exact size/hash differs')
        require(last == b'\n' and newlines == profile['csv_data_rows'] + 1,
                'Decoded CSV full data-row/line count differs')
        spool.flush()
        require(os.fstat(spool.fileno()).st_size == total, 'Temporary CSV byte count differs')
        with mmap.mmap(spool.fileno(), 0, access=mmap.ACCESS_READ) as buffer:
            scan_complete_plain_buffer(module, buffer)
    return {**profile, 'single_complete_xz_stream': True, 'trailing_bytes': 0,
            'maximum_decoder_output_chunk_bytes': chunk_bytes,
            'full_original_compressed_buffer_scanned': True,
            'complete_decoded_buffer_scanned': True, 'all_original_and_additional_privacy_patterns': True,
            'bounded_streaming_to_private_unnamed_spool': True, 'persistent_decoded_copy_written': False,
            'csv_schema_and_numerical_predicates': 'Remain independently required from the completed original full-row dense audit; this privacy scan grants no scientific acceptance.'}


def mask_exact_blend_defaults(data):
    """Privacy scan projection only; returned bytes are never published/written."""
    require(digest(data) == BLEND, 'Exact Blend privacy profile hash differs')
    masked = bytearray(data)
    effective = [b'/' + b'home/agent', b'/' + b'tmp/']
    for (offset, size, h), text in zip(BLEND_FIELDS, effective):
        raw = data[offset:offset + size]
        require(len(raw) == size and digest(raw) == h and raw.split(b'\0', 1)[0] == text,
                'Exact SDNA full-buffer identity differs')
        require(data.count(text) == 1, 'Unexpected repeated generic path outside approved field')
        masked[offset:offset + len(text)] = b'_' * len(text)
    return bytes(masked)


