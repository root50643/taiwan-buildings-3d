"""Bind completed controlled reviewers into one bounded-digital-result receipt.
No geometric predicate, original producer result, or privacy rule is changed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os

STL = '66f0516f35df2df734b6d8a4d37a8f93b73e5685fd47b0b7d74ff15c88ccf978'
SCENE = '24405788a4c5bf2e88a2402089f5d7fc9bc6b360afa97cc316760bdf3e668a1b'


def require(v, message):
    if not v:
        raise RuntimeError(message)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--author', type=Path, required=True)
    ap.add_argument('--independent', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    require(sorted(os.sched_getaffinity(0)) == [0], 'Caller must hold shared lock and use CPU0')
    require(not a.out.exists(), 'Fresh receipt required')
    roots = {'author': a.author, 'independent': a.independent}
    tracked = {}

    def read(logical):
        owner, relative = logical.split('/', 1)
        path = roots[owner] / relative
        raw = path.read_bytes()
        tracked[logical] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        return json.loads(raw)

    for mode, level in [('normal', 0), ('optimized', 1)]:
        review = read('independent/postflight-v10/' + mode + '-complete/review-result.json')
        require(review['passed'] is True and review['bounded_verification_passed'] is True
                and review['optimization_level'] == level and review['stl_sha256'] == STL
                and review['original_numerical_strict_passed'] is False
                and review['all_read_evidence_unchanged'] is True, 'Complete candidate review differs')
        require(len(review['images']) == 9 and all(v['decoded_rgba_bytes_identical'] is True
                for v in review['images'].values()), 'Nine-image proof incomplete')
        for owner in ('author', 'independent'):
            r = read('independent/postflight-v10/' + mode + '-' + owner + '-structure/artifact-structure-review.json')
            require(r['passed'] is True and r['optimization_level'] == level
                    and r['all_inputs_unchanged'] is True, 'All-record review differs')
        r = read('independent/result-binding-v10/binding-' + mode + '.json')
        require(r['passed'] is True and r['stl_sha256'] == STL
                and r['checker_optimization_level'] == level
                and r['full_author_inventory_members_verified'] == 2363
                and r['frozen_runner_inputs_verified'] == 54
                and len(r['science_comparisons']) == 14
                and all(x['all_four_scientifically_identical'] is True for x in r['science_comparisons'])
                and len(r['full_csv_four_source_copy_map']) == 4
                and all(x['data_rows'] == 51760 and x['all_decoded_bytes_read'] is True
                        for x in r['full_csv_four_source_copy_map']), 'Four-source binding incomplete')
        require(r['original_strict_results']['author_full_passed'] is False
                and r['original_strict_results']['author_full_strict_passed'] is False
                and r['original_strict_results']['author_full_producer_returncode'] == 1
                and r['original_strict_results']['independent_strict_passed'] is False,
                'Original numerical result changed')
    execution = read('independent/run-v10/independent-execution-summary.json')
    require(execution['completed'] is True and execution['strict_passed'] is False
            and execution['all_frozen_inputs_and_tools_unchanged'] is True
            and len(execution['executions']) == 14, 'Execution ledger incomplete')
    stage_exits = {r['name']: r['returncode'] for r in execution['executions']}
    require(all(v == (1 if k.endswith('-standard') else 0) for k, v in stage_exits.items()),
            'Unexpected original execution exit')
    image = read('independent/run-v10/saved-blend-rerenders/blend-rerender-audit.json')
    require(image['passed'] is True and image['inspect_only'] is False
            and image['original_blend_sha256'] == SCENE and len(image['checks']) == 38
            and all(v is True for v in image['checks'].values()), 'Saved scene replay incomplete')
    certificate = read('author/qa/source-review/SOURCE-APPEARANCE-CERTIFICATE-v10.public.json')
    require(certificate['decision'] == 'GO_WITH_REPRESENTATIVE_MODEL_LIMITS'
            and certificate['model']['stl_sha256'] == STL
            and certificate['model']['scene_sha256'] == SCENE, 'Source appearance identity differs')
    for logical, row in tracked.items():
        owner, relative = logical.split('/', 1)
        data = (roots[owner] / relative).read_bytes()
        require(len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'],
                'Evidence changed during receipt generation')
    result = {
        'schema': 'cgust-bounded-digital-science-review-v10-v1',
        'status': 'BOUNDED_DIGITAL_VERIFICATION_PASSED',
        'bounded_digital_verification_passed': True,
        'original_numerical_strict_passed': False,
        'stl_sha256': STL, 'scene_sha256': SCENE,
        'source_revision': 'v10', 'author_geometry_evidence_revision': 'v9',
        'geometry': {'original_triangles': 5176, 'connected_surface_shells': 1,
            'extents_mm': [146, 222, 53], 'sampled_layers_per_mode': 795,
            'original_polygons_per_mode': 3950, 'failed_layers': 0, 'failed_polygons': 0,
            'dense_original_rays_per_mode': 51760, 'short_numerical_first_chords': 0,
            'minimum_sampled_numerical_first_chord_mm': 1.0022034306271335,
            'original_numerical_flags_per_mode': 10, 'same_run_exact_flags_classified_per_mode': 10,
            'exact_contact_pairs_per_mode': 37510, 'bad_exact_contact_pairs': 0,
            'exact_closed_aabb_candidate_pairs_per_mode': 59258,
            'coordinate_lattice_minimal_denominator': 8388608},
        'source_and_render': {'source_stl_bitwise_reproduced': True,
            'complete_saved_scene_state_reproduced': True,
            'unique_independent_saved_blend_nine_view_replay_completed': True,
            'cycles_cpu_threads': 1, 'samples_per_image': 64,
            'resolution': [1000, 780], 'decoded_rgba_bytes_identical_for_all_nine': True,
            'png_cleanup_metadata_only': True, 'source_appearance_scope': certificate['decision']},
        'four_source_science': {'author_modes': ['normal', 'optimized'],
            'independent_modes': ['normal', 'optimized'], 'comparison_groups': 14,
            'all_four_complete_csv_payloads_byte_identical': True,
            'all_four_csv_streams_completely_read': True, 'canonical_csv_payloads_required': 1},
        'original_execution_returncodes': stage_exits,
        'evidence': tracked,
        'receipt_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': 'Complete controlled numerical gates, per-record exact supplemental diagnosis, source/scene reproduction, and nine-image identity for this exact representative STL and scene. Finite sections and rays do not prove a global minimum wall thickness, physical printability, exact as-built scale, or current building condition. Numerical strict=false and original exit1 remain unchanged. Full public-package privacy, recovery, publication authorization and private official checkpoint are separate gates.',
        'publication_go': False,
    }
    with a.out.open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'evidence_files': len(tracked),
                      'original_numerical_strict_passed': False}))


if __name__ == '__main__':
    main()
