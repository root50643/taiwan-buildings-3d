#!/usr/bin/env python3
"""Small adversarial regression tests; these do not certify any building STL."""
from pathlib import Path
import gzip,json,subprocess,sys
import numpy as np
import trimesh
R=Path(__file__).resolve().parent
D=R/'dense-tests'

def box(lo,hi):
 lo=np.asarray(lo,float);hi=np.asarray(hi,float);m=trimesh.creation.box(extents=hi-lo);m.apply_translation((lo+hi)/2);return m

def run(name,mesh,expected,extra=()):
 out=D/name;out.mkdir(exist_ok=True);mesh.export(out/'model.stl')
 p=subprocess.run([sys.executable,str(R/'check_dense_surface.py'),'--out',str(out),*extra],capture_output=True,text=True)
 (out/'dense-test.log').write_text(p.stdout+p.stderr)
 assert p.returncode==expected,(name,p.returncode,p.stdout,p.stderr)
 r=json.loads((out/'dense-audit.json').read_text());assert r['passed']==(expected==0)
 print(name,'expected exit',p.returncode,'samples',r['samples'],'flags',r['flagged_or_short_samples'],flush=True)
 return r,out

r,_=run('cube-pass',box([0,0,0],[2,2,2]),0)
assert r['samples']==120 and r['minimum_first_material_mm']==2
r,p=run('thin-fail',box([0,0,0],[.6,2,2]),1)
assert r['reason_counts']['first material interval below requested minimum']==40 and r['whole_mesh_solid_angle_controls']==200 and r['checks']['all_independent_winding_controls_pass']
r,_=run('stored-normal-pass',box([0,0,0],[2,2,2]),0,['--normal-mode','stored'])
r,p=run('finite-next-air',trimesh.util.concatenate([box([0,0,0],[2,2,2]),box([3,0,0],[5,2,2])]),0)
a=np.load(p/'dense-intervals.npz');assert np.any(np.isclose(a['next_air_mm'],1))
r,p=run('coplanar-overlap-fail',trimesh.util.concatenate([box([0,0,0],[3,100,100]),box([1,1,0],[2,2,2])]),1)
assert r['positive_length_coplanar_intervals']>0 and r['reason_counts']['positive-length coplanar boundary overlap in first material/next air']>0
m=box([0,0,0],[2,2,2]);m.update_faces(np.arange(len(m.faces))!=0)
r,_=run('open-mesh-fail',m,1);assert not r['checks']['raw_topology_and_stored_orientation']
r,_=run('partial-must-fail',box([0,0,0],[2,2,2]),1,['--face-limit','1']);assert not r['checks']['all_original_faces_ten_samples']
# Decimal evaluation prevents a float64 rounding-to-threshold from hiding failure.
import importlib.util
spec=importlib.util.spec_from_file_location('densecheck',R/'check_dense_surface.py');checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
line='0,0,0,0,0,0,0,1,1,0,0,1,1,1,1,0,0,0,0|0.00001,0,.3,.3,-1;0.80000999999999999999,1,.3,.3,1;|\n'
assert checker.classify(checker.parse(line),.8)[0]==64
line='0,0,0,0,0,0,0,1,1,0,0,1,1,1,1,0,0,0,0|0.00001,0,.3,.3,-1;2.00001,1,.3,.3,1;|0.1,0.10000000000000000001,2,0,0;\n'
assert checker.classify(checker.parse(line),.8)[0]==256
print('All nine dense-helper regression cases passed.')
