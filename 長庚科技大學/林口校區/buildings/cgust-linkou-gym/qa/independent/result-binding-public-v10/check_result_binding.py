"""Read-only CGUST v10 result binding; canonical author v9 evidence stays in place.
Narrow adaptation of retained WFU v13 check_result_binding.py. No geometry/render run.
A successful binding is neither a strict numerical pass nor a publication approval.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json
import lzma
import math
import sys

STL = '66f0516f35df2df734b6d8a4d37a8f93b73e5685fd47b0b7d74ff15c88ccf978'
AUTHOR_PREFIX = None  # Configured only by the required validated CLI argument.
PUBLIC_PREVIEWS = 'qa/render-check/v10-author/sanitized-previews'
PINS = {
    'qa/source-review/FINAL-SOURCE-APPEARANCE-GO-v10.private.json': '816f169ce11248e3e92b0fcad7efd28f36f1c5a289e344648eaebe3fe89bb8ad',
    'qa/source-review/SOURCE-APPEARANCE-CERTIFICATE-v10.public.json': 'b7e90cde6a2616312cbb73e0cc4084401a9d4ea6a7ad914d58938b82ca832b0f',
    'qa/source-review/SOURCE-BINDING-v10.private.json': '4e08fa40f889f8a8f6d82a0dbef9324f9219134ea311f94744f1bd18c8fbabcd',
    'qa/freeze-v10/SCIENCE-INVENTORY.json': '17216ac4437866e14986688d6760fc3606d2c8a02be833731d4241b637e9721a',
}
SELECTION = '076c6330b40b7e9dbddae9b3bf74d6361a89a39c5cba1b2defc28f16284c5e5b'
VIEWS = {'front', 'rear', 'west', 'east', 'south', 'north', 'top', 'courtyard-gallery', 'courtyard-arcade'}
FILES = [
    'standard/qa-summary.json', 'standard/raw/raw-mesh-check.json',
    'standard/sections/section-check.json', 'standard/sections/section-details.json.gz',
    'standard/sections/section-failures.json.gz', 'standard/dense/dense-check.json',
    'standard/dense/dense-original.csv.xz', 'standard/dense/dense-flagged-samples.json.gz',
    'standard/dense/dense-short-samples.json.gz', 'dense-evidence.json',
    'intersections.json', 'intersections.json.contacts.jsonl.gz',
    'exact-recorded-rays/exact-recorded-ray-summary.json',
    'exact-recorded-rays/exact-recorded-ray-details.jsonl.gz',
]
MODES = ('normal', 'optimized')
REPLAY_CHECKS = {
    'exact_world_directed_triangle_multiset_matches', 'original_triangle_count_matches',
    'no_modifiers', 'no_hidden_replacement_mesh', 'no_external_photo_images',
    'scene_stl_hash_matches', 'mesh_stl_hash_matches', 'millimetre_units',
    'one_cpu_render_thread', 'cycles_cpu_renderer', 'no_compositor_or_sequencer',
    'no_view_layer_material_overrides', 'mesh_normally_visible', 'no_shader_node_groups',
    'no_shape_keys', 'no_object_constraints', 'no_animation_or_drivers',
    'fixed_nonanimated_render_seed', 'denoising_disabled', 'exactly_64_samples',
    'no_image_textures', 'no_environment_image_textures', 'no_light_shader_nodes',
    'no_unexpected_renderable_objects', 'one_camera_two_suns', 'frozen_image_resolution',
    'manifest_blend_binding_matches', 'manifest_render_policy_matches',
    'manifest_per_view_projection_lens_policy_matches', 'saved_initial_camera_matches_front',
    'all_nine_decoded_rgba_bytes_identical', 'all_nine_nonremoved_metadata_identical',
    'all_nine_metadata_only_cleanups_proved', 'inspector_source_unchanged',
    'png_comparator_source_unchanged', 'original_blend_unchanged',
    'original_stl_unchanged', 'original_manifest_unchanged',
}


def require(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def record(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), 'Missing/nonregular evidence: ' + str(path))
    return {'bytes': path.stat().st_size, 'sha256': sha(path)}


def pairs(rows):
    result = {}
    for key, value in rows:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def read(path):
    def invalid(value):
        raise RuntimeError('Nonfinite JSON constant: ' + value)
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs, parse_constant=invalid)


def exact(a, b):
    # Type-sensitive: false is not zero, and integer is not floating-point.
    return json.dumps(a, sort_keys=True, allow_nan=False) == json.dumps(b, sort_keys=True, allow_nan=False)


def member(root, relative):
    p = Path(relative)
    require(not p.is_absolute() and '..' not in p.parts and str(p) == relative, 'Invalid member path')
    result = root / p
    require(result.resolve().is_relative_to(root.resolve()), 'Member escapes root')
    return result


def logical_path(path, roots):
    """Only an exact declared root may be converted to a stable logical key."""
    require(set(roots) == {'author', 'run', 'checker'}, 'Metadata roots differ')
    path = Path(path).resolve()
    matches = [(name, path.relative_to(Path(root).resolve())) for name, root in roots.items()
               if path.is_relative_to(Path(root).resolve())]
    require(len(matches) == 1, 'Metadata path outside or ambiguous declared roots')
    name, relative = matches[0]
    require(relative.parts and '..' not in relative.parts, 'Metadata path is a root, not a member')
    return name + '/' + relative.as_posix()


def physical_path(logical, roots):
    require(type(logical) is str and '/' in logical and '\\' not in logical, 'Invalid logical metadata path')
    name, relative = logical.split('/', 1)
    require(name in roots and name in {'author', 'run', 'checker'}, 'Unknown logical metadata root')
    path = member(Path(roots[name]), relative)
    require(logical_path(path, roots) == logical, 'Noncanonical logical metadata path')
    return path


def validate_output_metadata(value, roots, key=''):
    """Fail closed on private physical paths; never alter a scientific value."""
    if isinstance(value, dict):
        for k, v in value.items():
            validate_output_metadata(k, roots)
            validate_output_metadata(v, roots, k)
    elif isinstance(value, list):
        for item in value:
            validate_output_metadata(item, roots, key)
    elif isinstance(value, str):
        require(not any(str(Path(root).resolve()) in value for root in roots.values()), 'Private physical root in report metadata')
        require(not any(prefix in value for prefix in (('/' + 'workspace/'), ('/' + 'home/'), ('/' + 'tmp/'))), 'Private absolute path in report metadata')
        if key in {'path', 'original_path', 'restore_from_canonical_path'}:
            physical_path(value, roots)


def validate_source_path_prefix(value):
    """Validate a caller-supplied relative directory prefix without disclosing it."""
    require(type(value) is str and bool(value), 'Source path prefix is required')
    require(value.endswith('/'), 'Source path prefix requires trailing slash')
    require('\\' not in value and ':' not in value and not any(c.isspace() or ord(c) < 32 for c in value),
            'Source path prefix contains unsafe characters')
    path = Path(value[:-1])
    require(not path.is_absolute() and bool(path.parts) and '..' not in path.parts and '.' not in path.parts,
            'Source path prefix must be a safe relative directory')
    require(path.as_posix() + '/' == value, 'Source path prefix must be canonical')
    return value


def source_relative(value):
    require(AUTHOR_PREFIX is not None, 'Source path prefix is not configured')
    require(type(value) is str and value.startswith(AUTHOR_PREFIX), 'Wrong source-binding author prefix')
    relative = value[len(AUTHOR_PREFIX):]
    p = Path(relative)
    require(relative and not p.is_absolute() and '..' not in p.parts and str(p) == relative,
            'Invalid source-binding member path')
    return relative


def index_files(rows):
    result = {}
    for row in rows:
        rel = row['path']
        require(rel not in result, 'Duplicate inventory member: ' + rel)
        result[rel] = {'bytes': row['bytes'], 'sha256': row['sha256']}
    return result


def check_record(path, expected):
    actual = record(path)
    require(exact(actual, expected), 'Bytes/hash mismatch: ' + str(path))
    return actual


def science_path(author, run, owner, mode, relative):
    if owner == 'independent':
        return run / 'geometry' / mode / relative
    if relative.startswith('exact-recorded-rays/'):
        return author / ('qa/v9-exact-' + mode) / Path(relative).name
    return author / 'qa/v9-full' / mode / relative


def comparable(document, relative, mode, intersections_sha):
    """Only these explicit non-scientific fields may differ; originals stay intact."""
    d = copy.deepcopy(document)
    omitted = {}
    level = MODES.index(mode)
    if relative == 'standard/qa-summary.json':
        require(d['optimized_python'] is (mode == 'optimized'), 'Incorrect QA interpreter mode')
        omitted['optimized_python'] = d.pop('optimized_python')
    if relative in ('intersections.json', 'exact-recorded-rays/exact-recorded-ray-summary.json'):
        t = d.pop('elapsed_seconds')
        require(type(t) in (int, float) and math.isfinite(t) and t >= 0, 'Invalid execution elapsed_seconds')
        omitted['elapsed_seconds'] = t
        if relative == 'intersections.json':
            require(type(d['tools']['optimization_level']) is int and d['tools']['optimization_level'] == level, 'Incorrect intersection interpreter mode')
            omitted['tools.optimization_level'] = d['tools'].pop('optimization_level')
        else:
            require(type(d['optimization_level']) is int and d['optimization_level'] == level, 'Incorrect exact-ray interpreter mode')
            omitted['optimization_level'] = d.pop('optimization_level')
            h = d['input_and_tool_sha256'].pop('intersections_report')
            require(h == intersections_sha, 'Exact summary not bound to its own compared intersection report')
            omitted['input_and_tool_sha256.intersections_report'] = h
    return d, omitted


def compare_group(entries, relative, roots):
    """Four entries, all bytes retained; compare all to author normal."""
    rows, science = [], []
    for label, mode, path, intersection_hash in entries:
        row = {'source': label, 'mode': mode, 'path': logical_path(path, roots), **record(path)}
        if relative in ('standard/qa-summary.json', 'intersections.json', 'exact-recorded-rays/exact-recorded-ray-summary.json'):
            value, omitted = comparable(read(path), relative, mode, intersection_hash)
            science.append(value)
            row['non_scientific_fields_retained_in_original'] = omitted
        else:
            science.append(row['sha256'])
        rows.append(row)
    require(len(rows) == 4, 'Expected all four original producer sources')
    require(all(exact(science[0], x) for x in science[1:]), 'Scientific content differs: ' + relative)
    return {'logical_file': relative, 'all_four_scientifically_identical': True,
            'all_four_bitwise_identical': len({r['sha256'] for r in rows}) == 1, 'sources': rows}


def full_csv(path, dense):
    compressed = record(path)
    require(exact(compressed, {'bytes': dense['csv_compressed_bytes'], 'sha256': dense['csv_compressed_sha256']}), 'CSV compressed hash/bytes differ')
    h, count, lines, last = hashlib.sha256(), 0, 0, b''
    with lzma.open(path, 'rb') as stream:
        while chunk := stream.read(1024 * 1024):
            h.update(chunk)
            count += len(chunk)
            lines += chunk.count(b'\n')
            last = chunk[-1:]
    require(count == dense['uncompressed_csv_bytes'] and h.hexdigest() == dense['uncompressed_csv_sha256'], 'CSV decoded hash/bytes differ')
    require(last == b'\n' and lines == dense['samples'] + 1, 'CSV whole-file row count differs')
    return {'compressed': compressed, 'decoded': {'bytes': count, 'sha256': h.hexdigest()},
            'data_rows': lines - 1, 'all_decoded_bytes_read': True}


def verify_strict_original(author, run):
    full = read(author / 'qa/v9-full/full-qa-summary.json')
    capture = read(author / 'qa/v9-capture-full/execution.json')
    require(full['completed'] is True and full['passed'] is False and full['strict_passed'] is False, 'Original author strict failure was changed')
    require(capture['completed'] is True and capture['returncode'] == 1 and capture['report_sha256'] == sha(author / 'qa/v9-full/full-qa-summary.json'), 'Original producer exit1/report binding lost')
    summary = read(run / 'independent-execution-summary.json')
    require(summary['completed'] is True and summary['strict_passed'] is False and summary['all_frozen_inputs_and_tools_unchanged'] is True, 'Independent execution incomplete or strict failure changed')
    require(summary['stl_sha256'] == STL and summary['version'] == 'v10', 'Independent execution identity differs')
    require(summary['runner_sha256'] == sha(run / 'independent-runner.py'), 'Independent runner snapshot changed')
    require(summary['input_and_tool_rechecks'] and all(v is True for v in summary['input_and_tool_rechecks'].values()), 'Independent input/tool recheck failed')
    executions = read(run / 'executions.json')
    require(exact(executions, summary['executions']), 'Independent execution ledgers differ')
    stages = {r['name']: r for r in executions}
    required = {m + '-' + stage: (1 if stage == 'standard' else 0) for m in MODES for stage in ['standard', 'exact-intersections', 'intersection-controls', 'dense-evidence', 'exact-recorded-rays']}
    required.update({name: 0 for name in ['source-stl-reproduction', 'source-scene-state-reproduction', 'saved-blend-nine-rerenders', 'public-png-metadata-cleanup']})
    require(len(stages) == len(executions) and set(stages) == set(required), 'Missing/duplicate/unexpected independent stages')
    for name, code in required.items():
        r = stages[name]
        require(r['finished'] is True and r['returncode'] == code, 'Wrong independent stage exit: ' + name)
        require(sha(member(run, r['log_file'])) == r['log_sha256'], 'Independent stage log changed: ' + name)
    for mode in MODES:
        require(full['modes'][mode]['strict_passed'] is False and full['modes'][mode]['child_exit_codes']['standard'] == 1, 'Author mode exit1 changed')
        for owner in ('author', 'independent'):
            for rel in ('standard/qa-summary.json', 'standard/dense/dense-check.json'):
                d = read(science_path(author, run, owner, mode, rel))
                require(d['passed'] is False and d['strict_passed'] is False and d['stl_sha256'] == STL, 'Numerical strict failure changed')
            d = read(science_path(author, run, owner, mode, 'exact-recorded-rays/exact-recorded-ray-summary.json'))
            require(d['original_numerical_strict_passed'] is False, 'Exact diagnosis waived original strict failure')
        capture = read(author / ('qa/v9-capture-exact-' + mode) / 'execution.json')
        require(capture['completed'] is True and capture['returncode'] == 0 and capture['report_sha256'] == sha(science_path(author, run, 'author', mode, FILES[-2])), 'Original exact capture binding differs')
    return {'author_full_passed': full['passed'], 'author_full_strict_passed': full['strict_passed'],
            'author_full_checks_preserved_verbatim': full['checks'], 'author_full_producer_returncode': 1,
            'author_mode_records_preserved_verbatim': full['modes'], 'independent_strict_passed': summary['strict_passed'],
            'independent_standard_returncodes': {m: stages[m + '-standard']['returncode'] for m in MODES}}


def source_schema(certificate, binding, approval):
    """CGUST's actual three-document schema, with no WFU-schema fallback."""
    require(certificate['document'] == 'Source and appearance review certificate' and certificate['revision'] == 'v10', 'Wrong CGUST certificate schema/revision')
    require(certificate['decision'] == 'GO_WITH_REPRESENTATIVE_MODEL_LIMITS' and certificate['all_nine_original_renders_actually_reviewed'] is True, 'Missing appearance-only approval')
    require(binding['revision'] == 'v10' and binding['private_only'] is True, 'Wrong CGUST source-binding revision/privacy')
    bound = index_files(binding['files'])
    require(len(bound) == 36, 'Source binding must retain all 36 original members')
    for rel in bound:
        source_relative(rel)
    require(approval['document'] == 'Independent final source and appearance approval' and approval['revision'] == 'v10' and approval['private'] is True, 'Wrong CGUST final approval schema/revision')
    require(approval['decision'] == certificate['decision'] and approval['source_appearance_go'] is True and approval['all_36_bound_files_independently_verified'] is True, 'Final source approval incomplete')
    for key in ('manufacturing_approval_in_this_document', 'general_privacy_approval_in_this_document', 'publication_approval_in_this_document'):
        require(approval[key] is False, 'Source approval scope promoted: ' + key)
    model = certificate['model']
    require(model['stl_sha256'] == approval['stl']['sha256'] == STL and model['ordered_scene_stl_triangles_exact'] == 5176, 'Wrong CGUST source STL/triangles')
    for key, ref in [('source_code_sha256', 'model_source'), ('parameters_sha256', 'parameters'), ('scene_sha256', 'scene')]:
        require(model[key] == approval[ref]['sha256'], 'Certificate/approval identity differs: ' + key)
    contract = certificate['render_contract']
    require(exact(contract, {'width_px': 1000, 'height_px': 780, 'engine': 'Cycles', 'samples': 64, 'denoising': False, 'exposure': 0}), 'Source render contract differs')
    identity = approval['identity']
    require(identity['triangles'] == 5176 and all(identity[k] is True for k in ('single_mesh', 'ordered_triangle_coordinates_exact', 'no_modifiers_constraints_shape_keys_or_instances', 'no_image_texture_materials')), 'Final source scene identity differs')
    require(set(certificate['renders']) == set(approval['views']) == VIEWS, 'Source nine-view coverage differs')
    for name in sorted(VIEWS):
        public, view = certificate['renders'][name], approval['views'][name]
        raw, clean, pixels = view['raw_png'], view['public_png'], view['raw_public_identity']
        require(source_relative(raw['path']) == 'previews/v10/' + name + '.png' and source_relative(clean['path']) == PUBLIC_PREVIEWS + '/' + name + '.png', 'Source view path differs: ' + name)
        require(exact(bound[raw['path']], {k: raw[k] for k in ('bytes', 'sha256')}) and exact(bound[clean['path']], {k: clean[k] for k in ('bytes', 'sha256')}), 'Source view not bound to original 36-file list: ' + name)
        require(public['reviewed_raw_sha256'] == pixels['raw_sha256'] == raw['sha256'] and public['public_png_sha256'] == pixels['clean_sha256'] == clean['sha256'] and public['rgba_sha256'] == pixels['rgba_sha256'], 'Certificate/approval PNG identity differs: ' + name)
        require(public['raw_public_nontext_chunks_idat_and_rgba_exact'] is True and all(pixels[k] is True for k in ('all_nontext_chunks_exact', 'idat_exact', 'decoded_rgba_exact', 'passed')), 'Source PNG identity incomplete: ' + name)
        require(exact(pixels['size'], [1000, 780]) and pixels['raw_path'] == raw['path'] and pixels['clean_path'] == clean['path'], 'Source PNG size/path differs: ' + name)


