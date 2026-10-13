"""Read-only reproducer. Usage: python reproduce_endpoint_rounding.py model.stl --z 16.071
Known fixture: NCU batch-06 ncu-mechanical model.stl, SHA2435ff13fab1003507fd7055c7ce154cde5740bada3671998f2e97e3fd70cae3.
Shows graph-degree failures in independently evaluated mesh_plane endpoints and
closed degree-two loops after canonical shared-edge interpolation. Does not mutate STL.
"""
import argparse,json,hashlib
from collections import Counter
from pathlib import Path
import numpy as np,trimesh
p=argparse.ArgumentParser();p.add_argument('stl');p.add_argument('--z',type=float,default=16.071);a=p.parse_args();m=trimesh.load(a.stl,force='mesh',process=True)
def stats(seg):
 adj={}
 for s in seg:
  u,v=[tuple(np.round(x[:2],6)) for x in s]
  if u==v:continue
  adj.setdefault(u,[]).append(v);adj.setdefault(v,[]).append(u)
 return {'nodes':len(adj),'degree_histogram':dict(Counter(map(len,adj.values()))),'all_degree_two':all(len(v)==2 for v in adj.values())}
old=stats(trimesh.intersections.mesh_plane(m,[0,0,1],[0,0,a.z]));tri=m.triangles;mask=(tri[:,:,2].min(axis=1)<a.z)&(tri[:,:,2].max(axis=1)>a.z);seg=[]
for f in tri[mask]:
 hit=[]
 for u,v in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
  if tuple(u)>tuple(v):u,v=v,u
  if u[2]<a.z<v[2] or v[2]<a.z<u[2]:hit.append(u+(v-u)*(a.z-u[2])/(v[2]-u[2]))
 if len(hit)==2:seg.append(hit)
new=stats(seg);print(json.dumps({'stl_sha256':hashlib.sha256(Path(a.stl).read_bytes()).hexdigest(),'z_mm':a.z,'old_mesh_plane_round6':old,'canonical_edge_round6':new},indent=2));assert new['all_degree_two']
