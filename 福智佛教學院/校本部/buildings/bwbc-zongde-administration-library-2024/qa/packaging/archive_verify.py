#!/usr/bin/env python3
"""Validate the indexed controls USTAR/XZ profile, optionally extract to a new directory.

Validation is read-only. No extraction starts until every byte and member passes.
The index must be independently trusted: matching an attacker-replaced index is
an integrity check, not proof of authorship. Linux/POSIX fd-relative extraction.
The output parent must be owned by this user and not writable by group/others;
the same user must not concurrently mutate the destination tree.
"""
import argparse
import hashlib
import json
import lzma
import os
from pathlib import Path
import re
import sys

FORMAT = 'bwbc-controls-ustar-xz-v1'
MAX_TAR_BYTES = 512 * 1024 * 1024
BLOCK = 512
HEX = re.compile(r'[0-9a-f]{64}\Z')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, 'duplicate JSON object key')
        out[key] = value
    return out


def safe_path(value):
    require(isinstance(value, str) and value, 'empty/non-string member path')
    require(not value.startswith('/') and '\\' not in value,
            'absolute/backslash member path')
    require(not re.match(r'^[A-Za-z]:', value), 'drive-prefixed member path')
    require(all(ord(c) >= 32 and ord(c) != 127 for c in value),
            'control character in member path')
    require(all(p not in ('', '.', '..') for p in value.split('/')),
            'unsafe member path segment')
    require(len(value.encode('utf-8')) <= 256, 'member path too long for USTAR')
    return value


