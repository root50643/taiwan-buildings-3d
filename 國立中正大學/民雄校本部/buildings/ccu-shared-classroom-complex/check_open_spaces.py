"""Ray checks on original STL, no repair: courtyard and actual recessed portal."""
from pathlib import Path
import json
import numpy as np
import trimesh
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',force='mesh',process=False)
def ray(o,d):
 o=np.array(o,dtype=float);d=np.array(d,dtype=float); t=m.triangles
 e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];p=np.cross(np.tile(d,(len(t),1)),e2);det=np.einsum('ij,ij->i',e1,p)
 good=np.abs(det)>1e-10;inv=np.zeros(len(t));inv[good]=1/det[good];s=o-t[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;dist=np.einsum('ij,ij->i',e2,q)*inv
 sel=good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(dist>1e-8)
 return sorted(set(round(float(v),5) for v in dist[sel]))
tests={};data={}
for name,x,y in [('central_courtyard',0,0),('west_lateral_recess',-64,0),('east_lateral_recess',64,0)]:
 hits=ray((x,y,100),(0,0,-1));z=100-hits[0];tests[name+'_open_to_base']=abs(z-2.25)<1e-4;data[name]={'first_hit_z_mm':z,'hits_mm':hits}
hits=ray((0,-100,8),(0,1,0));first=-100+hits[0];tests['portal_clear_through_front_to_rear_connector']=first>10;data['portal']={'first_hit_y_mm':first,'hits_mm':hits}
hits=ray((0,-16,100),(0,0,-1));tests['portal_has_overhead_roof']=100-hits[0]>19;data['portal_roof']={'first_hit_z_mm':100-hits[0]}
report={'passed':all(tests.values()),'checks':tests,'rays':data,'method':'Moller-Trumbore intersections against original unprocessed STL triangles; courtyard rays start above roof and hit only base; horizontal portal ray meets rear connector.'}
(R/'open-space-check.json').write_text(json.dumps(report,indent=2));print(report);assert report['passed']
