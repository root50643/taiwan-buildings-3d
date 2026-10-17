"""Final-map identity controls only; no payload restoration or archive reading."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, hashlib, json, types
from unittest.mock import patch


def require(v, m):
    if not v:
        raise ValueError(m)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--original-tool', type=Path, required=True)
    ap.add_argument('--copy-map', type=Path, required=True)
    a = ap.parse_args()
    source = Path(__file__).with_name('restore_low_disk.py')
    module = types.ModuleType('pinned_case')
    module.__file__ = str(source.absolute())
    code = source.read_bytes()
    exec(compile(code, str(source), 'exec'), module.__dict__)
    original = module.load_original(a.original_tool)
    raw = a.copy_map.read_bytes()
    rows = []
    def check(label, callback, reject=False):
        try: callback()
        except ValueError as error:
            require(reject, 'Unexpected rejection: ' + label)
            rows.append({'case': label, 'passed': True, 'expected': 'reject', 'reason': str(error)})
        else:
            require(not reject, 'Unexpected acceptance: ' + label)
            rows.append({'case': label, 'passed': True, 'expected': 'accept'})
    check('exact_final_map_sha_counts_and_archive_alias', lambda: module.validate_case_map(original, raw))
    check('changed_map_bytes', lambda: module.validate_case_map(original, raw + b'\n'), True)
    for label, attribute, replacement in [('wrong_expected_sha', 'MAP_SHA', '0' * 64),
                                           ('wrong_canonical_count', 'CANONICAL_COUNT', 551),
                                           ('wrong_logical_count', 'LOGICAL_COUNT', 1270),
                                           ('unpinned_identity', 'MAP_SHA', None)]:
        def changed(attribute=attribute, replacement=replacement):
            with patch.object(module, attribute, replacement):
                module.validate_case_map(original, raw)
        check(label, changed, True)
    replay = types.ModuleType('pinned_replay')
    exec(compile(source.with_name('replay_public_restore.py').read_bytes(), 'replay_public_restore.py', 'exec'), replay.__dict__)
    check('replay_pins_exact_final_restore_source', lambda: require(replay.CASE_RESTORE_SHA == hashlib.sha256(code).hexdigest(),
                                                                 'Replay target source pin differs'))
    d = module.validate_case_map(original, raw)
    subset, files, targets = module.split_map(original, d)
    print(json.dumps({'passed': True, 'case_count': len(rows), 'cases': rows,
                      'actual_optimization_level': sys.flags.optimize,
                      'actual_cpu_affinity': sorted(__import__('os').sched_getaffinity(0)),
                      'copy_map_sha256': module.MAP_SHA, 'canonical_files': len(files), 'logical_files': len(targets),
                      'newly_written_logical_files': len(subset['copy_map']),
                      'newly_written_payload_bytes': sum(r['bytes'] for r in subset['copy_map']),
                      'hardlinked_payload_bytes': module.ARCHIVE['bytes'], 'archive_alias': module.ARCHIVE,
                      'case_restore_source_sha256': hashlib.sha256(code).hexdigest(),
                      'replay_source_sha256': hashlib.sha256(source.with_name('replay_public_restore.py').read_bytes()).hexdigest(),
                      'test_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      'actual_public_restore_performed': False,
                      'scope': 'Final case identity and exact archive partition only; original hardlink edge controls not repeated.'}, indent=2))


if __name__ == '__main__':
    main()
