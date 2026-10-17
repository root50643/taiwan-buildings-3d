"""Pure helpers and fail-closed AEUST v15 publication checks. No import-time I/O.

Assembly and verification consume completed evidence. They never run geometry,
Blender, compression, safe extraction or replay, and never edit a producer file.
"""
from pathlib import Path, PurePosixPath
import hashlib
import importlib.util
import json
import os
import re
import stat
import sys

sys.dont_write_bytecode = True
STL = '46649566e965a049e6e333e9d82b075407c8e926e55c9034f11fbe3dbdf15a5d'
SOURCE_GO = 'e3e24f4fc32f0682f7e19b7c775118b6786ce4223c060e451d5117ae22cf9ea9'
ORIGINAL_FREEZE = 'a46bf5d5eba7ba570dd0bd4adb832663f43146858751118d619b18f2ceab6224'
ADAPTER = '11794b224ea898237e21a54b387956ba2cfbab26c8161e2da1be467f0474d368'
BLEND = 'e3ec3b7f00c8ae33b9734a3f6d10b7bc7ab1ff24fae3f0f97349616dabe8e67a'
SDNA_SOURCE = '4f81ba671556fdcee59e548ad4193e734e7c9d70d57c9846f8960e1a9ec3a065'
BLEND_FIELDS = [(171624, 1090, '2d1dc02e846e766c501535dfda01be83adbdea6d8e03a42e4e5df5377da744d1'),
                (231956, 1024, 'a27bf0cff013ac91d264ac7f6b87fe91b392cee0ed657588929e56c4f0b4d07d')]
ARCHIVE_VERIFIER = '1af27c8212057503323899b7a5f9f9171de42f78a28ff1e3e07f82d688e021fd'
VIEWS = {'front', 'rear', 'east', 'west', 'north', 'south', 'top', 'courtyard-gallery', 'courtyard-arcade'}
SCIENCE = ('standard/qa-summary.json', 'standard/raw/raw-mesh-check.json',
           'standard/sections/section-check.json', 'standard/sections/section-details.json.gz',
           'standard/sections/section-failures.json.gz', 'standard/dense/dense-check.json',
           'standard/dense/dense-original.csv.xz', 'standard/dense/dense-flagged-samples.json.gz',
           'standard/dense/dense-short-samples.json.gz', 'dense-evidence.json',
           'intersections.json', 'intersections.json.contacts.jsonl.gz')
EXACT = ('exact-recorded-ray-summary.json', 'exact-recorded-ray-details.jsonl.gz')
AUTHOR_ASSET_NAMES = ('README.md', 'STATUS.md', 'PRINTING-LIMITS.md', 'ESTIMATES-AND-SIMPLIFICATIONS.md', 'SOURCE-CREDITS.md', 'REPRODUCE.md', 'public-sources.json', 'source-geometry-mapping.json', 'parameters.json', 'requirements.txt', 'toolchain.json', 'source/build_model.py', 'source/render_preview.py', 'models/v15/build-report.json', 'models/v15/build_model.py', 'models/v15/color-regions.json', 'models/v15/model.stl', 'models/v15/parameters.json', 'models/v15/render_preview.py', 'models/v15/scene.blend', 'qa/render-check/v15-author-preflight/sanitized-previews/courtyard-arcade.png', 'qa/render-check/v15-author-preflight/sanitized-previews/courtyard-gallery.png', 'qa/render-check/v15-author-preflight/sanitized-previews/east.png', 'qa/render-check/v15-author-preflight/sanitized-previews/front.png', 'qa/render-check/v15-author-preflight/sanitized-previews/metadata-cleanup-binding.json', 'qa/render-check/v15-author-preflight/sanitized-previews/north.png', 'qa/render-check/v15-author-preflight/sanitized-previews/rear.png', 'qa/render-check/v15-author-preflight/sanitized-previews/render-manifest.json', 'qa/render-check/v15-author-preflight/sanitized-previews/south.png', 'qa/render-check/v15-author-preflight/sanitized-previews/top.png', 'qa/render-check/v15-author-preflight/sanitized-previews/west.png', 'qa/source-review/final-v15/PUBLIC-SOURCE-REVIEW.md', 'qa/source-review/final-v15/SOURCE-APPEARANCE-GO.json')
PUBLICATION_TOOLS = ('assemble_public_v15.py', 'verify_public_v15.py', 'public_bundle_common_v15.py', 'test_public_bundle_tools.py')
OMISSION_CATEGORIES = {'private_execution_log', 'raw_png_private_metadata',
                       'historical_or_failed_evidence', 'private_path_report',
                       'duplicate_reproduction_or_scratch', 'private_source_reference',
                       'outside_independent_publication_scope', 'private_control_fixture'}
ADDITIONAL_PRIVATE_MARKERS = (b'/' + b'home/', b'/' + b'root/', b'/' + b'private/var/',
                              b'GH_CONFIG_' + b'DIR', b'file:' + b'//', b'C:' + b'\\Users\\')
ADDITIONAL_SECRET_PATTERNS = (
    re.compile(rb'(?<![A-Za-z0-9_])(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})(?![A-Za-z0-9_])'),
    re.compile(rb'(?i)(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*["\x27][A-Za-z0-9_+/=-]{20,}["\x27]'))
SCIENCE_CSV_PROFILE = {
    'compressed_bytes': 31965628,
    'compressed_sha256': 'c628b2150cecf8b894bf3f0716b5e60420bec9e77eec31c320ad8e34456b4016',
    'decoded_bytes': 580378890,
    'decoded_sha256': '8534788024a73b04e27e1184fa23cacc59da04aa5f2c2180d8b7b528315deedc',
    'csv_data_rows': 477700}
SCIENCE_CSV_PATHS = {
    'author/qa/v15-full/' + mode + '/standard/dense/dense-original.csv.xz':
        'qa/v15-full/' + mode + '/standard/dense/dense-original.csv.xz'
    for mode in ('normal', 'optimized')}
SCIENCE_CSV_PATHS.update({
    'independent/final-v15-r1/geometry/' + mode + '/standard/dense/dense-original.csv.xz':
        'qa/independent/geometry/' + mode + '/standard/dense/dense-original.csv.xz'
    for mode in ('normal', 'optimized')})


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


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


def regular(root, name):
    safe_relative(name)
    require(root.is_dir() and not root.is_symlink(), 'Unsafe source root')
    p = root
    for part in PurePosixPath(name).parts:
        p = p / part
        require(not p.is_symlink(), 'Symlink in file path')
    require(p.is_file() and stat.S_ISREG(p.stat().st_mode), 'Missing/nonregular input: ' + name)
    return p


def inventory(root, exclude=(), hash_files=True):
    """All regular files; reject links/specials even in excluded subtrees."""
    require(root.is_dir() and not root.is_symlink(), 'Unsafe inventory root')
    result = {}
    def fail(error):
        raise error
    for base, dirs, files in os.walk(root, followlinks=False, onerror=fail):
        dirs.sort()
        files.sort()
        for name in dirs + files:
            p = Path(base) / name
            require(not p.is_symlink(), 'Symlink in inventory')
        for name in files:
            p = Path(base) / name
            rel = p.relative_to(root).as_posix()
            require(stat.S_ISREG(p.stat().st_mode), 'Special inventory file')
            if any(rel == x or rel.startswith(x + '/') for x in exclude):
                continue
            result[rel] = {'bytes': p.stat().st_size, 'sha256': sha(p)} if hash_files else None
    return result


