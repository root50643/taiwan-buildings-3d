"""Run original-STL gates and synthetic controls, preserving all failed evidence."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
from qa_common import require, sha256, write_json, checker_inventory

ROOT = Path(__file__).resolve().parent


def inspect(stl, out, expected_longest):
    before = sha256(stl)
    source_inventory = checker_inventory()
    mode = ['-B'] + (['-O'] if sys.flags.optimize else [])
    jobs = [('raw', 'check_raw_mesh.py', 'raw-mesh-check.json'),
            ('sections', 'check_sections.py', 'section-check.json'),
            ('dense', 'check_dense_surface.py', 'dense-check.json'),
            ('controls', 'check_controls.py', 'control-check.json')]
    rows, reports = [], {}
    for name, script, report_name in jobs:
        destination = out / name
        command = [sys.executable, *mode, str(ROOT / script), '--out', str(destination)]
        if name != 'controls':
            command += ['--stl', str(stl)]
        if name == 'raw' and expected_longest is not None:
            command += ['--expected-longest-mm', str(expected_longest)]
        process = subprocess.run(command, capture_output=True, text=True)
        destination.mkdir(parents=True, exist_ok=True)
        (destination / 'stdout.txt').write_text(process.stdout)
        (destination / 'stderr.txt').write_text(process.stderr)
        report_path = destination / report_name
        report = json.loads(report_path.read_text()) if report_path.exists() else {}
        reports[name] = report
        rows.append({'gate': name, 'returncode': process.returncode,
                     'passed': process.returncode == 0 and report.get('passed') is True and report.get('strict_passed') is True,
                     'report_file': str(report_path.relative_to(out)),
                     'report_sha256': sha256(report_path) if report_path.exists() else None,
                     'failed_checks': [key for key, value in report.get('checks', {}).items() if value is False]})
        print(f'{name}: {rows[-1]["passed"]}; {report_path}', flush=True)
    raw, section, dense = (reports[name] for name in ('raw', 'sections', 'dense'))
    checks = {'all_gates_explicitly_pass': all(row['passed'] for row in rows),
              'all_gate_check_flags_true': all(report.get('checks') and all(value is True for value in report['checks'].values()) for report in reports.values()),
              'original_stl_unchanged': sha256(stl) == before,
              'all_geometry_reports_bound_to_current_stl': all(reports[name].get('stl_sha256') == before for name in ('raw','sections','dense')),
              'checker_sources_unchanged_during_run': checker_inventory() == source_inventory,
              'all_reports_bound_to_current_checkers': all(report.get('checker_sources_sha256') == source_inventory for report in reports.values()),
              'three_required_layer_offsets': section.get('offsets_from_z_min_mm') == [.031,.071,.137] and section.get('pitch_mm') == .2,
              'every_original_face_has_ten_rays': dense.get('samples') == 10 * raw.get('triangles', -1),
              'zero_short_or_flagged_dense_samples': dense.get('under_0p8mm_count') == 0 and dense.get('flagged_sample_count') == 0}
    evidence_pairs = [('sections','detail_file','detail_sha256'), ('sections','failure_file','failure_sha256'),
                      ('dense','csv_file','csv_gzip_sha256'), ('dense','short_chords_file','short_chords_sha256'),
                      ('dense','flagged_samples_file','flagged_samples_sha256')]
    evidence = []
    for name, file_key, hash_key in evidence_pairs:
        file_name = reports[name].get(file_key)
        path = out / name / file_name if isinstance(file_name, str) else None
        valid = path is not None and path.is_file() and sha256(path) == reports[name].get(hash_key)
        evidence.append({'gate': name, 'key': file_key, 'verified': valid})
    checks['all_full_detail_artifact_hashes_current'] = all(row['verified'] for row in evidence)
    if dense.get('csv_file') and (out / 'dense' / dense['csv_file']).is_file():
        with gzip.open(out / 'dense' / dense['csv_file'], 'rb') as handle:
            checks['dense_lossless_csv_hash_current'] = hashlib.file_digest(handle, 'sha256').hexdigest() == dense.get('uncompressed_csv_sha256')
    else:
        checks['dense_lossless_csv_hash_current'] = False
    return {'passed': all(checks.values()), 'strict_passed': all(checks.values()), 'checks': checks,
            'stl_sha256': before, 'expected_longest_mm': expected_longest,
            'gate_reports': rows, 'evidence_files': evidence,
            'checker_sources_sha256': source_inventory, 'optimized_python': bool(sys.flags.optimize),
            'limits': 'Raw mesh topology, finite XY layers and finite original-normal rays only. No geometry repair, waived short rays, architecture approval, render audit, global wall guarantee, or independent review claim.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stl', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--expected-longest-mm', type=float)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    try:
        report = inspect(args.stl.resolve(), args.out.resolve(), args.expected_longest_mm)
    except Exception as error:
        report = {'passed': False, 'strict_passed': False, 'checks': {'aggregate_completed': False},
                  'error_type': type(error).__name__, 'error': str(error),
                  'stl_sha256': sha256(args.stl) if args.stl.is_file() else None,
                  'checker_sources_sha256': checker_inventory()}
    write_json(args.out / 'qa-summary.json', report)
    print({'passed': report['passed'], 'report': str(args.out / 'qa-summary.json'), 'error': report.get('error')})
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
