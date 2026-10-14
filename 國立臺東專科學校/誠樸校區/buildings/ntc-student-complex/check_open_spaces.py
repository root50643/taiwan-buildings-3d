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
S=2.25; BASE=3.0; FLOOR=4.1
def point(x,y,z):return ((x-29.24)*S,(10.2-y)*S,BASE+z*S)
# Vertical ray into the central 4F notch must first meet the actual 3F balcony,
# not a fictional fourth-storey room or main roof.
o=point(25.5,13.0,30);hits=ray(o,(0,0,-1));hit=o[2]-hits[0]
expected=BASE+(2*FLOOR+.021)*S
tests['central_notch_open_above_3F_balcony']=abs(hit-expected)<1e-4
data['central_balcony']={'first_hit_z_mm':hit,'expected_z_mm':expected,'hits_mm':hits}
# C034's separate L-shaped balcony remains open, with no invented roof above.
for name,x,y in [('west_leg',14.9,17),('east_leg',19,14.6)]:
 o=point(x,y,30);hits=ray(o,(0,0,-1));hit=o[2]-hits[0]
 expected=BASE+(3*FLOOR+.021)*S
 tests['fourth_floor_L_balcony_'+name+'_open']=abs(hit-expected)<1e-4
 data['fourth_floor_L_balcony_'+name]={'first_hit_z_mm':hit,'expected_z_mm':expected,'hits_mm':hits}
# Outside the balcony edge, open sky must reach the common base.
o=point(25.5,20,30);hits=ray(o,(0,0,-1));hit=o[2]-hits[0]
tests['south_notch_outside_platform_open_to_base']=abs(hit-BASE)<1e-4
data['south_notch']={'first_hit_z_mm':hit,'hits_mm':hits}
# Entrance at 1F and 2F passes through the south porch and meets its north wall.
for floor,z in [('ground',2),('second',6)]:
 o=point(25.5,30,z);hits=ray(o,(0,1,0));hit_y=o[1]+hits[0]
 expected_y=(10.2-9.8-.001)*S
 tests[f'{floor}_entrance_below_balcony_clear']=abs(hit_y-expected_y)<1e-4
 data[f'{floor}_entrance']={'first_hit_y_mm':hit_y,'expected_y_mm':expected_y,'clear_distance_mm':hits[0]}
# A horizontal ray through the actual north balcony stays clear between its
# front balustrade and backing wall (individual wall-backed balconies).
o=point(15.5,-1,3*FLOOR+1.5);hits=ray(o,(0,-1,0));first_y=o[1]-hits[0]
tests['north_balcony_air_space_real']=first_y<(10.2)*S
# South setbacks are verified between major windows (X=37.73 is a pier).
# Use rays at actual bay piers so the first hit is the outer wall, not a window recess.
for name,x,ywall,z in [('2F_balcony',37.73,17.701,FLOOR+2),('3F_balcony',37.73,15.801,2*FLOOR+2),('4F_west_balcony',30,15.801,3*FLOOR+2),('4F_east_projection',41.5,17.701,3*FLOOR+2)]:
 o=point(x,27,z);hits=ray(o,(0,1,0));first_y=o[1]+hits[0]
 expected=(10.2-ywall)*S
 tests[name+'_air_or_wall_position']=abs(first_y-expected)<1e-4
 data[name]={'first_hit_y_mm':first_y,'expected_y_mm':expected,'clear_distance_mm':hits[0]}
# Lower north hall facade projects 1.8m beyond the structural grid at both levels.
for name,z in [('north_1F',2),('north_2F',FLOOR+2)]:
 o=point(21.73,-10,z);hits=ray(o,(0,-1,0));first_y=o[1]-hits[0]
 expected=(10.2+1.801)*S
 tests[name+'_projected_wall_position']=abs(first_y-expected)<1e-4
 data[name]={'first_hit_y_mm':first_y,'expected_y_mm':expected}
# The southwest wing roof is one full storey below the north main roof.
zs=[]
for x,y in [(7,19),(27,7)]:
 o=point(x,y,30);hits=ray(o,(0,0,-1));zs.append(o[2]-hits[0])
tests['southwest_roof_one_storey_lower']=zs[1]-zs[0]>3.9*S
data['roof_step']={'southwest_first_hit_z_mm':zs[0],'main_first_hit_z_mm':zs[1],'height_difference_mm':zs[1]-zs[0]}
report={'passed':all(tests.values()),'checks':tests,'rays':data,'method':'Moller-Trumbore intersections against original unprocessed STL triangles. Source plan establishes central platform and notch; exact vertical clearances are inferred. No closed atrium is claimed.'}
(R/'open-space-check.json').write_text(json.dumps(report,indent=2));print(report);assert report['passed']