def bind(path, row):
    require(type(row.get('bytes')) is int and row['bytes'] >= 0
            and type(row.get('sha256')) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']),
            'Invalid hash/size descriptor')
    require(path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], 'Hash/size differs')


def check_strict_false(summary, dense):
    require(summary.get('strict_passed') is False and dense.get('strict_passed') is False,
            'Original numerical strict=false must remain false')


def check_report(report, fields, label, opt=None):
    require(all(report.get(k) is True for k in fields), label + ': required completed result absent/false')
    if opt is not None:
        require(type(report.get('optimization_level')) is int and report['optimization_level'] == opt,
                label + ': optimization mode differs')


def completed_gates(read):
    """Read-only completed prerequisite checks; missing files/keys always fail."""
    reports = {}
    for mode, opt in [('normal', 0), ('optimized', 1)]:
        for relative, fields, check_opt in [
            ('final-v15-r1/review-' + mode + '/review-result.json',
             ['passed', 'bounded_verification_passed', 'all_read_evidence_unchanged'], True),
            ('final-v15-r1/review-artifacts-' + mode + '/artifact-structure-review.json',
             ['passed', 'all_inputs_unchanged'], True),
            ('case-controls-' + mode + '/case-controls.json', ['passed'], True),
            ('structure-parser-controls-' + mode + '/results.json', ['passed', 'all_sources_unchanged'], True),
            ('batch-manifest-' + mode + '-v1/results.json', ['passed'], False),
            ('handoff-controls-' + mode + '-v15/adapter-controls.json', ['passed', 'all_original_author_files_unchanged'], True),
            ('public-bundle-controls-' + mode + '-v15/results.json', ['passed'], True),
            ('blend-sdna-controls-' + mode + '-v15/results.json',
             ['passed', 'all_original_input_and_tool_bytes_unchanged'], True),
            ('control-blend-sdna-controls-' + mode + '-v15/results.json',
             ['passed', 'all_original_input_and_tool_bytes_unchanged'], True),
        ]:
            d = read(relative)
            check_report(d, fields, relative, opt if check_opt else None)
            reports[relative] = d
        review = reports['final-v15-r1/review-' + mode + '/review-result.json']
        require(review.get('original_numerical_strict_passed') is False and review.get('stl_sha256') == STL,
                'Review candidate/strict flag differs')
    for relative, fields in [
        ('render-policy-controls-v15/results.json', ['passed', 'all_original_inputs_unchanged']),
        ('final-v15-r1/postflight-cache-empty.json', ['passed', 'before_empty', 'after_empty']),
        ('final-v15-r1/independent-execution-summary.json', ['completed', 'all_frozen_inputs_and_tools_unchanged']),
        ('final-v15-r1/author-independent-science-comparison.json', ['passed', 'both_modes_all_scientific_evidence_identical', 'original_producer_files_unchanged']),
        ('final-v15-r1/source-appearance-binding.json', ['passed']),
        ('final-v15-r1/original-freeze-adapter-binding.json', ['passed', 'original_member_mapping_exact', 'original_manifest_itself_frozen_as_additional_file', 'no_original_member_omitted_or_rewritten']),
        ('public-controls-v15/packaging-result.json', ['passed', 'all_selected_inputs_accounted', 'sources_unchanged', 'safe_extract_all_member_hashes_verified', 'bitwise_rebuild_verified', 'all_tracked_dependencies_selected_and_copied']),
        ('public-controls-v15/replay-verification.json', ['passed', 'both_modes_safe_extraction_and_bitwise_rebuild']),
    ]:
        d = read(relative)
        check_report(d, fields, relative)
        reports[relative] = d
    require(reports['final-v15-r1/independent-execution-summary.json'].get('strict_passed') is False,
            'Execution cannot relabel strict failure')
    return reports


def load_module(path, name, expected):
    import types
    require(path.is_file() and not path.is_symlink(), 'Missing/nonregular executable helper')
    source = path.read_bytes()
    require(digest(source) == expected, 'Executable helper hash differs')
    # Compile exactly the verified in-memory bytes. Never use timestamp-valid
    # preexisting bytecode or reopen the source after its identity check.
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__package__ = ''
    sys.modules[name] = module
    exec(compile(source, str(path), 'exec'), module.__dict__)
    return module


def exact_science_csv_profile(source, destination, descriptor):
    """Only these four fixed original scientific identities may use the spool."""
    require(source in SCIENCE_CSV_PATHS and SCIENCE_CSV_PATHS[source] == destination,
            'Not an exact authorized scientific CSV source/destination')
    require(descriptor == {'bytes': SCIENCE_CSV_PROFILE['compressed_bytes'],
                           'sha256': SCIENCE_CSV_PROFILE['compressed_sha256']},
            'Exact scientific compressed CSV identity differs')
    return dict(SCIENCE_CSV_PROFILE)


def check_science_csv_reports(dense, audit, profile):
    require(dense.get('strict_passed') is False and dense.get('stl_sha256') == STL
            and dense.get('samples') == profile['csv_data_rows']
            and dense.get('csv_file') == 'dense-original.csv.xz'
            and dense.get('csv_compression') == 'xz'
            and dense.get('csv_compressed_bytes') == profile['compressed_bytes']
            and dense.get('csv_compressed_sha256') == profile['compressed_sha256']
            and dense.get('uncompressed_csv_bytes') == profile['decoded_bytes']
            and dense.get('uncompressed_csv_sha256') == profile['decoded_sha256'],
            'Original dense CSV report identity/strict flag differs')
    require(audit.get('passed') is True and audit.get('completed') is True
            and audit.get('original_numerical_strict_passed') is False
            and audit.get('stl_sha256') == STL
            and audit.get('csv_rows_verified') == profile['csv_data_rows']
            and audit.get('all_original_numerical_flag_predicates_recomputed') is True
            and audit.get('all_expected_flag_indices_and_reasons_match') is True,
            'Completed original full-row dense audit required')


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


def extended_scanner(module, sources, selected, malformed, privacy, negative):
    """Reuse v2's exact proof-bound in-memory scanner, tighten token/path checks."""
    class PublicationScanner(module.Scanner):
        def walk(self, data, name, logical, budget, depth=0, top=False, negative_tar=False):
            require(Path(name).suffix.lower() not in ('.pdf', '.jpg', '.jpeg', '.tif', '.tiff'),
                    'Source photo/PDF forbidden at every container depth')
            return super().walk(data, name, logical, budget, depth=depth, top=top, negative_tar=negative_tar)

        def plain(self, data, context, top=False):
            data = super().plain(data, context, top=top)
            require(type(data) is bytes, 'Scanner must return the validated privacy projection')
            require(not any(x in data for x in ADDITIONAL_PRIVATE_MARKERS)
                    and not any(pattern.search(data) for pattern in ADDITIONAL_SECRET_PATTERNS),
                    'Additional private path/credential pattern: ' + context)
            return data
    return PublicationScanner(sources, selected, malformed, privacy, negative)


