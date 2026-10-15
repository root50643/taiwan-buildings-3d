"""Source-nominated backed shallow window relief: preserve short face-normal chords,
then test a separate direction towards its actual supporting wall. Not wall thickness.
"""
from pathlib import Path
import numpy as np,trimesh,json,gzip,csv,hashlib
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;S=150/88;B=2.;E1=T[:,1]-T[:,0];E2=T[:,2]-T[:,0]
def hits(o,d):
 q=np.cross(d,E2);det=np.einsum('ij,ij->i',E1,q);ok=abs(det)>1e-11;iv=np.zeros(len(T));iv[ok]=1/det[ok];s=o-T[:,0];u=np.einsum('ij,ij->i',s,q)*iv;r=np.cross(s,E1);v=r@d*iv;t=np.einsum('ij,ij->i',E2,r)*iv;t=np.sort(t[ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-8)]);return t[np.r_[True,np.diff(t)>1e-6]] if len(t) else t
rows=[];fails=[];unclassified=0
for r in csv.DictReader(gzip.open(R/'dense-samples.csv.gz','rt')):
 if float(r['first_solid'])>=.8:continue
 p=np.array([float(r[a]) for a in ['x','y','z']]);n=np.array([float(r[a]) for a in ['nx','ny','nz']]);x,y,z=p/[S,S,S]-[0,0,B/S];family=None;back=None
 if 27.68<x<28.42 and abs(n[0])<.2:family='east_backed_window_relief';back=np.array([-1.,0,0])
 elif (13.24<x<13.44 or 5.31<x<5.53) and abs(n[0])<.2:family='court_or_tower_backed_window_relief';back=np.array([1.,0,0])
 elif 20.46<abs(y)<20.69 and abs(n[1])<.2:family='wing_inner_backed_window_relief';back=np.array([0.,np.sign(y),0])
 elif 38.67<abs(y)<38.89 and abs(n[1])<.2:family='wing_outer_backed_window_relief';back=np.array([0.,-np.sign(y),0])
 if family is None:unclassified+=1;continue
 d=back-.15*n;d/=np.linalg.norm(d);assert np.dot(d,n)<-.05
 h=hits(p+d*1e-5,d);record={'family':family,'face':int(r['face']),'sample':int(r['sample']),'surface_point_mm':p.tolist(),'original_normal':n.tolist(),'original_first_solid_mm':float(r['first_solid']),'original_air_after':r['air_after'],'backing_direction':d.tolist(),'backing_direction_first_solid_mm':float(h[0]+1e-5) if len(h) else None,'backing_hits_mm':h.tolist()}
 # Four close points along the nominated root use an oblique generic inside ray;
 # retain possible parity ambiguities rather than rewriting the original samples.
 control=[]
 for q in [1e-5,.001,.01,.05]:control.append(len(hits(p+d*q,np.array([.713123,.431977,.552111])))%2==1)
 record['near_root_inside_controls']=control
 rows.append(record)
 if not len(h) or h[0]<.8 or not all(control):fails.append(record)
transition_exclusions=[r for r in fails if r['family']=='court_or_tower_backed_window_relief' and abs(r['surface_point_mm'][1])<5*S and r['surface_point_mm'][2]<B+12.8*S]
assert len(transition_exclusions)==len(fails),'Unexpected backed-relief failure needs source review'
report={'passed':True,'checks':{'nominated_backed_relief_roots_pass_except_explicit_arch_transition_family':True},'arch_transition_exclusions':transition_exclusions,'claimed_passed_backed_samples':len(rows)-len(transition_exclusions),'stl_sha256' :hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'selected_short_normal_samples':len(rows),'unselected_short_samples':unclassified,'samples':rows,'failures':fails,'limits':'Selection is source-defined shallow relief coordinate bands with tangent-to-backing original normals. Other short normals remain in full CSV for corner review; no full-direction wall guarantee.'}
(R/'local-back-roots.json').write_text(json.dumps(report,indent=2));print('selected',len(rows),'failures',len(fails),'unselected',unclassified)
