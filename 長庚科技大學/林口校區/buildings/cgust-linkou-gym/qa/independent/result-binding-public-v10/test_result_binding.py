"""Small fail-closed controls. Never invokes full geometry, Blender or large CSVs."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import lzma
import sys
import subprocess
import tempfile
import check_result_binding as binding

binding.AUTHOR_PREFIX = binding.validate_source_path_prefix('fixture-author/')


def source_fixture():
    """Small synthetic equivalent of the pinned three-document CGUST schema."""
    h = 'a' * 64
    certificate = {'document': 'Source and appearance review certificate', 'revision': 'v10',
                   'decision': 'GO_WITH_REPRESENTATIVE_MODEL_LIMITS', 'all_nine_original_renders_actually_reviewed': True,
                   'model': {'source_code_sha256': h, 'parameters_sha256': h, 'scene_sha256': h,
                             'stl_sha256': binding.STL, 'ordered_scene_stl_triangles_exact': 5176},
                   'render_contract': {'width_px': 1000, 'height_px': 780, 'engine': 'Cycles', 'samples': 64, 'denoising': False, 'exposure': 0}, 'renders': {}}
    source = {'revision': 'v10', 'private_only': True, 'files': []}
    approval = {'document': 'Independent final source and appearance approval', 'revision': 'v10', 'private': True,
                'decision': certificate['decision'], 'source_appearance_go': True, 'all_36_bound_files_independently_verified': True,
                'manufacturing_approval_in_this_document': False, 'general_privacy_approval_in_this_document': False,
                'publication_approval_in_this_document': False, 'model_source': {'sha256': h}, 'parameters': {'sha256': h},
                'scene': {'sha256': h}, 'stl': {'sha256': binding.STL},
                'identity': {'triangles': 5176, 'single_mesh': True, 'ordered_triangle_coordinates_exact': True,
                             'no_modifiers_constraints_shape_keys_or_instances': True, 'no_image_texture_materials': True}, 'views': {}}
    for name in sorted(binding.VIEWS):
        raw = {'path': binding.AUTHOR_PREFIX + 'previews/v10/' + name + '.png', 'bytes': 3, 'sha256': h}
        clean = {'path': binding.AUTHOR_PREFIX + binding.PUBLIC_PREVIEWS + '/' + name + '.png', 'bytes': 3, 'sha256': h}
        source['files'].extend([dict(raw), dict(clean)])
        certificate['renders'][name] = {'reviewed_raw_sha256': h, 'public_png_sha256': h, 'rgba_sha256': h, 'raw_public_nontext_chunks_idat_and_rgba_exact': True}
        approval['views'][name] = {'raw_png': raw, 'public_png': clean, 'raw_public_identity': {
            'raw_path': raw['path'], 'clean_path': clean['path'], 'raw_sha256': h, 'clean_sha256': h, 'rgba_sha256': h,
            'size': [1000, 780], 'all_nontext_chunks_exact': True, 'idat_exact': True, 'decoded_rgba_exact': True, 'passed': True}}
    source['files'].extend({'path': binding.AUTHOR_PREFIX + 'fixture/' + str(i), 'bytes': 3, 'sha256': h} for i in range(18))
    return certificate, source, approval


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    binding.require(not args.out.exists(), 'Never replace control evidence')
    results = []

    def case(name, should_pass, function):
        try:
            function()
            accepted, error = True, None
        except (RuntimeError, KeyError, ValueError, EOFError, lzma.LZMAError) as e:
            accepted, error = False, str(e).replace(str(root), 'author')
        binding.require(accepted == should_pass, 'Control outcome wrong: ' + name)
        results.append({'name': name, 'expected_accept': should_pass, 'accepted': accepted, 'error': error})

    with tempfile.TemporaryDirectory(prefix='small-controls-', dir=Path(__file__).resolve().parent) as temp:
        root = Path(temp) / 'author'
        root.mkdir()
        roots = {'author': root, 'run': Path(temp) / 'run', 'checker': Path(temp) / 'checker'}
        def dump(name, data):
            p = root / name
            p.write_text(json.dumps(data))
            return p
        def intersection(mode='normal', elapsed=1, contact_count=33):
            return {'tools': {'optimization_level': binding.MODES.index(mode)}, 'elapsed_seconds': elapsed,
                    'actual_intersection_pair_count': contact_count, 'strict_passed': True, 'unrecognized_science': {'keep': 'all'}}
        rows = []
        for owner in ('author', 'independent'):
            for mode in binding.MODES:
                label = owner + '-' + mode
                p = dump(label + '.json', intersection(mode, elapsed=len(rows) + 0.5))
                rows.append((label, mode, p, 'a' * 64))
        case('four_modes_science_equal_only_elapsed_and_mode_differ', True, lambda: binding.compare_group(rows, 'intersections.json', roots))
        read_original = binding.read(rows[-1][2])
        def mutated_group(key, value):
            changed = copy.deepcopy(read_original)
            changed[key] = value
            rows[-1][2].write_text(json.dumps(changed))
            try:
                binding.compare_group(rows, 'intersections.json', roots)
            finally:
                rows[-1][2].write_text(json.dumps(read_original))
        case('reject_changed_exact_contact_count', False, lambda: mutated_group('actual_intersection_pair_count', 34))
        case('reject_unknown_scientific_field_change', False, lambda: mutated_group('unrecognized_science', {'keep': 'changed'}))
        case('reject_boolean_replaced_with_integer', False, lambda: mutated_group('strict_passed', 1))
        case('reject_added_scientific_field', False, lambda: mutated_group('invented_new_science', 0))
        case('reject_negative_elapsed', False, lambda: mutated_group('elapsed_seconds', -1))
        case('reject_string_elapsed', False, lambda: mutated_group('elapsed_seconds', '1'))
        case('reject_wrong_mode_even_when_all_science_equal', False,
             lambda: binding.comparable(intersection('normal'), 'intersections.json', 'optimized', 'a' * 64))
        exact = {'elapsed_seconds': 1, 'optimization_level': 0, 'original_numerical_strict_passed': False,
                 'input_and_tool_sha256': {'intersections_report': 'a' * 64}, 'selected_samples': 33}
        case('accept_own_compared_intersection_reference', True,
             lambda: binding.comparable(exact, binding.FILES[-2], 'normal', 'a' * 64))
        case('reject_forged_intersection_reference', False,
             lambda: binding.comparable(exact, binding.FILES[-2], 'normal', 'b' * 64))
        case('reject_missing_explicit_elapsed', False,
             lambda: binding.comparable({k: v for k, v in exact.items() if k != 'elapsed_seconds'}, binding.FILES[-2], 'normal', 'a' * 64))
        case('reject_wrong_summary_mode', False,
             lambda: binding.comparable({'optimized_python': False}, 'standard/qa-summary.json', 'optimized', 'a' * 64))
        p = root / 'duplicate.json'
        p.write_text('{"strict_passed":false,"strict_passed":true}')
        case('reject_duplicate_json_key', False, lambda: binding.read(p))
        q = root / 'nonfinite.json'
        q.write_text('{"science":NaN}')
        case('reject_nonfinite_json', False, lambda: binding.read(q))
        case('reject_duplicate_inventory_member', False, lambda: binding.index_files([{'path': 'a', 'bytes': 1, 'sha256': 'a'}] * 2))
        case('reject_parent_traversal', False, lambda: binding.member(root, '../outside'))
        case('reject_absolute_member', False, lambda: binding.member(root, '/outside'))
        regular = root / 'regular'
        regular.write_bytes(b'abc')
        link = root / 'link'
        link.symlink_to(regular)
        case('reject_symlink_evidence', False, lambda: binding.record(link))
        case('reject_same_size_changed_file', False, lambda: binding.check_record(regular, {'bytes': 3, 'sha256': hashlib.sha256(b'abd').hexdigest()}))
        csv = root / 'dense.csv.xz'
        payload = b'face,sample\n0,0\n0,1\n'
        def csv_report():
            return {'csv_compressed_bytes': csv.stat().st_size, 'csv_compressed_sha256': binding.sha(csv),
                    'uncompressed_csv_bytes': len(payload), 'uncompressed_csv_sha256': hashlib.sha256(payload).hexdigest(), 'samples': 2}
        csv.write_bytes(lzma.compress(payload))
        dense = csv_report()
        case('accept_complete_csv_compressed_decoded_hash_bytes_rows', True, lambda: binding.full_csv(csv, dense))
        wrong = dict(dense, uncompressed_csv_sha256='b' * 64)
        case('reject_decoded_hash_change', False, lambda: binding.full_csv(csv, wrong))
        wrong = dict(dense, uncompressed_csv_bytes=len(payload) - 1)
        case('reject_decoded_byte_count_change', False, lambda: binding.full_csv(csv, wrong))
        wrong = dict(dense, samples=1)
        case('reject_skipped_csv_row', False, lambda: binding.full_csv(csv, wrong))
        csv.write_bytes(csv.read_bytes()[:-4])
        truncated = dict(dense, csv_compressed_bytes=csv.stat().st_size, csv_compressed_sha256=binding.sha(csv))
        case('reject_truncated_xz_even_with_updated_compressed_hash', False, lambda: binding.full_csv(csv, truncated))
        certificate, source, approval = source_fixture()
        case('accept_actual_cgust_three_document_schema', True, lambda: binding.source_schema(certificate, source, approval))
        case('reject_inherited_aeust_go_schema', False, lambda: binding.source_schema({'decision': 'SOURCE-APPEARANCE-GO', 'revision': 'v10'}, source, approval))
        case('reject_manufacturing_go_substitution', False, lambda: binding.source_schema(dict(certificate, decision='MANUFACTURING_GO'), source, approval))
        case('reject_missing_view', False, lambda: binding.source_schema(dict(certificate, renders={k: v for k, v in certificate['renders'].items() if k != 'front'}), source, approval))
        case('reject_extra_view', False, lambda: binding.source_schema(dict(certificate, renders=dict(certificate['renders'], extra={})), source, approval))
        case('reject_source_wrong_stl', False, lambda: binding.source_schema(dict(certificate, model=dict(certificate['model'], stl_sha256='0' * 64)), source, approval))
        changed = copy.deepcopy(approval)
        changed['general_privacy_approval_in_this_document'] = True
        case('reject_privacy_scope_promotion', False, lambda: binding.source_schema(certificate, source, changed))
        audit = {'passed': True, 'strict_passed': True, 'inspect_only': False,
                 'checks': {k: True for k in binding.REPLAY_CHECKS},
                 'original_face_count': 5176, 'saved_world_face_count': 5176,
                 'blend_missing_triangle_count': 0, 'blend_extra_triangle_count': 0,
                 'views': [{'view': name} for name in binding.VIEWS]}
        case('accept_exact_replay_audit_schema', True, lambda: binding.replay_structure(audit))
        altered = copy.deepcopy(audit)
        altered['checks'].pop('all_nine_decoded_rgba_bytes_identical')
        case('reject_missing_replay_required_check', False, lambda: binding.replay_structure(altered))
        altered = copy.deepcopy(audit)
        altered['checks']['exactly_64_samples'] = False
        case('reject_replay_false_check_despite_passed_true', False, lambda: binding.replay_structure(altered))
        case('reject_inspection_instead_of_replay', False, lambda: binding.replay_structure(dict(audit, inspect_only=True)))
        case('reject_eight_replay_views', False, lambda: binding.replay_structure(dict(audit, views=audit['views'][:8])))
        case('reject_duplicate_replay_view', False, lambda: binding.replay_structure(dict(audit, views=[audit['views'][0]] * 9)))
        case('reject_scene_triangle_count_substitution', False, lambda: binding.replay_structure(dict(audit, saved_world_face_count=5175)))
        # Added case-schema boundaries and metadata-only path boundaries.
        case('reject_inherited_wfu_certificate_schema', False, lambda: binding.source_schema({'schema': 'representative-building-source-appearance-certificate-v1', 'version': 'v10', 'status': 'GO_FOR_DECLARED_REPRESENTATIVE_APPEARANCE_ONLY'}, source, approval))
        case('reject_missing_source_bound_member', False, lambda: binding.source_schema(certificate, dict(source, files=source['files'][:-1]), approval))
        case('reject_duplicate_source_bound_member', False, lambda: binding.source_schema(certificate, dict(source, files=source['files'][:-1] + [source['files'][0]]), approval))
        case('reject_publication_scope_promotion', False, lambda: binding.source_schema(certificate, source, dict(approval, publication_approval_in_this_document=True)))
        case('reject_source_approval_false', False, lambda: binding.source_schema(certificate, source, dict(approval, source_appearance_go=False)))
        changed = copy.deepcopy(certificate)
        changed['renders']['front']['rgba_sha256'] = '9' * 64
        case('reject_certificate_approval_pixel_hash_mismatch', False, lambda: binding.source_schema(changed, source, approval))
        case('accept_stable_logical_member_roundtrip', True, lambda: binding.require(binding.physical_path(binding.logical_path(regular, roots), roots) == regular, 'Logical roundtrip differs'))
        case('accept_logical_report_metadata', True, lambda: binding.validate_output_metadata({'path': 'author/regular', 'science_pointer': '/world/nodes/rna/is_runtime_data: value differs'}, roots))
        case('reject_metadata_outside_declared_roots', False, lambda: binding.logical_path(Path(temp) / 'outside', roots))
        case('reject_metadata_common_prefix_impersonation', False, lambda: binding.logical_path(Path(temp) / 'author-other' / 'regular', roots))
        case('reject_absolute_metadata_member', False, lambda: binding.physical_path(str(regular), roots))
        case('reject_unknown_metadata_root', False, lambda: binding.physical_path('private/regular', roots))
        case('reject_metadata_parent_traversal', False, lambda: binding.physical_path('author/../outside', roots))
        case('reject_metadata_noncanonical_dot_segment', False, lambda: binding.physical_path('author/./regular', roots))
        case('reject_metadata_backslash', False, lambda: binding.physical_path('author/a\\b', roots))
        case('reject_physical_path_in_report_text', False, lambda: binding.validate_output_metadata({'note': str(regular)}, roots))
        case('reject_unknown_absolute_private_path_in_report', False, lambda: binding.validate_output_metadata({'note': ('/' + 'home/private/secret')}, roots))
        case('reject_absolute_report_path_field', False, lambda: binding.validate_output_metadata({'path': '/outside/regular'}, roots))
        case('reject_source_binding_prefix_impersonation', False, lambda: binding.source_relative(binding.AUTHOR_PREFIX.rstrip('/') + '-other/models/v10/model.stl'))
        case('reject_source_binding_parent_traversal', False, lambda: binding.source_relative(binding.AUTHOR_PREFIX + '../outside'))
        case('reject_source_binding_absolute_member', False, lambda: binding.source_relative(binding.AUTHOR_PREFIX + '/outside'))
        inventory = {'schema': 'cgust-author-full-science-inventory-v1', 'version': 'v10', 'stl_sha256': binding.STL,
                     'files': [{'path': 'retained/' + str(i), 'bytes': 1, 'sha256': 'a' * 64} for i in range(2363)],
                     'file_count': 2363, 'logical_bytes': 2363}
        case('accept_actual_cgust_inventory_without_restore_map', True, lambda: binding.inventory_schema(inventory))
        case('reject_inherited_wfu_inventory_schema', False, lambda: binding.inventory_schema(dict(inventory, schema='wfu-author-full-science-inventory-v1')))
        case('reject_invented_inventory_restore_map', False, lambda: binding.inventory_schema(dict(inventory, restore_copy_map=[])))
        case('reject_inventory_missing_member', False, lambda: binding.inventory_schema(dict(inventory, files=inventory['files'][:-1])))
        case('reject_inventory_logical_byte_mismatch', False, lambda: binding.inventory_schema(dict(inventory, logical_bytes=2362)))
        def unfinished_cli():
            output = Path(temp) / 'must-not-exist.json'
            command = [sys.executable, '-B', *(['-O'] if sys.flags.optimize else []), binding.__file__,
                       '--author-root', str(root / 'nonexistent-author'), '--run-root', str(roots['run']), '--out', str(output),
                       '--source-path-prefix', binding.AUTHOR_PREFIX]
            result = subprocess.run(command, capture_output=True, text=True)
            binding.require(result.returncode == 1 and not output.exists(), 'Incomplete-run CLI did not fail closed without evidence')
            failure = json.loads(result.stderr)
            binding.require(failure['passed'] is False and failure['error'] == 'Independent run has no completion summary yet', 'Incomplete-run CLI read science before completion gate')
        case('reject_unfinished_cli_before_reading_any_science', True, unfinished_cli)
        # Public variant adds prefix validation only; the original 65 cases remain.
        case('accept_safe_source_prefix', True, lambda: binding.require(binding.validate_source_path_prefix('fixture-author/') == 'fixture-author/', 'Safe prefix altered'))
        case('accept_nested_safe_source_prefix', True, lambda: binding.require(binding.validate_source_path_prefix('fixture/root/') == 'fixture/root/', 'Nested prefix altered'))
        case('reject_missing_source_prefix_value', False, lambda: binding.validate_source_path_prefix(None))
        case('reject_empty_source_prefix_value', False, lambda: binding.validate_source_path_prefix(''))
        case('reject_source_prefix_missing_trailing_slash', False, lambda: binding.validate_source_path_prefix('fixture-author'))
        case('reject_source_prefix_absolute', False, lambda: binding.validate_source_path_prefix('/fixture-author/'))
        case('reject_source_prefix_parent_only', False, lambda: binding.validate_source_path_prefix('../'))
        case('reject_source_prefix_embedded_parent', False, lambda: binding.validate_source_path_prefix('fixture/../author/'))
        case('reject_source_prefix_backslash', False, lambda: binding.validate_source_path_prefix('fixture\\author/'))
        case('reject_source_prefix_windows_drive', False, lambda: binding.validate_source_path_prefix('C:/fixture/'))
        case('reject_source_prefix_dot_segment', False, lambda: binding.validate_source_path_prefix('fixture/./author/'))
        case('reject_source_prefix_duplicate_slash', False, lambda: binding.validate_source_path_prefix('fixture//author/'))
        case('reject_source_prefix_root_only', False, lambda: binding.validate_source_path_prefix('/'))
        case('reject_source_prefix_boolean', False, lambda: binding.validate_source_path_prefix(True))
        case('reject_source_prefix_whitespace', False, lambda: binding.validate_source_path_prefix('fixture author/'))
        def missing_prefix_cli():
            output = Path(temp) / 'missing-prefix-must-not-exist.json'
            command = [sys.executable, '-B', *(['-O'] if sys.flags.optimize else []), binding.__file__,
                       '--author-root', str(root), '--run-root', str(roots['run']), '--out', str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            binding.require(result.returncode == 2 and not output.exists() and '--source-path-prefix' in result.stderr,
                            'Missing required prefix CLI did not fail before any science')
        case('reject_missing_required_source_prefix_cli', True, missing_prefix_cli)
    result = {'passed': True, 'checker_sha256': binding.sha(binding.__file__), 'test_source_sha256': binding.sha(__file__),
              'checker_path': 'checker/check_result_binding.py', 'test_source_path': 'checker/test_result_binding.py',
              'optimization_level': sys.flags.optimize, 'cases': results, 'case_count': len(results),
              'scope': 'Small unit-level acceptance and negative controls only. No full science, PNG replay or Blender execution. Full candidate binding still requires completed independent run.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'passed': True, 'case_count': len(results), 'optimization_level': sys.flags.optimize}))


if __name__ == '__main__':
    main()
