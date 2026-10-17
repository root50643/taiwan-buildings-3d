"""Small pure-function controls. No project geometry, images, replay or model GO.
Creates only synthetic fixtures in its own NEW output directory. Run separately
under normal Python and -O after the parent grants the CPU scheduling slot.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse
import gzip
import io
import json
import lzma
import tempfile
import tarfile
import unittest
import zipfile
# Pin and execute exactly the helper bytes read here. -B alone does not stop
# stale bytecode reads; this bootstrap never consults Python's module cache.
import hashlib as _hashlib
import types as _types
COMMON_SOURCE_SHA256 = '75f1604d4f67e87906325c7394d39b96fad98e1c44ca59db862307b4a35b935a'
_common_path = Path(__file__).with_name('public_bundle_common_v15.py')
_common_bytes = _common_path.read_bytes()
if _hashlib.sha256(_common_bytes).hexdigest() != COMMON_SOURCE_SHA256:
    raise ValueError('Publication helper source identity differs')
_common = _types.ModuleType('aeust_verified_publication_common')
_common.__file__ = str(_common_path)
exec(compile(_common_bytes, str(_common_path), 'exec'), _common.__dict__)
require = _common.require
digest = _common.digest
dump = _common.dump
parse = _common.parse
sha = _common.sha
bind = _common.bind
coverage = _common.coverage
inventory = _common.inventory
check_strict_false = _common.check_strict_false
check_report = _common.check_report
completed_gates = _common.completed_gates
verify_public_set = _common.verify_public_set
safe_relative = _common.safe_relative
extended_scanner = _common.extended_scanner
load_module = _common.load_module

SCANNER = None
WORK = None
FIXTURES = {}


class PublicationControls(unittest.TestCase):
    def test_missing_prerequisite_rejected(self):
        def unavailable(path):
            raise FileNotFoundError(path)
        with self.assertRaises(FileNotFoundError):
            completed_gates(unavailable)

    def test_required_report_completion(self):
        check_report({'passed': True, 'completed': True}, ['passed', 'completed'], 'synthetic validation only')
        for bad in [False, None, 1, 'true']:
            with self.subTest(value=bad), self.assertRaises(ValueError):
                check_report({'passed': bad}, ['passed'], 'synthetic validation only')

        for wrong in [True, 0.0, '0', None]:
            with self.subTest(optimization=wrong), self.assertRaises(ValueError):
                check_report({'passed': True, 'optimization_level': wrong}, ['passed'], 'synthetic mode', 0)

    def test_strict_false_preserved(self):
        check_strict_false({'strict_passed': False}, {'strict_passed': False})
        for a, b in [(True, False), (False, True), (True, True), (0, False), (False, None)]:
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                check_strict_false({'strict_passed': a}, {'strict_passed': b})

    def test_verified_memory_source_loader(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory(dir=WORK) as d:
            p = Path(d) / 'synthetic_helper.py'
            source = b'VALUE = 7\n'
            p.write_bytes(source)
            with patch('importlib.util.spec_from_file_location', side_effect=RuntimeError('Forbidden path-based import')):
                module = load_module(p, 'synthetic_publication_loader_control', digest(source))
            self.assertEqual(module.VALUE, 7)
            with self.assertRaises(ValueError):
                load_module(p, 'synthetic_publication_loader_wrong_hash', '0' * 64)

    def test_entrypoints_ignore_stale_bytecode(self):
        import importlib.util
        import marshal
        import struct
        import subprocess
        source_dir = Path(__file__).parent
        with tempfile.TemporaryDirectory(dir=WORK) as d:
            root = Path(d)
            helper = root / 'public_bundle_common_v15.py'
            helper.write_bytes(_common_bytes)
            cache = root / '__pycache__'
            cache.mkdir()
            bad_code = compile("raise RuntimeError('STALE_PUBLICATION_CACHE_EXECUTED')", str(helper), 'exec')
            header = importlib.util.MAGIC_NUMBER + struct.pack('<III', 0, int(helper.stat().st_mtime), helper.stat().st_size)
            for opt in ['', '1']:
                target = Path(importlib.util.cache_from_source(str(helper), optimization=opt))
                target.write_bytes(header + marshal.dumps(bad_code))
            for name in ['assemble_public_v15.py', 'verify_public_v15.py']:
                with self.subTest(entrypoint=name):
                    script = root / name
                    script.write_bytes((source_dir / name).read_bytes())
                    command = [sys.executable, '-B'] + (['-O'] if sys.flags.optimize else []) + [str(script), '--help']
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr.decode())
                    self.assertIn(b'--contract', result.stdout)
                    self.assertEqual(helper.read_bytes(), _common_bytes)

    def test_hash_and_freeze_descriptor(self):
        with tempfile.TemporaryDirectory(dir=WORK) as d:
            p = Path(d) / 'fixture'
            p.write_bytes(b'original')
            bind(p, {'bytes': 8, 'sha256': digest(b'original')})
            for row in [{'bytes': 7, 'sha256': digest(b'original')}, {'bytes': 8, 'sha256': '0' * 64}]:
                with self.subTest(row=row), self.assertRaises(ValueError):
                    bind(p, row)

    def test_public_exact_file_set(self):
        with tempfile.TemporaryDirectory(dir=WORK) as d:
            root = Path(d)
            (root / 'a').write_bytes(b'A')
            expected = inventory(root)
            verify_public_set(root, expected)
            (root / 'extra').write_bytes(b'B')
            with self.assertRaises(ValueError):
                verify_public_set(root, expected)
            (root / 'extra').unlink()
            (root / 'a').unlink()
            with self.assertRaises(ValueError):
                verify_public_set(root, expected)

    def test_public_identity_changed(self):
        with tempfile.TemporaryDirectory(dir=WORK) as d:
            root = Path(d)
            (root / 'a').write_bytes(b'A')
            expected = inventory(root)
            (root / 'a').write_bytes(b'B')
            with self.assertRaises(ValueError):
                verify_public_set(root, expected)

    def test_public_symlink_rejected(self):
        with tempfile.TemporaryDirectory(dir=WORK) as d:
            root = Path(d)
            (root / 'a').write_bytes(b'A')
            expected = inventory(root)
            (root / 'link').symlink_to('a')
            with self.assertRaises(ValueError):
                verify_public_set(root, expected)

    def test_science_coverage(self):
        row = {'source_relative_path': 'synthetic/science.json', 'bytes': 2, 'sha256': digest(b'{}')}
        source = {'synthetic/science.json': {k: row[k] for k in ['bytes', 'sha256']}}
        result = coverage(source, [row], [], [], set(source))
        self.assertEqual(result['accounted_files'], 1)
        with self.assertRaises(ValueError):
            coverage(source, [], [], [], set(source))
        omission = dict(row, category='historical_or_failed_evidence', reason='Synthetic omission cannot hide required science.')
        with self.assertRaises(ValueError):
            coverage(source, [], [], [omission], set(source))

    def test_safe_paths_and_json(self):
        for name in ['../escape', '/absolute', 'a/../b', 'a//b', 'C:/root', 'a\\b']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                safe_relative(name)
        for data in [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b'{"x":-1e999}']:
            with self.subTest(data=data), self.assertRaises(ValueError):
                parse(data)

    def scan(self, data, name, privacy=False):
        row = {'source_relative_path': 'synthetic/' + name, 'bytes': len(data), 'sha256': digest(data)}
        fixture_relative = 'payloads/' + digest(data) + '/' + name
        fixture = WORK / fixture_relative
        fixture.parent.mkdir(parents=True, exist_ok=True)
        if fixture.exists():
            require(fixture.read_bytes() == data, 'Synthetic fixture collision')
        else:
            fixture.write_bytes(data)
        FIXTURES[fixture_relative] = {'bytes': len(data), 'sha256': digest(data)}
        allowances = [dict(row, kind='json_blender_render_default', json_pointer='/render/filepath')] if privacy else []
        scanner = extended_scanner(SCANNER, SCANNER.Sources({'synthetic': WORK}), [row], [], allowances, [])
        scanner.scan(row, data)
        scanner.complete()

    def test_unknown_bad_compression(self):
        for name, data in [('bad.gz', b'bad gzip'), ('bad.xz', b'bad xz'), ('bad.zip', b'bad zip')]:
            with self.subTest(name=name), self.assertRaises((ValueError, EOFError, lzma.LZMAError)):
                self.scan(data, name)

    def test_complete_compression_and_trailing_rejected(self):
        for suffix, data in [('gz', gzip.compress(b'plain', mtime=0)), ('xz', lzma.compress(b'plain'))]:
            with self.subTest(kind=suffix):
                self.scan(data, 'good.' + suffix)
                with self.assertRaises(ValueError):
                    self.scan(data + b'junk', 'tail.' + suffix)

    def test_nested_private_paths(self):
        private = b'/' + b'workspace/' + b'private-fixture'
        nested = gzip.compress(lzma.compress(private), mtime=0)
        with self.assertRaises(ValueError):
            self.scan(nested, 'nested.xz.gz')
        z = io.BytesIO()
        with zipfile.ZipFile(z, 'w') as f:
            f.writestr('plain.txt', private)
        with self.assertRaises(ValueError):
            self.scan(z.getvalue(), 'nested.zip')
        t = io.BytesIO()
        with tarfile.open(fileobj=t, mode='w', format=tarfile.USTAR_FORMAT) as f:
            member = tarfile.TarInfo('plain.txt')
            member.size = len(private)
            f.addfile(member, io.BytesIO(private))
        with self.assertRaises(ValueError):
            self.scan(t.getvalue(), 'nested.tar')

    def test_credential_patterns(self):
        examples = [b'gh' + b'p_' + b'A' * 36, b'sk-' + b'proj-' + b'A' * 40,
                    b'xox' + b'b-' + b'A' * 24, b'AK' + b'IA' + b'A' * 16,
                    b'Authorization: ' + b'Bearer ' + b'A' * 24]
        for data in examples:
            with self.subTest(hash=digest(data)), self.assertRaises(ValueError):
                self.scan(data, 'credentials.txt')

    def test_exact_scene_default(self):
        tmp = '/' + 'tmp/'
        data = dump({'render': {'filepath': tmp}, 'objects': []})
        self.scan(data, 'scene.json', privacy=True)
        with self.assertRaises(ValueError):
            self.scan(data, 'scene.json')
        for obj in [{'render': {'filepath': tmp + 'private'}},
                    {'render': {'filepath': tmp}, 'extra': '/' + 'home/agent/' + 'private'},
                    {'render': {'filepath': tmp}, 'extra': tmp}]:
            with self.subTest(obj=obj), self.assertRaises(ValueError):
                self.scan(dump(obj), 'scene.json', privacy=True)

    def test_source_imagery_rejected(self):
        for name in ['source.pdf', 'source.jpg', 'source.jpeg', 'source.tif', 'source.tiff']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.scan(b'synthetic non-image bytes', name)
        z = io.BytesIO()
        with zipfile.ZipFile(z, 'w') as f:
            f.writestr('nested-source.pdf', b'synthetic non-image bytes')
        with self.assertRaises(ValueError):
            self.scan(z.getvalue(), 'nested-source.zip')

    def test_private_plaintext_is_not_allowed_by_filename(self):
        for name in ['controls.txt', 'controls.json', 'source.py', 'scene.blend']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.scan(b'/' + b'Users/' + b'private-fixture', name)

    def streaming_fixture(self, raw, encoded=None, changes=None):
        encoded = lzma.compress(raw) if encoded is None else encoded
        profile = {'compressed_bytes': len(encoded), 'compressed_sha256': digest(encoded),
                   'decoded_bytes': len(raw), 'decoded_sha256': digest(raw),
                   'csv_data_rows': raw.count(b'\n') - 1}
        if changes:
            profile.update(changes)
        for suffix, data in [('csv', raw), ('csv.xz', encoded)]:
            relative = 'streaming/' + digest(data) + '.' + suffix
            target = WORK / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                self.assertEqual(target.read_bytes(), data)
            else:
                target.write_bytes(data)
            FIXTURES[relative] = {'bytes': len(data), 'sha256': digest(data)}
        return encoded, profile

    def test_streaming_exact_csv_identity_scope(self):
        expected = _common.SCIENCE_CSV_PROFILE
        descriptor = {'bytes': expected['compressed_bytes'], 'sha256': expected['compressed_sha256']}
        self.assertEqual(len(_common.SCIENCE_CSV_PATHS), 4)
        for source, destination in _common.SCIENCE_CSV_PATHS.items():
            self.assertEqual(_common.exact_science_csv_profile(source, destination, descriptor), expected)
            for wrong_source, wrong_destination, wrong_descriptor in [
                ('synthetic/other.csv.xz', destination, descriptor),
                (source, 'qa/other.csv.xz', descriptor),
                (source, destination, dict(descriptor, bytes=descriptor['bytes'] - 1)),
                (source, destination, dict(descriptor, sha256='0' * 64))]:
                with self.subTest(source=source, destination=wrong_destination), self.assertRaises(ValueError):
                    _common.exact_science_csv_profile(wrong_source, wrong_destination, wrong_descriptor)

    def test_streaming_csv_positive_complete_buffer(self):
        raw = b'column\n' + b'0123456789,' * 8192 + b'\n'
        encoded, profile = self.streaming_fixture(raw)
        original_limit = SCANNER.MAX_BYTES
        before = inventory(WORK)
        proof = _common.bounded_xz_csv_privacy_scan(SCANNER, encoded, profile, chunk_bytes=31)
        self.assertTrue(proof['complete_decoded_buffer_scanned'])
        self.assertTrue(proof['full_original_compressed_buffer_scanned'])
        self.assertTrue(proof['single_complete_xz_stream'])
        self.assertFalse(proof['persistent_decoded_copy_written'])
        self.assertEqual(SCANNER.MAX_BYTES, original_limit)
        self.assertEqual(inventory(WORK), before)

    def test_streaming_csv_private_paths_across_chunks_and_tail(self):
        markers = tuple(SCANNER.PRIVATE_MARKERS) + (SCANNER.TMP_MARKER,) + _common.ADDITIONAL_PRIVATE_MARKERS
        for marker in markers:
            for position in ['cross_chunk', 'tail']:
                with self.subTest(marker_sha256=digest(marker), position=position):
                    body = (b'0' * 24 + marker + b'0' * 8192 if position == 'cross_chunk'
                            else b'0' * 8192 + marker)
                    encoded, profile = self.streaming_fixture(b'col\n' + body + b'\n')
                    # The compressed raw scan must pass: rejection below then
                    # specifically demonstrates the complete decoded scan.
                    _common.scan_complete_plain_buffer(SCANNER, encoded)
                    with self.assertRaisesRegex(ValueError, 'Private path marker'):
                        # One-byte decoder output guarantees every multi-byte
                        # marker crosses actual writes, independent of framing.
                        _common.bounded_xz_csv_privacy_scan(SCANNER, encoded, profile,
                                                           chunk_bytes=1 if position == 'cross_chunk' else 31)

    def test_streaming_csv_credentials_across_chunks_and_tail(self):
        tokens = [b'gh' + b'p_' + b'A' * 36, b'sk-' + b'proj-' + b'A' * 40,
                  b'xox' + b'b-' + b'A' * 24, b'AK' + b'IA' + b'A' * 16,
                  b'Authorization: ' + b'Bearer ' + b'A' * 24,
                  b'password=' + b'"' + b'A' * 24 + b'"',
                  b'-----BEGIN ' + b'RSA PRIVATE KEY-----']
        for token in tokens:
            for position in ['cross_chunk', 'tail']:
                with self.subTest(token_sha256=digest(token), position=position):
                    body = (b'0' * 23 + b' ' + token + b' ' + b'0' * 8192 if position == 'cross_chunk'
                            else b'0' * 8192 + b' ' + token)
                    encoded, profile = self.streaming_fixture(b'col\n' + body + b'\n')
                    _common.scan_complete_plain_buffer(SCANNER, encoded)
                    with self.assertRaisesRegex(ValueError, 'Credential-shaped content'):
                        _common.bounded_xz_csv_privacy_scan(SCANNER, encoded, profile,
                                                           chunk_bytes=1 if position == 'cross_chunk' else 31)

    def test_streaming_csv_exact_lengths_and_hashes(self):
        raw = b'column\n' + b'0' * 8192 + b'\n'
        encoded, profile = self.streaming_fixture(raw)
        changes = [{'compressed_bytes': len(encoded) - 1}, {'compressed_bytes': len(encoded) + 1},
                   {'compressed_sha256': '0' * 64}, {'decoded_bytes': len(raw) - 1},
                   {'decoded_bytes': len(raw) + 1}, {'decoded_sha256': '0' * 64},
                   {'csv_data_rows': 2}, {'decoded_bytes': 0}]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                _common.bounded_xz_csv_privacy_scan(SCANNER, encoded, dict(profile, **change), chunk_bytes=31)
        encoded, profile = self.streaming_fixture(raw[:-1])
        with self.assertRaisesRegex(ValueError, 'data-row/line count'):
            _common.bounded_xz_csv_privacy_scan(SCANNER, encoded, profile, chunk_bytes=31)

    def test_streaming_csv_single_stream_and_trailing(self):
        raw = b'column\n' + b'0' * 8192 + b'\n'
        original = lzma.compress(raw)
        for encoded in [original + b'garbage', original + b'\0' * 4,
                        original + lzma.compress(b''), original[:-1], b'bad' + original[3:]]:
            encoded, profile = self.streaming_fixture(raw, encoded)
            with self.subTest(hash=digest(encoded)), self.assertRaises((ValueError, lzma.LZMAError)):
                _common.bounded_xz_csv_privacy_scan(SCANNER, encoded, profile, chunk_bytes=31)

    def test_streaming_csv_compressed_plain_patterns_required(self):
        for marker, message in [(b'/' + b'workspace/' + b'negative', 'Private path marker'),
                                (b'sk-' + b'proj-' + b'A' * 40, 'Credential-shaped content')]:
            encoded, profile = self.streaming_fixture(b'column\n0\n', b'prefix ' + marker)
            with self.subTest(hash=digest(encoded)), self.assertRaisesRegex(ValueError, message):
                _common.bounded_xz_csv_privacy_scan(SCANNER, encoded, profile)

    def test_streaming_csv_original_reports_remain_required(self):
        p = _common.SCIENCE_CSV_PROFILE
        dense = {'strict_passed': False, 'stl_sha256': _common.STL, 'samples': p['csv_data_rows'],
                 'csv_file': 'dense-original.csv.xz', 'csv_compression': 'xz',
                 'csv_compressed_bytes': p['compressed_bytes'], 'csv_compressed_sha256': p['compressed_sha256'],
                 'uncompressed_csv_bytes': p['decoded_bytes'], 'uncompressed_csv_sha256': p['decoded_sha256']}
        audit = {'passed': True, 'completed': True, 'original_numerical_strict_passed': False,
                 'stl_sha256': _common.STL, 'csv_rows_verified': p['csv_data_rows'],
                 'all_original_numerical_flag_predicates_recomputed': True,
                 'all_expected_flag_indices_and_reasons_match': True}
        _common.check_science_csv_reports(dense, audit, p)
        for change in [{'strict_passed': True}, {'samples': p['csv_data_rows'] - 1},
                       {'uncompressed_csv_sha256': '0' * 64}]:
            with self.subTest(dense_change=change), self.assertRaises(ValueError):
                _common.check_science_csv_reports(dict(dense, **change), audit, p)
        for change in [{'completed': False}, {'original_numerical_strict_passed': True},
                       {'csv_rows_verified': p['csv_data_rows'] - 1}]:
            with self.subTest(audit_change=change), self.assertRaises(ValueError):
                _common.check_science_csv_reports(dense, dict(audit, **change), p)

    def test_unknown_large_file_has_no_streaming_exception(self):
        from unittest.mock import patch
        raw = b'0' * (256 * 1024 + 1)
        encoded = lzma.compress(raw, filters=[{'id': lzma.FILTER_LZMA2, 'dict_size': 4096}])
        with patch.object(SCANNER, 'MAX_BYTES', 256 * 1024):
            with self.assertRaises(ValueError):
                self.scan(encoded, 'unknown-large.xz')
        self.assertEqual(SCANNER.MAX_BYTES, 512 * 1024 * 1024)


class LedgerResult(unittest.TextTestResult):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.ledger = []
    def addSuccess(self, test):
        super().addSuccess(test)
        self.ledger.append({'test': test.id(), 'passed': True, 'kind': 'method'})
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.ledger.append({'test': test.id(), 'passed': False, 'kind': 'method'})
    def addError(self, test, err):
        super().addError(test, err)
        self.ledger.append({'test': test.id(), 'passed': False, 'kind': 'error'})
    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        self.ledger.append({'test': test.id(), 'subtest_descriptor_sha256': digest(str(subtest).encode()), 'passed': err is None, 'kind': 'subtest'})


def main():
    global SCANNER, WORK
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--scanner', type=Path, required=True)
    ap.add_argument('--scanner-sha256', required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    require(not a.out.exists() and not a.out.is_symlink(), 'Fresh test output required')
    a.out.mkdir(parents=True)
    WORK = a.out / 'fixtures'
    WORK.mkdir()
    SCANNER = load_module(a.scanner, 'publication_control_scanner', a.scanner_sha256)
    result = unittest.TextTestRunner(verbosity=2, resultclass=LedgerResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(PublicationControls))
    summary = {'passed': result.wasSuccessful(), 'optimization_level': sys.flags.optimize,
               'model_go': False, 'synthetic_only': True, 'geometry_or_render_run': False,
               'test_methods': result.testsRun, 'subtest_count': sum(r['kind'] == 'subtest' for r in result.ledger),
               'source_sha256': sha(__file__), 'helper_sha256': sha(Path(__file__).with_name('public_bundle_common_v15.py')),
               'scanner_sha256': sha(a.scanner), 'cases': result.ledger,
               'fixture_inventory': FIXTURES,
               'fixture_policy': 'Synthetic private-path and credential-shaped negative inputs remain original bytes in the private fixture tree. Do not bulk publish these fixtures; exact omission hashes remain required.'}
    (a.out / 'results.json').write_bytes(dump(summary))
    print(dump(summary).decode(), end='')
    return 0 if summary['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
