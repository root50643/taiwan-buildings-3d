import trimesh,numpy as np,json
from pathlib import Path
p=Path(__file__).resolve().parent; mesh=trimesh.load(p/'model.stl')
result=[]
for z in np.arange(.1,150,.2):
 lines=trimesh.intersections.mesh_plane(mesh,[0,0,1],[0,0,z]); points=np.round(lines[:,:,:2],5).reshape(-1,2);v,inv=np.unique(points,axis=0,return_inverse=True);adj=[[] for _ in v]
 for a,b in inv.reshape(-1,2):adj[a].append(b);adj[b].append(a)
 left=set(range(len(v)));count=0
 while left:
  stack=[left.pop()];count+=1
  while stack:
   for q in adj[stack.pop()]:
    if q in left:left.remove(q);stack.append(q)
 if count!=1:result.append({'z_mm':round(float(z),2),'contours':count})
r={'layer_height_mm':.2,'sample_count':750,'no_empty_sampled_layers':not any(x['contours']==0 for x in result),'multi_contour_layers':result,'limitation':'Cross-section contour test only. Multiple contours occur in roof strips and relief details and do not by themselves mean floating geometry. This does not verify support, slicing, or physical printability.'};(p/'layer_check.json').write_text(json.dumps(r,indent=2));print(r)
