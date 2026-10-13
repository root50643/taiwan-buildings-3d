"""Verify selected front-to-rear entry rays against the unmodified STL.
Supplemental local opening proof, not a general printability check.
"""
from pathlib import Path
import trimesh,numpy as np,json,hashlib
P=Path(__file__).resolve().parent
m=trimesh.load(P/'model.stl',force='mesh',process=False)
tri=m.triangles.astype(float);direction=np.array([0,1,0])
e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
pv=np.cross(np.broadcast_to(direction,e2.shape),e2)
det=(e1*pv).sum(1);nz=abs(det)>1e-9
inv=np.zeros_like(det);inv[nz]=1/det[nz];rows=[]
for x,z in [(0,8),(0,15),(0,23),(-9,15),(9,15)]:
 origin=np.array([x,-40,z]);tv=origin-tri[:,0]
 u=(tv*pv).sum(1)*inv;qv=np.cross(tv,e1)
 v=(qv*direction).sum(1)*inv;t=(e2*qv).sum(1)*inv
 hit=nz&(u>=0)&(v>=0)&(u+v<=1)&(t>=0)&(t<=80)
 rows.append({'x_mm':x,'z_mm':z,'y_start_mm':-40,'y_end_mm':40,'triangle_hits':int(hit.sum())})
r={'checks':{'five_front_to_rear_test_rays_clear':all(x['triangle_hits']==0 for x in rows)},'method':'Moller-Trumbore triangle ray intersection on unmodified delivered STL; finite rays across y=-40..+40 mm','stl_sha256':hashlib.sha256((P/'model.stl').read_bytes()).hexdigest(),'rays':rows}
(P/'entry-opening-check.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2));raise SystemExit(0 if all(r['checks'].values()) else 1)
