"""Read-only structure/math review of explicitly bound CGUST candidate evidence.

Author full and exact directories may be separate. This entry does not perform
producer-exit, independent-freeze, source/render, or overall model acceptance.
Original numerical strict=False remains unchanged.
"""
from pathlib import Path
import argparse, gzip, hashlib, json, os, sys, types

HELPER = '3ec28d504422014bf847eb25ec2f65aab34715e43ce8ebf3e3300752bc8db6a7'
EXACT_CORE = '0116a42a06e53723a71bf1a16e6864e71ff3f2b76ca5dbb6aa455fb5bd719d46'
DIAGNOSTIC = 'f3b9cb43c9bfa35915d8661a122f5dcbffb947e3cdc7492af4d43c23693309d4'


def require(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def regular(path):
    path = Path(path).absolute()
    require('..' not in path.parts and path.is_file()
            and not any(p.is_symlink() for p in (path, *path.parents)),
            'Nonregular or symlink evidence path')
    return path


def artifact(root, name):
    require(type(name) is str and name not in ('', '.', '..')
            and Path(name).name == name and not Path(name).is_absolute(),
            'Artifact must be a safe basename')
    return regular(root / name)


ROOT_KEYS = ('stl', 'qa-root', 'full-root', 'exact-normal', 'exact-optimized')


def logical_path_bindings(paths):
    require(set(paths) == set(ROOT_KEYS), 'Logical root set differs')
    require(all(isinstance(value, Path) and value.is_absolute() and '..' not in value.parts
                for value in paths.values()), 'Logical roots must be absolute and safe')
    require(len(set(paths.values())) == len(ROOT_KEYS), 'Logical roots must be distinct')
    return {key: key for key in ROOT_KEYS}


def logical_key(path, paths):
    logical_path_bindings(paths)
    path = Path(path)
    require(path.is_absolute() and '..' not in path.parts, 'Logical evidence path must be absolute and safe')
    if path == paths['stl']:
        return 'stl'
    matches = [(len(root.parts), key, path.relative_to(root))
               for key, root in paths.items() if key != 'stl' and path.is_relative_to(root)]
    require(bool(matches), 'Evidence path outside explicit CLI roots')
    depth = max(item[0] for item in matches)
    selected = [item for item in matches if item[0] == depth]
    require(len(selected) == 1, 'Ambiguous logical evidence root')
    _, key, relative = selected[0]
    return key if relative == Path('.') else key + '/' + relative.as_posix()


def report_for_output(summary, paths, tracked):
    # Only path metadata changes; every other report value and every inventory row is retained.
    inventory = {}
    for absolute, row in tracked.items():
        key = logical_key(absolute, paths)
        require(key not in inventory, 'Logical inventory key collision')
        inventory[key] = row
    return {**summary, 'input_path_bindings': logical_path_bindings(paths),
            'evidence_inventory': inventory}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for flag in ('stl', 'qa-root', 'full-root', 'exact-normal', 'exact-optimized', 'out'):
        ap.add_argument('--' + flag, type=Path, required=True)
    args = ap.parse_args()
    require(len(os.sched_getaffinity(0)) == 1, 'Caller must hold shared QA lock and use one CPU')
    require(not args.out.exists() and not args.out.is_symlink(), 'Fresh output required')
    args.out.mkdir(parents=True)
    paths = {key: Path(getattr(args, key.replace('-', '_'))).absolute()
             for key in ('stl', 'qa-root', 'full-root', 'exact-normal', 'exact-optimized')}
    for path in paths.values():
        require('..' not in path.parts and not any(p.is_symlink() for p in (path, *path.parents)),
                'Input root has a symlink or unsafe component')
    require(all(paths[key].is_dir() for key in ('qa-root', 'full-root', 'exact-normal', 'exact-optimized')),
            'Input evidence directory missing')
    require(paths['exact-normal'] != paths['exact-optimized'], 'Exact mode roots must differ')
    helper = Path(__file__).absolute().with_name('artifact_structure.py')
    helper_bytes = regular(helper).read_bytes()
    require(hashlib.sha256(helper_bytes).hexdigest() == HELPER, 'Controlled sibling helper differs')
    module = types.ModuleType('structure')
    module.__file__ = str(helper)
    exec(compile(helper_bytes, str(helper), 'exec'), module.__dict__)
    tracked = {}
    summary = {'passed': False, 'optimization_level': sys.flags.optimize,
               'cpu_affinity': sorted(os.sched_getaffinity(0)), 'helper_sha256': HELPER,
               'reviewer_sha256': sha(__file__),
               'input_path_bindings': logical_path_bindings(paths),
               'postflight_overlay_inputs': {'artifact_structure.py': {'bytes': len(helper_bytes), 'sha256': HELPER}},
               'producer_exit_review_performed': False, 'independent_freeze_review_performed': False,
               'source_render_review_performed': False, 'full_csv_decoded_by_this_entry': False,
               'original_numerical_strict_passed': False, 'model_go': False,
               'scope': 'Additional read-only all-record structural/math consistency review. Explicit full/exact inputs and original hashes are bound; public path metadata uses stable logical roots and the actual CLI is retained in private capture. Complete producer-exit, raw-CSV, source/render and independent-freeze reviews remain separate requirements; no model acceptance.'}

    def track(path):
        path = regular(path)
        require(path == paths['stl'] or any(path.is_relative_to(root) for key, root in paths.items() if key != 'stl'),
                'Evidence path outside explicit CLI roots')
        key = str(path)
        row = {'bytes': path.stat().st_size, 'sha256': sha(path)}
        require(key not in tracked or tracked[key] == row, 'Evidence changed during read')
        tracked[key] = row
        return row['sha256']

    def read(path, gz=False):
        expected = track(path)
        raw = Path(path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected, 'Read changed')
        return json.loads(gzip.decompress(raw) if gz else raw)

    try:
        require(track(paths['stl']) == module.STL_SHA256, 'Candidate STL identity differs')
        sources = {'exact_core_source': paths['qa-root'] / 'tools/exact_ray_diagnosis.py',
                   'diagnostic_source': paths['qa-root'] / 'tools/diagnose_recorded_cpp_rays.py'}
        require(track(sources['exact_core_source']) == EXACT_CORE
                and track(sources['diagnostic_source']) == DIAGNOSTIC, 'Original exact tools changed')
        results = {}
        for mode, level in [('normal', 0), ('optimized', 1)]:
            base = paths['full-root'] / mode
            std = base / 'standard'
            section_path = std / 'sections/section-check.json'
            section = read(section_path)
            details_path = artifact(std / 'sections', section['detail_file'])
            failures_path = artifact(std / 'sections', section['failure_file'])
            require(track(details_path) == section['detail_sha256']
                    and track(failures_path) == section['failure_sha256'], 'Section detail hash differs')
            sections = module.validate_sections(section, read(details_path, True), read(failures_path, True))
            dense_path = std / 'dense/dense-check.json'
            dense = read(dense_path)
            require(dense['stl_sha256'] == module.STL_SHA256 and dense['strict_passed'] is False
                    and type(dense['under_0p8mm_count']) is int and dense['under_0p8mm_count'] == 0
                    and type(dense['flagged_sample_count']) is int and dense['flagged_sample_count'] > 0,
                    'Exact review requires original zero-short, positive-flag, strict=False case')
            flags_path = artifact(std / 'dense', dense['flagged_samples_file'])
            require(track(flags_path) == dense['flagged_samples_sha256'], 'Flags hash differs')
            flags = read(flags_path, True)
            raw_path = std / 'raw/raw-mesh-check.json'
            raw = read(raw_path)
            inter_path = base / 'intersections.json'
            inter = read(inter_path)
            require(raw['passed'] is True and raw['strict_passed'] is True
                    and raw['stl_sha256'] == module.STL_SHA256 and raw['triangles'] == module.FACES,
                    'Original raw prerequisite differs')
            exact_root = paths['exact-' + mode]
            exact = read(exact_root / 'exact-recorded-ray-summary.json')
            required = ('completed', 'all_selected_rays_exactly_classified', 'all_selected_first_chords_ge_0p8mm',
                        'all_original_inputs_and_sources_unchanged', 'original_raw_and_exact_intersection_prerequisites_passed',
                        'full_original_csv_exact_face_sample_coverage', 'all_flagged_samples_selected',
                        'all_selected_descriptors_match_original_full_csv')
            require(all(exact.get(key) is True for key in required) and 'error' not in exact
                    and 'error_type' not in exact and type(exact['optimization_level']) is int
                    and exact['optimization_level'] == level and exact['original_numerical_strict_passed'] is False,
                    'Exact summary incomplete or mode/strict semantics differ')
            csv_path = artifact(std / 'dense', dense['csv_file'])
            require(track(csv_path) == dense['csv_compressed_sha256'], 'Original compressed CSV binding differs')
            bindings = {'stl': paths['stl'], 'flags': flags_path, 'dense_report': dense_path,
                        'raw_report': raw_path, 'intersections_report': inter_path, 'original_csv': csv_path, **sources}
            require(set(exact['input_and_tool_sha256']) == set(bindings)
                    and all(track(path) == exact['input_and_tool_sha256'][key] for key, path in bindings.items()),
                    'Exact evidence is not bound to these full-run inputs and tools')
            require(all(type(exact[key]) is int for key in ('total_flagged_samples', 'selected_samples', 'full_original_csv_rows_verified'))
                    and exact['total_flagged_samples'] == exact['selected_samples'] == len(flags) == dense['flagged_sample_count']
                    and exact['full_original_csv_rows_verified'] == dense['samples'] == 10 * module.FACES,
                    'Original exact flag/CSV coverage count differs')
            exact_path = artifact(exact_root, exact['detail_file'])
            require(track(exact_path) == exact['detail_sha256'], 'Exact rows hash differs')
            with gzip.open(exact_path, 'rt') as stream:
                rows = [json.loads(line) for line in stream]
            exact_rows = module.validate_exact_rows(rows, flags)
            contacts = artifact(base, inter['all_actual_intersections']['path'])
            require(track(contacts) == inter['all_actual_intersections']['sha256'], 'Contact rows hash differs')
            with gzip.open(contacts, 'rt') as stream:
                contact = module.validate_intersection_contacts(inter, (json.loads(line) for line in stream))
            results[mode] = {'sections': sections, 'exact_recorded_rays': exact_rows, 'exact_contacts': contact}
        require(results['normal'] == results['optimized'], 'Structural/math results differ between modes')
        require(sha(__file__) == summary['reviewer_sha256'] and sha(helper) == HELPER
                and helper.stat().st_size == len(helper_bytes), 'Reviewer/helper changed')
        require(all(regular(Path(key)).stat().st_size == row['bytes'] and sha(Path(key)) == row['sha256']
                    for key, row in tracked.items()), 'Input changed during review')
        summary.update(passed=True, all_inputs_unchanged=True, modes=results)
    except Exception as error:
        summary.update(error_type=type(error).__name__, error=str(error))
    summary = report_for_output(summary, paths, tracked)
    with (args.out / 'artifact-structure-review.json').open('x') as stream:
        json.dump(summary, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'passed': summary['passed'], 'optimization_level': sys.flags.optimize,
                      'error': summary.get('error')}))
    return 0 if summary['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
