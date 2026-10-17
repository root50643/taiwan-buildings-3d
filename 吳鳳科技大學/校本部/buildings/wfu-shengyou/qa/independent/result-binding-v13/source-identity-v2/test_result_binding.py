"""Small fail-closed controls. Never invokes full geometry, Blender or large CSVs."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import lzma
import sys
import os
import py_compile
import importlib.util
from types import ModuleType
import tempfile
# Test the source bytes directly too, so -B cannot silently read stale test imports.
checker_path = Path(__file__).with_name('check_result_binding.py')
checker_bytes = checker_path.read_bytes()
binding = ModuleType('check_result_binding')
binding.__file__ = str(checker_path)
exec(compile(checker_bytes, str(checker_path), 'exec'), binding.__dict__)


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
            accepted, error = False, str(e)
        binding.require(accepted == should_pass, 'Control outcome wrong: ' + name)
        results.append({'name': name, 'expected_accept': should_pass, 'accepted': accepted, 'error': error})

    with tempfile.TemporaryDirectory(prefix='small-controls-', dir=Path(__file__).resolve().parent) as temp:
        root = Path(temp)
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
        case('four_modes_science_equal_only_elapsed_and_mode_differ', True, lambda: binding.compare_group(rows, 'intersections.json'))
        read_original = binding.read(rows[-1][2])
        def mutated_group(key, value):
            changed = copy.deepcopy(read_original)
            changed[key] = value
            rows[-1][2].write_text(json.dumps(changed))
            try:
                binding.compare_group(rows, 'intersections.json')
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
        certificate = {'schema': 'representative-building-source-appearance-certificate-v1', 'version': 'v13',
                       'status': 'GO_FOR_DECLARED_REPRESENTATIVE_APPEARANCE_ONLY', 'approval_bound_to_exact_hashes': True,
                       'verification': {'views_visually_reviewed': 9, 'image_pixels': [1000, 780], 'samples': 64,
                           'denoising': False, 'triangle_count': 20946, 'scene_stl_ordered_triangle_coordinates_exact': True,
                           'public_png_nontext_chunks_idat_and_rgba_exact_to_reviewed_originals': True,
                           'image_identity_is_not_general_privacy_clearance': True}}
        source = {'schema': 'wfu-source-appearance-binding-v1', 'version': 'v13', 'stl_sha256': binding.STL,
                  'views': {name: {} for name in binding.VIEWS}}
        case('accept_actual_wfu_source_schema', True, lambda: binding.source_schema(certificate, source))
        case('reject_inherited_aeust_go_schema', False, lambda: binding.source_schema({'decision': 'SOURCE-APPEARANCE-GO', 'revision': 'v13'}, source))
        case('reject_manufacturing_go_substitution', False, lambda: binding.source_schema(dict(certificate, status='MANUFACTURING_GO'), source))
        case('reject_missing_view', False, lambda: binding.source_schema(certificate, dict(source, views={k: v for k, v in source['views'].items() if k != 'front'})))
        case('reject_extra_view', False, lambda: binding.source_schema(certificate, dict(source, views=dict(source['views'], extra={}))))
        case('reject_source_wrong_stl', False, lambda: binding.source_schema(certificate, dict(source, stl_sha256='0' * 64)))
        changed = copy.deepcopy(certificate)
        changed['verification']['image_identity_is_not_general_privacy_clearance'] = False
        case('reject_privacy_scope_promotion', False, lambda: binding.source_schema(changed, source))
        audit = {'passed': True, 'strict_passed': True, 'inspect_only': False,
                 'checks': {k: True for k in binding.REPLAY_CHECKS},
                 'original_face_count': 20946, 'saved_world_face_count': 20946,
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
        case('reject_scene_triangle_count_substitution', False, lambda: binding.replay_structure(dict(audit, saved_world_face_count=20945)))
        source_file = root / 'source_identity.py'
        source_file.write_bytes(b"value = 'new'\n")
        original_source = source_file.read_bytes()
        source_digest = hashlib.sha256(original_source).hexdigest()
        case('accept_unchanged_executed_source_bytes', True,
             lambda: binding.require_source_unchanged(source_file, original_source))
        source_file.write_bytes(b"value = 'old'\n")
        case('reject_same_size_source_change_after_snapshot', False,
             lambda: binding.require_source_unchanged(source_file, original_source))
        case('reject_source_not_matching_frozen_selection_sha', False,
             lambda: binding.load_exact_source(source_file, source_digest))
        # Both timestamp/size cache keys match, so ordinary import sees old code.
        timestamp = 1700000000
        os.utime(source_file, (timestamp, timestamp))
        py_compile.compile(str(source_file), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        source_file.write_bytes(original_source)
        os.utime(source_file, (timestamp, timestamp))
        def stale_cache_control():
            spec = importlib.util.spec_from_file_location('demonstrate_stale_fixture', source_file)
            stale = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(stale)
            binding.require(stale.value == 'old', 'Stale-pyc fixture did not reproduce stale import')
            exact_source, used_bytes = binding.load_exact_source(source_file, source_digest)
            binding.require(exact_source.value == 'new' and used_bytes == original_source,
                            'Source-only loader used stale bytecode')
        case('reject_stale_pyc_same_mtime_same_size_substitution', True, stale_cache_control)
        def mid_execution_change_control():
            module, used_bytes = binding.load_exact_source(source_file, source_digest)
            binding.require(module.value == 'new', 'Wrong exact source executed')
            source_file.write_bytes(b"value = 'old'\n")
            binding.require_source_unchanged(source_file, used_bytes)
        case('reject_loaded_source_changed_before_result', False, mid_execution_change_control)
    binding.require_source_unchanged(checker_path, checker_bytes)
    result = {'passed': True, 'checker_sha256': binding.sha(binding.__file__), 'test_source_sha256': binding.sha(__file__),
              'optimization_level': sys.flags.optimize, 'cases': results, 'case_count': len(results),
              'scope': 'Small unit-level acceptance and negative controls only. No full science, PNG replay or Blender execution. Full candidate binding still requires completed independent run.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'passed': True, 'case_count': len(results), 'optimization_level': sys.flags.optimize}))


if __name__ == '__main__':
    main()
