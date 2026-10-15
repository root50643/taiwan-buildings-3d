"""v3 replacement runner. Replays numerical checks; strict diagnostic must exit 1."""
from pathlib import Path
import hashlib, json, os, subprocess, sys
R = Path(__file__).resolve().parent
steps = [
    ('check_raw_mesh.py', 0), ('check_component_detail.py', 0),
    ('check_negative_controls.py', 0), ('check_dense_surface.py', 1),
    ('check_drum_relief_roots.py', 0), ('check_drum_root_intervals.py', 0),
    ('check_full_boundary_intervals.py', 0), ('check_flag_boundaries.py', 0),
    ('check_reproducibility.py', 0), ('validate_model.py', 0),
    ('check_v3_gate_controls.py', 0), ('check_documentation.py', 0),
]
env = {**os.environ, 'MALLOC_ARENA_MAX': '2', 'LP_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'}
rows = []
for name, expected in steps:
    code = subprocess.run([sys.executable, str(R / name)], cwd=R, env=env).returncode
    rows.append({'script': name, 'script_sha256': hashlib.sha256((R / name).read_bytes()).hexdigest(), 'expected_exit': expected, 'actual_exit': code, 'passed': code == expected})
    result = {'revision': 'recovered-release-v3', 'complete': len(rows) == len(steps), 'passed': len(rows) == len(steps) and all(q['passed'] for q in rows), 'stl_sha256': hashlib.sha256((R / 'model.stl').read_bytes()).hexdigest(), 'steps': rows}
    (R / 'checks-run.json').write_text(json.dumps(result, indent=2) + '\n')
    assert code == expected, (name, code, expected)
assert result['passed']
