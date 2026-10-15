"""Original curved-facet/true-edge witnesses for all short normal intervals.
Uses source and actual first-exit normals, local original facet paths and first continuous roots.
No skipped gaps, alternative distant wall, repair, or author-approved exception.
"""
from pathlib import Path
import numpy as np,trimesh,json,gzip,hashlib,tempfile,subprocess,os
from original_rays import OriginalRays
R=Path(__file__).resolve().parent;m0=trimesh.load(R/'model.stl',process=False);V,I=np.unique(m0.triangles.reshape(-1,3),axis=0,return_inverse=True);m=trimesh.Trimesh(V,I.reshape(-1,3),process=False);N=m.face_normals;T=m.triangles;ray=OriginalRays(m0)
mask=m.face_adjacency_angles>np.radians(12);adj=m.face_adjacency[mask];edges=m.vertices[m.face_adjacency_edges[mask]];en=N[adj];neighbours=[[] for _ in T]
for a,b in m.face_adjacency:neighbours[a].append(int(b));neighbours[b].append(int(a))
short=json.loads((R/'dense-short-chords.json').read_text())['short_chords'];rows=[];points=[]
def path(start,target,p,n):
 ids=np.array(list(m.triangles_tree.intersection(np.r_[p-1,p+1])),int);close=trimesh.triangles.closest_point(T[ids],np.tile(p,(len(ids),1)));allowed=set(ids[(np.linalg.norm(close-p,axis=1)<=1+1e-8)&(N[ids]@n>np.cos(np.radians(12)))].tolist());prev={start:None};todo=[start]
 for f in todo:
  if f==target:
   out=[]
   while f is not None:out.append(f);f=prev[f]
   return list(reversed(out))
  for q in neighbours[f]:
   if q in allowed and q not in prev:prev[q]=f;todo.append(q)
 return None
for q in short:
 fi=q['original_triangle_index'];sample=q['sample_index'];p=np.array(q['surface_point_mm']);n=N[fi];h=q['all_ray_intersections_mm_face'];ef=h[1][1];exitn=N[ef];a=en@n;b=en@exitn;quality=np.maximum(np.minimum(a[:,0],b[:,1]),np.minimum(a[:,1],b[:,0]));exact=np.maximum(np.maximum(a[:,0],b[:,1]),np.maximum(a[:,1],b[:,0]));ids=np.where((quality>np.cos(np.radians(12)))&(exact>.99999))[0];e=edges[ids];v=e[:,1]-e[:,0];t=np.clip(np.einsum('ij,ij->i',p-e[:,0],v)/np.einsum('ij,ij->i',v,v),0,1);ds=np.linalg.norm(p-e[:,0]-v*t[:,None],axis=1);k=int(ds.argmin());ix=int(ids[k]);fs=adj[ix]
 if min(N[fs[0]]@n,N[fs[1]]@exitn)<min(N[fs[1]]@n,N[fs[0]]@exitn):fs=fs[::-1]
 pp=path(fi,int(fs[0]),p,n);ep=path(ef,int(fs[1]),p,exitn);d=-n-exitn;d/=np.linalg.norm(d);rootorigin=p+d*1e-5;rh=ray.hits(rootorigin,d);rootlen=rh[0][0];o=p+n*1e-6;gap=h[2][0]-h[1][0] if len(h)>2 else 1;rgap=rh[1][0]-rh[0][0] if len(rh)>1 else 1
 ps=[o,o-n*(h[0][0]+min((h[1][0]-h[0][0])/4,1e-5)),o-n*((h[0][0]+h[1][0])/2),o-n*(h[1][0]+min(gap/4,1e-5)),rootorigin,rootorigin+d*rootlen/2,rootorigin+d*(rootlen+min(rgap/4,1e-5))];idx=list(range(len(points),len(points)+7));points.extend(ps)
 rows.append(dict(face=fi,sample=sample,surface=p.tolist(),source_normal=n.tolist(),first_exit_face=int(ef),first_exit_normal=exitn.tolist(),original_normal_hits=h,true_edge_original_faces=fs.tolist(),true_edge_mm=edges[ix].tolist(),true_edge_distance_mm=float(ds[k]),normal_deviation_deg=float(np.degrees(np.arccos(np.clip(quality[ix],-1,1)))),source_patch_original_faces=pp,exit_patch_original_faces=ep,inward_root=d.tolist(),root_origin=rootorigin.tolist(),root_all_hits=rh,first_root_length_mm=rootlen,indices=idx))
with tempfile.TemporaryDirectory() as td:
 D=Path(td);T.astype('<f8').tofile(D/'tri');np.array(points,dtype='<f8').tofile(D/'pts');subprocess.run(['g++','-O3','-fopenmp',str(R/'winding_parallel.cpp'),'-o',str(D/'w')],check=True);subprocess.run([str(D/'w'),str(D/'tri'),str(D/'pts'),str(D/'vals')],check=True,env={**os.environ,'OMP_NUM_THREADS':'4'});values=np.loadtxt(D/'vals',delimiter=',')[:,1]
for q in rows:q['controls']=[dict(point_mm=points[i].tolist(),expected=e,winding=float(values[i]),passed=bool(abs(values[i]-e)<1e-7)) for i,e in zip(q['indices'],[0,1,1,0,1,1,0])]
checks=dict(every_short_sample_included=len(rows)==len(short),all_true_edge_distance_le_0p8=all(q['true_edge_distance_mm']<=.8 for q in rows),all_actual_local_smooth_patch_paths=all(q['source_patch_original_faces'] is not None and q['exit_patch_original_faces'] is not None for q in rows),all_first_roots_ge_0p8=all(q['first_root_length_mm']>=.8 for q in rows),all_controls=all(c['passed'] for q in rows for c in q['controls']))
out=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),checks=checks,count=len(rows),max_true_edge_distance_mm=max(q['true_edge_distance_mm'] for q in rows),max_normal_deviation_deg=max(q['normal_deviation_deg'] for q in rows),minimum_first_root_mm=min(q['first_root_length_mm'] for q in rows),rows=rows,limits='Finite local root witnesses. Does not waive strict short chords or certify all-direction thickness. Local path vertices are original facets with point-to-triangle distance <=1mm and normal deviation <12 degrees; edge selection uses one exact matching plane and the adjacent smoothly curved patch.')
with gzip.open(R/'curved-patch-roots.json.gz','wt') as f:json.dump(out,f)
print({k:v for k,v in out.items() if k not in ['rows','limits']});print('failed patches',[(q['face'],q['sample'])for q in rows if q['source_patch_original_faces'] is None or q['exit_patch_original_faces'] is None]);print('failed controls',[(q['face'],q['sample'],q['controls'])for q in rows if not all(c['passed'] for c in q['controls'])]);raise SystemExit(0 if all(checks.values()) else 1)
