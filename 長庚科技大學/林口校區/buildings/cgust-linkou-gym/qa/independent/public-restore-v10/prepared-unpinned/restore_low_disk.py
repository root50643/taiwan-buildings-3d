"""Case-specific low-disk logical restore; original safe restorer stays byte-exact.
Writes all but one pinned history alias; that alias is an authenticated regular
hardlink, not newly allocated payload. No decoding, geometry, render, or network.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, hashlib, os, stat, types

RESTORE_SHA = '60b9e1f3b6974e8884501e7f7a5b18446dea04a15886ed864ff7c2de2ab2581e'
PRIMITIVES_SHA = '7211c544e258dd4855ca9747837845aa683d6c28c3939ea0b9a08cb271d69273'
CAPTURE_SHA = 'f44673ed9c2bc04e21bf907fe19745dab18a25ba59c2241bd227b986710c6244'
OFFICIAL_PROOF_SHA = '005f25a70aceab80f36061e8b18930150d20a09807fccf99f8c75e15083da2fb'
ARCHIVE = {'canonical_public_path': 'qa/controls-history/controls.tar.xz',
           'restore_path': 'history/qa/controls/controls.tar.xz',
           'bytes': 59649412,
           'sha256': 'e5c4465705d5e5299c5d9aa7fa7e99f5db44a61437990508ecee72d615e165b9',
           'mode': 'byte_exact'}
# Final publication map is deliberately not guessed. Pin only after final review.
MAP_SHA = None
CANONICAL_COUNT = None
LOGICAL_COUNT = None
FLOOR = 128 * 1024 * 1024
MAX_FILE = 64 * 1024 * 1024
DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
FILE_FLAGS = os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC


def require(value, message):
    if not value:
        raise ValueError(message)


def identity(s):
    return s.st_dev, s.st_ino


def snapshot(s):
    return identity(s) + (s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


class DirectoryChain:
    """Pin every ancestor and detect detach/replacement as well as symlinks."""
    def __init__(self, path):
        p = Path(path).absolute()
        require(p.anchor == '/' and all(x not in ('', '.', '..') for x in p.parts[1:]),
                'Unsafe directory path')
        self.fds, self.edges = [], []
        try:
            self.fds.append(os.open('/', DIR_FLAGS))
            for name in p.parts[1:]:
                parent = self.fds[-1]
                child = os.open(name, DIR_FLAGS, dir_fd=parent)
                self.fds.append(child)
                self.edges.append((parent, name, child))
            self.check()
        except BaseException:
            self.close()
            raise

    @property
    def fd(self):
        return self.fds[-1]

    def check(self):
        for parent, name, child in self.edges:
            named = os.stat(name, dir_fd=parent, follow_symlinks=False)
            require(stat.S_ISDIR(named.st_mode) and identity(named) == identity(os.fstat(child)),
                    'Directory ancestor changed')

    def close(self):
        for fd in reversed(self.fds):
            os.close(fd)
        self.fds = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def hash_fd(fd, expected=None, maximum=MAX_FILE):
    before = os.fstat(fd)
    require(stat.S_ISREG(before.st_mode) and 0 <= before.st_size <= maximum,
            'Expected bounded regular file')
    if expected is not None:
        require(type(expected['bytes']) is int and before.st_size == expected['bytes'],
                'Exact regular file size differs')
    os.lseek(fd, 0, os.SEEK_SET)
    h, total = hashlib.sha256(), 0
    while True:
        chunk = os.read(fd, min(1024 * 1024, before.st_size + 1 - total))
        if not chunk:
            break
        total += len(chunk)
        require(total <= before.st_size, 'File grew while hashing')
        h.update(chunk)
    after = os.fstat(fd)
    require(snapshot(before) == snapshot(after) and total == before.st_size,
            'File changed while hashing')
    digest = h.hexdigest()
    if expected is not None:
        require(digest == expected['sha256'], 'Exact regular file digest differs')
    return before, digest


def read_source(path, expected_sha, maximum=256 * 1024):
    p = Path(path).absolute()
    with DirectoryChain(p.parent) as chain:
        fd = os.open(p.name, FILE_FLAGS, dir_fd=chain.fd)
        try:
            st, actual = hash_fd(fd, maximum=maximum)
            require(actual == expected_sha, 'Pinned input source differs')
            os.lseek(fd, 0, os.SEEK_SET)
            data = b''
            while len(data) <= st.st_size:
                part = os.read(fd, st.st_size + 1 - len(data))
                if not part:
                    break
                data += part
            require(hashlib.sha256(data).hexdigest() == expected_sha and
                    snapshot(st) == snapshot(os.fstat(fd)), 'Pinned input changed')
            named = os.stat(p.name, dir_fd=chain.fd, follow_symlinks=False)
            require(snapshot(named) == snapshot(st), 'Pinned input name changed')
            chain.check()
            return data
        finally:
            os.close(fd)


def load_original(restore_path):
    p = Path(restore_path).absolute()
    read_source(p.with_name('roster_primitives.py'), PRIMITIVES_SHA)
    raw = read_source(p, RESTORE_SHA)
    module = types.ModuleType('original_verified_restore')
    module.__file__ = str(p)
    exec(compile(raw, str(p), 'exec'), module.__dict__)
    return module


def split_map(original, mapping):
    files, targets = original.validated_map(mapping)
    require(ARCHIVE['canonical_public_path'] in files and ARCHIVE['restore_path'] in targets,
            'Pinned archive alias missing')
    canonical = files[ARCHIVE['canonical_public_path']]
    require(all(canonical[k] == ARCHIVE[k] for k in ('bytes', 'sha256')), 'Archive canonical identity differs')
    aliases = [r for r in targets.values() if r['canonical_public_path'] == ARCHIVE['canonical_public_path']]
    require(len(aliases) == 1 and all(aliases[0][k] == v for k, v in ARCHIVE.items()),
            'Expected exactly one pinned archive alias')
    subset = dict(mapping)
    subset['copy_map'] = [r for r in mapping['copy_map'] if r['restore_path'] != ARCHIVE['restore_path']]
    subset['files'] = [r for r in mapping['files'] if r['canonical_public_path'] != ARCHIVE['canonical_public_path']]
    subfiles, subtargets = original.validated_map(subset)
    require(set(files) - set(subfiles) == {ARCHIVE['canonical_public_path']} and
            set(targets) - set(subtargets) == {ARCHIVE['restore_path']}, 'Partition identity differs')
    require(all(subfiles[k] == files[k] for k in subfiles) and
            all(subtargets[k] == targets[k] for k in subtargets), 'Partition modified retained identities')
    return subset, files, targets


def verified_hardlink(source, destination, row):
    """No chmod/utime; fail closed on leaf swaps, ancestor drift or existing target."""
    source, destination = Path(source).absolute(), Path(destination).absolute()
    with DirectoryChain(source.parent) as sc, DirectoryChain(destination.parent) as dc:
        ds = os.fstat(dc.fd)
        require(ds.st_uid == os.geteuid() and not ds.st_mode & 0o022,
                'Link destination parent must be owned and private')
        sf = os.open(source.name, FILE_FLAGS, dir_fd=sc.fd)
        try:
            before, sha = hash_fd(sf, row)
            require(identity(os.stat(source.name, dir_fd=sc.fd, follow_symlinks=False)) == identity(before),
                    'Source name replaced before link')
            sc.check(); dc.check()
            os.link(source.name, destination.name, src_dir_fd=sc.fd, dst_dir_fd=dc.fd,
                    follow_symlinks=False)
            df = os.open(destination.name, FILE_FLAGS, dir_fd=dc.fd)
            try:
                linked, linked_sha = hash_fd(df, row)
                after, after_sha = hash_fd(sf, row)
                require(identity(before) == identity(linked) == identity(after), 'Linked inode differs')
                require((before.st_mode, before.st_size, before.st_mtime_ns) ==
                        (after.st_mode, after.st_size, after.st_mtime_ns), 'Source mode/size/mtime changed')
                require(after.st_nlink == before.st_nlink + 1, 'Unexpected link-count change')
                require(snapshot(os.stat(source.name, dir_fd=sc.fd, follow_symlinks=False)) == snapshot(after)
                        and snapshot(os.stat(destination.name, dir_fd=dc.fd, follow_symlinks=False)) == snapshot(linked),
                        'Source or destination name changed')
                sc.check(); dc.check()
                return {'same_inode_verified': True, 'source_bytes_reauthenticated': True,
                        'source_mode_size_mtime_unchanged': True, 'bytes': row['bytes'], 'sha256': sha,
                        'new_payload_allocation': False}
            finally:
                os.close(df)
        finally:
            os.close(sf)


def expected_directories(targets):
    return {str(parent) for name in targets for parent in Path(name).parents if str(parent) != '.'}


def verify_tree(out, targets):
    """Check exact file and directory sets, regular types, sizes and every digest."""
    expected = {}
    for name, row in targets.items():
        node = expected
        parts = name.split('/')
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = (row,)
    checked = []
    def visit(fd, node, prefix=''):
        before = os.fstat(fd)
        require(set(os.listdir(fd)) == set(node), 'Logical fileset or directoryset differs')
        for name in sorted(node):
            value, logical = node[name], prefix + name
            if isinstance(value, tuple):
                value = value[0]
                child = os.open(name, FILE_FLAGS, dir_fd=fd)
                try:
                    st, sha = hash_fd(child, value)
                    require(snapshot(os.stat(name, dir_fd=fd, follow_symlinks=False)) == snapshot(st),
                            'Logical file name changed')
                    checked.append({'path': logical, 'bytes': st.st_size, 'sha256': sha})
                finally:
                    os.close(child)
            else:
                child = os.open(name, DIR_FLAGS, dir_fd=fd)
                try:
                    visit(child, value, logical + '/')
                    require(identity(os.stat(name, dir_fd=fd, follow_symlinks=False)) == identity(os.fstat(child)),
                            'Logical directory name changed')
                finally:
                    os.close(child)
        require(snapshot(before) == snapshot(os.fstat(fd)) and set(os.listdir(fd)) == set(node),
                'Logical directory changed during verification')
    with DirectoryChain(out) as chain:
        visit(chain.fd, expected)
        chain.check()
    return checked


def disk_checkpoint(parent, phase, required=0):
    v = os.statvfs(parent)
    available = v.f_bavail * v.f_frsize
    require(available - required >= FLOOR, '128 MiB disk floor would be crossed')
    return {'phase': phase, 'available_bytes': available, 'estimated_new_allocation_bytes': required,
            'projected_remaining_bytes': available - required, 'minimum_remaining_bytes': FLOOR}


def verify_official_proof(original, proof_path, source):
    raw = read_source(proof_path, OFFICIAL_PROOF_SHA, 16 * 1024 * 1024)
    proof = original.parse(raw)
    require(proof['passed'] is True and proof['every_original_payload_read'] is True and
            proof['every_restored_file_rehashed'] is True and proof['canonical_files'] == 5695 and
            len(proof['files']) == 5695, 'Official source proof differs')
    rows = [r for r in proof['files'] if r['sha256'] == ARCHIVE['sha256'] and r['bytes'] == ARCHIVE['bytes']]
    require(len(rows) == 1, 'Official archive identity is not unique')
    original.safe_relative(rows[0]['path'])
    require(Path(source).absolute() == Path(proof['restored_root']) / rows[0]['path'],
            'Archive path is not the proven official canonical source')
    return {'official_verification_sha256': OFFICIAL_PROOF_SHA, 'official_source_row_verified': True}


def execute(root, mapping, out, original, source, proof):
    subset, files, targets = split_map(original, mapping)
    for name, row in sorted(files.items()):
        original.read_exact(root, name, row)
    source_proof = verify_official_proof(original, proof, source)
    # Source is authenticated before writing anything, even though link rechecks it.
    read_source(source, ARCHIVE['sha256'], MAX_FILE)
    allocation_unit = os.statvfs(out.parent).f_frsize
    required = sum(((r['bytes'] + allocation_unit - 1) // allocation_unit) * allocation_unit
                   for r in subset['copy_map'])
    required += (len(expected_directories(targets)) + 1) * allocation_unit + 2 * 1024 * 1024
    disk = [disk_checkpoint(out.parent, 'before_new_tree', required)]
    result = original.restore(root, subset, out)
    require(result['passed'] is True and result['logical_files_restored'] == len(targets) - 1,
            'Original subset restore incomplete')
    disk.append(disk_checkpoint(out.parent, 'after_original_subset_restore'))
    destination = out / ARCHIVE['restore_path']
    # Missing parent directories, if any, use pinned relative directory FDs.
    with DirectoryChain(out) as chain:
        fd = os.dup(chain.fd)
        try:
            for part in ARCHIVE['restore_path'].split('/')[:-1]:
                try: os.mkdir(part, mode=0o700, dir_fd=fd)
                except FileExistsError: pass
                child = os.open(part, DIR_FLAGS, dir_fd=fd)
                os.close(fd); fd = child
            chain.check()
        finally:
            os.close(fd)
    link = verified_hardlink(source, destination, ARCHIVE)
    disk.append(disk_checkpoint(out.parent, 'after_verified_hardlink'))
    roster = verify_tree(out, targets)
    disk.append(disk_checkpoint(out.parent, 'after_complete_verification'))
    for name, row in sorted(files.items()):
        original.read_exact(root, name, row)
    return {'passed': True, 'canonical_files_verified': len(files), 'logical_files_restored': len(targets),
            'newly_written_logical_files': len(targets) - 1, 'hardlinked_logical_files': 1,
            'newly_written_payload_bytes': sum(r['bytes'] for r in subset['copy_map']),
            'hardlinked_payload_bytes': ARCHIVE['bytes'], 'all_written_bytes_reauthenticated': True,
            'complete_logical_fileset_type_size_sha256_verified': True,
            'archive_logical_path': ARCHIVE['restore_path'], 'archive_canonical_path': ARCHIVE['canonical_public_path'],
            'archive_link': link, 'official_source_proof': source_proof, 'files': roster, 'disk_checkpoints': disk,
            'restore_source_sha256': RESTORE_SHA, 'primitives_source_sha256': PRIMITIVES_SHA,
            'original_numerical_strict_passed': False, 'publication_go': False,
            'scope': 'Declared public logical layout; newly written payload plus one verified hardlink, not wholly new allocation. Public projections remain projections. No archive decoding or geometry/render rerun.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--public-root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--archive-source', type=Path, required=True)
    ap.add_argument('--archive-proof', type=Path, required=True)
    a = ap.parse_args()
    require(MAP_SHA is not None and CANONICAL_COUNT is not None and LOGICAL_COUNT is not None,
            'Final case map identity has not been pinned; actual restore is disabled')
    root, out = a.public_root.absolute(), a.out.absolute()
    require(not out.is_relative_to(root) and not root.is_relative_to(out), 'Output overlaps public source')
    original = load_original(root / 'qa/restore_scientific_layout.py')
    raw = read_source(root / 'qa/PUBLIC-COPY-MAP.json', MAP_SHA, 16 * 1024 * 1024)
    mapping = original.parse(raw)
    require(len(mapping['files']) == CANONICAL_COUNT and len(mapping['copy_map']) == LOGICAL_COUNT,
            'Final case map count differs')
    result = execute(root, mapping, out, original, a.archive_source, a.archive_proof)
    read_source(root / 'qa/PUBLIC-COPY-MAP.json', MAP_SHA, 16 * 1024 * 1024)
    load_original(root / 'qa/restore_scientific_layout.py')
    result['copy_map_sha256'] = MAP_SHA
    print(original.dump(result).decode(), end='')


if __name__ == '__main__':
    main()
