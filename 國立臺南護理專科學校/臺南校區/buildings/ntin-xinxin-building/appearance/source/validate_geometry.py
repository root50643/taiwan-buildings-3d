#!/usr/bin/env python3
"""Read original geometry and prove the appearance mesh is identical; no repairs."""
import argparse,json,hashlib,struct
from pathlib import Path
import numpy as np
import trimesh
p=argparse.ArgumentParser();p.add_argument('--stl',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();b=a.stl.read_bytes();D=np.load(a.out/'mesh-data.npz');P=json.loads((a.out/'parameters.json').read_text())
assert hashlib.sha256(b).hexdigest()==P['original_stl_sha256'];n=struct.unpack_from('<I',b,80)[0];T=np.frombuffer(b,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),offset=84)['v'].astype(float)
v,f=D['vertices'],D['faces'];assert np.array_equal(v[f],T) and np.array_equal(D['original_triangles'],T)
m=trimesh.Trimesh(v,f,process=False);assert m.is_watertight and m.is_winding_consistent and m.volume>0 and len(m.split(only_watertight=False))==1
# Exact two-use edges, oriented opposite uses, and circular vertex links.
edges={};links=[[]for _ in v]
for x,y,z in f:
 for u,w in [(x,y),(y,z),(z,x)]:edges.setdefault(tuple(sorted((u,w))),[]).append((int(u),int(w)))
 links[x].append((int(y),int(z)));links[y].append((int(z),int(x)));links[z].append((int(x),int(y)))
assert all(len(e)==2 and e[0]==e[1][::-1]for e in edges.values())
for link in links:
 adj={}
 for x,y in link:adj.setdefault(x,set()).add(y);adj.setdefault(y,set()).add(x)
 assert all(len(t)==2 for t in adj.values());seen=set();todo=[next(iter(adj))]
 while todo:
  z=todo.pop()
  if z not in seen:seen.add(z);todo.extend(adj[z]-seen)
 assert len(seen)==len(adj)
# Open gallery/portico loops give this original closed boundary nonzero genus.
chi=len(v)-len(edges)+len(f);assert chi==-26
report={'source_stl_sha256':hashlib.sha256(b).hexdigest(),'all_original_triangle_coordinates_exact_in_order':True,'triangles':len(f),'vertices':len(v),'edges':len(edges),'connected_components':1,'watertight':True,'winding_consistent':True,'edge_two_use_opposite_orientation':True,'all_vertex_links_one_cycle':True,'euler_characteristic':int(chi),'closed_surface_genus':int((2-chi)//2),'positive_volume_mm3':float(m.volume),'bounds_mm':m.bounds.tolist(),'extents_mm':m.extents.tolist(),'geometry_modified':False,'original_print_warnings_still_apply':True,'not_slicer_or_physical_print_test':True}
(a.out/'qa/geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
