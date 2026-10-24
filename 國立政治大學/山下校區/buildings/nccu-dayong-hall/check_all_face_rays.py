from pathlib import Path
import json,hashlib,sys,numpy as np,trimesh
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J));from qa_model import raw_read
_,v,f=raw_read(J/'model.stl');m=trimesh.Trimesh(v,f,process=False);norm=m.face_normals;orig=m.triangles_center-norm*.00001;mins=np.full(len(f),np.inf)
for start in range(0,len(f),64):
 loc,ir,it=m.ray.intersects_location(orig[start:start+64],-norm[start:start+64],multiple_hits=True)
 for i,d in zip(ir,np.linalg.norm(loc-orig[start+ir],axis=1)):
  if d>1e-7:mins[start+i]=min(mins[start+i],d)
# Preserve first BVH no-hit IDs, then check the SAME rays against every raw triangle.
# Shared-edge barycentric roundoff is handled only in the ray predicate, not mesh repair.
initial_missing=np.flatnonzero(~np.isfinite(mins)).tolist();fallback=[]
tri=m.triangles;e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
for i in initial_missing:
 o=orig[i];d=-norm[i];pv=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,pv);valid=np.abs(det)>1e-12
 inv=np.divide(1,det,out=np.zeros_like(det),where=valid);tv=o-tri[:,0];u=np.einsum('ij,ij->i',tv,pv)*inv;qv=np.cross(tv,e1);vv=qv@d*inv;dist=np.einsum('ij,ij->i',e2,qv)*inv
 sel=valid&(u>=-1e-9)&(vv>=-1e-9)&(u+vv<=1+1e-9)&(dist>1e-7);hits=np.flatnonzero(sel);assert len(hits),(i,o,d)
 mins[i]=dist[hits].min();fallback.append(dict(face=i,origin_mm=o.tolist(),direction=d.tolist(),hits=[dict(face=int(k),distance_mm=float(dist[k]),u=float(u[k]),v=float(vv[k])) for k in hits]))
assert np.isfinite(mins).all()
order=np.argsort(mins)
r=dict(stl_sha256=hashlib.sha256((J/'model.stl').read_bytes()).hexdigest(),method='Every raw triangle centroid, inward normal offset0.00001mm, nearest positive rawtriangle exit; exact raw STL/no repair,64point chunks',initial_bvh_no_hit_faces=initial_missing,same_ray_all_triangle_fallback=fallback,count=len(f),finite_hits=int(np.isfinite(mins).sum()),minimum_mm=float(mins.min()),below_0_05mm=int((mins<.05).sum()),below_0_8mm=int((mins<.8).sum()),smallest=[dict(face=int(i),distance_mm=float(mins[i]),centroid_design=(m.triangles_center[i]/2.5).tolist(),normal=norm[i].tolist(),triangle_design=(m.triangles[i]/2.5).tolist()) for i in order[:30]],all_faces=[dict(face=i,distance_mm=float(d)) for i,d in enumerate(mins)],limitations='One centroid ray per face, not global wallthickness/strength or printability proof. Geometric edges/tapers may have smaller thickness.')
(J/'qa/all-face-normal-rays.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items() if k not in ['smallest','all_faces']});print(r['smallest'][:5])
