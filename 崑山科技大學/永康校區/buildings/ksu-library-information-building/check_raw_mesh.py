"""Exact raw STL topology: only identical float32 coordinates are indexed. No repair."""
from pathlib import Path
import numpy as np,json,struct,hashlib
R=Path(__file__).resolve().parent;raw=(R/'model.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0]
a=np.frombuffer(raw,offset=84,dtype=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attribute','<u2')]),count=n);t=a['v'].astype(float);v,iv=np.unique(t.reshape(-1,3),axis=0,return_inverse=True);f=iv.reshape(-1,3)
edges={};links=[[]for _ in v];parent=list(range(n))
def root(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for i,(x,y,z)in enumerate(f):
 for u,w in [(x,y),(y,z),(z,x)]:edges.setdefault(tuple(sorted((u,w))),[]).append((i,u,w))
 for u,w,k in [(x,y,z),(y,z,x),(z,x,y)]:links[u].append((w,k))
for e in edges.values():
 for q in e[1:]:parent[root(q[0])]=root(e[0][0])
bad=0
for pairs in links:
 adj={}
 for x,y in pairs:adj.setdefault(x,[]).append(y);adj.setdefault(y,[]).append(x)
 if any(len(q)!=2 for q in adj.values()):bad+=1;continue
 seen=set();todo=[next(iter(adj))]
 while todo:
  x=todo.pop()
  if x not in seen:seen.add(x);todo.extend(adj[x])
 if len(seen)!=len(adj):bad+=1
c=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area2=np.linalg.norm(c,axis=1);unit=c/area2[:,None];norm=a['normal'].astype(float);components=len({root(i)for i in range(n)});volume=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6)
checks=dict(binary_length_exact=len(raw)==84+n*50,finite=bool(np.isfinite(t).all() and np.isfinite(norm).all()),original_face_nondegenerate=bool((area2>1e-9).all()),original_normals_unit=bool(np.allclose(np.linalg.norm(norm,axis=1),1,atol=1e-5)),original_normals_match=bool(np.allclose(unit,norm,atol=1e-5)),exact_edge_two_faces=all(len(q)==2 for q in edges.values()),exact_edge_opposite_winding=all(len(q)==2 and q[0][1]==q[1][2] and q[0][2]==q[1][1]for q in edges.values()),exact_vertex_link_one_cycle=bad==0,exact_single_surface_shell=components==1,positive_volume=volume>0)
r=dict(passed=all(checks.values()),checks=checks,raw_triangles=n,exact_unique_vertices=len(v),surface_shells=components,bad_vertex_links=bad,volume_mm3=volume,stl_sha256=hashlib.sha256(raw).hexdigest(),method='Original binary float32 triangles and normals. np.unique creates exact coordinate indices only; no rounding, welding tolerance, repair or trimesh processing.')
(R/'raw-mesh-check.json').write_text(json.dumps(r,indent=2));assert r['passed'],r;print('PASS exact raw mesh',n,len(v))