class Context:
    def __init__(self, q, contract_path, root_overrides=None):
        self.q = q.resolve()
        self.r = self.q / 'final-v15-r1'
        self.f = self.r / 'frozen'
        self.c = self.q / 'public-controls-v15'
        self.prep = Path(__file__).parent
        self.contract_path = contract_path.resolve()
        self.contract_source_sha256 = sha(self.contract_path)
        self.contract = parse(self.contract_path.read_bytes())
        require(self.contract.get('schema') == 'aeust-v15-public-contract-1'
                and self.contract.get('ready_for_final_assembly') is True,
                'Publication contract still HOLD/incomplete')
        require(self.contract.get('publication_tool_sources_sha256') ==
                {name: sha(self.prep / name) for name in PUBLICATION_TOOLS}, 'Publication tool source freeze differs')
        self.roots = {'independent': self.q, 'author': self.f}
        for key, path in (root_overrides or {}).items():
            require(key not in self.roots and '/' not in safe_relative(key), 'Duplicate/invalid source root')
            require(path.is_dir() and not path.is_symlink(), 'Unsafe source root override')
            self.roots[key] = path.resolve()
        self.tracked = {}
        self.directory_snapshots = []

    def path(self, logical):
        safe_relative(logical)
        label, sep, rel = logical.partition('/')
        require(sep and label in self.roots, 'Unknown source label')
        return regular(self.roots[label], rel)

    def data(self, logical):
        p = self.path(logical)
        b = p.read_bytes()
        row = {'bytes': len(b), 'sha256': digest(b)}
        require(logical not in self.tracked or self.tracked[logical] == row, 'Evidence changed while reading')
        self.tracked[logical] = row
        return b

    def read(self, logical):
        return parse(self.data(logical))

    def qread(self, relative):
        return self.read('independent/' + relative)

    def unchanged(self):
        require(sha(self.contract_path) == self.contract_source_sha256, 'Publication contract changed during read')
        require(self.contract['publication_tool_sources_sha256'] ==
                {name: sha(self.prep / name) for name in PUBLICATION_TOOLS}, 'Publication tool source changed during read')
        for root, excluded, expected_names in self.directory_snapshots:
            require(set(inventory(root, exclude=excluded, hash_files=False)) == expected_names,
                    'Covered directory membership changed during read')
        for logical, row in list(self.tracked.items()):
            bind(self.path(logical), row)

    def source_control_gates(self):
        def same(report, key, logical):
            require(report[key] == digest(self.data(logical)), 'Control source identity differs: ' + key)
        for mode in ['normal', 'optimized']:
            case = self.reports['case-controls-' + mode + '/case-controls.json']
            same(case, 'source_sha256', 'independent/independent-tools/test_case_postflight.py')
            same(case, 'case_policy_source_sha256', 'independent/independent-tools/inspect_flagged_aeust_mode.py')
            require(case['baseline_stl_sha256'] == STL, 'Case-control candidate differs')
            same(case, 'baseline_dense_audit_sha256', 'independent/final-v15-r1/geometry/normal/dense-evidence.json')
            parser = self.reports['structure-parser-controls-' + mode + '/results.json']
            for key, logical in [('helper_sha256', 'author/qa/postflight-tools/artifact_structure.py'),
                                 ('test_source_sha256', 'author/qa/postflight-tools/test_artifact_structure.py'),
                                 ('launcher_source_sha256', 'independent/independent-tools/run_structure_parser_controls.py')]:
                same(parser, key, logical)
            handoff = self.reports['handoff-controls-' + mode + '-v15/adapter-controls.json']
            same(handoff, 'test_source_sha256', 'independent/independent-tools/test_handoff_adapter.py')
            same(handoff, 'adapter_source_sha256', 'independent/independent-tools/prepare_frozen_handoff.py')
            require(handoff['original_author_freeze_sha256'] == ORIGINAL_FREEZE, 'Handoff original freeze differs')
            control_sdna = self.reports['control-blend-sdna-controls-' + mode + '-v15/results.json']
            require(control_sdna['base_blend_sha256'] == BLEND, 'Control Blend baseline differs')
            same(control_sdna, 'source_sha256', 'independent/independent-tools/audit_control_blend_sdna.py')
            same(control_sdna, 'test_source_sha256', 'independent/independent-tools/test_control_blend_sdna.py')
            sdna = self.reports['blend-sdna-controls-' + mode + '-v15/results.json']
            same(sdna, 'test_source_sha256', 'independent/independent-tools/test_blend_sdna.py')
        render = self.reports['render-policy-controls-v15/results.json']
        require(render['stl_sha256'] == STL and render['original_blend_sha256'] == BLEND, 'Render-control candidate differs')
        same(render, 'original_manifest_sha256', 'author/previews/v15/render-manifest.json')
        same(render, 'test_source_sha256', 'independent/independent-tools/test_hdut_render_policy.py')
        for name, h in render['tools_sha256'].items():
            require('/' not in safe_relative(name) and h == digest(self.data('author/qa/render-tools/' + name)),
                    'Render-control tested tool differs')
        cache = self.reports['final-v15-r1/postflight-cache-empty.json']
        same(cache, 'source_sha256', 'independent/independent-tools/run_final_postflight_v15.py')
        require(cache['guard_control_count'] == 4 and cache['logical_roots'] == ['frozen', 'independent/independent-tools']
                and cache['checks'] and len({r['stage'] for r in cache['checks']}) == len(cache['checks'])
                and all(r.get('before') is True and r.get('after') is True for r in cache['checks']),
                'Completed source bytecode-cache provenance differs')

    def gates(self):
        self.reports = completed_gates(self.qread)
        self.source_control_gates()
        for mode in ['normal', 'optimized']:
            review = self.reports['final-v15-r1/review-' + mode + '/review-result.json']
            require(review.get('review_source_sha256') == digest(self.data('independent/independent-tools/review_completed_aeust_candidate.py'))
                    and review.get('case_review_source_sha256') == digest(self.data('independent/independent-tools/inspect_flagged_aeust_mode.py')),
                    'Completed review source binding differs')
            for key, row in review['evidence_inventory'].items():
                namespace, sep, rel = safe_relative(key).partition('/')
                require(sep and namespace in ('run', 'author'), 'Unknown review evidence namespace')
                logical = ('independent/final-v15-r1/' if namespace == 'run' else 'author/') + rel
                bind(self.path(logical), row)
                require(logical not in self.tracked or self.tracked[logical] == row, 'Review inventories disagree')
                self.tracked[logical] = row
            structure = self.reports['final-v15-r1/review-artifacts-' + mode + '/artifact-structure-review.json']
            require(structure.get('reviewer_sha256') == digest(self.data('independent/independent-tools/review_artifact_structure.py')),
                    'Structure reviewer source binding differs')
            for relative, row in structure['evidence_inventory'].items():
                logical = 'independent/final-v15-r1/' + safe_relative(relative)
                bind(self.path(logical), row)
                require(logical not in self.tracked or self.tracked[logical] == row, 'Structure/review identities disagree')
                self.tracked[logical] = row
        for mode in ['normal', 'optimized']:
            result = self.reports['public-bundle-controls-' + mode + '-v15/results.json']
            require(result.get('synthetic_only') is True and result.get('model_go') is False
                    and result.get('source_sha256') == sha(self.prep / 'test_public_bundle_tools.py')
                    and result.get('helper_sha256') == sha(__file__)
                    and result.get('scanner_sha256') == self.contract['control_bundle']['scanner_sha256'],
                    'Public bundle pure-control source binding differs')
        require(digest(self.data('author/qa/V15-SCIENTIFIC-HANDOFF-FREEZE.json')) == ORIGINAL_FREEZE,
                'Original author freeze hash differs')
        require(digest(self.data('independent/final-v15-r1/author-freeze-manifest.json')) == ADAPTER,
                'Runner adapter hash differs')
        original = self.read('author/qa/V15-SCIENTIFIC-HANDOFF-FREEZE.json')
        adapter = self.qread('final-v15-r1/author-freeze-manifest.json')
        require(len(original['files']) == original['file_count'] == 3690 and len(adapter['files']) == 3691,
                'Known freeze count differs')
        frozen = inventory(self.f)
        self.directory_snapshots.append((self.f, (), set(frozen)))
        expected = {row['path']: {k: row[k] for k in ['bytes', 'sha256']} for row in adapter['files']}
        require(len(expected) == len(adapter['files']) and frozen == expected, 'Frozen all-member inventory differs')
        require({k: v for k, v in expected.items() if k != 'qa/V15-SCIENTIFIC-HANDOFF-FREEZE.json'} == original['files'],
                'Adapter altered original payload')
        require(sha(regular(self.f, 'models/v15/model.stl')) == STL, 'STL differs')
        source = self.read('author/qa/source-review/final-v15/SOURCE-APPEARANCE-GO.json')
        require(digest(self.data('author/qa/source-review/final-v15/SOURCE-APPEARANCE-GO.json')) == SOURCE_GO
                and source.get('decision') == 'SOURCE-APPEARANCE-GO' and source.get('public_safe') is True,
                'Original source review differs')
        for mode, opt in [('normal', 0), ('optimized', 1)]:
            for base in ['author/qa/v15-full/' + mode, 'independent/final-v15-r1/geometry/' + mode]:
                check_strict_false(self.read(base + '/standard/qa-summary.json'), self.read(base + '/standard/dense/dense-check.json'))
            bound = self.read('author/qa/v15-author-bounded-' + mode + '-r2/bounded-review.json')
            require(bound.get('review_completed') is True and bound.get('bounded_supplemental_pass') is True
                    and bound.get('original_numerical_strict_passed') is False
                    and bound.get('all_original_flags_exactly_resolved') is True
                    and bound.get('review_optimization_level') == opt and bound.get('stl_sha256') == STL,
                    'Author bounded-r2 completion differs')
        preflight = self.read('author/qa/render-check/v15-author-preflight/SOURCE-RENDER-VERIFICATION.json')
        require(preflight.get('passed') is True and preflight.get('completed') is True
                and preflight.get('full_nine_view_rerender_verified') is False
                and preflight.get('rerender_requested') is False, 'Author preflight scope differs')
        rerender = self.qread('final-v15-r1/saved-blend-rerenders/blend-rerender-audit.json')
        require(rerender.get('passed') is True and rerender.get('strict_passed') is True
                and rerender.get('inspect_only') is False and len(rerender.get('views', [])) == 9
                and {r['view'] for r in rerender['views']} == VIEWS
                and all(r.get('posed_world_directed_geometry_matches_stl') is True for r in rerender['views']),
                'Sole formal nine-image replay incomplete')
        checks = rerender.get('checks', {})
        require(all(checks.get(k) is True for k in ['cycles_cpu_renderer', 'exactly_64_samples',
                'one_cpu_render_thread', 'fixed_nonanimated_render_seed', 'denoising_disabled',
                'all_nine_decoded_rgba_bytes_identical', 'all_nine_metadata_only_cleanups_proved',
                'all_nine_nonremoved_metadata_identical']), 'Render policy/metadata proof differs')
        require(digest(self.data('independent/independent-tools/audit_blend_sdna.py')) == SDNA_SOURCE,
                'SDNA validator original source changed')
        profiles = []
        for mode in ['normal', 'optimized']:
            sdna = self.reports['blend-sdna-controls-' + mode + '-v15/results.json']
            require(sdna['blend_sha256'] == BLEND and sdna['source_sha256'] == SDNA_SOURCE
                    and sdna['case_count'] == len(sdna['cases']) == 9
                    and all(x.get('passed') is True for x in sdna['cases']), 'SDNA control binding differs')
            profiles.append(sdna['profile'])
        require(profiles[0] == profiles[1], 'SDNA mode profiles differ')
        require([(f['field_absolute_byte_offset'], f['field_buffer_bytes'], f['field_buffer_sha256'])
                 for f in profiles[0]] == BLEND_FIELDS, 'SDNA exact field profile differs')
        self.blend_profile = profiles[0]
        comparison = self.reports['final-v15-r1/author-independent-science-comparison.json']
        expected_comparisons = {(mode, rel) for mode in ['normal', 'optimized']
                                for rel in list(SCIENCE) + ['exact-recorded-rays/' + n for n in EXACT]}
        require(len(comparison['comparisons']) == len(expected_comparisons)
                and {(x['mode'], x['logical_file']) for x in comparison['comparisons']} == expected_comparisons,
                'Scientific comparison file set incomplete/duplicated')
        for row in comparison['comparisons']:
            mode, rel = row['mode'], row['logical_file']
            author = ('author/qa/v15-recorded-rays/' + mode + '/' + Path(rel).name
                      if rel.startswith('exact-recorded-rays/') else 'author/qa/v15-full/' + mode + '/' + rel)
            independent = 'independent/final-v15-r1/geometry/' + mode + '/' + rel
            a, b = self.data(author), self.data(independent)
            require(digest(a) == row['author_sha256'] and digest(b) == row['independent_sha256']
                    and row.get('scientific_evidence_identical') is True
                    and row.get('bitwise_identical') is (a == b), 'Completed science comparison identity differs')
            exceptions = []
            if a != b:
                left, right = parse(a), parse(b)
                if rel == 'intersections.json':
                    exceptions = ['elapsed_seconds']
                    left.pop('elapsed_seconds'); right.pop('elapsed_seconds')
                elif rel == 'exact-recorded-rays/exact-recorded-ray-summary.json':
                    exceptions = ['elapsed_seconds', 'input_and_tool_sha256.intersections_report']
                    left.pop('elapsed_seconds'); right.pop('elapsed_seconds')
                    require(left['input_and_tool_sha256'].pop('intersections_report') ==
                            digest(self.data('author/qa/v15-full/' + mode + '/intersections.json'))
                            and right['input_and_tool_sha256'].pop('intersections_report') ==
                            digest(self.data('independent/final-v15-r1/geometry/' + mode + '/intersections.json')),
                            'Exact summary own intersection binding differs')
                else:
                    raise ValueError('Required original scientific byte mismatch')
                require(left == right, 'Unapproved scientific value difference')
            require(row['only_allowed_non_scientific_differences'] == exceptions,
                    'Comparison exception list differs')
        self.frozen_inventory = frozen
        self.source_review = source
        self.preflight = preflight
        return self.reports

    def scanner_setup(self):
        cfg = self.contract['control_bundle']
        # Paths are exact contract fields, not globs; fixed public names below.
        self.scanner_module = load_module(self.path(cfg['scanner_source']), 'aeust_public_v2_scanner', cfg['scanner_sha256'])
        self.selection = self.read(cfg['selection'])
        require(self.selection.get('passed') is True and self.selection.get('model_go', False) is False,
                'Controls selection incomplete or claiming model GO')
        self.malformed = self.read(cfg['malformed_allowlist'])['files']
        self.negative = self.read(cfg['negative_archive_allowlist'])['files']
        self.privacy = self.read(cfg['privacy_allowlist'])['files']
        self.sources = self.scanner_module.Sources(self.roots)
        return cfg

    def audit_archive(self):
        cfg = self.scanner_setup()
        index = self.qread('public-controls-v15/controls-index.json')
        package = self.qread('public-controls-v15/packaging-result.json')
        verifier = load_module(regular(self.f, 'qa/tools/archive_verify.py'), 'aeust_public_outer_archive', ARCHIVE_VERIFIER)
        verified, raw_tar, records = verifier.verify(self.c / 'controls.tar.xz', self.c / 'controls-index.json')
        require(sha(self.c / 'controls.tar.xz') == package['archive_sha256'] == index['archive_sha256']
                and sha(self.c / 'controls-index.json') == package['index_sha256'], 'Archive/index/package binding differs')
        require(package['source_sha256'] == cfg['scanner_sha256']
                and package['selection_sha256'] == digest(self.data(cfg['selection'])), 'Packager/selection source differs')
        replay = self.qread('public-controls-v15/replay-verification.json')
        require(replay.get('archive_sha256') == index['archive_sha256']
                and replay.get('index_sha256') == package['index_sha256']
                and replay.get('tar_sha256') == index['tar_sha256']
                and replay.get('members') == len(index['members'])
                and set(replay.get('modes', {})) == {'normal', 'optimized'}, 'Safe replay binding differs')
        for mode in ['normal', 'optimized']:
            replay_mode = replay['modes'][mode]
            require(replay_mode.get('rebuilt_archive_byte_identical') is True, 'Replay archive differs')
            for field in ['safe_validation_and_extraction', 'rebuild']:
                report = replay_mode[field]
                require(report.get('passed') is True and report.get('archive_sha256') == index['archive_sha256']
                        and report.get('tar_sha256') == index['tar_sha256']
                        and report.get('members') == len(index['members']), 'Replay mode completion differs')
        selected = self.selection['files']
        wanted = [{k: r[k] for k in ['source_relative_path', 'archive_path', 'bytes', 'sha256']} for r in selected]
        require(sorted(wanted, key=lambda r: r['archive_path']) == sorted(package['copies'], key=lambda r: r['archive_path']),
                'Package copies do not exactly match selection')
        members = {row['path']: row for row in index['members']}
        require(len(members) == len(index['members']) == len(package['copies']) + 1
                and set(members) == {r['archive_path'] for r in package['copies']} | {'ARCHIVE-SCOPE.json'},
                'Archive all-member set differs')
        # Verify raw outer tar using the original strict verifier, then inspect
        # regular members in memory. Never call extract/extractall/extract_new.
        import io
        import tarfile
        with tarfile.open(fileobj=io.BytesIO(raw_tar), mode='r:') as archive:
            actual = archive.getmembers()
            require(len(actual) == len(members) and {m.name for m in actual} == set(members)
                    and all(m.isfile() for m in actual), 'Unsafe/extra/duplicate outer member')
            scanner = extended_scanner(self.scanner_module, self.sources, selected,
                                       self.malformed, self.privacy, self.negative)
            lookup = {r['archive_path']: r for r in selected}
            for member in actual:
                safe_relative(member.name)
                require(Path(member.name).suffix.lower() not in ('.pdf', '.jpg', '.jpeg', '.tif', '.tiff'),
                        'Source photo/PDF forbidden in outer controls archive')
                data = archive.extractfile(member).read()
                row = members[member.name]
                require(len(data) == row['bytes'] and digest(data) == row['sha256'], 'Outer member identity differs')
                if member.name == 'ARCHIVE-SCOPE.json':
                    scanner.plain(data, member.name)
                    scope = parse(data)
                    require(scope['copies'] == package['copies'], 'Archive scope copy mapping differs')
                    for key, path in [('malformed_allowlist_sha256', cfg['malformed_allowlist']),
                                      ('negative_archive_allowlist_sha256', cfg['negative_archive_allowlist']),
                                      ('privacy_allowlist_sha256', cfg['privacy_allowlist'])]:
                        require(scope[key] == digest(self.data(path)), 'Archive proof-list binding differs')
                else:
                    row = lookup[member.name]
                    require(data == self.sources.read(row['source_relative_path'], row['sha256'], row['bytes']),
                            'Archive/source original bytes differ')
                    scanner.scan(row, data)
            scanner.complete()
            self.sources.unchanged()
        self.archive_copies = package['copies']
        return {'archive_members': len(members), 'archive_original_byte_copies': len(package['copies']),
                'archive_sha256': index['archive_sha256'], 'index_sha256': package['index_sha256'],
                'intentional_negative_fixture_count': len(scanner.events), 'nested_containers_extracted': False}


