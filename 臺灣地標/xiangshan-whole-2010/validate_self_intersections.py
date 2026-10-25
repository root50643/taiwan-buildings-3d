#!/usr/bin/env python3
"""Independent delivered-STL triangle intersection preflight with an AABB tree.
Coplanar area overlap and non-topological triangle intersections are rejected.
Shared manifold edges/vertices are allowed; tolerance is explicit, not metrology.
"""
from pathlib import Path
import argparse,json,time,hashlib,io
import numpy as np,trimesh
from rtree import index
from shapely.geometry import Polygon, Point, LineString, GeometryCollection
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();(a.out/'qa').mkdir(parents=True,exist_ok=True);stl_bytes=(a.out/'xiangshan-whole-2010.stl').read_bytes();stl_hash=hashlib.sha256(stl_bytes).hexdigest();t=trimesh.load_mesh(io.BytesIO(stl_bytes),file_type='stl',process=True);tri=t.triangles;faces=t.faces;norm=t.face_normals;bounds=np.c_[tri.min(axis=1),tri.max(axis=1)];prop=index.Property();prop.dimension=3;tree=index.Index(((i,tuple(b),None)for i,b in enumerate(bounds)),properties=prop);eps=1e-5;area_eps=1e-8;candidates=0;coplanar=0;noncoplanar=0;bad=[];raw_hit_points=0;rejected_unconfirmed_points=0;confirmed_hit_points=0;started=time.time()
def hits_edges(A,B):
 # All A edges against B, inclusive barycentric interval.
 out=[];e1=B[1]-B[0];e2=B[2]-B[0]
 starts=A;dirs=np.roll(A,-1,axis=0)-A;h=np.cross(dirs,e2);det=h@e1;ok=np.abs(det)>1e-12
 inv=np.divide(1.,det,out=np.zeros(3),where=ok);ss=starts-B[0];uu=inv*np.einsum('ij,ij->i',ss,h);q=np.cross(ss,e1);vv=inv*np.einsum('ij,ij->i',dirs,q);tt=inv*(q@e2)
 mask=ok&(uu>=-1e-8)&(vv>=-1e-8)&(uu+vv<=1+1e-8)&(tt>=-1e-8)&(tt<=1+1e-8)
 return starts[mask]+tt[mask,None]*dirs[mask]
def point_confirmation(points,T,normal):
 # The near-parallel Moller-Trumbore determinant can suffer cancellation.
 # A claimed hit is evidence only if the reconstructed point independently lies
 # on this triangle's plane AND inside its dominant-axis 2D projection. This
 # confirmation uses the same 1e-5 mm coordinate tolerance, never a wider one.
 points=np.asarray(points,float);ok=np.all(points>=T.min(axis=0)-eps,axis=1)&np.all(points<=T.max(axis=0)+eps,axis=1)
 ok &= np.abs((points-T[0])@normal)<=eps
 axis=int(np.argmax(np.abs(normal)));q=np.delete(points,axis,axis=1);v=np.delete(T,axis,axis=1)
 e=np.roll(v,-1,axis=0)-v;u=v[1]-v[0];w=v[2]-v[0];orientation=u[0]*w[1]-u[1]*w[0];sign=1.0 if orientation>0 else -1.0
 for k in range(3):
  d=q-v[k];signed=sign*(e[k,0]*d[:,1]-e[k,1]*d[:,0]);ok &= signed>=-eps*np.linalg.norm(e[k])
 return ok
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
   ax=int(np.argmax(np.abs(norm[i])));A=np.delete(tri[i],ax,axis=1);B=np.delete(tri[j],ax,axis=1);contact=Polygon(A).intersection(Polygon(B));overlap=contact.area
   if overlap>area_eps:bad.append({'triangles':[i,j],'kind':'coplanar area overlap','projected_overlap_area_mm2':overlap})
   elif not contact.is_empty:
    topology=np.delete(t.vertices[shared],ax,axis=1)
    permitted=Point(topology[0]).buffer(eps) if len(shared)==1 else LineString(topology).buffer(eps) if len(shared)==2 else GeometryCollection()
    if not contact.difference(permitted).is_empty:bad.append({'triangles':[i,j],'kind':'non-topological coplanar contact'})
  else:
   if len(shared)>=2:continue
   # Separate planes that do not straddle the other's triangle cannot intersect.
   d1=(tri[j]-tri[i,0])@norm[i];d2=(tri[i]-tri[j,0])@norm[j]
   if d1.min()>eps or d1.max()<-eps or d2.min()>eps or d2.max()<-eps:continue
   noncoplanar+=1
   points=np.concatenate([hits_edges(tri[i],tri[j]),hits_edges(tri[j],tri[i])])
   if len(points):
    raw_hit_points+=len(points)
    verified=point_confirmation(points,tri[i],norm[i])&point_confirmation(points,tri[j],norm[j])
    rejected_unconfirmed_points+=int((~verified).sum());points=points[verified];confirmed_hit_points+=len(points)
    if len(shared)==1:points=points[np.linalg.norm(points-t.vertices[shared[0]],axis=1)>eps]
    if len(points):bad.append({'triangles':[i,j],'kind':'non-topological intersection','point':points[0].tolist()})
 if len(bad)>20:break
report={'source':'xiangshan-whole-2010.stl reloaded independently','stl_sha256':stl_hash,'triangles':len(tri),'aabb_candidate_pairs':candidates,'coplanar_pairs_checked':coplanar,'noncoplanar_pairs_checked':noncoplanar,'coordinate_tolerance_mm':eps,'parallel_normal_sine_tolerance':1e-5,'coplanar_area_tolerance_mm2':area_eps,'raw_edge_triangle_hit_points':raw_hit_points,'rejected_unconfirmed_hit_points':rejected_unconfirmed_points,'confirmed_edge_triangle_hit_points':confirmed_hit_points,'candidate_hit_confirmation':'Both triangle plane distances, both 3D bounding boxes and both dominant-axis projected triangle edge halfspaces must confirm each candidate point within the unchanged coordinate tolerance.','forbidden_intersections':bad,'all_pass':not bad,'scan_complete':len(bad)<=20,'stopped_early_after_many_violations':len(bad)>20,'method':'3D R-tree broad phase; near-parallel planes require reciprocal vertex-plane distances within coordinate tolerance before coplanar projected polygon area; noncoplanar edge/triangle candidate intersections independently confirmed on both planes and inside both projected triangles; points from ill-conditioned determinant cancellation are not accepted as intersections; shared mesh edges and vertices allowed; coplanar point/line contacts outside shared topology rejected. Numerical preflight, not exact-predicate proof.','elapsed_seconds':round(time.time()-started,3)}
assert hashlib.sha256((a.out/'xiangshan-whole-2010.stl').read_bytes()).hexdigest()==stl_hash,'Artifact changed during validation'
(a.out/'qa/self-intersection-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert not bad
