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
S=1.3; B=1.78
tests={};data={}
def horizontal(name,x,z):
 hits=ray((x*S,-100,z*S+B),(0,1,0));first=None if not hits else -100+hits[0]
 data[name]={'x_m':x,'z_m':z,'first_hit_y_mm':first,'hits_mm':hits};return first
for name,x in [('west_arcade',-32.5833333333),('east_arcade',36.25)]:
 for floor,z in [('lower',1.6),('upper',5.65)]:
  first=horizontal(name+'_'+floor,x,z);tests[name+'_'+floor+'_genuine_depth']=first is not None and first>-4.1
first=horizontal('central_through_portal',5.5,1.6);tests['central_portal_clear_south_to_north']=first is None
first=horizontal('porch_right_pier',7.8,1.6);tests['porch_has_actual_front_pier']=first is not None and first<-13.3
hits=ray((5.5*S,-9.2*S,100),(0,0,-1));roof=100-hits[0];data['porch_roof_z_mm']=roof;tests['porch_has_overhead_solid_roof']=6.7<roof<7.2
for sign,side in [(-1,'west'),(1,'east')]:
 for label,y,lo,hi in [('lower_tread',2.52,2.7,3.0),('upper_landing',-3.6,6.8,7.2)]:
  hits=ray((sign*53.55*S,y*S,100),(0,0,-1));z=100-hits[0];data[side+'_'+label]={'first_hit_z_mm':z,'hits_mm':hits};tests[side+'_'+label+'_exposed_at_expected_height']=lo<z<hi
 hits=ray((sign*100,2.52*S,4.7*S+B),(-sign,0,0));wall=100-hits[0];data[side+'_air_above_stair']={'first_hit_abs_x_mm':wall,'hits_mm':hits};tests[side+'_stair_not_box_infilled_above_treads']=68.4<wall<69.0
# Roof slopes and dropped corridor are actually present in the STL.
for label,y in [('crest',1.53),('rear_eave',5.7),('corridor',-4.4),('front_fascia',-5.73)]:
 hits=ray((-30*S,y*S,100),(0,0,-1));data['roof_'+label+'_z_mm']=100-hits[0]
tests['main_roof_has_low_ridge']=data['roof_crest_z_mm']>data['roof_rear_eave_z_mm']+.20
tests['corridor_roof_drops_below_ridge']=data['roof_crest_z_mm']>data['roof_corridor_z_mm']+.45
tests['front_fascia_above_lowered_corridor']=data['roof_front_fascia_z_mm']>data['roof_corridor_z_mm']+.10
tests['stair_tread_heights_are_mirrored']=abs(data['west_lower_tread']['first_hit_z_mm']-data['east_lower_tread']['first_hit_z_mm'])<1e-5
report={'passed':all(tests.values()),'checks':tests,'rays':data,'method':'Moller-Trumbore ray intersections against original unprocessed STL triangles. No repair. Air-over-tread, portal, arcade depth and roof-height checks are geometric tests, not real-life access dimensions.'}
(R/'open-space-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['passed']
