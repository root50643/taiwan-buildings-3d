"""Seal an explicit roster and exact public path projections; copy no science.

Run only in the owner's shared slot after the draft's required inputs are final.
The sole output is a new small recipe/projection directory for the publisher.
It is not a privacy, publication or strict-numerical acceptance decision.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, copy, hashlib, types

HERE = Path(__file__).absolute().parent
# This private preparation entry is source-frozen before execution. Its public
# restore dependency authenticates the shared primitive source on load.
raw = (HERE / 'restore_scientific_layout.py').read_bytes()
M = types.ModuleType('roster_restore')
M.__file__ = str(HERE / 'restore_scientific_layout.py')
exec(compile(raw, M.__file__, 'exec'), M.__dict__)


def observed(root, path, expected=None):
    M.safe_relative(path)
    data = M._m._read_regular_snapshot(root, path, None, M.MAX_FILE_BYTES)
    row = {'bytes': len(data), 'sha256': M.digest(data)}
    if expected is not None:
        M.require(M.typed_equal(row, expected), 'Frozen source descriptor changed: ' + path)
    return data, row


def project_json_keys(data, changes):
    """Rename explicitly listed path-label keys, preserving every typed value."""
    original = M.parse(data)
    result = copy.deepcopy(original)
    seen = set()
    for change in changes:
        M.require(set(change) == {'parent_pointer', 'old', 'new'}, 'Unknown key projection instruction')
        pointer, old, new = (change[k] for k in ('parent_pointer', 'old', 'new'))
        M.require(type(old) is str and type(new) is str and old != new,
                  'Key projection requires distinct string labels')
        M.require((pointer, old) not in seen, 'Duplicate key projection')
        seen.add((pointer, old))
        parent, key = M.pointer_parent(result, pointer)
        target = parent[key]
        M.require(type(target) is dict and old in target and new not in target,
                  'Key projection source drift or destination collision')
        target[new] = target.pop(old)
    reverse = copy.deepcopy(result)
    for change in reversed(changes):
        parent, key = M.pointer_parent(reverse, change['parent_pointer'])
        target = parent[key]
        M.require(type(target) is dict and change['new'] in target and change['old'] not in target,
                  'Key projection reverse collision')
        target[change['old']] = target.pop(change['new'])
    M.require(M.typed_equal(original, reverse), 'Unexpected key-projection value change')
    return M.dump(result)


def public_omission_labels(omissions):
    """Only explicit flat omission labels may use a public logical alias."""
    result = []
    for original in omissions:
        row = copy.deepcopy(original)
        if 'public_relative_path_alias' in row:
            alias = row.pop('public_relative_path_alias')
            old = row['original_relative_path']
            M.require(type(old) is str and type(alias) is str and old != alias,
                      'Omission alias requires distinct string labels')
            M.safe_relative(alias)
            M.require('original_relative_path_label_sha256' not in row and
                      'original_relative_path_is_public_logical_alias' not in row,
                      'Omission alias metadata collision')
            row['original_relative_path'] = alias
            row['original_relative_path_label_sha256'] = M.digest(old.encode())
            row['original_relative_path_is_public_logical_alias'] = True
        result.append(row)
    return result


def seal(plan, roots, out):
    M.require(plan['schema'] == 'wfu-public-qa-explicit-roster-v1', 'Wrong explicit roster')
    M.require(plan['original_numerical_strict_passed'] is False, 'Strict result upgraded')
    M.require(not plan.get('awaiting_assignments'), 'Final roster assignments are still pending')
    gate_bindings = []
    for gate in plan['required_gates']:
        data, desc = observed(roots[gate['source_root']], gate['source_relative_path'], gate.get('expected'))
        value = M.parse(data)
        for check in gate['checks']:
            parent, key = M.pointer_parent(value, check['pointer'])
            M.require(M.typed_equal(parent[key], check['equals']), 'Unfinished/failed required gate')
        gate_bindings.append({'logical_source': gate['source_root'] + '/' + gate['source_relative_path'], **desc})
    generated, recipe, canonical, aliases, projections = {}, [], {}, [], []
    identities, sources = {}, {}
    destinations = set()
    for entry in plan['items']:
        root_name, source_name = entry['source_root'], entry['source_relative_path']
        destination = M.safe_relative(entry['public_path'])
        restore = M.safe_relative(entry['restore_path'])
        M.require(restore not in destinations, 'Duplicate logical source destination')
        destinations.add(restore)
        M.require(entry.get('projection_status') != 'awaiting', 'Projection assignment still pending')
        original, original_desc = observed(roots[root_name], source_name, entry.get('expected'))
        sources[(root_name, source_name)] = original_desc
        data = original
        changes = entry.get('changes', [])
        key_changes = entry.get('key_changes', [])
        if changes or key_changes:
            data = M.project_json(original, changes)
            if key_changes:
                data = project_json_keys(data, key_changes)
            projection_path = 'projections/' + str(len(projections)).zfill(4) + '.json'
            generated[projection_path] = data
            projections.append({'public_path': destination, 'logical_original': restore,
                'original_bytes': original_desc['bytes'], 'original_sha256': original_desc['sha256'],
                'public_bytes': len(data), 'public_sha256': M.digest(data),
                'changes': [{'json_pointer': c['pointer'], 'original_string_sha256': M.digest(c['old'].encode()),
                             'public_value': c['new']} for c in changes],
                'key_changes': [{'parent_json_pointer': c['parent_pointer'],
                    'original_key_sha256': M.digest(c['old'].encode()), 'public_key': c['new']}
                    for c in key_changes],
                'all_other_typed_JSON_values_identical': True, 'original_bytes_retained_privately': True})
            copy_source = {'source_root': 'generated', 'source_relative_path': projection_path}
        else:
            copy_source = {'source_root': root_name, 'source_relative_path': source_name}
        desc = {'bytes': len(data), 'sha256': M.digest(data)}
        identity = (desc['bytes'], desc['sha256'])
        preferred = identities.get(identity)
        if entry.get('force_canonical', False):
            preferred = None
        if preferred is None:
            M.require(destination not in canonical, 'Canonical public destination conflict')
            canonical[destination] = {'canonical_public_path': destination, **desc}
            identities.setdefault(identity, destination)
            preferred = destination
            recipe.append({'public_path': destination, **copy_source, **desc,
                           'publisher_owned_existing': entry.get('publisher_owned_existing', False),
                           'new_controls_member': entry.get('new_controls_member', False)})
        aliases.append({'restore_path': restore, 'canonical_public_path': preferred, **desc,
            'mode': 'metadata_only_json_projection' if changes or key_changes else 'byte_exact',
            'original_bytes': original_desc['bytes'], 'original_sha256': original_desc['sha256'],
            'new_controls_member': entry.get('new_controls_member', False)})
    # Reauthenticate all selected source bytes before emitting the small recipe.
    for (root_name, path), desc in sources.items():
        M.read_exact(roots[root_name], path, desc)
    mapping = {'schema': 'wfu-public-scientific-copy-map-v1',
        'status': 'byte_bound_ready_for_publication_gate', 'publication_go': False,
        'original_numerical_strict_passed': False, 'stl_sha256': plan['stl_sha256'],
        'scope': 'Final four-source science, selected reproducibility tools and controls only. Original historical inventory is retained, but private historical payloads are not reconstructed.',
        'files': list(canonical.values()), 'copy_map': aliases,
        'required_gate_bindings': gate_bindings, 'projection_bindings': projections,
        'omissions': public_omission_labels(plan['omissions']), 'full_author_inventory_publicly_reconstructible': False}
    M.validated_map(mapping)
    generated['PUBLIC-COPY-MAP.json'] = M.dump(mapping)
    generated['PUBLISHER-COPY-RECIPE.private.json'] = M.dump({'schema':'wfu-publisher-copy-recipe-v1',
        'status':'byte_bound_ready_for_publication_gate', 'files':recipe,
        'public_map_path':'qa/PUBLIC-COPY-MAP.json', 'publication_go':False})
    generated['PROJECTION-BINDINGS.json'] = M.dump({'schema':'wfu-exact-public-json-projections-v1',
        'files':projections,'originals_retained_privately':True})
    generated['NEW-CONTROLS-SELECTION.json'] = M.dump({'schema':'wfu-new-control-logical-selection-v1',
        'files':[r for r in aliases if r['new_controls_member']],
        'scope':'Only new control sources, per-case results and reproduction/omission proofs. No model science payload is added to the controls archive.'})
    control_aliases = [r for r in aliases if r['new_controls_member']]
    control_canonical = {r['canonical_public_path'] for r in control_aliases}
    stage_map = {k: mapping[k] for k in ('schema', 'status', 'publication_go',
        'original_numerical_strict_passed', 'stl_sha256')}
    stage_map.update(files=[r for r in mapping['files'] if r['canonical_public_path'] in control_canonical],
                     copy_map=control_aliases,
                     scope='Exact small new-controls staging selection only. No model science archive member.')
    M.validated_map(stage_map)
    generated['NEW-CONTROLS-STAGING-MAP.json'] = M.dump(stage_map)
    M._m.write_new_tree(out, [(name, lambda data=data: data) for name, data in sorted(generated.items())])
    return {'canonical_files':len(canonical),'logical_files':len(aliases),
            'projections':len(projections),'science_payload_copies_created':0,
            'publication_go':False,'status':'byte_bound_ready_for_publication_gate'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan', type=Path, required=True)
    ap.add_argument('--root', action='append', required=True, help='Logical name=existing source root')
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    roots = {}
    for assignment in a.root:
        name, value = assignment.split('=', 1)
        M.require(name not in roots, 'Duplicate source root assignment')
        roots[name] = Path(value)
    print(M.dump(seal(M.parse(a.plan.read_bytes()), roots, a.out)).decode(), end='')


if __name__ == '__main__':
    main()