def inventory_schema(inventory):
    require(inventory['schema'] == 'cgust-author-full-science-inventory-v1' and inventory['version'] == 'v10' and inventory['stl_sha256'] == STL, 'Original inventory schema/identity differs')
    members = index_files(inventory['files'])
    require(len(members) == inventory['file_count'] == 2363 and sum(v['bytes'] for v in members.values()) == inventory['logical_bytes'], 'Original inventory count/bytes differ')
    require('restore_copy_map' not in inventory, 'Unexpected restore map in original CGUST inventory')
    return members


def replay_structure(audit):
    require(audit['passed'] is True and audit['strict_passed'] is True and audit['inspect_only'] is False, 'Independent nine-view replay failed/incomplete')
    require(set(audit['checks']) == REPLAY_CHECKS and all(v is True for v in audit['checks'].values()), 'Replay required checks missing/failed')
    require(audit['original_face_count'] == audit['saved_world_face_count'] == 5176 and audit['blend_missing_triangle_count'] == audit['blend_extra_triangle_count'] == 0, 'Replay original triangle identity differs')
    require(len(audit['views']) == 9 and {r['view'] for r in audit['views']} == VIEWS, 'Replay nine-view coverage differs')


def verify_source(author, run, roots):
    frozen = run / 'frozen'
    certificate = read(author / 'qa/source-review/SOURCE-APPEARANCE-CERTIFICATE-v10.public.json')
    binding = read(author / 'qa/source-review/SOURCE-BINDING-v10.private.json')
    approval_path = author / 'qa/source-review/FINAL-SOURCE-APPEARANCE-GO-v10.private.json'
    approval = read(approval_path)
    source_schema(certificate, binding, approval)
    bound = {source_relative(k): v for k, v in index_files(binding['files']).items()}
    for rel, expected in bound.items():
        check_record(member(author, rel), expected)
        if (frozen / rel).exists():
            check_record(member(frozen, rel), expected)
    check_record(member(author, source_relative(approval['binding']['path'])), {k: approval['binding'][k] for k in ('bytes', 'sha256')})
    require(approval['binding']['sha256'] == PINS['qa/source-review/SOURCE-BINDING-v10.private.json'], 'Final approval source-binding pin differs')
    for key in ('model_source', 'parameters', 'stl', 'scene', 'versioned_estimates'):
        row = approval[key]
        check_record(member(author, source_relative(row['path'])), {k: row[k] for k in ('bytes', 'sha256')})
    pm = read(run / 'public-previews/render-manifest.json')
    raw_manifest = read(frozen / 'previews/v10/render-manifest.json')
    require(set(pm['views']) == set(raw_manifest['views']) == VIEWS and pm['stl_sha256'] == raw_manifest['stl_sha256'] == STL, 'Manifest view/STL mismatch')
    require(certificate['model']['scene_sha256'] == raw_manifest['blend_sha256'] == sha(frozen / 'models/v10/scene.blend'), 'Scene identity differs')
    for rel in ('render-manifest.json', 'metadata-cleanup-binding.json'):
        require(record(run / 'public-previews' / rel) == record(author / 'qa/render-check/v10-author/sanitized-previews' / rel), 'Author/independent public binding differs: ' + rel)
    require(pm['source_raw_manifest_sha256'] == sha(frozen / 'previews/v10/render-manifest.json'), 'Public manifest raw reference differs')
    scene_dir = run / 'source-scene-reproduction'
    scene = read(scene_dir / 'source-scene-audit.json')
    require(scene['passed'] is True and scene['exact_scene_state_matches'] is True and scene['state_difference_count'] == 0 and scene['state_differences'] == [], 'Scene-state comparison failed')
    require(all(scene[k] is True for k in ['all_nine_camera_definitions_match', 'source_unchanged', 'original_blend_unchanged', 'manifest_unchanged']), 'Source scene audit input/camera flags failed')
    require(set(scene['camera_definition_checks']) == VIEWS and all(v is True for v in scene['camera_definition_checks'].values()), 'Scene-state camera coverage differs')
    for key, rel in [('source_sha256', 'source/render_preview.py'), ('original_blend_sha256', 'models/v10/scene.blend'), ('manifest_sha256', 'previews/v10/render-manifest.json'), ('checker_sha256', 'qa/render-tools/compare_source_scene.py')]:
        require(scene[key] == sha(frozen / rel), 'Scene-state input/tool binding differs: ' + key)
    rebuild = read(run / 'source-rebuild-binding.json')
    require(rebuild['returncode'] == 0 and rebuild['original_stl_bitwise_identical'] is True and rebuild['original_color_regions_bitwise_identical'] is True, 'Original source geometry reproduction failed')
    for name in ['model.stl', 'color-regions.json']:
        require(record(run / 'reproduction/models/v10' / name) == record(frozen / 'models/v10' / name), 'Source rebuild content differs: ' + name)
    require(scene['generated_blend_sha256'] == sha(run / 'reproduction/models/v10/scene.blend'), 'Rebuilt Blend hash differs')
    require(record(scene_dir / 'original-scene-state.json') == record(scene_dir / 'source-scene-state.json'), 'Scene-state file bytes differ')
    audit = read(run / 'saved-blend-rerenders/blend-rerender-audit.json')
    replay_structure(audit)
    for key, rel in [('original_stl_sha256', 'models/v10/model.stl'), ('original_blend_sha256', 'models/v10/scene.blend'), ('original_manifest_sha256', 'previews/v10/render-manifest.json'), ('source_sha256', 'qa/render-tools/inspect_and_rerender_blend.py'), ('png_comparator_source_sha256', 'qa/render-tools/png_exact_compare.py')]:
        require(audit[key] == sha(frozen / rel), 'Replay input/tool binding differs: ' + key)
    replay = {r['view']: r for r in audit['views']}
    require(len(audit['views']) == 9 and set(replay) == VIEWS, 'Replay nine-view coverage differs')
    module_path = frozen / 'qa/render-tools/png_exact_compare.py'
    spec = importlib.util.spec_from_file_location('frozen_png_exact_compare', module_path)
    png = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(png)
    views = {}
    for name in sorted(VIEWS):
        approved, replay_row = approval['views'][name], replay[name]
        row = {'raw': approved['raw_png'], 'metadata_only_public': approved['public_png'], 'decoded_rgba_sha256': approved['raw_public_identity']['rgba_sha256']}
        paths = {'raw': frozen / source_relative(row['raw']['path']), 'replay': run / 'saved-blend-rerenders' / (name + '.png'), 'clean': run / 'public-previews' / (name + '.png')}
        for key in ('camera', 'projection', 'lens_mm'):
            require(exact(raw_manifest['views'][name][key], pm['views'][name][key]), 'Camera policy differs: ' + name)
        check_record(paths['raw'], {'bytes': row['raw']['bytes'], 'sha256': row['raw']['sha256']})
        check_record(paths['clean'], {'bytes': row['metadata_only_public']['bytes'], 'sha256': row['metadata_only_public']['sha256']})
        require(sha(paths['replay']) == replay_row['rerendered_raw_png_sha256'] and replay_row['original_raw_png_sha256'] == row['raw']['sha256'], 'Replay PNG reference differs: ' + name)
        require(pm['views'][name]['sha256'] == row['metadata_only_public']['sha256'] and pm['views'][name]['original_raw_png_sha256'] == row['raw']['sha256'], 'Clean PNG manifest differs: ' + name)
        parsed = {key: png.parse(path) for key, path in paths.items()}
        require(all(v['width'] == 1000 and v['height'] == 780 and v['rgba_sha256'] == row['decoded_rgba_sha256'] for v in parsed.values()), 'Decoded PNG identity differs: ' + name)
        require(parsed['raw']['rgba_bytes'] == parsed['replay']['rgba_bytes'] == parsed['clean']['rgba_bytes'], 'Decoded PNG byte comparison differs: ' + name)
        require(parsed['raw']['idat_sha256'] == parsed['replay']['idat_sha256'] == parsed['clean']['idat_sha256'], 'PNG IDAT content differs: ' + name)
        for key in ('raw', 'replay'):
            kept = [(tag, payload) for tag, payload in parsed[key]['chunks'] if not (tag == b'tEXt' and png.text_payload(tag, payload)[0] in png.SANITIZE_TEXT_KEYS)]
            require(kept == parsed['clean']['chunks'], 'PNG nonremoved chunks differ: ' + name)
        require(replay_row['posed_world_directed_geometry_matches_stl'] is True and replay_row['sanitized_png_comparison']['passed'] is True, 'Replay geometry/pixel audit failed: ' + name)
        require(pm['views'][name]['decoded_rgba_sha256'] == row['decoded_rgba_sha256'], 'Clean manifest RGBA reference differs')
        views[name] = {key: {'path': logical_path(path, roots), **record(path)} for key, path in paths.items()}
        views[name]['decoded_rgba_sha256'] = row['decoded_rgba_sha256']
    return {'passed': True, 'status': certificate['decision'], 'certificate_scope_verbatim': certificate['scope'],
            'certificate_limitations_verbatim': certificate['limits'],
            'source_documents': {'author/' + rel: record(author / rel) for rel in PINS if rel.startswith('qa/source-review/')},
            'original_source_binding_members': [{'path': 'author/' + rel, **expected} for rel, expected in bound.items()],
            'scene_state_scope_verbatim': scene['scope'], 'scene_state_policy_verbatim': scene['state_comparison_policy'],
            'construction_to_saved_reload_differences_retained': scene['source_construction_to_saved_reload_differences'],
            'source_prefix_executed_lines': scene['executed_source_lines'], 'image_render_tail_excluded_lines': scene['excluded_source_lines'],
            'views': views, 'scene_state': {name: record(scene_dir / name) for name in ['source-scene-audit.json', 'original-scene-state.json', 'source-scene-state.json', 'source-constructed-memory-state.json']},
            'replay_audit': record(run / 'saved-blend-rerenders/blend-rerender-audit.json'),
            'public_manifest': record(run / 'public-previews/render-manifest.json'),
            'metadata_cleanup_binding': record(run / 'public-previews/metadata-cleanup-binding.json')}


