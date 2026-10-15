"""Original binary STL verification. Exact coordinate indexing only; no repair."""

import sys
sys.dont_write_bytecode=True
def require(condition, message='Required check failed'):
    if not bool(condition): raise RuntimeError(message)
from pathlib import Path
import struct,json,hashlib
import numpy as np
R=Path(__file__).resolve().parent;raw=(R/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0]
rec=np.frombuffer(raw,offset=84,dtype=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),count=n);T=rec['v'].astype(float);N=rec['normal'].astype(float)
V,inv=np.unique(T.reshape(-1,3),axis=0,return_inverse=True);F=inv.reshape(-1,3);C=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);norm=np.linalg.norm(C,axis=1)
edges={};links=[[] for _ in V];adj=[set() for _ in F]
for fi,(a,b,c) in enumerate(F):
 for u,v in [(a,b),(b,c),(c,a)]:edges.setdefault(tuple(sorted((int(u),int(v)))),[]).append((fi,int(u),int(v)))
 for x,u,v in [(a,b,c),(b,c,a),(c,a,b)]:links[x].append((int(u),int(v)))
edge2=all(len(e)==2 for e in edges.values());oriented=edge2 and all(e[0][1]==e[1][2] and e[0][2]==e[1][1] for e in edges.values())
for es in edges.values():
 for i,*_ in es:
  for j,*_ in es:
   if i!=j:adj[i].add(j)
seen=set();shells=0
for i in range(len(F)):
 if i in seen:continue
 shells+=1;stack=[i]
 while stack:
  a=stack.pop()
  if a in seen:continue
  seen.add(a);stack.extend(adj[a]-seen)
bad=0
for pairs in links:
 d={}
 for a,b in pairs:d.setdefault(a,set()).add(b);d.setdefault(b,set()).add(a)
 if not d or any(len(v)!=2 for v in d.values()):bad+=1;continue
 seen=set();stack=[next(iter(d))]
 while stack:
  a=stack.pop()
  if a in seen:continue
  seen.add(a);stack.extend(d[a]-seen)
 if len(seen)!=len(d):bad+=1
vol=float(np.einsum('ij,ij->i',T[:,0],np.cross(T[:,1],T[:,2])).sum()/6)
checks={'binary_length_exact':len(raw)==84+50*n,'finite_original_data':bool(np.isfinite(T).all() and np.isfinite(N).all()),'original_faces_nondegenerate':bool((norm>1e-9).all()),'original_normals_unit':bool(np.allclose(np.linalg.norm(N,axis=1),1,atol=1e-5)),'original_normals_agree':bool(np.allclose(N,C/np.maximum(norm[:,None],1e-30),atol=1e-5)),'exact_coordinate_edges_two_faces':edge2,'exact_coordinate_consistent_winding':oriented,'exact_coordinate_vertex_links_cycles':bad==0,'single_surface_no_internal_shell':shells==1,'positive_signed_volume':vol>0,'longest_150mm':abs(float(np.ptp(V,axis=0).max())-150)<1e-5}
r={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256(raw).hexdigest(),'triangles':n,'vertices_exact':len(V),'surface_shells':shells,'bad_vertex_links':bad,'volume_mm3':vol,'method':'Binary triangles, saved normals, exact-coordinate indexing, edge orientations, vertex links, face BFS. No mesh processing, repair, rounding or dropped triangles.'};r['evidence_sources']={n:__import__('hashlib').sha256((R/n).read_bytes()).hexdigest() for n in ['check_raw_mesh.py']};(R/'raw-mesh-check.json').write_text(json.dumps(r,indent=2));print(r);require((r['passed']), ('Required check failed'))
