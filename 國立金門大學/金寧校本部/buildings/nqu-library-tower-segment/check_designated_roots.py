"""Declared feature-specific original surface rays. First continuous intervals only.
Does not certify all-direction/global minimum wall thickness or physical printability.
"""
from pathlib import Path
import json,hashlib,tempfile,subprocess
import numpy as np,trimesh
from original_rays import OriginalRays
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',process=False);ray=OriginalRays(m);cases=[]
def add(family,p,d,minimum):cases.append((family,np.array(p,float),np.array(d,float),minimum))
for y in [-2.5,0,2.5]:
 add('new_door_grille_back',[-20,y,6],[1,0,0],1)
 add('new_door_grille_width',[-19.5,y-.5,6],[0,1,0],.8)
 add('new_door_grille_bottom',[-19.5,y,9],[0,0,-1],4)
for z in [20,45,70,95]:
 for y in [-2.1,2.1]:add('new_window_frame_back',[-19.95,y,z+4],[1,0,0],1)
for x in [-17,17]:
 for y in [-28,28]:
  add('gable_tip_down_root',[x,y,137],[0,0,-1],3)
  add('gable_true_normal',[x-1.5,y,136],[1,0,0],2.9)
for y in [-22,22]:add('thickened_roof_valley',[0,y,132.5],[0,0,-1],1)
for x in [-15,15]:add('balcony_hole_upper_lintel',[x,-25.5,118],[0,0,-1],1)
for x in [-28,28]:
 for y in [-28,28]:add('hip_roof_corner_down_root',[x,y,float(np.float32(136.7))],[0,0,-1],5)
rows=[];points=[]
for family,p,d,minimum in cases:
 o=p-d*1e-5;h=ray.hits(o,d);assert len(h)>=2,(family,p,h);a,b=h[0][0],h[1][0];entry=abs(a-1e-5)<1e-6;length=b-a;probes=[o,o+d*(a+1e-5),o+d*((a+b)/2),o+d*(b+1e-5)];ix=list(range(len(points),len(points)+4));points.extend(probes);rows.append(dict(family=family,surface=p.tolist(),inward=d.tolist(),hits=h,first_chord_mm=length,minimum_required_mm=minimum,entry_matches=entry,length_sufficient=length>=minimum-1e-5,indices=ix))
with tempfile.TemporaryDirectory() as td:
 D=Path(td);m.triangles.astype('<f8').tofile(D/'tri');np.array(points,dtype='<f8').tofile(D/'pts');subprocess.run(['g++','-O3',str(R/'original_winding.cpp'),'-o',str(D/'w')],check=True);subprocess.run([str(D/'w'),str(D/'tri'),str(D/'pts'),str(D/'vals')],check=True);vals=np.loadtxt(D/'vals',delimiter=',')[:,1]
for q in rows:q['winding']=[float(vals[i]) for i in q['indices']];q['winding_passed']=all(abs(v-e)<1e-7 for v,e in zip(q['winding'],[0,1,1,0]))
checks={'all_declared_surface_entries':all(q['entry_matches'] for q in rows),'all_first_roots_meet_specific_threshold':all(q['length_sufficient'] for q in rows),'all_before_inside_mid_after_winding':all(q['winding_passed'] for q in rows)}
out=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),checks=checks,passed=all(checks.values()),rows=rows);(R/'designated-roots.json').write_text(json.dumps(out,indent=2));print(checks);print([q for q in rows if not(q['entry_matches']and q['length_sufficient']and q['winding_passed'])]);raise SystemExit(0 if out['passed'] else 1)