def verify_public_set(root, expected):
    require(inventory(root) == expected, 'Public extra/missing/nonregular/hash-changed files')


def coverage(all_sources, direct, archived, omissions, mandatory):
    """Exactly one disposition for every covered original regular file."""
    destinations = {}
    for label, rows in [('identity', direct), ('archive_identity', archived), ('explicit_private_omission', omissions)]:
        for row in rows:
            key = safe_relative(row['source_relative_path'])
            if key not in all_sources:
                continue
            require(key not in destinations, 'Overlapping source dispositions: ' + key)
            require({k: row[k] for k in ['bytes', 'sha256']} == all_sources[key], 'Coverage identity differs')
            if label == 'explicit_private_omission':
                require(key not in mandatory and row.get('category') in OMISSION_CATEGORIES
                        and type(row.get('reason')) is str and len(row['reason']) >= 20,
                        'Unapproved science omission or missing explicit reason')
            destinations[key] = dict(row, disposition=label)
    require(set(destinations) == set(all_sources), 'Unaccounted original regular files: ' + str(sorted(set(all_sources)-set(destinations))[:20]))
    require(all(destinations[k]['disposition'] == 'identity' for k in mandatory), 'Required original science not directly published')
    return {'passed': True, 'expected_files': len(all_sources), 'accounted_files': len(destinations),
            'unaccounted_files': [], 'artifacts': destinations}



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


