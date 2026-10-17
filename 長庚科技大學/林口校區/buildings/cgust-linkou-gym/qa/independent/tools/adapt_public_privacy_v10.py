"""Prepare narrow case constants from the final, corrected WFU public scanner.
Does not execute a scan, build payloads, or grant approval. Output is fresh only.
"""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import os

W = Path(__file__).resolve().parents[2]
OLD = W / 'wfu-shengyou-independent-qa/public-package-privacy-v1'
OUT = W / 'cgust-linkou-gym-independent-qa/public-package-privacy-v10'
BLEND = '24405788a4c5bf2e88a2402089f5d7fc9bc6b360afa97cc316760bdf3e668a1b'
CSV = {'compressed_bytes': 2644728,
       'compressed_sha256': '99ccbee592a29e80c02e0565212a2cbff03fc8feb1b4300cc6ed372b53753359',
       'decoded_bytes': 40229114,
       'decoded_sha256': '42cd8adaf225258b0cc38c08496c91925e22acfb495db739cae3f89aa2c4df89',
       'csv_data_rows': 51760}
SOURCE_PINS = {
    'exact_privacy_primitives.py': '1b8f3d36243bdd1bc090bbf1dffa55e9f80d803bce73c2354efb7f466b15f6cd',
    'check_wfu_privacy.py': '58e7025590eec9efc7f242552ac22c950fc8e41d41c5eb74051ee323c3a9e950',
    'package_controls_v2.py': '1402e983241d78d19969380b45ce79b7cd3936207a4324710a17b094f5ac256c',
    'roster_primitives.py': '7211c544e258dd4855ca9747837845aa683d6c28c3939ea0b9a08cb271d69273',
    'restore_scientific_layout.py': '60b9e1f3b6974e8884501e7f7a5b18446dea04a15886ed864ff7c2de2ab2581e',
    'archive_verify.py': '1af27c8212057503323899b7a5f9f9171de42f78a28ff1e3e07f82d688e021fd',
}


def require(v, m):
    if not v:
        raise RuntimeError(m)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def assignment(source, name, value):
    tree = ast.parse(source)
    matches = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
               and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name]
    require(len(matches) == 1, 'Single fixed assignment required: ' + name)
    n = matches[0]
    lines = source.splitlines(keepends=True)
    return ''.join(lines[:n.lineno-1]) + name + ' = ' + repr(value) + '\n' + ''.join(lines[n.end_lineno:])


def main():
    require(not OUT.exists(), 'Refuse existing adaptation output')
    raw = {name: (OLD / name).read_bytes() for name in SOURCE_PINS}
    require(all(sha(raw[name]) == pin for name, pin in SOURCE_PINS.items()), 'Original source pin differs')
    OUT.mkdir()
    changed = {}
    primitive = raw['exact_privacy_primitives.py'].decode()
    primitive = primitive.replace('Only fixed WFU candidate/profile constants', 'Only fixed CGUST candidate/profile constants')
    primitive = assignment(primitive, 'BLEND', BLEND)
    primitive = assignment(primitive, 'SCIENCE_CSV_PROFILE', CSV)
    primitive_bytes = primitive.encode()
    changed['exact_privacy_primitives.py'] = ('exact_privacy_primitives.py', primitive_bytes)
    checker = raw['check_wfu_privacy.py'].decode()
    checker = checker.replace('WFU', 'CGUST').replace('wfu_verified_', 'cgust_verified_')
    checker = assignment(checker, 'PRIMITIVES_SHA', sha(primitive_bytes))
    checker = assignment(checker, 'BLEND_SHA', BLEND)
    checker = assignment(checker, 'BLEND_BYTES', 883140)
    checker = assignment(checker, 'BLEND_PATH', 'models/v10/scene.blend')
    checker = assignment(checker, 'CSV_PATH', 'qa/v9-full/normal/standard/dense/dense-original.csv.xz')
    checker = assignment(checker, 'CSV_ITEMS', tuple(CSV.items()))
    # Keep old-case markers too; adding this case never weakens original coverage.
    old = "CGUST_MARKERS = (b'wfu-shengyou-' + b'private-v1', b'wfu-shengyou-source-' + b'audit-private')"
    require(old in checker, 'Original marker assignment absent')
    checker = checker.replace(old, old + " + (b'cgust-linkou-gym-' + b'private-v1', b'cgust-linkou-gym-source-' + b'audit-private')")
    checker = checker.replace("'exact_privacy_primitives.py': 6783", "'exact_privacy_primitives.py': " + str(len(primitive_bytes)))
    checker = checker.replace('decoded_newline_count=209461', 'decoded_newline_count=51761')
    checker = checker.replace('exact_decoded_bound_bytes=194500309', 'exact_decoded_bound_bytes=40229114')
    checker = checker.replace('all_original_patterns_plus_common_and_wfu_markers', 'all_original_patterns_plus_common_and_case_markers')
    changed['check_cgust_privacy.py'] = ('check_wfu_privacy.py', checker.encode())
    records = []
    for new_name, (old_name, data) in changed.items():
        ast.parse(data)
        (OUT / new_name).write_bytes(data)
        diff = ''.join(difflib.unified_diff(raw[old_name].decode().splitlines(True), data.decode().splitlines(True),
                                          fromfile='original/' + old_name, tofile='adapted/' + new_name))
        (OUT / (new_name + '.diff')).write_text(diff)
        records.append({'source': 'historical-scanner/' + old_name, 'source_bytes': len(raw[old_name]),
                        'source_sha256': sha(raw[old_name]), 'adapted': new_name,
                        'bytes': len(data), 'sha256': sha(data), 'diff_sha256': sha(diff.encode())})
    for name in SOURCE_PINS:
        if name not in ('exact_privacy_primitives.py', 'check_wfu_privacy.py'):
            os.link(OLD / name, OUT / name)
            records.append({'source': 'historical-scanner/' + name, 'adapted': name,
                            'bytes': len(raw[name]), 'sha256': sha(raw[name]), 'byte_exact_reuse': True})
    report = {'scope': 'Preparation only. Final scanner integration and both-mode controls are still required.',
              'files': records, 'scene_sha256': BLEND, 'csv_profile': CSV,
              'originals_unchanged': all((OLD / name).read_bytes() == data for name, data in raw.items())}
    (OUT / 'CASE-HELPERS-ADAPTATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'prepared_files': len(records), 'publication_go': False}))


if __name__ == '__main__':
    main()
