"""Selected original-triangle O-column roots and passage clearances; no mesh repair."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
R=Path(__file__).parent;m=trimesh.load(R/'model.stl',process=False)
def ray(o,d):
 o=np.array(o);d=np.array(d);p,_,_=m.ray.intersects_location([o],[d],multiple_hits=True)
 return sorted(set(round(float(np.dot(v-o,d)),7)for v in p if np.dot(v-o,d)>0))
rows=[]
for z in [3.,5.,7.,9.,11.]:
 for axis in [0,1]:
  q=np.array([27.125,1.875,z]);v=np.zeros(3);v[axis]=1;o=q-v*3;hit=ray(o,v);width=hit[1]-hit[0]
  rows.append(dict(feature='O first square column',z=z,axis=axis,all_original_hits_mm=hit,normal_chord_mm=width));assert width>=1.29999
h=ray([27.125,1.875,-1],[0,0,1]);assert len(h)==2 and h[0]==1;rows.append(dict(feature='O first column downward root',all_original_hits_mm=h,continuous_base_to_roof=True))
a=np.array([22.125,-12.75]);b=np.array([27.125,1.875]);u=(b-a)/np.linalg.norm(b-a);normal=np.array([-u[1],u[0]])
for t in [.2,.4,.6,.8]:
 p=a*(1-t)+b*t+normal*1.0;h=ray([*p,0.1],[0,0,1]);zs=[v+.1 for v in h];assert len(zs)>=3 and abs(zs[0]-2.4)<1e-5 and zs[1]-zs[0]>6
 rows.append(dict(feature='O roofed passage interior',fraction=t,xy=p.tolist(),all_original_hit_z=zs,clear_height_mm=zs[1]-zs[0]))
checks=dict(square_column_two_axes_at_five_heights=True,column_continuous_to_base=True,four_O_passage_clearances_gt_6mm=True)
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),checks=checks,passed=all(checks.values()),samples=rows,limits='Only designated original-face rays; not whole-model minimum wall, toolpaths, or physical print testing.');(R/'feature-rays.json').write_text(json.dumps(r,indent=2));print(r)
