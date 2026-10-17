"""Narrow final-scanner identity/table binding. No archive or CSV decoding."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import os
from adapt_public_privacy_v10 import assignment, require

W = Path(__file__).resolve().parents[2]
OLD = W / 'wfu-shengyou-independent-qa/public-package-privacy-v1'
OUT = W / 'cgust-linkou-gym-independent-qa/public-package-privacy-v10'
TABLE = W / 'cgust-linkou-gym-independent-qa/scene-state-bridge-v10/SOURCE-STATE-DEFAULT-EXCEPTIONS.json'


def row(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def main():
    require(OUT.is_dir() and not (OUT / 'scan_public_package.py').exists(), 'Fresh scanner output required')
    table = TABLE.read_bytes()
    table_value = json.loads(table)
    require(table_value['schema'] == 'cgust-source-state-exact-generic-default-scan-exceptions-v1'
            and len(table_value['files']) == 6, 'Exact final state table required')
    raw = (OLD / 'scan_public_package.py').read_bytes()
    require(row(raw)['sha256'] == '20a8bcfe207d8b9e6b268669e629a107b8067456502a6df4c712f00794712366', 'Final original scanner differs')
    source = raw.decode().replace('WFU', 'CGUST').replace('wfu', 'cgust')
    tree = ast.parse(source)
    tools = ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign)
                             and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'TOOLS'))
    for name in tools:
        tools[name] = row((OUT / name).read_bytes())
    source = assignment(source, 'TOOLS', tools)
    source = assignment(source, 'STATE_EXCEPTIONS', row(table))
    source = assignment(source, 'STATE_HASHES', {
        '0e03d8ce76b8a040925bdf70d0a93b94f17c043000866f32cb33b8e2a1f694e7': 120264,
        '3c5ecbeb2109c40e0ba7662907d116725986d4e25d82a47ad3f0922ccde5ac73': 120263})
    source = source.replace('== 155195', '== 108037').replace('== 155196', '== 108038')
    data = source.encode()
    ast.parse(data)
    (OUT / 'scan_public_package.py').write_bytes(data)
    (OUT / 'provenance').mkdir()
    os.link(TABLE, OUT / 'provenance/state-exceptions.reference.json')
    diff = ''.join(difflib.unified_diff(raw.decode().splitlines(True), source.splitlines(True),
                                      fromfile='historical-scanner/scan_public_package.py',
                                      tofile='cgust-scanner/scan_public_package.py'))
    (OUT / 'scan_public_package.py.diff').write_text(diff)
    original_test = (OLD / 'test_public_package.py').read_bytes()
    test = original_test.decode().replace('check_wfu_privacy.py', 'check_cgust_privacy.py')
    test = test.replace('WFU_MARKERS', 'CGUST_MARKERS').replace('new_wfu_', 'new_cgust_')
    test = assignment(test, 'ENTRY_BYTES', len(data))
    test = assignment(test, 'ENTRY_SHA', row(data)['sha256'])
    ast.parse(test)
    (OUT / 'test_public_package.py').write_text(test)
    testdiff = ''.join(difflib.unified_diff(original_test.decode().splitlines(True), test.splitlines(True),
                                          fromfile='historical-scanner/test_public_package.py',
                                          tofile='cgust-scanner/test_public_package.py'))
    (OUT / 'test_public_package.py.diff').write_text(testdiff)
    report = {'scope': 'Narrow current-case bindings and labels only; historical archive constants/policy unchanged. Both-mode small integration controls and real full-package scans remain required.',
              'source': row(raw), 'adapted': row(data), 'diff': row(diff.encode()),
              'original_test': row(original_test), 'adapted_test': row(test.encode()),
              'test_diff': row(testdiff.encode()), 'exact_state_table': row(table),
              'bound_sources': tools,
              'original_sources_unchanged': (OLD / 'scan_public_package.py').read_bytes() == raw and
                  (OLD / 'test_public_package.py').read_bytes() == original_test}
    (OUT / 'SCANNER-ADAPTATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'prepared': True, 'scanner': row(data), 'publication_go': False}))


if __name__ == '__main__':
    main()
