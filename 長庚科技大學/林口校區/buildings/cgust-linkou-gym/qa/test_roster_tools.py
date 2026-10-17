"""Tiny synthetic restore and exact-pointer controls; no original evidence reads."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, copy, hashlib, json, os, tempfile, types

HERE = Path(__file__).absolute().parent
SOURCE = (HERE / 'restore_scientific_layout.py').read_bytes()
M = types.ModuleType('tested_public_restore')
M.__file__ = str(HERE / 'restore_scientific_layout.py')
exec(compile(SOURCE, M.__file__, 'exec'), M.__dict__)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    cases = []
    def case(name, action, accept=False):
        caught = None
        try:
            action()
            accepted = True
        except (ValueError, OSError, KeyError, IndexError, TypeError) as error:
            accepted = False
            caught = type(error).__name__
        passed = accepted is accept
        cases.append({'case': name, 'expected_accept': accept, 'accepted': accepted,
                      'passed': passed, 'caught_type': caught})
        if not passed:
            raise RuntimeError('Control failed: ' + name)
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        public = root / 'public'
        public.mkdir()
        (public / 'qa').mkdir()
        (public / 'qa/evidence.json').write_bytes(b'{"strict_passed":false}\n')
        (public / 'qa/empty.log').write_bytes(b'')
        def descriptor(name):
            data = (public / name).read_bytes()
            return {'canonical_public_path': name, 'bytes': len(data), 'sha256': M.digest(data)}
        files = [descriptor('qa/evidence.json'), descriptor('qa/empty.log')]
        mapping = {'schema': 'wfu-public-scientific-copy-map-v1',
            'status': 'byte_bound_ready_for_publication_gate', 'publication_go': False,
            'original_numerical_strict_passed': False, 'files': files,
            'copy_map': [dict(row, restore_path='author/' + row['canonical_public_path'], mode='byte_exact')
                         for row in files]}
        mapping['copy_map'].append(dict(mapping['copy_map'][0], restore_path='independent/evidence.json'))
        case('exact_restore_including_zero_byte_and_alias',
             lambda: M.restore(public, mapping, root / 'good'), True)
        case('existing_output_rejected', lambda: M.restore(public, mapping, root / 'good'))
        for number, bad in enumerate(('../outside', '/absolute', 'a//b', 'a/./b', 'a/../b',
                                       'C:/drive', 'a\\b', 'a\nb', 'a\x00b')):
            changed = copy.deepcopy(mapping)
            changed['copy_map'][0]['restore_path'] = bad
            case('unsafe_restore_path_' + str(number), lambda c=changed: M.validated_map(c))
        changed = copy.deepcopy(mapping)
        changed['copy_map'].append(copy.deepcopy(changed['copy_map'][0]))
        case('duplicate_restore_destination', lambda: M.validated_map(changed))
        changed = copy.deepcopy(mapping)
        changed['files'].append(copy.deepcopy(changed['files'][0]))
        case('duplicate_canonical_destination', lambda: M.validated_map(changed))
        changed = copy.deepcopy(mapping)
        changed['copy_map'][1]['restore_path'] = changed['copy_map'][0]['restore_path'] + '/nested'
        case('file_directory_collision', lambda: M.validated_map(changed))
        for key, value in [('status', 'awaiting_final_inputs'), ('publication_go', True),
                           ('original_numerical_strict_passed', True)]:
            changed = copy.deepcopy(mapping)
            changed[key] = value
            case('invalid_map_' + key, lambda c=changed: M.validated_map(c))
        changed = copy.deepcopy(mapping)
        changed['files'][0]['bytes'] = True
        case('boolean_descriptor_size', lambda: M.validated_map(changed))
        case('wrong_source_hash', lambda: M.read_exact(public, 'qa/evidence.json', dict(files[0], sha256='0'*64)))
        case('wrong_source_size', lambda: M.read_exact(public, 'qa/evidence.json', dict(files[0], bytes=1)))
        case('missing_source', lambda: M.read_exact(public, 'qa/absent', files[0]))
        (public / 'leaf-link').symlink_to('qa/evidence.json')
        (public / 'ancestor-link').symlink_to('qa', target_is_directory=True)
        (root / 'root-link').symlink_to(public, target_is_directory=True)
        case('source_leaf_symlink', lambda: M.read_exact(public, 'leaf-link', files[0]))
        case('source_ancestor_symlink', lambda: M.read_exact(public, 'ancestor-link/evidence.json', files[0]))
        case('source_root_symlink', lambda: M.read_exact(root / 'root-link', 'qa/evidence.json', files[0]))
        os.mkfifo(public / 'fifo')
        case('fifo_nonblocking_rejection', lambda: M.read_exact(public, 'fifo', files[1]))
        case('directory_source_leaf', lambda: M.read_exact(public, 'qa', files[1]))
        (root / 'out-link').symlink_to(root / 'absent', target_is_directory=True)
        case('output_leaf_symlink', lambda: M.restore(public, mapping, root / 'out-link'))
        (root / 'parent-link').symlink_to(root, target_is_directory=True)
        case('output_ancestor_symlink', lambda: M.restore(public, mapping, root / 'parent-link/absent'))
        loose = root / 'loose'; loose.mkdir(); loose.chmod(0o777)
        case('writable_output_parent', lambda: M.restore(public, mapping, loose / 'out'))
        source = M.dump({'path': 'original/location', 'strict_passed': False, 'exit': 1,
                         'values': [1, True, 0.8], 'unexpected_science': {'x': 7}})
        changes = [{'pointer': '/path', 'old': 'original/location', 'new': 'logical/location'}]
        def positive_projection():
            value = M.parse(M.project_json(source, changes))
            M.require(value['strict_passed'] is False and value['exit'] == 1, 'Strict or exit altered')
            M.require(value['unexpected_science'] == {'x': 7}, 'Unknown science altered')
        case('exact_path_projection_preserves_all_science', positive_projection, True)
        case('projection_wrong_old_value', lambda: M.project_json(source, [dict(changes[0], old='wrong')]))
        case('projection_missing_pointer', lambda: M.project_json(source, [dict(changes[0], pointer='/missing')]))
        case('projection_duplicate_pointer', lambda: M.project_json(source, changes * 2))
        case('projection_bool_science_change', lambda: M.project_json(source, [{'pointer':'/strict_passed','old':False,'new':True}]))
        case('projection_unknown_instruction', lambda: M.project_json(source, [dict(changes[0], recursive=True)]))
        case('duplicate_json_key', lambda: M.parse(b'{"a":1,"a":2}'))
        case('nonfinite_json_number', lambda: M.parse(b'{"a":NaN}'))
        case('overflow_json_number', lambda: M.parse(b'{"a":1e999}'))
        case('typed_bool_int_difference', lambda: M.require(M.typed_equal({'x':True},{'x':1}), 'type'))
    result = {'passed': all(c['passed'] for c in cases), 'optimization_level': sys.flags.optimize,
              'case_count': len(cases), 'cases': cases, 'restore_source_sha256': M.digest(SOURCE),
              'primitives_source_sha256': M.PRIMITIVES_SHA,
              'test_source_sha256': M.digest(Path(__file__).read_bytes()),
              'original_evidence_read': False, 'science_or_publication_go': False}
    with a.out.open('xb') as stream:
        stream.write(M.dump(result))
    print(json.dumps({'passed': result['passed'], 'case_count': len(cases)}))


if __name__ == '__main__':
    main()
