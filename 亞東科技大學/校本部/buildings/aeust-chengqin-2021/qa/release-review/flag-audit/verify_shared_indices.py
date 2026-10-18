"""Separately confirm delivered shared index metadata against a fresh load."""
from pathlib import Path
import hashlib
import json
import os
import numpy as np
import trimesh

root = Path(__file__).resolve().parent
candidate = Path(os.environ['CHENGQIN_PACKAGE']).resolve()
stl = candidate / 'models/v1/model.stl'
mesh = trimesh.load_mesh(stl, process=True)
raw = trimesh.load_mesh(stl, process=False)
rows = []
for name in ('diagnosis.json', 'diagnosis-verified.json'):
    diagnosis = json.loads((candidate/'qa/flag-diagnosis'/name).read_text(encoding='utf-8'))
    for pair in diagnosis['pairs']:
        i, j = pair['original_flag']['faces']
        shared = np.intersect1d(mesh.faces[i], mesh.faces[j])
        rows.append({'diagnosis_file': name, 'faces': [i, j],
                     'fresh_shared_indices': shared.tolist(),
                     'indices_exactly_equal': shared.tolist() == pair['shared_vertex_indices'],
                     'coordinates_exactly_equal': mesh.vertices[shared].tolist() == pair['shared_coordinates_mm']})
result = {'scope': 'Fresh trimesh load confirms metadata indices only; exact contact proof is separately performed directly on binary STL records.',
          'input_sha256': hashlib.sha256(stl.read_bytes()).hexdigest(),
          'triangle_order_and_coordinates_unchanged_by_processing': bool(np.array_equal(mesh.triangles, raw.triangles)),
          'checked_rows': len(rows), 'rows': rows}
result['all_checks_passed'] = (result['triangle_order_and_coordinates_unchanged_by_processing']
    and len(rows) == 40 and all(r['indices_exactly_equal'] and r['coordinates_exactly_equal'] for r in rows))
(root/'shared-index-results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k != 'rows'}, indent=2))
raise SystemExit(0 if result['all_checks_passed'] else 1)
