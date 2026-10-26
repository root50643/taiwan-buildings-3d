"""Pure-NumPy closed oriented 2-manifold checks, usable in both export runtimes."""
from collections import Counter, defaultdict
import numpy as np

def check_topology(vertices, faces, artifact):
    v=np.asarray(vertices,dtype=float);f=np.asarray(faces,dtype=np.int64)
    assert v.ndim==2 and v.shape[1]==3 and f.ndim==2 and f.shape[1]==3
    assert np.isfinite(v).all() and len(v)>3 and len(f)>3
    assert f.min()>=0 and f.max()<len(v)
    edges=Counter();oriented=Counter();links=defaultdict(list);adj=defaultdict(set)
    for a,b,c in f:
        for u,w in ((a,b),(b,c),(c,a)):
            key=tuple(sorted((int(u),int(w))));edges[key]+=1
            oriented[key]+=1 if u<w else -1
            adj[int(u)].add(int(w));adj[int(w)].add(int(u))
        links[int(a)].append((int(b),int(c)));links[int(b)].append((int(c),int(a)));links[int(c)].append((int(a),int(b)))
    bad_links=[]
    for vertex,es in links.items():
        ring=defaultdict(set)
        for a,b in es:ring[a].add(b);ring[b].add(a)
        seen=set();todo=[next(iter(ring))]
        while todo:
            x=todo.pop()
            if x in seen:continue
            seen.add(x);todo.extend(ring[x]-seen)
        if len(seen)!=len(ring) or any(len(q)!=2 for q in ring.values()):bad_links.append(vertex)
    remaining=set(adj);components=0
    while remaining:
        components+=1;todo=[next(iter(remaining))]
        while todo:
            x=todo.pop()
            if x not in remaining:continue
            remaining.remove(x);todo.extend(adj[x]&remaining)
    t=v[f];area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)*.5
    volume=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6)
    nonmanifold=sum(n!=2 for n in edges.values());inconsistent=sum(n!=0 for n in oriented.values())
    report={'artifact':artifact,'vertices':len(v),'triangles':len(f),'closed_shells':components,
      'watertight':nonmanifold==0,'winding_consistent':inconsistent==0,'positive_volume_mm3':volume,
      'edge_incidence_histogram':dict(Counter(edges.values())),'nonmanifold_edges':nonmanifold,
      'nonmanifold_vertex_links':len(bad_links),'inconsistently_oriented_edges':inconsistent,
      'degenerate_triangles':int((area<1e-9).sum()),
      'duplicate_triangles':len(f)-len(np.unique(np.sort(f,axis=1),axis=0)),
      'unreferenced_vertices':len(v)-len(links),'size_model_mm':np.ptp(v,axis=0).tolist(),
      'bounds_model_mm':[v.min(axis=0).tolist(),v.max(axis=0).tolist()],
      'euler_characteristic':len(v)-len(edges)+len(f)}
    report['all_pass']=bool(components==1 and volume>0 and not any(report[k]for k in [
      'nonmanifold_edges','nonmanifold_vertex_links','inconsistently_oriented_edges',
      'degenerate_triangles','duplicate_triangles','unreferenced_vertices']))
    return report