def load_index(path):
    raw = Path(path).read_bytes()
    obj = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object)
    require(isinstance(obj, dict) and set(obj) ==
            {'format', 'archive_sha256', 'tar_sha256', 'members'}, 'index schema')
    require(obj['format'] == FORMAT, 'index format')
    for key in ('archive_sha256', 'tar_sha256'):
        require(isinstance(obj[key], str) and HEX.fullmatch(obj[key]), key)
    require(isinstance(obj['members'], list) and obj['members'], 'empty member index')
    names = []
    total = 0
    for row in obj['members']:
        require(isinstance(row, dict) and set(row) == {'path', 'bytes', 'sha256'},
                'member index schema')
        names.append(safe_path(row['path']))
        require(type(row['bytes']) is int and 0 <= row['bytes'] <= MAX_TAR_BYTES,
                'member byte count')
        require(isinstance(row['sha256'], str) and HEX.fullmatch(row['sha256']),
                'member SHA256')
        total += BLOCK + ((row['bytes'] + BLOCK - 1) // BLOCK) * BLOCK
    require(total + 2 * BLOCK <= MAX_TAR_BYTES, 'indexed tar exceeds limit')
    require(names == sorted(names) and len(set(names)) == len(names),
            'index paths must be unique and sorted')
    name_set = set(names)
    for name in names:
        parts = name.split('/')
        require(not any('/'.join(parts[:i]) in name_set for i in range(1, len(parts))),
                'file/directory prefix collision')
    return obj, sha(raw)


def read_xz(path):
    decoder = lzma.LZMADecompressor(format=lzma.FORMAT_XZ, memlimit=512 * 1024 * 1024)
    digest = hashlib.sha256()
    tar = bytearray()
    with open(path, 'rb') as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            require(not decoder.eof, 'data after first XZ stream')
            digest.update(block)
            pending = block
            while True:
                decoded = decoder.decompress(pending, max_length=MAX_TAR_BYTES - len(tar) + 1)
                tar.extend(decoded)
                require(len(tar) <= MAX_TAR_BYTES, 'decompressed tar exceeds 512 MiB')
                pending = b''
                if decoder.eof:
                    require(not decoder.unused_data, 'extra XZ stream/trailing bytes')
                    break
                if decoder.needs_input:
                    break
    require(decoder.eof, 'incomplete XZ stream')
    return tar, digest.hexdigest()


def octal(field, label, empty=False):
    value = field.strip(b'\x00 ')
    require((empty and not value) or
            (value and all(c in b'01234567' for c in value)), 'invalid octal ' + label)
    return int(value, 8) if value else 0


def string_field(field, label):
    value, sep, padding = field.partition(b'\x00')
    require(not sep or not any(padding), 'nonzero string padding: ' + label)
    return value.decode('utf-8')


def validate_tar(tar, index):
    require(len(tar) % BLOCK == 0, 'tar length not block aligned')
    position = 0
    records = []
    for row in index['members']:
        require(position + BLOCK <= len(tar), 'missing tar member header')
        header = tar[position:position + BLOCK]
        require(any(header), 'missing indexed tar member')
        checksum = octal(header[148:156], 'checksum')
        require(checksum == sum(header[:148]) + 8 * 32 + sum(header[156:]),
                'tar header checksum')
        require(header[257:265] == b'ustar\x0000', 'not POSIX USTAR')
        require(header[156:157] == b'0', 'only ordinary file members allowed')
        require(not any(header[157:257]), 'link name must be empty')
        require(not any(header[265:329]), 'uname/gname must be empty')
        require(not any(header[500:512]), 'reserved USTAR bytes must be zero')
        require(octal(header[100:108], 'mode') == 0o644, 'mode must be 0644')
        require(octal(header[108:116], 'uid') == 0, 'uid must be zero')
        require(octal(header[116:124], 'gid') == 0, 'gid must be zero')
        require(octal(header[136:148], 'mtime') == 0, 'mtime must be zero')
        require(octal(header[329:337], 'devmajor', True) == 0 and
                octal(header[337:345], 'devminor', True) == 0, 'device numbers must be zero')
        name = string_field(header[:100], 'name')
        prefix = string_field(header[345:500], 'prefix')
        require(name, 'empty USTAR name')
        name = safe_path(prefix + '/' + name if prefix else name)
        require(name == row['path'], 'tar/index path or order mismatch')
        size = octal(header[124:136], 'size')
        require(size == row['bytes'], 'tar/index byte count mismatch')
        start = position + BLOCK
        end = start + size
        position = start + ((size + BLOCK - 1) // BLOCK) * BLOCK
        require(position <= len(tar), 'truncated member data')
        require(sha(memoryview(tar)[start:end]) == row['sha256'], 'member SHA256 mismatch')
        require(not any(tar[end:position]), 'nonzero member padding')
        records.append((name, start, end))
    require(len(tar) - position >= 2 * BLOCK, 'missing two-block tar terminator')
    require(not any(tar[position:]), 'extra tar members/nonzero trailing data')
    return records


def verify(archive, index_path):
    index, index_hash = load_index(index_path)
    tar, archive_hash = read_xz(archive)
    require(archive_hash == index['archive_sha256'], 'archive SHA256 mismatch')
    tar_hash = sha(tar)
    require(tar_hash == index['tar_sha256'], 'tar SHA256 mismatch')
    records = validate_tar(tar, index)
    result = {'format': FORMAT, 'passed': True, 'archive_sha256': archive_hash,
              'tar_sha256': tar_hash, 'index_sha256': index_hash,
              'members': len(records), 'tar_bytes': len(tar),
              'member_bytes': sum(end - start for _, start, end in records)}
    return result, tar, records


def extract_new(out, tar, records):
    require(hasattr(os, 'O_NOFOLLOW') and hasattr(os, 'O_DIRECTORY'),
            'safe fd-relative extraction unavailable')
    path = os.fspath(out)
    require(path and '\\' not in path, 'invalid output path')
    parts = path.split('/')
    if path.startswith('/'):
        parts = parts[1:]
    require(parts and all(p not in ('', '.', '..') for p in parts), 'unsafe output path')
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    parent_fd = os.open('/' if path.startswith('/') else '.', directory_flags)
    root_fd = None
    try:
        for part in parts[:-1]:
            next_fd = os.open(part, directory_flags, dir_fd=parent_fd)
            os.close(parent_fd)
            parent_fd = next_fd
        parent_stat = os.fstat(parent_fd)
        require(parent_stat.st_uid == os.geteuid() and not (parent_stat.st_mode & 0o022),
                'output parent must be user-owned and not group/other writable')
        os.mkdir(parts[-1], mode=0o700, dir_fd=parent_fd)  # EEXIST includes symlinks.
        root_fd = os.open(parts[-1], directory_flags, dir_fd=parent_fd)
        for name, start, end in records:
            directory_fd = os.dup(root_fd)
            try:
                components = name.split('/')
                for component in components[:-1]:
                    try:
                        os.mkdir(component, mode=0o700, dir_fd=directory_fd)
                    except FileExistsError:
                        pass
                    next_fd = os.open(component, directory_flags, dir_fd=directory_fd)
                    os.close(directory_fd)
                    directory_fd = next_fd
                fd = os.open(components[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                             os.O_NOFOLLOW, 0o644, dir_fd=directory_fd)
                try:
                    data = memoryview(tar)[start:end]
                    while data:
                        written = os.write(fd, data)
                        require(written > 0, 'short extraction write')
                        data = data[written:]
                    os.fchmod(fd, 0o644)
                    os.utime(fd, ns=(0, 0))
                finally:
                    os.close(fd)
            finally:
                os.close(directory_fd)
    finally:
        if root_fd is not None:
            os.close(root_fd)
        os.close(parent_fd)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', required=True)
    parser.add_argument('--index', required=True)
    parser.add_argument('--out', help='new directory; its parent must already exist')
    args = parser.parse_args(argv)
    try:
        result, tar, records = verify(args.archive, args.index)
        if args.out is not None:
            extract_new(args.out, tar, records)
        result['extracted'] = args.out is not None
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception as error:
        print(json.dumps({'format': FORMAT, 'passed': False,
                          'error': type(error).__name__ + ': ' + str(error)}, sort_keys=True))
        return 1


if __name__ == '__main__':
    sys.exit(main())
