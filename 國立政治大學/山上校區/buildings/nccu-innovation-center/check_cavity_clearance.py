"""Exhaustive disjoint-shell vertex/face and edge/edge distance, raw triangles."""
from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;r,v,f=raw_read(A/'model.stl');m=trimesh.Trimesh(v,f,process=False);shells=m.split(only_watertight=False,repair=False);outer=[s for s in shells if s.volume>0];inner=[s for s in shells if s.volume<0];assert len(outer)==1 and len(inner)==2
sat=json.loads((A/'qa/nonadjacent-triangle-contacts.json').read_text());sha=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest();assert sat['stl_sha256']==sha and sat['nonadjacent_contact_pairs']==0

def minimum_distance(a,b):
 # For disjoint triangles the minimum is attained vertex-face or edge-edge.
 d1=trimesh.proximity.closest_point(a,b.vertices)[1];d2=trimesh.proximity.closest_point(b,a.vertices)[1];best=float(min(d1.min(),d2.min()))
 ea=a.vertices[a.edges_unique];eb=b.vertices[b.edges_unique]
 for start in range(0,len(ea),128):
  p=ea[start:start+128,0,None,:];u=(ea[start:start+128,1]-ea[start:start+128,0])[:,None,:];q=eb[None,:,0,:];w=(eb[:,1]-eb[:,0])[None,:,:];r=p-q
  aa=np.sum(u*u,-1);bb=np.sum(u*w,-1);cc=np.sum(w*w,-1);dd=np.sum(u*r,-1);ee=np.sum(w*r,-1);den=aa*cc-bb*bb
  good=den>1e-20;s=np.divide(bb*ee-cc*dd,den,out=np.zeros_like(den),where=good);t=np.divide(aa*ee-bb*dd,den,out=np.zeros_like(den),where=good)
  good &= (s>=0)&(s<=1)&(t>=0)&(t<=1)
  ds=np.sum((r+s[:,:,None]*u-t[:,:,None]*w)**2,-1);best=min(best,float(np.sqrt(ds[good].min()))) if good.any() else best
  # All four endpoint-to-opposite-segment distances include parallel cases.
  for rr,dirn,denom in [(r,w,cc),(r+u,w,cc),(-r,u,aa),(-r+w,u,aa)]:
   along=np.clip(np.sum(rr*dirn,-1)/denom,0,1);d=np.linalg.norm(rr-along[:,:,None]*dirn,axis=-1);best=min(best,float(d.min()))
 return dict(minimum_mm=best,method='all vertices to opposite triangles via exact closest-point plus exhaustive all-edge-pair interior and four boundary candidates',edge_pairs=int(len(ea)*len(eb)),vertex_face_points=int(len(a.vertices)+len(b.vertices)))
rows=[]
for i,c in enumerate(inner):
 inside=outer[0].contains(c.vertices);assert inside.all();d=minimum_distance(outer[0],c);assert d['minimum_mm']>0
 rows.append(dict(cavity=i,signed_volume_mm3=float(c.volume),all_vertices_inside_outer=True,positive_outer_clearance=d))
d=minimum_distance(inner[0],inner[1]);assert d['minimum_mm']>0
report=dict(stl_sha256=sha,boundary_shells=3,positive_outer_shells=1,negative_finite_hall_shells=2,global_raw_nonadjacent_SAT_contacts=0,negative_shells=rows,cavity_to_cavity_clearance=d,limits='Exhaustive mesh-shell clearance is not an exhaustive minimum wall bound of all outer facade protrusions; thin surface detail separately ray-sampled. Not physically printed.')
(A/'qa/cavity-clearance.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
