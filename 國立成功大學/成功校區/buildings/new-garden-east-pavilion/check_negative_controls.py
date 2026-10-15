"""Prove the unchanged gates reject open, duplicated, inverted and thin meshes.
All control inputs/reports remain under a separate output directory. The deliverable
STL is never edited. No expected failure is converted into a model pass.
"""

import sys
sys.dont_write_bytecode=True
def require(condition, message='Required check failed'):
    if not bool(condition): raise RuntimeError(message)
from pathlib import Path
import hashlib,json,shutil,struct,subprocess,sys
from manifold3d import Manifold
from build_model import box,union,save_stl
R=Path(__file__).resolve().parent
O=R/'negative-control-results';O.mkdir(exist_ok=True)
original=(R/'model.stl').read_bytes();n=struct.unpack_from('<I',original,80)[0]
def binary(triangles):return original[:80]+struct.pack('<I',len(triangles)//50)+triangles
cases={
 'missing_triangle':('check_raw_mesh.py',binary(original[134:]),'exact_coordinate_edges_two_faces'),
 'duplicated_triangle':('check_raw_mesh.py',binary(original[84:]+original[84:134]),'exact_coordinate_edges_two_faces'),
}
t=bytearray(original);a=t[96:108];t[96:108]=t[108:120];t[108:120]=a
cases['reversed_face']=('check_raw_mesh.py',bytes(t),'exact_coordinate_consistent_winding')
# This extra cube is within the 150 mm bounds and is a separate closed shell.
separate=O/'separate-cube.stl';save_stl(box(-8,-4,-8,-4,5,9),separate)
cube=separate.read_bytes();cases['extra_closed_shell']=('check_raw_mesh.py',binary(original[84:]+cube[84:]),'single_surface_no_internal_shell')
neck=union([box(0,10,0,10,0,3),box(14,24,0,10,0,3),box(9,15,4.7,5.3,0,3)])
island=union([box(0,30,0,12,0,.4),box(0,10,0,10,0,3),box(25,25.6,5,5.6,0,3)])
for name,shape in [('narrow_root',neck),('tiny_separate_polygon',island)]:
 p=O/(name+'.stl');save_stl(shape,p);cases[name]=('check_component_detail.py',p.read_bytes(),'original_component_erosion')
rows=[]
for name,(checker,data,reason) in cases.items():
 d=O/name;d.mkdir(exist_ok=True);(d/'model.stl').write_bytes(data)
 shutil.copy2(R/checker,d/checker)
 r=subprocess.run([sys.executable,str(d/checker)],capture_output=True,text=True)
 (d/'stdout.txt').write_text(r.stdout);(d/'stderr.txt').write_text(r.stderr.replace(str(R),'.'))
 reportfile=d/('raw-mesh-check.json' if checker=='check_raw_mesh.py' else 'first-layer-failure.json')
 rejected=r.returncode!=0
 if checker=='check_raw_mesh.py':
  report=json.loads(reportfile.read_text());rejected=rejected and report['passed'] is False and report['checks'][reason] is False
 else:
  rejected=rejected and reportfile.exists() and 'vanishes or splits' in r.stderr
 rows.append({'name':name,'rejected':rejected,'returncode':r.returncode,'expected_reason':reason,
              'input_sha256':hashlib.sha256(data).hexdigest(),'report_path':str(reportfile.relative_to(R))})
report={'passed':all(q['rejected'] for q in rows),'stl_sha256':hashlib.sha256(original).hexdigest(),'checks':{q['name']:q['rejected'] for q in rows},'controls':rows}
report['evidence_sources']={n:__import__('hashlib').sha256((R/n).read_bytes()).hexdigest() for n in ['check_negative_controls.py', 'check_raw_mesh.py', 'check_component_detail.py', 'build_model.py', 'parameters.json']}
(R/'negative-controls.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));require((report['passed']), ('Required check failed'))