def main():
    global AUTHOR_PREFIX
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--author-root', type=Path, required=True)
    ap.add_argument('--run-root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--source-path-prefix', required=True, help='Exact relative directory prefix used in source-bound inputs, ending in /; never emitted in reports')
    args = ap.parse_args()
    AUTHOR_PREFIX = validate_source_path_prefix(args.source_path_prefix)
    require(not args.out.exists(), 'Never replace evidence output')
    author, run = args.author_root.resolve(), args.run_root.resolve()
    roots = {'author': author, 'run': run, 'checker': Path(__file__).resolve().parent}
    output_key = logical_path(args.out, roots)
    require(output_key.startswith('checker/'), 'Result output must be a new checker member')
    # Fail before reading large files if the independent full/replay run is unfinished.
    require((run / 'independent-execution-summary.json').is_file(), 'Independent run has no completion summary yet')
    strict = verify_strict_original(author, run)
    inputs = {}
    for rel, expected in PINS.items():
        require(sha(author / rel) == expected, 'Pinned original input changed: ' + rel)
        inputs['author/' + rel] = record(author / rel)
        if (run / 'frozen' / rel).exists():
            require(sha(run / 'frozen' / rel) == expected, 'Frozen pinned original input changed: ' + rel)
    inventory = read(author / 'qa/freeze-v10/SCIENCE-INVENTORY.json')
    members = inventory_schema(inventory)
    for rel, value in members.items():
        check_record(member(author, rel), value)
    selection_path = run / 'author-freeze-manifest.json'
    require(sha(selection_path) == SELECTION, '54-input runner selection changed')
    selection = read(selection_path)
    require(selection['schema'] == 'cgust-runner-input-selection-v1' and selection['version'] == 'v10' and selection['stl_sha256'] == STL and len(selection['files']) == 54, 'Runner input selection differs')
    require(selection['full_science_inventory']['path'] == 'qa/freeze-v10/SCIENCE-INVENTORY.json', 'Selection inventory path differs')
    check_record(author / selection['full_science_inventory']['path'], {k: selection['full_science_inventory'][k] for k in ['bytes', 'sha256']})
    require(selection['full_science_inventory']['sha256'] == PINS['qa/freeze-v10/SCIENCE-INVENTORY.json'], 'Selection lost full science inventory binding')
    frozen_members = index_files(selection['files'])
    require(exact(read(run / 'frozen-input-inventory.json'), frozen_members), 'Frozen input inventory differs from pinned selection')
    validation = read(run / 'author-freeze-validation.json')
    require(validation['passed'] is True and validation['file_count'] == 54 and validation['manifest_sha256'] == SELECTION and validation['stl_sha256'] == STL, 'Runner freeze validation differs')
    for rel, value in frozen_members.items():
        check_record(member(author, rel), value)
        check_record(member(run / 'frozen', rel), value)
    require(sha(author / 'models/v9/model.stl') == sha(author / 'models/v10/model.stl') == STL, 'v9-v10 STL byte identity differs')
    groups, csv_map = [], []
    for rel in FILES:
        entries = []
        for owner in ('author', 'independent'):
            for mode in MODES:
                p = science_path(author, run, owner, mode, rel)
                intersection_hash = sha(science_path(author, run, owner, mode, 'intersections.json'))
                entries.append((owner + '-' + mode, mode, p, intersection_hash))
        groups.append(compare_group(entries, rel, roots))
        if rel.endswith('.csv.xz'):
            for label, mode, p, _ in entries:
                owner = 'author' if label.startswith('author-') else 'independent'
                dense = read(science_path(author, run, owner, mode, 'standard/dense/dense-check.json'))
                csv_map.append({'source': label, 'original_path': logical_path(p, roots), 'restore_from_canonical_path': logical_path(science_path(author, run, 'author', 'normal', rel), roots), **full_csv(p, dense)})
    require(all(exact({k: r[k] for k in ['compressed', 'decoded', 'data_rows']}, {k: csv_map[0][k] for k in ['compressed', 'decoded', 'data_rows']}) for r in csv_map), 'Four-source CSV content differs')
    source = verify_source(author, run, roots)
    # Re-read every original/frozen retained member after all comparisons; no producer mutation.
    for rel, value in members.items():
        check_record(member(author, rel), value)
    for rel, value in frozen_members.items():
        check_record(member(run / 'frozen', rel), value)
    for group in groups:
        for row in group['sources']:
            check_record(physical_path(row['path'], roots), {k: row[k] for k in ['bytes', 'sha256']})
    result = {'schema': 'cgust-independent-result-binding-v10-v1', 'passed': True, 'stl_sha256': STL,
              'checker_path': logical_path(__file__, roots), 'checker_sha256': sha(__file__), 'checker_optimization_level': sys.flags.optimize,
              'source_path_prefix_metadata': {'provided_via': '--source-path-prefix', 'validated_form': 'canonical relative directory prefix ending in /', 'value_disclosed': False},
              'original_pinned_inputs': inputs, 'runner_selection': record(selection_path),
              'full_author_inventory_members_verified': len(members), 'frozen_runner_inputs_verified': len(frozen_members),
              'science_comparisons': groups, 'full_csv_four_source_copy_map': csv_map,
              'csv_payloads_created': 0, 'original_strict_results': strict, 'source_appearance_binding': source,
              'scope': 'Read-only exact primary raw/sections/dense/exact science comparison across author normal/-O and independent normal/-O. Full author inventory retained and rehashed. Only explicit execution-time, interpreter-mode and independently compared intersection-report-reference fields are excluded from science equality; their original values remain recorded. No producer file is edited. Original numerical strict=false and standard/producer exit1 remain. Appearance-only GO is not manufacturing, physical-print, privacy, licensing or publication approval.'}
    validate_output_metadata(result, roots)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'passed': True, 'science_groups': len(groups), 'four_source_csv_rows_each': csv_map[0]['data_rows'], 'views': len(source['views']), 'original_numerical_strict_passed': False, 'out': output_key}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'passed': False, 'error_type': type(error).__name__, 'error': str(error)}), file=sys.stderr)
        raise SystemExit(1)
