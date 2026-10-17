"""Run lattice-bound parser controls and independent coordinate proof serially.
Caller owns the shared QA lock and must apply one-CPU affinity. No geometry or
rendering is run. All outputs must be new; prior failure evidence stays intact.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys

PINS = {'artifact_structure.py': '0c0830d6929697522cbbc9b692a66649aa6fb9cc7aaedc9a60fc193638dd3a7b', 'test_artifact_structure.py': '30d9b4c44c31a28d6240f231cd6ebcfa295352ac94ea8e587b31182e29cb3c05', 'run_structure_parser_controls.py': '624f87c600f0572a2d8328181bebdc84bcdbdf94dea16b9db0c42ebdf78b56d6', 'review_artifact_structure.py': '18911a8a647d6cd8b4c56f4b46f7e788ab2caf0bf9f590c2470e1396cb224b1c', 'prove_stl_coordinate_lattice.py': 'c19aa7a2f861ce47525388e86fe454aa9280c75586eca1f09b733973b0c0de06'}
HERE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stl', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(len(os.sched_getaffinity(0)) == 1, 'One CPU required')
    require(args.out.parent.is_dir() and not args.out.exists() and not args.out.is_symlink(), 'Fresh output required')
    require(all(sha(HERE/name) == value for name, value in PINS.items()), 'Prepared source identity differs')
    require(not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('*.pyo'))
            and not list(HERE.rglob('__pycache__')), 'Local bytecode cache is forbidden')
    own_sha = sha(__file__)
    args.out.mkdir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    env.pop('PYTHONOPTIMIZE', None)
    records = []
    proofs = []
    ledgers = []
    for mode, level in [('normal', 0), ('optimized', 1)]:
        prefix = [sys.executable, '-B', *(['-O'] if level else [])]
        control_out = args.out / ('parser-' + mode)
        proof_out = args.out / ('coordinate-proof-' + mode + '.json')
        stages = [('parser-' + mode, prefix + [str(HERE/'run_structure_parser_controls.py'), '--out', str(control_out)], control_out/'results.json'),
                  ('coordinate-proof-' + mode, prefix + [str(HERE/'prove_stl_coordinate_lattice.py'), '--stl', str(args.stl.absolute()), '--out', str(proof_out)], proof_out)]
        for name, command, report_path in stages:
            stdout = args.out/(name + '.stdout.log')
            stderr = args.out/(name + '.stderr.log')
            with stdout.open('xb') as out, stderr.open('xb') as err:
                code = subprocess.run(command, stdout=out, stderr=err, env=env).returncode
            row = {'stage': name, 'command': command, 'returncode': code,
                   'stdout_sha256': sha(stdout), 'stderr_sha256': sha(stderr)}
            records.append(row)
            (args.out/'executions.json').write_text(json.dumps(records, indent=2) + '\n')
            require(code == 0 and report_path.is_file(), 'Child failed: ' + name)
            report = json.loads(report_path.read_text())
            require(report['passed'] is True and type(report['optimization_level']) is int
                    and report['optimization_level'] == level
                    and report['cpu_affinity'] == sorted(os.sched_getaffinity(0)), 'Wrong actual child outcome/mode/CPU')
            row.update(report=str(report_path.relative_to(args.out)), report_sha256=sha(report_path))
            if name.startswith('parser-'):
                require(report['test_count'] == 13 and report['subtest_count'] == 79
                        and report['all_sources_unchanged'] is True
                        and report['helper_sha256'] == PINS['artifact_structure.py']
                        and report['test_source_sha256'] == PINS['test_artifact_structure.py']
                        and all(x['passed'] is True for x in report['cases']), 'Incomplete parser controls')
                ledgers.append(report['cases'])
            else:
                require(report['original_coordinate_values_checked'] == 188514
                        and report['coordinate_denominator_lcm'] == '72057594037927936'
                        and report['maximum_denominator_power'] == 56
                        and report['exact_rational_round_trips'] == report['binary32_byte_round_trips'] == 188514
                        and report['source_sha256'] == PINS['prove_stl_coordinate_lattice.py'], 'Incomplete independent coordinate proof')
                normalized = dict(report)
                del normalized['optimization_level']
                proofs.append(normalized)
    require(len(records) == 4 and ledgers[0] == ledgers[1] and proofs[0] == proofs[1], 'Normal/optimized evidence differs')
    require(sha(__file__) == own_sha and all(sha(HERE/name) == value for name, value in PINS.items()), 'Source changed during controls')
    require(not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('*.pyo'))
            and not list(HERE.rglob('__pycache__')), 'Local bytecode cache appeared')
    (args.out/'executions.json').write_text(json.dumps(records, indent=2) + '\n')
    result = {'passed': True, 'completed': True, 'both_modes_passed': True,
              'each_mode_test_methods': 13, 'original_subtests_retained': 69,
              'additional_lattice_subtests': 10, 'each_mode_subtests': 79,
              'independent_original_coordinate_proof_both_modes': True,
              'source_sha256': PINS, 'orchestrator_sha256': own_sha,
              'all_sources_unchanged': True, 'executions': records,
              'model_go': False, 'geometry_predicates_or_render_rerun': False,
              'scope': 'Synthetic parser controls plus exact original coordinate-value lattice proof only. Fresh full-artifact reviews remain required; original strict=False is unchanged.'}
    with (args.out/'controls-summary.json').open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'passed': True, 'stages': len(records), 'subtests_per_mode': 79}))


if __name__ == '__main__':
    main()
