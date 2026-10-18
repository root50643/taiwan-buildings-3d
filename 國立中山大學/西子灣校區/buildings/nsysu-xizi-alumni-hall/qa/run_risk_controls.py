"""Small numerical controls for STL facet/support risk measurements."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'risk-controls'
OUT.mkdir(exist_ok=True)


def frustum(run):
    vertices = np.array([
        [-1,-1,0], [1,-1,0], [1,1,0], [-1,1,0],
        [-1-run,-1,1], [1+run,-1,1], [1+run,1,1], [-1-run,1,1],
    ], dtype=float)
    faces = np.array([
        [0,2,1], [0,3,2], [4,5,6], [4,6,7],
        [0,1,5], [0,5,4], [1,2,6], [1,6,5],
        [2,3,7], [2,7,6], [3,0,4], [3,4,7],
    ])
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=True)


cube = trimesh.creation.box(extents=[2,2,2]); cube.apply_translation([0,0,1])
floating = cube.copy(); floating.apply_translation([0,0,3])
samples = {
    'clean_plate_supported_cube': cube,
    'exactly_45_degree_frustum': frustum(1),
    'quantized_45_degree_excess': frustum(1+2**-20),
    'large_overhang_frustum': frustum(2),
    'detached_underside': trimesh.util.concatenate([cube, floating]),
}
rows = {}
for name, mesh in samples.items():
    stl, generic, measured = (OUT/f'{name}{suffix}' for suffix in ('.stl','.generic.json','.measured.json'))
    stl.write_bytes(trimesh.exchange.stl.export_stl(mesh))
    run = subprocess.run([sys.executable, str(ROOT/'independent_geometry_qa.py'), str(stl), '--json', str(generic)], capture_output=True, text=True, encoding='utf8')
    (OUT/f'{name}.generic.stdout.txt').write_text(run.stdout, encoding='utf8')
    (OUT/f'{name}.generic.stderr.txt').write_text(run.stderr, encoding='utf8')
    measure = subprocess.run([sys.executable, str(ROOT/'measure_print_risks.py'), str(stl), str(generic), '--json', str(measured)], capture_output=True, text=True, encoding='utf8')
    (OUT/f'{name}.measure.stdout.txt').write_text(measure.stdout, encoding='utf8')
    (OUT/f'{name}.measure.stderr.txt').write_text(measure.stderr, encoding='utf8')
    if measure.returncode:
        raise RuntimeError(measure.stderr)
    data = json.loads(measured.read_text(encoding='utf8'))
    flags = len(data['exact_over_45_degree_face_indices'])
    excess = [r['axis_aligned_slope_outward_excess_over_45_mm'] for r in data['nonbase_downward_facets'] if 'axis_aligned_slope_outward_excess_over_45_mm' in r]
    if name == 'clean_plate_supported_cube':
        expected = data['nonbase_downward_face_count']==0 and data['support_flagged_layer_count']==0
    elif name == 'exactly_45_degree_frustum':
        expected = flags==0 and max(excess)==0
    elif name == 'quantized_45_degree_excess':
        expected = flags==4 and 0<max(excess)<1e-5
    elif name == 'large_overhang_frustum':
        expected = flags==4 and max(excess)==1 and data['support_flagged_layer_count']>0
    else:
        expected = len(data['connected_horizontal_underside_patches'])==1 and data['connected_horizontal_underside_patches'][0]['area_mm2']==4 and data['support_flagged_layer_count']>0
    rows[name] = {'expectation_passed':expected, 'generic_exit_status_retained':run.returncode,
        'measurer_exit_status':measure.returncode, 'stl_sha256':hashlib.sha256(stl.read_bytes()).hexdigest(),
        'exact_over_45_face_count':flags, 'support_flagged_layer_count':data['support_flagged_layer_count'],
        'maximum_axis_aligned_plane_excess_mm':max(excess,default=None),
        'horizontal_underside_patch_count':len(data['connected_horizontal_underside_patches']),
        'measurement_report':measured.relative_to(ROOT).as_posix()}
result = {'scope':'Synthetic risk measurement controls; generic CLI failures are retained and are expected for the overhang/detached specimens.',
    'script_sha256':hashlib.sha256((ROOT/'measure_print_risks.py').read_bytes()).hexdigest(),
    'cases':rows,'all_control_expectations_passed':all(r['expectation_passed'] for r in rows.values())}
(OUT/'controls.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,indent=2))
raise SystemExit(0 if result['all_control_expectations_passed'] else 1)
