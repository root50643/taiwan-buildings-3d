"""Ten original-face-normal rays per raw STL face; any short ray fails strict QA."""
from pathlib import Path
import argparse
import csv
import gzip
import hashlib
import math
import shutil
import subprocess
import tempfile
import numpy as np
from qa_common import (require, load_stl, write_json, write_gzip_json, sha256,
                       error_report, checker_inventory)

WEIGHTS = np.array([[1/3]*3, [.98,.01,.01], [.01,.98,.01], [.01,.01,.98],
                    [.495,.495,.01], [.01,.495,.495], [.495,.01,.495],
                    [.49,.49,.02], [.49,.02,.49], [.02,.49,.49]])
MINIMUM_CHORD = 0.8
ORIGIN_OFFSET = 1e-5


def inspect(stl, out):
    raw, triangles, stored_normals, _ = load_stl(stl)
    crosses = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    norms = np.linalg.norm(crosses, axis=1)
    require((norms > 0).all(), 'Degenerate original triangles cannot define normal rays')
    normals = crosses / norms[:, None]
    normal_agreement = bool(np.all(np.abs(stored_normals - normals) <= 1e-5))
    count, minimum = 0, math.inf
    seen = np.zeros((len(triangles), len(WEIGHTS)), dtype=np.uint8)
    flags, short = [], []
    source = Path(__file__).resolve().parent / 'dense_original.cpp'
    compiler = shutil.which('g++')
    require(compiler is not None, 'Existing g++ compiler not found; nothing will be installed')
    with tempfile.TemporaryDirectory(prefix='original-stl-dense-') as directory:
        temporary = Path(directory)
        np.asarray(triangles, dtype='<f8').tofile(temporary / 'triangles.bin')
        compile_command = [compiler, '-O3', '-std=c++17', '-Wall', '-Wextra', str(source), '-o', str(temporary / 'dense')]
        compiled = subprocess.run(compile_command, capture_output=True, text=True)
        (out / 'dense-compiler.log').write_text(compiled.stdout + compiled.stderr)
        require(compiled.returncode == 0, 'Original-ray C++ compilation failed; see dense-compiler.log')
        executable_hash = sha256(temporary / 'dense')
        executed = subprocess.run([str(temporary / 'dense'), str(temporary / 'triangles.bin'), str(temporary / 'all.csv')],
                                  capture_output=True, text=True)
        (out / 'dense-run.log').write_text(executed.stdout + executed.stderr)
        require(executed.returncode == 0, 'Original-ray C++ calculation failed; see dense-run.log')
        with (temporary / 'all.csv').open(newline='') as handle:
            for row in csv.DictReader(handle):
                count += 1
                face, sample = int(row['face']), int(row['sample'])
                require(0 <= face < len(triangles) and 0 <= sample < len(WEIGHTS), 'Out-of-range original face/sample in dense CSV')
                reasons = []
                if seen[face, sample]:
                    reasons.append('duplicate_original_face_sample')
                seen[face, sample] = min(int(seen[face, sample]) + 1, 255)
                chord, entry, finish = (float(row[key]) for key in ('first_solid', 'entry', 'exit'))
                point = np.array([float(row[key]) for key in ('x','y','z')])
                direction_normal = np.array([float(row[key]) for key in ('nx','ny','nz')])
                expected_point = WEIGHTS[sample] @ triangles[face]
                if not np.allclose(point, expected_point, atol=1e-9, rtol=1e-12):
                    reasons.append('sample_not_on_original_barycentric_point')
                if not np.allclose(direction_normal, normals[face], atol=1e-10, rtol=1e-12):
                    reasons.append('ray_not_original_face_normal')
                if not math.isfinite(entry) or abs(entry - ORIGIN_OFFSET) > 1e-8:
                    reasons.append('entry_not_at_original_face_offset')
                if not math.isfinite(chord) or not math.isfinite(finish) or chord <= 0:
                    reasons.append('missing_or_nonpositive_first_original_interval')
                elif abs((finish - entry) - chord) > 1e-9:
                    reasons.append('inconsistent_original_interval')
                else:
                    minimum = min(minimum, chord)
                if int(row['source_face_in_entry']) != 1:
                    reasons.append('source_original_face_missing_from_entry')
                if int(row['alternating_crossings']) != 1:
                    reasons.append('original_crossings_not_alternating_enter_exit')
                if int(row['ambiguous_events']) != 0:
                    reasons.append('near_coincident_or_opposing_original_crossings')
                parity = [int(row[key]) for key in ('inside_control','outside_control','mid_control','after_exit_control')]
                if parity != [1,0,1,0]:
                    reasons.append('original_triangle_parity_controls_failed')
                if reasons:
                    flags.append({'original_face_index': face, 'sample_index': sample,
                                  'reasons': reasons, 'original_cpp_row': row})
                if math.isfinite(chord) and chord < MINIMUM_CHORD:
                    short.append({'original_face_index': face, 'sample_index': sample,
                                  'surface_point_mm': point.tolist(),
                                  'original_geometric_outward_normal': direction_normal.tolist(),
                                  'original_stored_normal': stored_normals[face].tolist(),
                                  'first_solid_chord_mm': chord,
                                  'first_original_interval_mm': [entry, finish] if math.isfinite(entry) and math.isfinite(finish) else None,
                                  'original_cpp_row': row})
        csv_hash = sha256(temporary / 'all.csv')
        csv_destination = out / 'dense-original.csv.gz'
        with (temporary / 'all.csv').open('rb') as original, csv_destination.open('wb') as target:
            with gzip.GzipFile(filename='', fileobj=target, mode='wb', mtime=0) as compressed:
                shutil.copyfileobj(original, compressed)
        with gzip.open(csv_destination, 'rb') as handle:
            require(hashlib.file_digest(handle, 'sha256').hexdigest() == csv_hash,
                    'Lossless compressed dense CSV failed decompression hash verification')
    write_gzip_json(out / 'dense-short-samples.json.gz', short)
    write_gzip_json(out / 'dense-flagged-samples.json.gz', flags)
    checks = {'every_original_face_exactly_ten_samples': bool((seen == 1).all()) and count == len(triangles) * 10,
              'stored_normals_agree_with_original_directed_faces': normal_agreement,
              'all_original_ray_intervals_and_controls_valid': not flags,
              'all_first_original_chords_ge_0p8mm': not short and math.isfinite(minimum) and minimum >= MINIMUM_CHORD}
    return {'passed': all(checks.values()), 'strict_passed': all(checks.values()), 'checks': checks,
            'stl_sha256': hashlib.sha256(raw).hexdigest(), 'original_triangles': len(triangles),
            'samples': count, 'samples_per_original_face': 10, 'barycentric_weights': WEIGHTS.tolist(),
            'minimum_first_chord_mm': minimum if math.isfinite(minimum) else None,
            'minimum_required_chord_mm': MINIMUM_CHORD, 'origin_outside_offset_mm': ORIGIN_OFFSET,
            'under_0p8mm_count': len(short), 'flagged_sample_count': len(flags),
            'csv_file': 'dense-original.csv.gz', 'csv_gzip_sha256': sha256(out / 'dense-original.csv.gz'),
            'uncompressed_csv_sha256': csv_hash,
            'short_chords_file': 'dense-short-samples.json.gz', 'short_chords_sha256': sha256(out / 'dense-short-samples.json.gz'),
            'flagged_samples_file': 'dense-flagged-samples.json.gz', 'flagged_samples_sha256': sha256(out / 'dense-flagged-samples.json.gz'),
            'cpp_source_sha256': sha256(source), 'compiled_executable_sha256': executable_hash,
            'checker_sources_sha256': checker_inventory(),
            'method': 'Every original binary triangle, unchanged face order, ten fixed barycentric samples, unit normal derived directly from its original coordinates and checked against saved normals. Long-double original-triangle Moller-Trumbore intersections through a BVH. CSV retains every raw intersection with original face ID and crossing direction, every clustered event, and all paired intervals. The first original solid interval is checked independently; no medians, means, nearest-thickness substitution, normal repair or waived short rays.',
            'limitations': 'Finite original-normal sampling and numerical intersection controls are not a global all-direction wall-thickness or self-intersection proof. Any short original ray makes strict_passed false; no automatic exception mechanism.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stl', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / 'dense-check.json'
    try:
        report = inspect(args.stl, args.out)
        write_json(path, report)
    except Exception as error:
        report = error_report(path, 'dense_surface', args.stl, error)
    print({'passed': report['passed'], 'report': str(path),
           'short_samples': report.get('under_0p8mm_count'), 'error': report.get('error')})
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
