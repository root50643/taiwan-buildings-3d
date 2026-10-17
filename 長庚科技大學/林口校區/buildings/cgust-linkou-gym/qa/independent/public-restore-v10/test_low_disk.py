"""Tiny controlled tests for only the new hardlink, split, and full-roster edges.
No full public restore, archive decoding, geometry or render. Production case
identity remains unpinned until reviewed separately.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, copy, hashlib, json, os, stat, tempfile, types
from unittest.mock import patch


def require(v, m):
    if not v:
        raise ValueError(m)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--original-tool', type=Path, required=True)
    ap.add_argument('--work-parent', type=Path, required=True)
    a = ap.parse_args()
    code = Path(__file__).with_name('restore_low_disk.py')
    raw = code.read_bytes()
    low = types.ModuleType('controlled_low_disk')
    low.__file__ = str(code.absolute())
    exec(compile(raw, str(code), 'exec'), low.__dict__)
    original = low.load_original(a.original_tool)
    rows = []
    disk = [low.disk_checkpoint(a.work_parent, 'before_small_controls', 1024 * 1024)]
    def expect(label, function, reject=False):
        try:
            detail = function()
        except (ValueError, OSError) as e:
            require(reject, label + ': unexpected rejection: ' + str(e))
            rows.append({'case': label, 'expected': 'reject', 'passed': True,
                         'error_type': type(e).__name__, 'reason': str(e).split(':')[0]})
        else:
            require(not reject, label + ': unexpectedly accepted')
            rows.append({'case': label, 'expected': 'accept', 'passed': True, 'detail': detail})

    with tempfile.TemporaryDirectory(prefix='tiny-controls-', dir=a.work_parent) as tmp:
        root = Path(tmp)
        counter = 0
        def fixtures():
            nonlocal counter
            counter += 1
            base = root / str(counter)
            base.mkdir(mode=0o700)
            src, dst = base / 'src', base / 'dst'
            src.mkdir(mode=0o700); dst.mkdir(mode=0o700)
            source, target = src / 'archive.bin', dst / 'archive.bin'
            source.write_bytes(b'controlled archive bytes\x00\xff')
            return base, source, target, {'bytes': source.stat().st_size,
                    'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}

        def positive():
            _, source, target, row = fixtures()
            s = source.stat()
            result = low.verified_hardlink(source, target, row)
            t = target.stat()
            require((s.st_dev, s.st_ino) == (t.st_dev, t.st_ino), 'Not a hardlink')
            require((s.st_mode, s.st_mtime_ns, s.st_size) ==
                    (source.stat().st_mode, source.stat().st_mtime_ns, source.stat().st_size), 'Source modified')
            return result
        expect('regular_hardlink_exact_inode_bytes_and_source_metadata', positive)

        def edge(kind):
            base, source, target, row = fixtures()
            if kind == 'digest': row['sha256'] = '0' * 64
            elif kind == 'size': row['bytes'] += 1
            elif kind == 'source_symlink':
                real = source.with_name('real'); source.rename(real); source.symlink_to(real.name)
            elif kind == 'source_fifo':
                source.unlink(); os.mkfifo(source)
            elif kind == 'source_parent_symlink':
                real = base / 'real-src'; source.parent.rename(real); (base / 'src').symlink_to(real.name)
            elif kind == 'destination_parent_symlink':
                real = base / 'real-dst'; target.parent.rename(real); (base / 'dst').symlink_to(real.name)
            elif kind == 'target_exists': target.write_bytes(b'preserve')
            elif kind == 'target_symlink': target.symlink_to(source)
            elif kind == 'unsafe_destination_parent': target.parent.chmod(0o777)
            return low.verified_hardlink(source, target, row)
        for kind in ('digest', 'size', 'source_symlink', 'source_fifo', 'source_parent_symlink',
                     'destination_parent_symlink', 'target_exists', 'target_symlink', 'unsafe_destination_parent'):
            expect('reject_' + kind, lambda kind=kind: edge(kind), True)

        def race(kind):
            base, source, target, row = fixtures()
            actual_link = os.link
            def substituted(*args, **kwargs):
                if kind == 'source_leaf_replacement':
                    old = source.with_name('old'); source.rename(old); source.write_bytes(old.read_bytes())
                elif kind == 'source_ancestor_drift':
                    source.parent.rename(base / 'detached-src'); (base / 'src').mkdir(mode=0o700)
                elif kind == 'destination_ancestor_drift':
                    target.parent.rename(base / 'detached-dst'); (base / 'dst').mkdir(mode=0o700)
                return actual_link(*args, **kwargs)
            with patch.object(low.os, 'link', substituted):
                low.verified_hardlink(source, target, row)
        for kind in ('source_leaf_replacement', 'source_ancestor_drift', 'destination_ancestor_drift'):
            expect('reject_' + kind + '_at_link', lambda kind=kind: race(kind), True)

        def mapping():
            archive = dict(low.ARCHIVE)
            payload = b'abc\n'
            ordinary = {'canonical_public_path': 'data/example.txt', 'restore_path': 'logical/example.txt',
                        'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest(), 'mode': 'byte_exact'}
            return {'schema': 'wfu-public-scientific-copy-map-v1', 'status': 'byte_bound_ready_for_publication_gate',
                    'publication_go': False, 'original_numerical_strict_passed': False,
                    'files': [{k: r[k] for k in ('canonical_public_path', 'bytes', 'sha256')}
                              for r in (ordinary, archive)], 'copy_map': [ordinary, archive]}
        def split_good():
            d = mapping(); before = copy.deepcopy(d)
            subset, files, targets = low.split_map(original, d)
            require(d == before and len(subset['files']) == len(subset['copy_map']) == 1 and
                    subset['copy_map'][0] == d['copy_map'][0], 'Partition changed original data')
            return {'full_canonical': len(files), 'full_logical': len(targets), 'new_write_logical': 1,
                    'archive_bytes_in_metadata_only': low.ARCHIVE['bytes']}
        expect('exact_fixed_archive_partition_preserves_original_map', split_good)
        def split_bad(kind):
            d = mapping()
            if kind == 'archive_sha':
                d['files'][1]['sha256'] = d['copy_map'][1]['sha256'] = '0' * 64
            elif kind == 'archive_size':
                d['files'][1]['bytes'] += 1; d['copy_map'][1]['bytes'] += 1
            elif kind == 'archive_alias_path': d['copy_map'][1]['restore_path'] = 'different/archive.tar.xz'
            elif kind == 'extra_archive_alias':
                r = dict(d['copy_map'][1]); r['restore_path'] = 'extra/archive.tar.xz'; d['copy_map'].append(r)
            elif kind == 'archive_mode': d['copy_map'][1]['mode'] = 'metadata_only_json_projection'
            return low.split_map(original, d)
        for kind in ('archive_sha', 'archive_size', 'archive_alias_path', 'extra_archive_alias', 'archive_mode'):
            expect('reject_' + kind + '_partition', lambda kind=kind: split_bad(kind), True)

        def synthetic_tree(kind=None):
            base, source, unused, row = fixtures()
            public = base / 'public'; public.mkdir(mode=0o700)
            (public / 'data').mkdir(mode=0o700)
            (public / 'data/example.txt').write_bytes(b'abc\n')
            d = mapping()
            subset, _, _ = low.split_map(original, d)
            restored = base / 'restored'
            r = original.restore(public, subset, restored)
            archive = dict(low.ARCHIVE, bytes=row['bytes'], sha256=row['sha256'])
            dst = restored / archive['restore_path']; dst.parent.mkdir(parents=True, mode=0o700)
            low.verified_hardlink(source, dst, row)
            targets = {d['copy_map'][0]['restore_path']: d['copy_map'][0], archive['restore_path']: archive}
            if kind == 'extra_file': (restored / 'extra.bin').write_bytes(b'!')
            elif kind == 'missing_file': (restored / 'logical/example.txt').unlink()
            elif kind == 'symlink_file':
                f = restored / 'logical/example.txt'; f.unlink(); f.symlink_to(source)
            elif kind == 'same_size_corruption': (restored / 'logical/example.txt').write_bytes(b'abd\n')
            roster = low.verify_tree(restored, targets)
            require(r['passed'] is True and len(roster) == 2, 'Synthetic full verification incomplete')
            return {'synthetic_only': True, 'new_write_files': 1, 'tiny_hardlink_files': 1, 'verified_roster': roster}
        expect('original_subset_plus_tiny_hardlink_complete_fileset', synthetic_tree)
        for kind in ('extra_file', 'missing_file', 'symlink_file', 'same_size_corruption'):
            expect('reject_full_roster_' + kind, lambda kind=kind: synthetic_tree(kind), True)
        # Test disk preflight without creating data or changing the real filesystem.
        class LowSpace:
            f_bavail = 128 * 1024 * 1024
            f_frsize = 1
        def floor():
            with patch.object(low.os, 'statvfs', lambda unused: LowSpace()):
                low.disk_checkpoint(root, 'synthetic_floor', 1)
        expect('reject_projected_disk_below_128_mib', floor, True)

    disk.append(low.disk_checkpoint(a.work_parent, 'after_small_controls'))
    report = {'passed': True, 'case_count': len(rows), 'disk_checkpoints': disk, 'actual_optimization_level': sys.flags.optimize,
              'actual_cpu_affinity': sorted(os.sched_getaffinity(0)), 'case_restore_source_sha256': hashlib.sha256(raw).hexdigest(),
              'test_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'original_restore_source_sha256': low.RESTORE_SHA, 'original_primitives_source_sha256': low.PRIMITIVES_SHA,
              'production_map_pinned': low.MAP_SHA is not None, 'actual_public_restore_performed': False,
              'generic_original_synthetic_suite_rerun': False, 'cases': rows,
              'scope': 'Small controls for new hardlink, fixed partition and complete-roster boundary only; no production public restore.'}
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
