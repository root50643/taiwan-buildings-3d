"""Unmodified STL ray checks. No mesh or polygon repair; fail closed."""
from pathlib import Path
import hashlib,json,numpy as np,trimesh,math
R=Path(__file__).resolve().parent;O=R/'openings-and-pavilion-check.json'
O.write_text(json.dumps({'passed':False,'checks':{'completed':False}}))
T=trimesh.load(R/'model.stl',process=False).triangles;a=T[:,0];e1=T[:,1]-a;e2=T[:,2]-a

def ray(origin,direction,length):
 o=np.array(origin,float);d=np.array(direction,float);d/=np.linalg.norm(d)
 h=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,h);good=np.abs(det)>1e-10
 inv=np.zeros_like(det);inv[good]=1/det[good];s=o-a;u=inv*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=inv*np.einsum('j,ij->i',d,q);t=inv*np.einsum('ij,ij->i',e2,q)
 ok=good&(u>=-1e-7)&(u<=1+1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(t>0)&(t<length)
 return {'origin_mm':o.tolist(),'direction':d.tolist(),'length_mm':length,'hit_distances_mm':sorted(set(round(float(x),5) for x in t[ok]))}
rt=math.sqrt(2);normal=np.array([1/rt,1/rt,0.])
def bridge(y,z):
 center=np.array([12+(-9-y)/rt,(-9+y)/rt,z]);return ray(center-6*normal,normal,12)
rays={'entrance_open':ray([38,0,5.5],[1,0,0],30),'entrance_header':ray([38,0,10.4],[1,0,0],30),'bridge_midspan_low':bridge(20,5.5),'bridge_midspan_high':bridge(20,9.5),'bridge_piers':bridge(24,5.5),'bridge_overhead_slab':bridge(20,11.3),'pavilion_center_vertical':ray([12+3/rt,3/rt,-1],[0,0,1],18),'pavilion_lobe_vertical':ray([12+(5-6)/rt,(5+6)/rt,-1],[0,0,1],18)}
h=lambda k:rays[k]['hit_distances_mm']
checks={'entry_is_true_open_passage':len(h('entrance_open'))==0,'entry_has_solid_header':len(h('entrance_header'))==2,'bridge_midspan_open_low':len(h('bridge_midspan_low'))==0,'bridge_midspan_open_high':len(h('bridge_midspan_high'))==0,'bridge_has_two_solid_piers':len(h('bridge_piers'))==4,'bridge_slab_continuous':len(h('bridge_overhead_slab'))==2,'pavilion_center_solid_from_base_to_roof':len(h('pavilion_center_vertical'))==2 and abs(h('pavilion_center_vertical')[1]-13.5)<.001,'pavilion_lobe_solid_from_base_to_roof':len(h('pavilion_lobe_vertical'))==2 and abs(h('pavilion_lobe_vertical')[1]-13.5)<.001}
r={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'method':'Moller-Trumbore ray intersections on raw unchanged STL triangles. Pavilion vertical hits establish solid closed body and integral roof, not an empty ring. Bridge rays establish real open underpass, two solid piers and continuous slab. Whole-model validation independently checks a single connected shell.','rays':rays,'not_structural_load_test':True}
O.write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,indent=2));raise SystemExit(0 if r['passed'] else 1)
