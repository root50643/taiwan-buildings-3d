"""Read-only recheck of completed source gates, public bytes and all-member scope.
Changes no producer/public files, extracts no archive, and emits only stdout.
The four exact large CSVs use a private unlinked temporary scan spool, removed
on completion or failure. Redirect stdout outside the public tree if desired.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
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
Context = _common.Context
argument_parser = _common.argument_parser
roots_from_args = _common.roots_from_args
make_plan = _common.make_plan
require = _common.require
parse = _common.parse
sha = _common.sha
dump = _common.dump
digest = _common.digest
verify_public_set = _common.verify_public_set
regular = _common.regular
STL = _common.STL


def main():
    ap = argument_parser(__doc__)
    ap.add_argument('--public', type=Path, required=True)
    ap.add_argument('--copylist', type=Path, required=True)
    a = ap.parse_args()
    require(a.public.is_dir() and not a.public.is_symlink(), 'Missing/unsafe public directory')
    manifest_bytes = a.copylist.read_bytes()
    manifest_digest = digest(manifest_bytes)
    manifest = parse(manifest_bytes)
    require(manifest.get('schema') == 'aeust-v15-public-copylist-1'
            and manifest.get('passed') is True and manifest.get('stl_sha256') == STL
            and manifest['file_count'] == len(manifest['files'])
            and manifest['root_directory'] == a.public.name, 'Public manifest scope differs')
    verify_public_set(a.public, manifest['files'])
    c = Context(a.qa_root, a.contract, roots_from_args(a.source_root))
    require(manifest['contract_sha256'] == sha(a.contract), 'Assembly contract differs')
    require(manifest.get('assembly_source_sha256') == c.contract['publication_tool_sources_sha256']['assemble_public_v15.py'],
            'Copylist assembler source binding differs')
    selected, generated, coverage, archive = make_plan(c)
    expected = {name: {k: row[k] for k in ['bytes', 'sha256']} for name, row in selected.items()}
    expected.update({name: {'bytes': len(data), 'sha256': digest(data)} for name, data in generated.items()})
    require(expected == manifest['files'], 'Recomputed exact publication plan differs')
    for name, row in selected.items():
        require(regular(a.public, name).read_bytes() == c.data(row['source_relative_path']), 'Identity source copy changed')
    for name, data in generated.items():
        require(regular(a.public, name).read_bytes() == data, 'Derived summary/binding/coverage differs')
    c.unchanged()
    require(sha(a.copylist) == manifest_digest, 'Copylist changed during verification')
    verify_public_set(a.public, expected)
    print(dump({'passed': True, 'stl_sha256': STL, 'copylist_sha256': manifest_digest,
                'public_file_count': len(expected), 'public_bytes': sum(x['bytes'] for x in expected.values()),
                'original_regular_files_accounted': coverage['accounted_files'],
                'original_numerical_strict_false_preserved': True,
                'author_preflight_nine_rerender_false_preserved': True,
                'direct_source_copies': len(selected), 'archive': archive,
                'source_photos_and_pdfs_not_included': True, 'read_only': True,
                'read_only_scope': 'All original producer and public files; only private unlinked temporary CSV scan storage is written, with no persistent decoded output.',
                'scope': 'Exact allowlist integrity and bounded token/private-path scan; no claim of universal secret detection, geometry proof beyond original gates, or physical-print certification.'}).decode(), end='')


if __name__ == '__main__':
    main()
