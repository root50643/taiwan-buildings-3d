"""Canonical shared-edge horizontal contour audit; not a printer slicer.
Canonical endpoint orientation follows NCU check_layers.py; vectorized equivalent.
Run python validate_sections.py; output cross_sections.json beside actual STL.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
p=Path(__file__).resolve().parent
mesh=trimesh.load(p/'model.stl',force='mesh',process=True)
tri=mesh.triangles;a=tri.copy();b=np.roll(tri,-1,axis=1).copy()
swap=(a[:,:,0]>b[:,:,0])|((a[:,:,0]==b[:,:,0])&(a[:,:,1]>b[:,:,1]))|((a[:,:,0]==b[:,:,0])&(a[:,:,1]==b[:,:,1])&(a[:,:,2]>b[:,:,2]))
aa=np.where(swap[:,:,None],b,a);bb=np.where(swap[:,:,None],a,b);a,b=aa,bb
zvalues=np.unique(mesh.vertices[:,2]);reports=[]
for z in np.arange(.1,float(mesh.bounds[1,2])-1e-4,.2):
 if np.any(np.abs(zvalues-z)<.001):z-=.0173
 hit=((a[:,:,2]<z)&(z<b[:,:,2]))|((b[:,:,2]<z)&(z<a[:,:,2]))
 countface=hit.sum(axis=1);ok=countface==2;aa=a[ok][hit[ok]];bb=b[ok][hit[ok]]
 q=aa+(bb-aa)*(z-aa[:,2,None])/(bb[:,2,None]-aa[:,2,None]);pts=np.round(q[:,:2],6)
 if len(pts):
  _,inv,count=np.unique(pts,axis=0,return_inverse=True,return_counts=True);collapsed=bool((inv.reshape(-1,2)[:,0]==inv.reshape(-1,2)[:,1]).any());bad=int((count!=2).sum())
 else:collapsed=False;bad=0
 malformed=int(((countface!=0)&(countface!=2)).sum())
 reports.append(dict(z_mm=round(float(z),6),closed=bool(len(pts)>0 and bad==0 and not collapsed and malformed==0),segments=len(pts)//2,bad_degree_nodes=bad,collapsed_segments=collapsed,malformed_triangle_intersections=malformed))
result=dict(passed=all(x['closed'] for x in reports),method='Canonical lexicographic edge orientation before shared-edge interpolation; degree-two and collapsed-segment checks',layer_step_mm=.2,start_mm=.1,vertex_plane_avoidance_mm=-.0173,endpoint_rounding_mm=1e-6,sample_count=len(reports),stl_sha256=hashlib.sha256((p/'model.stl').read_bytes()).hexdigest(),failed_samples=[x for x in reports if not x['closed']],samples=reports,limitations=['Horizontal sampled contours only; not slicer toolpaths or a physical print test.','Does not measure exhaustive wall thickness or prove fidelity to the building.'])
(p/'cross_sections.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(result['passed'],len(reports),result['failed_samples'][:3]);raise SystemExit(0 if result['passed'] else 1)
