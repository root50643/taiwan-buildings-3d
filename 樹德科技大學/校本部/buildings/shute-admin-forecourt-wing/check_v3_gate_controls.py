"""Negative controls for the new v3 aggregation gate, using temporary copies only."""
from pathlib import Path
import gzip, hashlib, json, shutil, subprocess, sys, tempfile
R = Path(__file__).resolve().parent
cases = [
    ('unclassified_root', 'drum-relief-roots.json', lambda q: q.update(unclassified=[{'injected_control': True}])),
    ('strict_failure_erased', 'dense-short-chords.json', lambda q: q.update(passed=True)),
    ('wrong_root_winding', 'drum-root-interval-details.json.gz', lambda q: q['controls'][0].update(winding=0, passed=False)),
    ('source_changed', 'render_preview.py', None),
    ('stl_changed', 'model.stl', None),
]
results = []
for name, filename, mutate in cases:
    with tempfile.TemporaryDirectory(prefix='shute-v3-gate-control-') as td:
        d = Path(td) / 'package'
        shutil.copytree(R, d, ignore=shutil.ignore_patterns('__pycache__', '*.blend1'))
        p = d / filename
        if mutate is not None:
            data = json.loads(gzip.decompress(p.read_bytes()).decode() if filename.endswith('.gz') else p.read_text())
            mutate(data)
            encoded = json.dumps(data).encode()
            p.write_bytes(gzip.compress(encoded, mtime=0) if filename.endswith('.gz') else encoded)
        elif name == 'source_changed':
            p.write_text(p.read_text() + '\n# Deliberate negative control.\n')
        else:
            data = bytearray(p.read_bytes())
            data[100] ^= 1
            p.write_bytes(data)
        run = subprocess.run([sys.executable, str(d / 'validate_model.py')], capture_output=True, text=True)
        report = json.loads((d / 'validation.json').read_text())
        rejected = run.returncode != 0 and report['passed'] is False and any(v is False for v in report['checks'].values())
        results.append({'case': name, 'exit_code': run.returncode, 'rejected': rejected, 'failed_checks': [k for k, v in report['checks'].items() if v is False]})
        assert rejected, name
out = {'passed': all(q['rejected'] for q in results), 'stl_sha256': hashlib.sha256((R / 'model.stl').read_bytes()).hexdigest(), 'validation_script_sha256': hashlib.sha256((R / 'validate_model.py').read_bytes()).hexdigest(), 'cases': results, 'method': 'Temporary copies only. Deliberately unclassified root, hidden strict failure, wrong winding, changed renderer and changed STL must each produce a false evidence gate and nonzero exit.'}
(R / 'gate-negative-controls.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
assert out['passed']
