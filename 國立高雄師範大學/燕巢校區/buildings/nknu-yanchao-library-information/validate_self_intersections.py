#!/usr/bin/env python3
"""Independent delivered-STL triangle intersection preflight with an AABB tree.
Coplanar area overlap and non-topological triangle intersections are rejected.
Shared manifold edges/vertices are allowed; tolerance is explicit, not metrology.
"""
from pathlib import Path
import argparse,json,time,hashlib,io
import numpy as np,trimesh
from rtree import index
from shapely.geometry import Polygon
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();(a.out/'qa').mkdir(parents=True,exist_ok=True);stl_bytes=(a.out/'nknu-yanchao-library-information.stl').read_bytes();stl_hash=hashlib.sha256(stl_bytes).hexdigest();t=trimesh.load_mesh(io.BytesIO(stl_bytes),file_type='stl',process=True);tri=t.triangles;faces=t.faces;norm=t.face_normals;bounds=np.c_[tri.min(axis=1),tri.max(axis=1)];prop=index.Property();prop.dimension=3;tree=index.Index(((i,tuple(b),None)for i,b in enumerate(bounds)),properties=prop);eps=1e-5;area_eps=1e-8;candidates=0;coplanar=0;noncoplanar=0;bad=[];started=time.time()
def hits_edges(A,B):
 # All A edges against B, inclusive barycentric interval.
 out=[];e1=B[1]-B[0];e2=B[2]-B[0]
 starts=A;dirs=np.roll(A,-1,axis=0)-A;h=np.cross(dirs,e2);det=h@e1;ok=np.abs(det)>1e-12
 inv=np.divide(1.,det,out=np.zeros(3),where=ok);ss=starts-B[0];uu=inv*np.einsum('ij,ij->i',ss,h);q=np.cross(ss,e1);vv=inv*np.einsum('ij,ij->i',dirs,q);tt=inv*(q@e2)
 mask=ok&(uu>=-1e-8)&(vv>=-1e-8)&(uu+vv<=1+1e-8)&(tt>=-1e-8)&(tt<=1+1e-8)
 return starts[mask]+tt[mask,None]*dirs[mask]
for i,b in enumerate(bounds):
 for j in tree.intersection(tuple(b)):
  if j<=i:continue
  candidates+=1;shared=np.intersect1d(faces[i],faces[j])
  if len(shared)==3:bad.append({'triangles':[i,j],'kind':'duplicate triangle'});continue
  cross=np.linalg.norm(np.cross(norm[i],norm[j]));dist=np.max(np.abs((tri[j]-tri[i,0])@norm[i]))
  if cross<1e-5 and dist<eps and np.max(np.abs((tri[i]-tri[j,0])@norm[j]))<eps:
   coplanar+=1
   if len(shared)==2:
    line=t.vertices[shared[1]]-t.vertices[shared[0]];a1=next(v for v in faces[i]if v not in shared);b1=next(v for v in faces[j]if v not in shared)
    side=np.dot(np.cross(line,t.vertices[a1]-t.vertices[shared[0]]),np.cross(line,t.vertices[b1]-t.vertices[shared[0]]))
    if side<=0:continue
   ax=int(np.argmax(np.abs(norm[i])));A=np.delete(tri[i],ax,axis=1);B=np.delete(tri[j],ax,axis=1);overlap=Polygon(A).intersection(Polygon(B)).area
   if overlap>area_eps:bad.append({'triangles':[i,j],'kind':'coplanar area overlap','projected_overlap_area_mm2':overlap})
  else:
   if len(shared)>=2:continue
   # Separate planes that do not straddle the other's triangle cannot intersect.
   d1=(tri[j]-tri[i,0])@norm[i];d2=(tri[i]-tri[j,0])@norm[j]
   if d1.min()>eps or d1.max()<-eps or d2.min()>eps or d2.max()<-eps:continue
   noncoplanar+=1
   points=np.concatenate([hits_edges(tri[i],tri[j]),hits_edges(tri[j],tri[i])])
   if len(points):
    if len(shared)==1:points=points[np.linalg.norm(points-t.vertices[shared[0]],axis=1)>eps]
    if len(points):bad.append({'triangles':[i,j],'kind':'non-topological intersection','point':points[0].tolist()})
 if len(bad)>20:break
report={'source':'nknu-yanchao-library-information.stl reloaded independently','stl_sha256':stl_hash,'triangles':len(tri),'aabb_candidate_pairs':candidates,'coplanar_pairs_checked':coplanar,'noncoplanar_pairs_checked':noncoplanar,'coordinate_tolerance_mm':eps,'parallel_normal_sine_tolerance':1e-5,'coplanar_area_tolerance_mm2':area_eps,'forbidden_intersections':bad,'all_pass':not bad,'scan_complete':len(bad)<=20,'stopped_early_after_many_violations':len(bad)>20,'method':'3D R-tree broad phase; near-parallel planes require reciprocal vertex-plane distances within coordinate tolerance before coplanar projected polygon area; noncoplanar edge/triangle intersections; shared mesh edges and vertices allowed. Numerical preflight, not exact-predicate proof.','elapsed_seconds':round(time.time()-started,3)}
assert hashlib.sha256((a.out/'nknu-yanchao-library-information.stl').read_bytes()).hexdigest()==stl_hash,'Artifact changed during validation'
(a.out/'qa/self-intersection-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert not bad
