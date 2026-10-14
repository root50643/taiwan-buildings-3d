"""Fail-closed Moller-Trumbore rays against original STL, without repair."""
from pathlib import Path
import json
import numpy as np
import trimesh
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',force='mesh',process=False)
def ray(o,d):
 o=np.array(o,dtype=float);d=np.array(d,dtype=float);t=m.triangles
 e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];p=np.cross(np.tile(d,(len(t),1)),e2);det=np.einsum('ij,ij->i',e1,p)
 good=np.abs(det)>1e-10;inv=np.zeros(len(t));inv[good]=1/det[good];s=o-t[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);v=q@d*inv;dist=np.einsum('ij,ij->i',e2,q)*inv
 sel=good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(dist>1e-8)
 return sorted(set(round(float(a),6) for a in dist[sel]))
checks={};rays={}
for name,x,y in [('large_front_court',0,-25),('small_rear_court',0,43)]:
 h=ray((x,y,30),(0,0,-1));z=30-h[0];checks[name+'_open_to_base']=abs(z-1.8)<1e-5;rays[name]={'origin':[x,y,30],'direction':[0,0,-1],'hits_distance_mm':h,'first_hit_z_mm':z}
h=ray((2,-80,4.8),(0,1,0));checks['main_gate_open_through_to_front_court']=abs(-80+h[0]-15.0)<1e-5;rays['main_gate']={'origin':[2,-80,4.8],'direction':[0,1,0],'hits_distance_mm':h,'first_hit_y_mm':-80+h[0]}
for name,o,d,expected in [('right_front_colonnade',(0,-30,4.0),(1,0,0),38.3),('left_front_colonnade',(0,-30,4.0),(-1,0,0),38.3),('crossbar_front_colonnade',(3,0,4.0),(0,1,0),15.0),('crossbar_rear_colonnade',(3,43,4.0),(0,-1,0),17.4),('rear_colonnade',(3,43,4.0),(0,1,0),16.6)]:
 h=ray(o,d);checks[name+'_air_between_columns_to_back_wall']=abs(h[0]-expected)<1e-5;rays[name]={'origin':o,'direction':d,'hits_distance_mm':h,'expected_first_hit_distance_mm':expected}
h=ray((0,-67,30),(0,0,-1));checks['gate_overhead_roof_present']=30-h[0]>8.5;rays['gate_roof']={'hits_distance_mm':h}
r={'passed':all(checks.values()),'checks':checks,'rays':rays,'method':'Unprocessed original STL triangles; roof-to-base courtyard rays and horizontal gate/colonnade rays. Courtyards are open to base, not holes through base.'}
(R/'open-space-check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));assert r['passed']
