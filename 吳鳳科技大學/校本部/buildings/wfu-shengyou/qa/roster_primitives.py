"""Exact inherited JSON/path helpers and narrowly adapted FD-safe regular reader.
No import-time I/O. Full source and extraction spans are retained privately.
"""
from pathlib import Path, PurePosixPath
import hashlib, json, os, re, stat

def require(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pairs_unique(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, 'Duplicate JSON key')
        out[key] = value
    return out


def parse(data):
    import math
    def finite_float(text):
        value = float(text)
        require(math.isfinite(value), 'Nonfinite JSON numeric value')
        return value
    return json.loads(data, object_pairs_hook=pairs_unique, parse_float=finite_float,
                      parse_constant=lambda v: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def dump(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


def safe_relative(name):
    require(type(name) is str and name and '\\' not in name, 'Invalid relative path')
    p = PurePosixPath(name)
    require(not p.is_absolute() and not re.match(r'^[A-Za-z]:', name)
            and p.as_posix() == name and all(x not in ('', '.', '..') for x in name.split('/'))
            and all(ord(c) >= 32 and ord(c) != 127 for c in name), 'Unsafe relative path')
    return name


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
        require(stat.S_ISREG(before.st_mode) and 0 <= before.st_size <= maximum_bytes
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


def write_new_tree(out, records):
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
        for name, payload in records:
            safe_relative(name)
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
                    data = memoryview(payload())
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

