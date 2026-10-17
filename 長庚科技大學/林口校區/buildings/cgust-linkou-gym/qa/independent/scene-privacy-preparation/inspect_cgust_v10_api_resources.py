"""One Blender inspect-only resource inventory plus tiny stdlib validator controls.

The Blend is opened with script auto-execution disabled. No render, scene save,
resource load, fixture Blend, or change to the source file is performed. Reports
contain logical identifiers, hashes and exact hex values rather than local paths.
This supplements the existing geometry/state inspector; it is not arbitrary RNA
serialization and does not replace the separately completed whole-byte scan.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys


SCENE_SHA = '24405788a4c5bf2e88a2402089f5d7fc9bc6b360afa97cc316760bdf3e668a1b'
SCENE_BYTES = 883140
LOGICAL_INPUT = 'models/v10/scene.blend'
OUTPUT_DEFAULT_HEX = '2f746d702f'
RESOURCE_COLLECTIONS = ('libraries', 'images', 'fonts', 'sounds', 'movieclips',
    'cache_files', 'volumes', 'texts', 'node_groups', 'particles', 'textures')
UNSUPPORTED_NODE_IDS = {'ShaderNodeScript', 'ShaderNodeTexImage', 'ShaderNodeTexEnvironment',
    'CompositorNodeImage', 'CompositorNodeMovieClip', 'CompositorNodeOutputFile'}


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate(snapshot):
    counts = snapshot.get('resource_counts')
    require(type(counts) is dict and set(counts) == set(RESOURCE_COLLECTIONS)
            and all(type(value) is int and value == 0 for value in counts.values()),
            'Unused or used resource datablock exists, or inventory shape differs')
    require(type(snapshot.get('scene_count')) is int and snapshot['scene_count'] == 1,
            'Expected one saved scene')
    require(snapshot.get('render_output_utf8_hex') == OUTPUT_DEFAULT_HEX,
            'Exact render-output default differs')
    options = snapshot.get('bpath_options')
    require(type(options) is dict and options == {'absolute': False, 'packed': False, 'local': False}
            and all(type(value) is bool for value in options.values()),
            'External-path API scope differs')
    require(type(snapshot.get('external_path_summaries')) is list
            and not snapshot['external_path_summaries'], 'External file paths remain')
    for key in ('nonempty_node_path_fields', 'unsupported_node_types'):
        require(type(snapshot.get(key)) is list and not snapshot[key],
                'Unused or used shader/compositor resource carrier remains')
    for key in ('modifiers', 'constraints', 'particle_systems', 'rigidbody_worlds',
                'sequencer_strips', 'scene_node_trees'):
        require(type(snapshot.get(key)) is int and snapshot[key] == 0,
                'Nested scene/cache/resource carrier remains')
    require(snapshot.get('autoexec_disabled_before_open') is True
            and snapshot.get('autoexec_disabled_after_open') is True,
            'Script execution was not disabled')
    return True


def summarize_path(value):
    require(type(value) is str, 'Path API did not return a string')
    raw = value.encode('utf8')
    return {'utf8_bytes': len(raw), 'sha256': digest(raw)}


def capture(bpy):
    counts = {name: len(getattr(bpy.data, name)) for name in RESOURCE_COLLECTIONS}
    scenes = list(bpy.data.scenes)
    require(len(scenes) == 1, 'Expected one saved scene before inventory')
    scene = scenes[0]
    paths = bpy.utils.blend_paths(absolute=False, packed=False, local=False)
    require(type(paths) is list, 'External-path API return type differs')
    path_fields, unsupported = [], []
    node_count = 0
    empty_path_fields = 0
    for collection_name in ('materials', 'worlds', 'lights', 'scenes', 'node_groups'):
        for block_index, block in enumerate(getattr(bpy.data, collection_name)):
            tree = block if collection_name == 'node_groups' else getattr(block, 'node_tree', None)
            if tree is None:
                continue
            for node_index, node in enumerate(tree.nodes):
                node_count += 1
                logical = '%s[%d].nodes[%d]' % (collection_name, block_index, node_index)
                if node.bl_idname in UNSUPPORTED_NODE_IDS:
                    unsupported.append({'logical': logical, 'rna_type': node.bl_idname})
                for prop in node.bl_rna.properties:
                    if prop.type == 'STRING' and (prop.subtype in ('FILE_PATH', 'DIR_PATH')
                            or prop.identifier in ('filepath', 'directory', 'filename')):
                        value = getattr(node, prop.identifier)
                        require(type(value) is str, 'Node path property type differs')
                        if value:
                            path_fields.append({'logical': logical + '.' + prop.identifier,
                                                **summarize_path(value)})
                        else:
                            empty_path_fields += 1
    return {'resource_counts': counts, 'scene_count': len(scenes),
        'render_output_utf8_hex': scene.render.filepath.encode('utf8').hex(),
        'render_output_value_sha256': digest(scene.render.filepath.encode('utf8')),
        'bpath_options': {'absolute': False, 'packed': False, 'local': False},
        'external_path_summaries': [summarize_path(path) for path in paths],
        'bpath_includes_packed_and_linked_resources': True,
        'nonempty_node_path_fields': path_fields, 'unsupported_node_types': unsupported,
        'all_data_node_count_inspected': node_count, 'empty_node_path_fields': empty_path_fields,
        'modifiers': sum(len(obj.modifiers) for obj in bpy.data.objects),
        'constraints': sum(len(obj.constraints) for obj in bpy.data.objects),
        'particle_systems': sum(len(obj.particle_systems) for obj in bpy.data.objects),
        'rigidbody_worlds': sum(scene.rigidbody_world is not None for scene in scenes),
        'sequencer_strips': sum(len(scene.sequence_editor.sequences_all)
            for scene in scenes if scene.sequence_editor is not None),
        'scene_node_trees': sum(scene.node_tree is not None for scene in scenes),
        'autoexec_disabled_after_open': not bpy.context.preferences.filepaths.use_scripts_auto_execute}


def self_tests():
    positive = {'resource_counts': {name: 0 for name in RESOURCE_COLLECTIONS},
        'scene_count': 1, 'render_output_utf8_hex': OUTPUT_DEFAULT_HEX,
        'bpath_options': {'absolute': False, 'packed': False, 'local': False},
        'external_path_summaries': [], 'nonempty_node_path_fields': [],
        'unsupported_node_types': [], 'modifiers': 0, 'constraints': 0,
        'particle_systems': 0, 'rigidbody_worlds': 0, 'sequencer_strips': 0,
        'scene_node_trees': 0, 'autoexec_disabled_before_open': True,
        'autoexec_disabled_after_open': True}
    cases = []

    def case(name, mutate=None):
        sample = json.loads(json.dumps(positive))
        if mutate is not None:
            mutate(sample)
        error = None
        try:
            validate(sample)
        except Exception as exc:
            error = type(exc).__name__ + ': ' + str(exc)
        encoded = json.dumps(sample, sort_keys=True, separators=(',', ':')).encode()
        cases.append({'logical_case': name, 'expected_accept': mutate is None,
            'accepted': error is None, 'passed': (error is None) == (mutate is None),
            'actual_error': error, 'synthetic_fixture_bytes': len(encoded),
            'synthetic_fixture_sha256': digest(encoded)})

    case('empty_resource_inventory_positive')
    for name in RESOURCE_COLLECTIONS:
        case('unused_' + name + '_rejected', lambda value, name=name: value['resource_counts'].__setitem__(name, 1))
    case('missing_inventory_category_rejected', lambda value: value['resource_counts'].pop('fonts'))
    case('bool_count_rejected', lambda value: value['resource_counts'].__setitem__('images', False))
    case('external_path_rejected', lambda value: value['external_path_summaries'].append({'sha256': '0' * 64}))
    case('skipped_packed_paths_rejected', lambda value: value['bpath_options'].__setitem__('packed', True))
    case('skipped_linked_paths_rejected', lambda value: value['bpath_options'].__setitem__('local', True))
    case('nonbool_path_option_rejected', lambda value: value['bpath_options'].__setitem__('packed', 0))
    case('wrong_output_default_rejected', lambda value: value.__setitem__('render_output_utf8_hex', '78'))
    case('extra_scene_rejected', lambda value: value.__setitem__('scene_count', 2))
    for key in ('nonempty_node_path_fields', 'unsupported_node_types'):
        case(key + '_rejected', lambda value, key=key: value[key].append({'logical': 'synthetic'}))
    for key in ('modifiers', 'constraints', 'particle_systems', 'rigidbody_worlds', 'sequencer_strips', 'scene_node_trees'):
        case(key + '_rejected', lambda value, key=key: value.__setitem__(key, 1))
    for key in ('autoexec_disabled_before_open', 'autoexec_disabled_after_open'):
        case(key + '_false_rejected', lambda value, key=key: value.__setitem__(key, False))
    return {'passed': all(case['passed'] for case in cases), 'case_count': len(cases),
            'cases': cases, 'synthetic_only': True, 'blender_executed': False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--blend', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    args = ap.parse_args(argv)
    require(os.sched_getaffinity(0) == {0}, 'CPU-0-only execution required')
    require(args.out.parent.is_dir() and not args.out.exists() and not args.out.is_symlink(),
            'Fresh output required')
    own = Path(__file__).read_bytes()
    if args.self_test:
        result = self_tests()
    else:
        require(args.blend is not None and not args.blend.is_symlink(), 'Original scene required')
        raw = args.blend.read_bytes()
        require(len(raw) == SCENE_BYTES and digest(raw) == SCENE_SHA, 'Exact scene identity differs')
        import bpy
        require(tuple(bpy.app.version) == (4, 3, 2), 'Reviewed Blender version differs')
        disabled = not bpy.context.preferences.filepaths.use_scripts_auto_execute
        require(disabled, 'Launch Blender with script auto-execution disabled')
        bpy.ops.wm.open_mainfile(filepath=str(args.blend.resolve()), load_ui=False, use_scripts=False)
        snapshot = capture(bpy)
        snapshot['autoexec_disabled_before_open'] = disabled
        accepted, error = False, None
        try:
            accepted = validate(snapshot)
        except ValueError as exc:
            error = str(exc)
        require(args.blend.read_bytes() == raw, 'Original scene changed during inspection')
        result = {'passed': accepted, 'validation_error': error, 'snapshot': snapshot,
            'original_scene_sha256': SCENE_SHA, 'original_scene_bytes': SCENE_BYTES,
            'original_scene_unchanged': True, 'blender_version': bpy.app.version_string,
            'blender_executed': True, 'render_called': False, 'scene_saved': False}
    require(Path(__file__).read_bytes() == own, 'Inspection source changed')
    result.update(logical_input=LOGICAL_INPUT, source_sha256=digest(own), source_bytes=len(own),
        optimization_level=sys.flags.optimize, model_go=False, publication_go=False,
        arbitrary_rna_serialization_claimed=False,
        scope='Used and unused resource datablocks, inclusive external-path API, all data shader-node path fields, and nested resource/cache carriers for the exact candidate; supplements byte privacy and original scene/state evidence.')
    with args.out.open('x', encoding='utf8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'passed': result['passed'], 'self_test': args.self_test}))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
