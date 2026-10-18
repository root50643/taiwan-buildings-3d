"""Exact-coordinate incidence and vertex-link supplement, no mesh repair."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, collections
import numpy as np
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('variant_qa',HERE/'variant_qa.py');qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)

def main():
 p=argparse.ArgumentParser();p.add_argument('--variant',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists():raise FileExistsError('Existing evidence not overwritten.')
 mesh=qa.load(a.variant);f=mesh['faces'];n=len(f);parent=list(range(n));edges=collections.defaultdict(list);links=collections.defaultdict(list)
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i,(v0,v1,v2) in enumerate(f):
  for v,x,y in [(v0,v1,v2),(v1,v2,v0),(v2,v0,v1)]:
   edges[tuple(sorted([int(v),int(x)]))].append(i);links[int(v)].append((int(x),int(y)))
 for faces in edges.values():
  for j in faces[1:]:parent[find(j)]=find(faces[0])
 bad=[]
 for v,segments in links.items():
  graph=collections.defaultdict(list)
  for x,y in segments:graph[x].append(y);graph[y].append(x)
  seen=set();todo=[next(iter(graph))]
  while todo:
   x=todo.pop()
   if x in seen:continue
   seen.add(x);todo.extend(graph[x])
  if len(seen)!=len(graph) or any(len(x)!=2 for x in graph.values()):bad.append(dict(vertex=v,link_node_count=len(graph),visited=len(seen),degree_histogram=dict(collections.Counter(map(len,graph.values())))))
 out=dict(stl_sha256=mesh['sha'],script_sha256=qa.sha(Path(__file__)),method='Exact-position indexing of saved float32 coordinates, without repair. Every undirected edge has its incident faces counted. Face components join only across shared edges. Every vertex link is formed from opposite triangle edges and required to be one connected degree-2 cycle.',vertices=len(mesh['verts']),edges=len(edges),faces=n,edge_face_incidence_histogram=dict(collections.Counter(map(len,edges.values()))),edge_connected_surface_component_count=len({find(i) for i in range(n)}),invalid_vertex_link_count=len(bad),invalid_vertex_links=bad,euler_characteristic=len(mesh['verts'])-len(edges)+n,closed_single_surface_with_manifold_vertex_links=all(len(x)==2 for x in edges.values()) and len({find(i) for i in range(n)})==1 and not bad,formal_slicer_run=False,physical_print_test=False)
 a.output.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
