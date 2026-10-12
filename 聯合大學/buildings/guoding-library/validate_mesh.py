import json, pathlib, numpy as np, trimesh
p=pathlib.Path(__file__).parent
m=trimesh.load(p/'guoding_library_150mm.stl',process=True)
e,c=np.unique(np.sort(m.edges,axis=1),axis=0,return_counts=True)
bad_edges=int(np.sum(c!=2))
# Connected links around every vertex must form a single cycle.
adj=[[] for _ in m.vertices]
for a,b,c in m.faces:
 adj[a].append((b,c));adj[b].append((a,c));adj[c].append((a,b))
bad_links=0
for pairs in adj:
 d={}
 for a,b in pairs:d.setdefault(int(a),set()).add(int(b));d.setdefault(int(b),set()).add(int(a))
 if any(len(v)!=2 for v in d.values()):bad_links+=1;continue
 todo=[next(iter(d))];seen=set()
 while todo:
  a=todo.pop()
  if a in seen:continue
  seen.add(a);todo.extend(d[a]-seen)
 if len(seen)!=len(d):bad_links+=1
report=json.loads((p/'validation.json').read_text());report.update(boundary_or_nonmanifold_edges=bad_edges,nonmanifold_vertex_links=bad_links,minimum_z_mm=float(m.bounds[0,2]),surface_area_mm2=float(m.area),independent_stl_reload_checked=True)
(p/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
assert m.is_watertight and m.is_winding_consistent and len(m.split())==1 and bad_edges==0 and bad_links==0 and m.volume>0
