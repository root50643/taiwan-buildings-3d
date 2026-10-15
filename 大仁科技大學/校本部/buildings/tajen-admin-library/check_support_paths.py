"""Source-defined support axes and real first-hit surfaces; never skip air intervals."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
R=Path(__file__).resolve().parent;T=trimesh.load(R/'model.stl',process=False).triangles;E1=T[:,1]-T[:,0];E2=T[:,2]-T[:,0];S=150/62;BASE=2

def hits(o,d):
 q=np.cross(d,E2);det=np.einsum('ij,ij->i',E1,q);ok=abs(det)>1e-13;iv=np.zeros(len(T));iv[ok]=1/det[ok];ss=o-T[:,0];u=np.einsum('ij,ij->i',ss,q)*iv;r=np.cross(ss,E1);v=r@d*iv;t=np.einsum('ij,ij->i',E2,r)*iv;ix=np.flatnonzero(ok&(u>=-1e-12)&(v>=-1e-12)&(u+v<=1+1e-12)&(t>1e-9));ix=ix[np.argsort(t[ix])];keep=[]
 for i in ix:
  if not keep or t[i]-t[keep[-1]]>1e-7:keep.append(i)
 return [{'face':int(i),'distance_mm':float(t[i]),'point_mm':(o+d*t[i]).tolist()} for i in keep]
rows=[]
def add(family,o,d,criterion):
 h=hits(np.array(o,float),np.array(d,float));assert len(h)>=2;ok=criterion(h);rows.append({'family':family,'origin_mm':list(o),'direction':list(d),'all_hits':h,'first_continuous_solid_mm':h[1]['distance_mm']-h[0]['distance_mm'],'passed':bool(ok)})
# Four source-nominated columns, 3x3 axis grid, no selected long-direction search.
for x in [-18,-6,6,17.2]:
 for dx in [-.1,0,.1]:
  for dy in [-.1,0,.1]:add('south_four_columns_to_ground_and_header',[x*S+dx,-22.4*S+dy,-1],[0,0,1],lambda h:h[0]['point_mm'][2]<1e-6 and h[1]['point_mm'][2]>=BASE+9.2*S)
# First-hit back surface must remain at least 4.8 metres inside front portico line.
for x in [-12,0,12]:
 for z in [2.,4.6,7.]:
  o=np.array([x*S,-26*S,BASE+z*S]);h=hits(o,np.array([0.,1.,0.]));depth=(h[0]['point_mm'][1]/S)-(-23.)
  rows.append({'family':'true_portico_recess_first_back_surface','origin_mm':o.tolist(),'direction':[0,1,0],'all_hits':h,'first_back_recess_depth_m':depth,'passed':depth>=4.8})
# Both red roof levels and their actual connecting body, plus eastern wing stair.
for x,y,minz in [(0,9.2,38.0),(0,0,31.4),(-6,14,38.0),(20,0,12.5),(30,0,7.7)]:
 add('roof_or_wing_support_to_ground',[x*S,y*S,110],[0,0,-1],lambda h,mz=minz:h[0]['point_mm'][2]>=BASE+mz*S and h[1]['point_mm'][2]<1e-6)
for i in [0,5,11,17,23]:
 y=-18+i*.56+.25;x=36.2
 add('external_stair_solid_step_ground_root',[x*S,y*S,35],[0,0,-1],lambda h:h[1]['point_mm'][2]<1e-6)
j={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'passed':all(x['passed'] for x in rows),'checks':{'all_source_support_and_portico_paths_pass':all(x['passed'] for x in rows)},'rays':rows,'limits':'All paths record first original-face entry/exit and subsequent air; actual nominated supports only. Roof/column centre axes are not normal wall thickness or exhaustive support simulation.'};(R/'support-paths.json').write_text(json.dumps(j,indent=2));print('rays',len(rows),'failed',[x for x in rows if not x['passed']]);assert j['passed']
