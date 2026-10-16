"""Reproduce the external lossless dense-ray cache, never declare full QA passed.

Import API (all return JSON-compatible dictionaries, including on failure):
    verify_contract(root)
    verify_cache(root, cache_path)
    rebuild_cache(root, destination)

Only the original manifest's pinned bytes authorize the scientific inputs.
The metadata is checked against that contract, not used as a trust anchor.
Rebuilding runs byte-identical original scientific code in a temporary snapshot.
No public scientific report is replaced. Exit zero means cache reproduction only.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile


ORIGINAL_MANIFEST = 'reference/full-release/freeze-manifest.json'
ORIGINAL_MANIFEST_SHA256 = '91c5af48df3f355a324bf4a54a631028e1d9a910fa7aedfa40d788b71a397fb2'
DENSE_REPORT = 'qa/dense/dense-check.json'
FLAG_FILE = 'qa/dense/dense-flagged-samples.json.gz'
SHORT_FILE = 'qa/dense/dense-short-samples.json.gz'
CACHE_LOGICAL_PATH = 'qa/dense/dense-original.csv.gz'
DEFAULT_EXTERNAL_PATH = '../nccu-public-center-cache/dense-original.csv.gz'
GZIP_BYTES = 31248909
UNCOMPRESSED_BYTES = 248127151
CHECKERS = (
    'check_controls.py', 'check_dense_surface.py', 'check_raw_mesh.py',
    'check_sections.py', 'dense_original.cpp', 'qa_common.py', 'run_qa.py',
)
PINNED_INPUTS = ('model.stl',) + tuple('verification/' + n for n in CHECKERS) + (
    DENSE_REPORT, FLAG_FILE, SHORT_FILE,
)
EXPECTED_FLAG_IDS = [(10272, 0), (17099, 0), (17100, 0), (17101, 0)]
EXPECTED_CHECKS = {
    'every_original_face_exactly_ten_samples': True,
    'stored_normals_agree_with_original_directed_faces': True,
    'all_original_ray_intervals_and_controls_valid': False,
    'all_first_original_chords_ge_0p8mm': True,
}


class ContractError(RuntimeError):
    """Messages are logical identifiers only, never exception paths or output."""


def _require(condition, reason):
    if not condition:
        raise ContractError(reason)


def _hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, 'duplicate_json_key')
        result[key] = value
    return result


def _bad_constant(_):
    raise ContractError('nonfinite_json_constant')


def _json(path, compressed=False):
    opener = gzip.open if compressed else open
    with opener(path, 'rt', encoding='utf-8') as handle:
        return json.load(handle, object_pairs_hook=_pairs, parse_constant=_bad_constant)


def _result(operation, passed=False, reasons=(), **details):
    return {
        'operation': operation,
        'passed': bool(passed),
        'reasons': list(reasons),
        'original_strict_passed': False,
        'current_science_replayed': False,
        'scope': 'External dense diagnostic cache only; not a full QA pass.',
        **details,
    }


def _error(operation, error, **details):
    # Ordinary Python exception strings can contain a private filesystem path.
    reason = str(error) if isinstance(error, ContractError) else 'operation_error:' + type(error).__name__
    return _result(operation, reasons=[reason], **details)


def _expected_metadata(manifest, dense):
    files = manifest['files']
    return {
        'schema': 1,
        'kind': 'external_lossless_dense_diagnostic_cache',
        'original_manifest': {'logical_path': ORIGINAL_MANIFEST, 'sha256': ORIGINAL_MANIFEST_SHA256},
        'stl_sha256': files['model.stl'],
        'checker_sources_sha256': {name: files['verification/' + name] for name in CHECKERS},
        'original_dense_report': {'logical_path': DENSE_REPORT, 'sha256': files[DENSE_REPORT]},
        'original_flags': {'logical_path': FLAG_FILE, 'sha256': files[FLAG_FILE], 'count': dense['flagged_sample_count']},
        'original_shorts': {'logical_path': SHORT_FILE, 'sha256': files[SHORT_FILE], 'count': dense['under_0p8mm_count']},
        'cache': {
            'logical_path': CACHE_LOGICAL_PATH,
            'default_external_path': DEFAULT_EXTERNAL_PATH,
            'gzip_sha256': dense['csv_gzip_sha256'],
            'uncompressed_sha256': dense['uncompressed_csv_sha256'],
            'gzip_bytes': GZIP_BYTES,
            'uncompressed_bytes': UNCOMPRESSED_BYTES,
        },
        'original_triangles': dense['original_triangles'],
        'samples': dense['samples'],
        'samples_per_original_face': dense['samples_per_original_face'],
        'minimum_first_chord_mm': dense['minimum_first_chord_mm'],
        'minimum_required_chord_mm': dense['minimum_required_chord_mm'],
        'origin_outside_offset_mm': dense['origin_outside_offset_mm'],
        'expected_original_checker_exit': 1,
        'original_strict_passed': False,
        'current_science_replayed': False,
        'success_means': 'Exact cache reproduction only. Four original flags and strict false remain.',
    }


def _contract(root):
    root = Path(root).resolve()
    manifest_path = root / ORIGINAL_MANIFEST
    _require(manifest_path.is_file(), 'missing_original_manifest')
    _require(_hash(manifest_path) == ORIGINAL_MANIFEST_SHA256, 'original_manifest_sha256_mismatch')
    manifest = _json(manifest_path)
    files = manifest['files']
    _require(manifest['algorithm'] == 'sha256', 'original_manifest_algorithm_mismatch')
    for logical in PINNED_INPUTS:
        path = root / logical
        _require(path.is_file(), 'missing_pinned_input:' + logical)
        _require(_hash(path) == files[logical], 'pinned_input_sha256_mismatch:' + logical)
    inventory = sorted(p.name for p in (root / 'verification').iterdir()
                       if p.is_file() and p.suffix in ('.py', '.cpp'))
    _require(inventory == sorted(CHECKERS), 'scientific_checker_inventory_mismatch')
    dense = _json(root / DENSE_REPORT)
    expected_sources = {n: files['verification/' + n] for n in CHECKERS}
    _require(_canonical(dense['checker_sources_sha256']) == _canonical(expected_sources), 'dense_checker_inventory_mismatch')
    _require(dense['stl_sha256'] == files['model.stl'] == manifest['stl_sha256'], 'dense_stl_binding_mismatch')
    _require(dense['cpp_source_sha256'] == expected_sources['dense_original.cpp'], 'dense_cpp_binding_mismatch')
    _require(dense['csv_file'] == Path(CACHE_LOGICAL_PATH).name, 'dense_csv_name_mismatch')
    _require(dense['csv_gzip_sha256'] == files[CACHE_LOGICAL_PATH], 'dense_csv_manifest_binding_mismatch')
    _require(dense['flagged_samples_sha256'] == files[FLAG_FILE], 'dense_flags_binding_mismatch')
    _require(dense['short_chords_sha256'] == files[SHORT_FILE], 'dense_shorts_binding_mismatch')
    _require(dense['flagged_samples_file'] == Path(FLAG_FILE).name, 'dense_flags_name_mismatch')
    _require(dense['short_chords_file'] == Path(SHORT_FILE).name, 'dense_shorts_name_mismatch')
    _require(dense['passed'] is False and dense['strict_passed'] is False, 'original_strict_false_not_preserved')
    _require(_canonical(dense['checks']) == _canonical(EXPECTED_CHECKS), 'original_dense_check_flags_mismatch')
    _require(dense['original_triangles'] == 30186 and dense['samples'] == 301860 and
             dense['samples_per_original_face'] == 10, 'original_dense_coverage_mismatch')
    _require(dense['under_0p8mm_count'] == 0 and dense['flagged_sample_count'] == 4, 'original_dense_outcome_mismatch')
    flags = _json(root / FLAG_FILE, compressed=True)
    shorts = _json(root / SHORT_FILE, compressed=True)
    _require([(r['original_face_index'], r['sample_index']) for r in flags] == EXPECTED_FLAG_IDS,
             'original_four_flag_rows_mismatch')
    _require(shorts == [], 'original_short_list_not_empty')
    expected = _expected_metadata(manifest, dense)
    metadata_path = root / 'compact-cache.json'
    _require(metadata_path.is_file(), 'missing_compact_cache_metadata')
    _require(_canonical(_json(metadata_path)) == _canonical(expected), 'compact_cache_metadata_mismatch')
    return root, manifest, dense, expected, flags, shorts


def verify_contract(root):
    """Verify immutable inputs and metadata without needing the external CSV."""
    try:
        _, manifest, dense, metadata, _, _ = _contract(root)
        return _result('verify_contract', True, original_manifest_sha256=ORIGINAL_MANIFEST_SHA256,
                       stl_sha256=manifest['files']['model.stl'], verified_input_count=len(PINNED_INPUTS),
                       expected_cache=metadata['cache'], samples=dense['samples'], original_flag_count=4)
    except Exception as error:
        return _error('verify_contract', error)


def _cache_bytes(cache_path, expected):
    _require(cache_path is not None, 'missing_dense_cache')
    path = Path(cache_path)
    _require(path.is_file(), 'missing_dense_cache')
    size = path.stat().st_size
    _require(size == expected['gzip_bytes'], 'external_dense_cache_gzip_size_mismatch')
    compressed_hash = _hash(path)
    _require(compressed_hash == expected['gzip_sha256'], 'external_dense_cache_gzip_sha256_mismatch')
    h = hashlib.sha256()
    count = 0
    with gzip.open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            count += len(block)
            _require(count <= expected['uncompressed_bytes'], 'external_dense_cache_decompressed_size_exceeded')
            h.update(block)
    _require(count == expected['uncompressed_bytes'], 'external_dense_cache_uncompressed_size_mismatch')
    _require(h.hexdigest() == expected['uncompressed_sha256'], 'external_dense_cache_uncompressed_sha256_mismatch')
    return {'logical_path': CACHE_LOGICAL_PATH, 'gzip_bytes': size, 'uncompressed_bytes': count,
            'gzip_sha256': compressed_hash, 'uncompressed_sha256': h.hexdigest()}


def verify_cache(root, cache_path):
    """Fail closed on missing/changed contract, metadata, gzip or decoded bytes."""
    try:
        _, _, _, metadata, _, _ = _contract(root)
        observed = _cache_bytes(cache_path, metadata['cache'])
        _contract(root)  # Inputs must also remain unchanged while cache is read.
        return _result('verify_cache', True, cache=observed, cache_reproduced=False)
    except Exception as error:
        return _error('verify_cache', error, cache_reproduced=False)


def _outside_package(destination, root):
    destination = Path(destination).resolve()
    _require(not destination.is_relative_to(root), 'cache_destination_must_be_outside_package')
    _require(not destination.is_dir(), 'cache_destination_is_directory')
    return destination


def rebuild_cache(root, destination):
    """Replay the exact dense checker; atomically publish only an exact CSV.

    The original checker must return exactly 1 and reproduce every dense report
    field (except the platform-specific compiled binary hash), the exact four
    flag rows, empty short output and both exact CSV hashes. Temporary output is
    discarded on failure, without changing any public report or previous cache.
    """
    details = {'cache_reproduced': False, 'expected_original_checker_exit': 1,
               'python_optimization_level': sys.flags.optimize}
    try:
        root, manifest, original, metadata, original_flags, original_shorts = _contract(root)
        destination = _outside_package(destination, root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.nccu-dense-replay-', dir=destination.parent) as temp:
            work = Path(temp)
            snapshot = work / 'snapshot'
            (snapshot / 'verification').mkdir(parents=True)
            for logical in ('model.stl',) + tuple('verification/' + n for n in CHECKERS):
                shutil.copyfile(root / logical, snapshot / logical)
                _require(_hash(snapshot / logical) == manifest['files'][logical],
                         'replay_snapshot_sha256_mismatch:' + logical)
            command = [sys.executable, '-B']
            if sys.flags.optimize:
                command.append('-' + 'O' * sys.flags.optimize)
            command += ['verification/check_dense_surface.py', '--stl', 'model.stl', '--out', 'dense']
            environment = os.environ.copy()
            environment['PYTHONDONTWRITEBYTECODE'] = '1'
            # Captured original output can mention temporary paths. Never save or
            # forward it: the import API and CLI expose logical identifiers only.
            run = subprocess.run(command, cwd=snapshot, env=environment,
                                 capture_output=True, text=True, timeout=1800)
            details['observed_original_checker_exit'] = run.returncode
            _require(run.returncode == 1, 'unexpected_original_dense_checker_exit')
            output = snapshot / 'dense'
            _require((output / 'dense-check.json').is_file(), 'replayed_dense_report_missing')
            replayed = _json(output / 'dense-check.json')
            details['fresh_original_dense_report_sha256'] = _hash(output / 'dense-check.json')
            details['fresh_original_dense_report'] = replayed
            binary_key = 'compiled_executable_sha256'
            _require(set(replayed) == set(original), 'replayed_dense_report_schema_mismatch')
            _require(isinstance(replayed[binary_key], str) and
                     re.fullmatch('[0-9a-f]{64}', replayed[binary_key]) is not None,
                     'replayed_compiled_binary_hash_invalid')
            scientific_original = {k: v for k, v in original.items() if k != binary_key}
            scientific_replayed = {k: v for k, v in replayed.items() if k != binary_key}
            _require(_canonical(scientific_replayed) == _canonical(scientific_original),
                     'replayed_dense_report_fields_mismatch')
            for logical in (FLAG_FILE, SHORT_FILE):
                _require(_hash(output / Path(logical).name) == manifest['files'][logical],
                         'replayed_evidence_bytes_mismatch:' + logical)
            replayed_flags = _json(output / Path(FLAG_FILE).name, compressed=True)
            replayed_shorts = _json(output / Path(SHORT_FILE).name, compressed=True)
            _require(_canonical(replayed_flags) == _canonical(original_flags), 'replayed_four_flag_rows_mismatch')
            _require(_canonical(replayed_shorts) == _canonical(original_shorts), 'replayed_short_rows_mismatch')
            observed = _cache_bytes(output / 'dense-original.csv.gz', metadata['cache'])
            for logical in ('model.stl',) + tuple('verification/' + n for n in CHECKERS):
                _require(_hash(snapshot / logical) == manifest['files'][logical],
                         'replay_snapshot_changed_during_run:' + logical)
            _contract(root)
            _outside_package(destination, root)
            # Same-filesystem temporary file, fully verified before replacement.
            with (output / 'dense-original.csv.gz').open('rb') as handle:
                os.fsync(handle.fileno())
            os.replace(output / 'dense-original.csv.gz', destination)
            observed = _cache_bytes(destination, metadata['cache'])
            details.update({
                'cache_reproduced': True,
                'dense_cache_replay_completed': True,
                'atomic_destination_readback_verified': True,
                'cache': observed,
                'original_flag_count': 4,
                'original_short_count': 0,
                'all_dense_report_fields_match_except_compiled_binary_hash': True,
                'compiled_binary_hash': {
                    'reference': original[binary_key], 'replayed': replayed[binary_key],
                    'matches_reference': replayed[binary_key] == original[binary_key],
                    'platform_difference_only_allowed_if_all_scientific_outputs_match': True,
                },
            })
        return _result('rebuild_cache', True, **details)
    except Exception as error:
        return _error('rebuild_cache', error, **details)


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ContractError('invalid_cli_arguments')


def main(argv=None):
    try:
        parser = _Parser(description=__doc__)
        parser.add_argument('--out', type=Path, help='External CSV destination; default is the sibling cache directory.')
        args = parser.parse_args(argv)
        root = Path(__file__).resolve().parent
        destination = args.out if args.out is not None else root / DEFAULT_EXTERNAL_PATH
        result = rebuild_cache(root, destination)
    except Exception as error:
        result = _error('rebuild_cache', error, cache_reproduced=False)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