def make_plan(c):
    c.gates()
    archive_audit = c.audit_archive()
    selected = {}
    mandatory = set()

    def add(logical, destination, compulsory=False, expected=None):
        safe_relative(destination)
        require(destination not in selected or selected[destination]['source_relative_path'] == logical,
                'Public destination collision')
        data = c.data(logical)
        row = {'source_relative_path': logical, 'public_relative_path': destination,
               'bytes': len(data), 'sha256': digest(data), 'transformation': 'identity'}
        if expected:
            require({k: row[k] for k in ['bytes', 'sha256']} == expected, 'Explicit selection identity differs')
        selected[destination] = row
        if compulsory:
            mandatory.add(logical)

    # Exactly the author's approved 33 minimum model/source/cleaned-image assets.
    # Their destinations retain original relative paths for publisher union.
    assets = c.contract['author_assets']
    require(len(assets) == 33 and {r['path'] for r in assets} == set(AUTHOR_ASSET_NAMES),
            'Exact author minimum asset set differs')
    required_assets = {'models/v15/model.stl', 'models/v15/scene.blend', 'source/build_model.py',
                       'source/render_preview.py', 'parameters.json', 'qa/source-review/final-v15/SOURCE-APPEARANCE-GO.json'}
    require(required_assets <= {r['path'] for r in assets}, 'Required author model/source assets missing')
    for row in assets:
        add('author/' + safe_relative(row['path']), row['path'], True,
            {k: row[k] for k in ['bytes', 'sha256']})
    for mode in ['normal', 'optimized']:
        for relative in SCIENCE:
            add('author/qa/v15-full/' + mode + '/' + relative,
                'qa/v15-full/' + mode + '/' + relative, True)
            add('independent/final-v15-r1/geometry/' + mode + '/' + relative,
                'qa/independent/geometry/' + mode + '/' + relative, True)
        for relative in EXACT:
            add('author/qa/v15-recorded-rays/' + mode + '/' + relative,
                'qa/v15-recorded-rays/' + mode + '/' + relative, True)
            add('independent/final-v15-r1/geometry/' + mode + '/exact-recorded-rays/' + relative,
                'qa/independent/geometry/' + mode + '/exact-recorded-rays/' + relative, True)
    # Preserve the generic wrapper's original false aggregate rather than
    # inferring a scientific mismatch from its fail-closed pre-comparison exit.
    add('author/qa/v15-full/full-qa-summary.json', 'qa/v15-full/full-qa-summary.json', True)
    for relative in ['qa/V15-SCIENTIFIC-HANDOFF-FREEZE.json', 'qa/V15-FINAL-ARTIFACT-FREEZE.json']:
        add('author/' + relative, relative, True)
    for relative in ['source-rebuild.json', 'source-scene/source-scene-audit.json',
                     'source-scene/original-scene-state.json', 'source-scene/source-scene-state.json',
                     'source-scene/source-constructed-memory-state.json', 'blend-inspect/blend-rerender-audit.json']:
        name = 'qa/render-check/v15-author-preflight/' + relative
        add('author/' + name, name)
    for name in ['author-independent-science-comparison.json', 'source-appearance-binding.json',
                 'original-freeze-adapter-binding.json', 'author-freeze-manifest.json', 'author-freeze-validation.json',
                 'source-scene-reproduction/source-scene-audit.json',
                 'source-scene-reproduction/original-scene-state.json',
                 'source-scene-reproduction/source-scene-state.json',
                 'source-scene-reproduction/source-constructed-memory-state.json',
                 'saved-blend-rerenders/blend-rerender-audit.json']:
        add('independent/final-v15-r1/' + name, 'qa/independent/' + name)
    for relative in c.reports:
        # Execution ledger can include private process arguments: keep its hash
        # and completed fields in the derived summary; exact omission required.
        if relative.endswith('/independent-execution-summary.json'):
            continue
        destination = ('qa/independent/' + relative.removeprefix('final-v15-r1/'))
        if relative.startswith('public-controls-v15/'):
            destination = 'qa/controls/' + relative.split('/', 1)[1]
        add('independent/' + relative, destination)
    for folder in ['verification', 'tools', 'render-tools']:
        for path in sorted((c.f / 'qa' / folder).iterdir()):
            if path.is_file() and path.suffix in ('.py', '.cpp'):
                relative = 'qa/' + folder + '/' + path.name
                add('author/' + relative, relative)
    for relative in ['inspect_flagged_aeust_mode.py', 'review_completed_aeust_candidate.py',
                     'review_artifact_structure.py', 'postprocess_v15.py', 'test_case_postflight.py',
                     'audit_blend_sdna.py', 'test_blend_sdna.py', 'audit_control_blend_sdna.py',
                     'test_control_blend_sdna.py', 'run_structure_parser_controls.py']:
        add('independent/independent-tools/' + relative, 'qa/case-review/' + relative)
    for source, destination in [('PUBLIC-QA-TEXT.md', 'qa/INDEPENDENT-QA.md'),
                                ('PUBLIC-QA-README.md', 'qa/README.md')]:
        add('independent/independent-tools/' + source, destination)
    for relative in ['assemble_public_v15.py', 'verify_public_v15.py', 'public_bundle_common_v15.py',
                     'test_public_bundle_tools.py']:
        add('independent/public-preparation/' + relative, 'qa/publication-tools/' + relative)
    for relative in ['controls.tar.xz', 'controls-index.json', 'packaging-result.json', 'replay-verification.json']:
        add('independent/public-controls-v15/' + relative, 'qa/controls/' + relative)
    cfg = c.contract['control_bundle']
    for key, name in [('scanner_source', 'package_controls_v2.py'), ('selection', 'controls-selection.json'),
                      ('malformed_allowlist', 'malformed-fixture-allowlist.json'),
                      ('negative_archive_allowlist', 'negative-archive-allowlist.json'),
                      ('privacy_allowlist', 'privacy-allowlist.json')]:
        add(cfg[key], 'qa/controls/' + name)
    for row in c.contract.get('additional_direct_files', []):
        add(row['source_relative_path'], row['public_relative_path'], False,
            {k: row[k] for k in ['bytes', 'sha256']})

    path_contract = c.contract['direct_path_contract']
    path_bytes = c.data(path_contract['source_relative_path'])
    require(digest(path_bytes) == path_contract['sha256'], 'Direct path contract identity differs')
    paths = parse(path_bytes)
    require(paths.get('schema') == 'aeust-v15-public-direct-destinations-1'
            and paths['files'] == [{'source_relative_path': row['source_relative_path'],
                                    'public_relative_path': destination}
                                   for destination, row in sorted(selected.items())],
            'Computed direct allowlist differs from exact static destination contract')

    # Every original frozen payload and every terminal independent file, including
    # logs, failed/historical evidence and scratch, needs a truthful disposition.
    all_sources = {'author/' + k: v for k, v in c.frozen_inventory.items()}
    run_inventory = inventory(c.r, exclude=('frozen',))
    c.directory_snapshots.append((c.r, ('frozen',), set(run_inventory)))
    all_sources.update({'independent/final-v15-r1/' + k: v for k, v in run_inventory.items()})
    roots = c.contract.get('additional_coverage_roots', [])
    required_roots = {'independent/handoff-controls-normal-v15', 'independent/handoff-controls-optimized-v15'}
    require(required_roots <= set(roots), 'Handoff fixtures must have private all-file accounting')
    for logical in roots:
        label, _, rel = safe_relative(logical).partition('/')
        require(label in c.roots, 'Unknown coverage root')
        root = c.roots[label] / rel
        root_inventory = inventory(root)
        c.directory_snapshots.append((root, (), set(root_inventory)))
        for k, v in root_inventory.items():
            all_sources[logical + '/' + k] = v
    source_inventory_ref = c.contract['control_source_inventory']
    source_inventory_bytes = c.data(source_inventory_ref['source_relative_path'])
    require(digest(source_inventory_bytes) == source_inventory_ref['sha256'],
            'Final original control-source inventory hash differs')
    source_inventory = parse(source_inventory_bytes)
    require(source_inventory.get('all_snapshot_paths_accounted') is True
            and source_inventory.get('source_changes_during_static_read') == [],
            'Original control payload inventory incomplete/unstable')
    original_records = source_inventory['files']
    require(len({r['source_relative_path'] for r in original_records}) == len(original_records),
            'Duplicate original control inventory source')
    regular_records = [r for r in original_records if r['type'] == 'regular']
    require(len(regular_records) == source_inventory['regular_file_count'], 'Original regular-file count differs')
    for row in regular_records:
        logical = safe_relative(row['source_relative_path'])
        descriptor = {k: row[k] for k in ['bytes', 'sha256']}
        bind(c.path(logical), descriptor)
        require(logical not in all_sources or all_sources[logical] == descriptor,
                'Original control inventory conflicts with frozen/current evidence')
        all_sources[logical] = descriptor
    nonregular_records = [r for r in original_records if r['type'] != 'regular']
    require(all(r['type'] == 'symlink' and re.fullmatch('[0-9a-f]{64}', r['target_descriptor_sha256'])
                for r in nonregular_records), 'Unrecognized original nonregular descriptor')
    for row in selected.values():
        all_sources.setdefault(row['source_relative_path'], {k: row[k] for k in ['bytes', 'sha256']})
    for row in c.archive_copies:
        all_sources.setdefault(row['source_relative_path'], {k: row[k] for k in ['bytes', 'sha256']})
    for logical, row in all_sources.items():
        require(logical not in c.tracked or c.tracked[logical] == row, 'Covered evidence changed during read')
        c.tracked[logical] = row
    omission_doc = c.read(c.contract['private_omissions'])
    require(omission_doc.get('ready_for_final_assembly') is True, 'Exact private omissions still HOLD')
    omissions = omission_doc['files']
    require(len({x['source_relative_path'] for x in omissions}) == len(omissions), 'Duplicate private omission')
    for row in omissions:
        bind(c.path(row['source_relative_path']), row)
        require(row['source_relative_path'] in all_sources, 'Omission outside declared payload coverage')
    # If a source is both directly copied and in archive, expose both locations.
    direct_keys = {r['source_relative_path'] for r in selected.values()}
    archive_only = [r for r in c.archive_copies if r['source_relative_path'] not in direct_keys]
    covered = coverage(all_sources, list(selected.values()), archive_only, omissions, mandatory)
    covered['control_source_inventory_sha256'] = digest(source_inventory_bytes)
    covered['original_nonregular_descriptor_snapshot'] = [
        {k: r[k] for k in ['source_relative_path', 'type', 'target_descriptor_sha256']}
        for r in nonregular_records]
    covered['nonregular_policy'] = 'Original synthetic negative-control links are represented only by the hash-bound inventory snapshot. No link is followed, copied, extracted, restored or treated as a regular scientific member.'
    covered['archive_identity_duplicates'] = [r for r in c.archive_copies if r['source_relative_path'] in direct_keys]
    covered['scope'] = 'Every regular file in the original frozen payload, terminal independent run, explicit supplemental coverage roots, and every selected source. No silent omissions; original scientific reports are unchanged.'

    # Public copies of the cleaned views are the same author relative paths.
    for name in VIEWS | {'render-manifest', 'metadata-cleanup-binding'}:
        suffix = '.png' if name in VIEWS else '.json'
        a = c.data('author/qa/render-check/v15-author-preflight/sanitized-previews/' + name + suffix)
        b = c.data('independent/final-v15-r1/public-previews/' + name + suffix)
        require(a == b, 'Author/independent cleaned preview differs')
    review = c.reports['final-v15-r1/review-normal/review-result.json']
    optimized = c.reports['final-v15-r1/review-optimized/review-result.json']
    require(review['geometry'] == optimized['geometry'] and review['images'] == optimized['images'],
            'Completed review scientific/image results differ')
    summary = {k: review[k] for k in ['stl_sha256', 'geometry', 'images', 'bounded_verification_passed',
               'original_numerical_strict_passed', 'source_stl_bitwise_identical',
               'source_color_regions_bitwise_identical', 'source_saved_scene_state_matches']}
    summary.update(schema='aeust-v15-derived-public-qa-1', passed=True,
                   both_readonly_review_modes_passed=True, physical_print_performed=False,
                   full_nine_view_rerender_verified=True,
                   author_preflight_full_nine_view_rerender_verified=c.preflight['full_nine_view_rerender_verified'],
                   author_preflight_report_sha256=c.tracked['author/qa/render-check/v15-author-preflight/SOURCE-RENDER-VERIFICATION.json']['sha256'],
                   original_full_qa_summary=c.read('author/qa/v15-full/full-qa-summary.json'),
                   architectural_scope=c.source_review['accepted_evidence_limits'],
                   source_appearance_decision=c.source_review['decision'],
                   render_policy={'engine': 'CYCLES', 'device': 'CPU', 'samples': 64, 'threads': 1,
                                  'fixed_seed': True, 'denoising': False, 'OIDN_used': False},
                   scope='Derived from completed original evidence only. Early representative exterior; all dimensions estimates. Two courtyards, nonparallel wings, giant frames and glass box remain. Local-axis view labels are not surveyed geographic bearings. Finite evidence is not a global minimum-wall-thickness or physical-print guarantee.',
                   control_result_bindings={k: c.tracked['independent/' + k] for k in c.reports},
                   controls_archive=archive_audit)
    # The original aggregate remains a direct byte copy. Avoid duplicating its
    # full structure in the derived report; record only its exact hash and false.
    original_summary = summary.pop('original_full_qa_summary')
    summary['original_full_qa_summary_sha256'] = c.tracked['author/qa/v15-full/full-qa-summary.json']['sha256']
    summary['original_full_qa_normal_optimized_scientific_evidence_identical'] = original_summary['checks']['normal_optimized_scientific_evidence_identical']
    require(summary['original_full_qa_normal_optimized_scientific_evidence_identical'] is False,
            'Original fail-closed wrapper comparison field changed')
    summary['original_wrapper_comparison_scope'] = 'The generic inspector failed closed on original numerical strict=false before comparison. Its false field is preserved; the separate completed byte/allowed-timing comparison establishes scientific equivalence.'
    binding = {'schema': 'aeust-v15-publication-binding-1', 'stl_sha256': STL,
               'original_author_freeze_sha256': ORIGINAL_FREEZE, 'runner_adapter_sha256': ADAPTER,
               'source_appearance_go_sha256': SOURCE_GO, 'contract_sha256': sha(c.contract_path),
               'files': sorted(selected.values(), key=lambda r: r['public_relative_path']),
               'omitted_private_evidence': omissions,
               'original_source_and_review_prose_unchanged': True,
               'scope': 'Independent allowlist including exact 33 author assets; publisher union requires identical overlapping bytes. Author README/STATUS retain author-stage wording. Raw PNGs, logs and historical failures have explicit private hash records. The public derived summary does not rewrite any producer verdict.',
               'publication_tool_hashes': {name: sha(c.prep / name) for name in PUBLICATION_TOOLS}}
    generated = {'qa/independent/QA-RESULT.json': dump(summary),
                 'qa/PUBLICATION-BINDING.json': dump(binding), 'qa/EVIDENCE-COVERAGE.json': dump(covered),
                 'qa/independent/blend-public-path-profile.json': dump({
                     'passed': True, 'blend_sha256': BLEND, 'source_sha256': SDNA_SOURCE,
                     'profile': c.blend_profile,
                     'control_results': {mode: c.tracked['independent/blend-sdna-controls-' + mode + '-v15/results.json']
                                         for mode in ['normal', 'optimized']},
                     'scope': 'Only this exact original Blend and these two full SDNA field buffers qualify. For privacy scanning only the two proven generic effective strings are masked in memory; every other byte, including all NUL tails, remains scanned. Original published Blend bytes are unchanged.'})}
    require(not set(generated) & set(selected), 'Derived/source destination collision')

    # Scan every direct payload plus derived files. Outer archive was already
    # fully scanned per original member above; don't give nested fixtures a
    # blanket compression exception by recursively rescanning the whole outer.
    normal_rows = [dict(row, source_relative_path='public/' + destination)
                   for destination, row in selected.items() if destination != 'qa/controls/controls.tar.xz']
    normal_rows += [{'source_relative_path': 'public/' + name, 'bytes': len(data), 'sha256': digest(data)}
                    for name, data in generated.items()]
    # Only complete scene JSON top-level render/filepath may use the exact generic temporary render default.
    privacy = []
    for row in normal_rows:
        destination = row['source_relative_path'][7:]
        if destination.endswith(('original-scene-state.json', 'source-scene-state.json', 'source-constructed-memory-state.json')):
            privacy.append({k: row[k] for k in ['source_relative_path', 'bytes', 'sha256']} |
                           {'kind': 'json_blender_render_default', 'json_pointer': '/render/filepath'})
    direct_sources = c.scanner_module.Sources(c.roots)
    scanner = extended_scanner(c.scanner_module, direct_sources, normal_rows, [], privacy, [])
    csv_scans = []
    csv_content_proofs = {}
    for row in normal_rows:
        destination = row['source_relative_path'][7:]
        data = generated[destination] if destination in generated else c.data(selected[destination]['source_relative_path'])
        require(Path(destination).suffix.lower() not in ('.pdf', '.jpg', '.jpeg', '.tif', '.tiff'),
                'Source photo/PDF must not be published')
        if Path(destination).suffix.lower() == '.png':
            require(destination in {'qa/render-check/v15-author-preflight/sanitized-previews/' + view + '.png' for view in VIEWS},
                    'Only the nine source-bound metadata-cleaned preview PNGs are direct public images')
        if destination.endswith('/dense-original.csv.xz'):
            require(destination in selected, 'Scientific CSV must be an original identity copy')
            source = selected[destination]['source_relative_path']
            profile = exact_science_csv_profile(source, destination, {'bytes': len(data), 'sha256': digest(data)})
            dense_source = source.rsplit('/', 1)[0] + '/dense-check.json'
            audit_source = source.split('/standard/dense/', 1)[0] + '/dense-evidence.json'
            dense, audit = c.read(dense_source), c.read(audit_source)
            check_science_csv_reports(dense, audit, profile)
            require(audit['dense_report_sha256'] == digest(c.data(dense_source)),
                    'Full-row dense audit is not bound to its original report')
            # The 32 MB original compressed bytes get the complete ordinary
            # plain scan even when an identical decoded proof can be reused.
            require(scanner.plain(data, row['source_relative_path'], top=True) == data,
                    'Scientific compressed bytes cannot use any privacy projection')
            content_key = (len(data), digest(data))
            reused = content_key in csv_content_proofs
            if not reused:
                csv_content_proofs[content_key] = bounded_xz_csv_privacy_scan(c.scanner_module, data, profile)
            csv_scans.append({'source_relative_path': source, 'public_relative_path': destination,
                              'dense_report': c.tracked[dense_source], 'full_row_dense_audit': c.tracked[audit_source],
                              'decoded_scan_reused_for_identical_payload': reused,
                              'complete_privacy_scan': csv_content_proofs[content_key]})
        elif destination == 'models/v15/scene.blend':
            scanner.scan(row, mask_exact_blend_defaults(data))
        else:
            scanner.scan(row, data)
    scanner.complete()
    require(len(csv_scans) == 4 and {r['source_relative_path'] for r in csv_scans} == set(SCIENCE_CSV_PATHS),
            'Complete four-source scientific CSV scan coverage required')
    csv_report_name = 'qa/independent/dense-csv-privacy-scan.json'
    require(csv_report_name not in generated and csv_report_name not in selected, 'CSV scan report destination collision')
    csv_report = dump({'schema': 'aeust-v15-exact-dense-csv-privacy-1', 'passed': True,
                       'helper_sha256': sha(__file__),
                       'scanner_sha256': c.contract['control_bundle']['scanner_sha256'],
                       'files': sorted(csv_scans, key=lambda r: r['public_relative_path']),
                       'generic_scanner_byte_limit_unchanged': c.scanner_module.MAX_BYTES,
                       'original_scientific_bytes_and_strict_false_unchanged': True,
                       'scope': 'Only four exact original CSV identities use a bounded unnamed private spool and complete read-only mmap privacy scan. No generic size limit increase, science omission, schema waiver, or model acceptance is granted.'})
    report_row = {'source_relative_path': 'public/' + csv_report_name, 'bytes': len(csv_report), 'sha256': digest(csv_report)}
    report_scanner = extended_scanner(c.scanner_module, c.scanner_module.Sources(c.roots), [report_row], [], [], [])
    report_scanner.scan(report_row, csv_report)
    report_scanner.complete()
    generated[csv_report_name] = csv_report
    c.unchanged()
    return selected, generated, covered, archive_audit


def argument_parser(description):
    import argparse
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--qa-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--source-root', action='append', default=[], metavar='LABEL=PATH')
    return parser


def roots_from_args(values):
    roots = {}
    for value in values:
        label, sep, path = value.partition('=')
        require(sep and label not in roots, 'Invalid/duplicate additional root')
        roots[label] = Path(path)
    return roots
