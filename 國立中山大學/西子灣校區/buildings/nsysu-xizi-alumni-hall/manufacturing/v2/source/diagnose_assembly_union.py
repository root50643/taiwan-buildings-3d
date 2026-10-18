"""Retain and diagnose the failed auxiliary union; never repair print parts."""
from pathlib import Path
import hashlib, json, importlib.util
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
checker_path=ROOT.parents[1]/'qa/independent_geometry_qa.py'
spec=importlib.util.spec_from_file_location('unchanged_checker',checker_path)
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
report=json.loads((ROOT/'models/build-report.json').read_text(encoding='utf-8'))
assembled=[]
for row in report['parts']:
    m=trimesh.load_mesh(ROOT/'models'/row['stl'],process=True)
    m.apply_transform(np.asarray(row['transform_print_to_assembled']))
    assembled.append(m)
native=trimesh.boolean.union(assembled,engine='manifold')
file=ROOT/'qa/design-probe/assembled-union-verification.stl'
raw=trimesh.load_mesh(file,process=False)
processed=trimesh.load_mesh(file,process=True)
indices=np.flatnonzero(raw.area_faces==0)
out={'artifact':'qa/design-probe/assembled-union-verification.stl',
     'artifact_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
     'unchanged_checker_sha256':hashlib.sha256(checker_path.read_bytes()).hexdigest(),
     'native_union_before_STL_export':checker.topology(native),
     'exported_binary32_processed_without_repairs':checker.topology(processed),
     'zero_area_raw_exported_triangle_indices':indices.tolist(),
     'zero_area_raw_exported_triangle_coordinates':[raw.triangles[i].tolist() for i in indices],
     'corresponding_native_triangle_areas_mm2':[float(native.area_faces[i]) for i in indices],
     'corresponding_native_triangle_coordinates':[native.triangles[i].tolist() for i in indices],
     'interpretation':'Auxiliary assembly union has two exact zero-area triangles before STL export and remains a failed artifact. Each flagged triangle repeats an identical original-coordinate point. Do not treat union topology as passed or use this artifact for printing. Six separately closed physical print pieces are the deliverables.'}
(ROOT/'qa/design-probe/assembly-union-failure-diagnosis.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out))
