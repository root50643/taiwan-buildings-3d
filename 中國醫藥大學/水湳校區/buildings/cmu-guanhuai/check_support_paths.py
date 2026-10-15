"""Source-defined support axes and real first-hit surfaces; never skip air intervals."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;E1=T[:,1]-T[:,0];E2=T[:,2]-T[:,0];S=148/55.2;BASE=2

def hits(o,d):
 q=np.cross(d,E2);det=np.einsum('ij,ij->i',E1,q);ok=abs(det)>1e-13;iv=np.zeros(len(T));iv[ok]=1/det[ok];ss=o-T[:,0];u=np.einsum('ij,ij->i',ss,q)*iv;r=np.cross(ss,E1);v=r@d*iv;t=np.einsum('ij,ij->i',E2,r)*iv;ix=np.flatnonzero(ok&(u>=-1e-12)&(v>=-1e-12)&(u+v<=1+1e-12)&(t>1e-9));ix=ix[np.argsort(t[ix])];keep=[]
 for i in ix:
  if not keep or t[i]-t[keep[-1]]>1e-7:keep.append(i)
 return [{'face':int(i),'distance_mm':float(t[i]),'point_mm':(o+d*t[i]).tolist()} for i in keep]
rows=[]
for y,dy in [(-3.8,-1.7),(4.3,1.7)]:
 d=np.array([1.72,dy,13.45]);d/=np.linalg.norm(d);base=np.array([-18.1*S,y*S,0.]);o=base-d*2;h=hits(o,d);p0=np.array(h[0]['point_mm']);p1=np.array(h[1]['point_mm']);ok=p0[2]<1e-6 and p1[2]>BASE+13.40*S
 rows.append({'family':'slanted_column_ground_and_main_body','origin_mm':o.tolist(),'direction':d.tolist(),'all_hits':h,'first_continuous_solid_mm':h[1]['distance_mm']-h[0]['distance_mm'],'root_check':bool(ok)})
for x,y in [(-10,-10),(-10,4),(-7,13),(9,-11),(10,2),(6,13)]:
 o=np.array([x*S,y*S,152.]);d=np.array([0.,0.,-1.]);h=hits(o,d);ok=h[0]['point_mm'][2]>BASE+51.6*S and h[1]['point_mm'][2]<BASE+49.7*S
 rows.append({'family':'roof_cap_column_and_main_slab','origin_mm':o.tolist(),'direction':d.tolist(),'all_hits':h,'first_continuous_solid_mm':h[1]['distance_mm']-h[0]['distance_mm'],'root_check':bool(ok)})
# Bottom landings of the three exterior recess groups: start in visible air.
for floor,cy,x in [(13.05,7.7,-13.),(24.0,-6.8,-13.),(34.95,19.5,-10.)]:
 o=np.array([x*S,cy*S,BASE+(floor+1.0)*S]);d=np.array([0.,0.,-1.]);h=hits(o,d);ok=len(h)>1 and h[1]['distance_mm']-h[0]['distance_mm']>=.8
 rows.append({'family':'terrace_bottom_landing','nominal_floor_m':floor,'origin_mm':o.tolist(),'direction':d.tolist(),'all_hits':h,'first_continuous_solid_mm':h[1]['distance_mm']-h[0]['distance_mm'],'root_check':bool(ok)})
j={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'passed':all(r['root_check'] for r in rows),'checks':{'all_source_nominated_support_paths_continuous':all(r['root_check'] for r in rows)},'rays':rows,'limits':'Support-axis rays start outside on real original first-hit surfaces. They demonstrate nominated connected paths, not global minimum normal thickness. Full original normal and air samples are separately preserved.'};(R/'support-paths.json').write_text(json.dumps(j,indent=2));print([(r['family'],r['first_continuous_solid_mm'],r['root_check']) for r in rows]);assert j['passed']
