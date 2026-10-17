"""Create one NEW explicit public directory only after all final results exist.
No geometry, Blender, compression, replay or repair is performed here.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import os
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
sha = _common.sha
dump = _common.dump
digest = _common.digest
inventory = _common.inventory
verify_public_set = _common.verify_public_set


def main():
    ap = argument_parser(__doc__)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    out = a.out.absolute()
    require(not out.exists() and not out.is_symlink(), 'Fresh public directory required')
    # Output may not be nested in any producer or formal run tree.
    q = a.qa_root.resolve()
    require(out.parent.resolve() == q, 'Output must be a new immediate child of the independent QA root')
    manifest = out.with_name(out.name + '-COPYLIST.json')
    require(not manifest.exists() and not manifest.is_symlink(), 'Fresh copylist path required')
    require(out.name.startswith('public-v15-') and out.name != 'public-controls-v15', 'Dedicated public output name required')
    c = Context(q, a.contract, roots_from_args(a.source_root))
    selected, generated, coverage, archive = make_plan(c)
    # No output exists before every completed gate, exact-byte coverage and
    # recursive privacy/proof audit has succeeded.
    out.mkdir(exist_ok=False)
    expected = {}
    for destination, row in sorted(selected.items()):
        data = c.data(row['source_relative_path'])
        require(len(data) == row['bytes'] and digest(data) == row['sha256'], 'Source changed before copy')
        target = out / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(data)
        expected[destination] = {k: row[k] for k in ['bytes', 'sha256']}
    for destination, data in sorted(generated.items()):
        target = out / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(data)
        expected[destination] = {'bytes': len(data), 'sha256': digest(data)}
    c.unchanged()
    verify_public_set(out, expected)
    # Manifest is intentionally outside the public root to avoid self-hashing.
    manifest = out.with_name(out.name + '-COPYLIST.json')
    require(not manifest.exists() and not manifest.is_symlink(), 'Fresh copylist path required')
    result = {'schema': 'aeust-v15-public-copylist-1', 'passed': True, 'stl_sha256': c.reports['final-v15-r1/review-normal/review-result.json']['stl_sha256'],
              'root_directory': out.name, 'file_count': len(expected), 'files': expected,
              'contract_sha256': sha(c.contract_path), 'assembly_source_sha256': sha(__file__),
              'scope': 'Exact relative paths for publisher union. Every overlap must have identical bytes; no source image/PDF, raw preview, silent omission or science rewrite.'}
    with manifest.open('xb') as stream:
        stream.write(dump(result))
    print(dump({'passed': True, 'public_root': out.name, 'copylist': manifest.name,
                'copylist_sha256': sha(manifest), 'public_file_count': len(expected),
                'original_regular_files_accounted': coverage['accounted_files']}).decode(), end='')


if __name__ == '__main__':
    main()
