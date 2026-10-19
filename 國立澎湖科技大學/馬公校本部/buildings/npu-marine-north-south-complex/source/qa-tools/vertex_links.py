"""All-vertex link-cycle check to detect pinched/nonmanifold vertex contacts."""
import argparse,json,hashlib,collections
from pathlib import Path
import trimesh

def main():
 p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--output',required=True);args=p.parse_args();manifest=Path(args.manifest);data=json.loads(manifest.read_text());records=[]
 for part in data['parts']:
  f=manifest.parent/part['stl'];m=trimesh.load_mesh(f,process=False);m.merge_vertices();links=[[] for _ in m.vertices]
  for face in m.faces:
   for i,v in enumerate(face):links[v].append((int(face[(i+1)%3]),int(face[(i+2)%3])))
  bad=[]
  for v,edges in enumerate(links):
   graph=collections.defaultdict(list)
   for a,b in edges:graph[a].append(b);graph[b].append(a)
   if not graph:bad.append({'vertex':v,'reason':'isolated'});continue
   visited=set();pending=[next(iter(graph))]
   while pending:
    n=pending.pop()
    if n in visited:continue
    visited.add(n);pending.extend(graph[n])
   if len(visited)!=len(graph) or any(len(ns)!=2 for ns in graph.values()):
    bad.append({'vertex':v,'position_mm':m.vertices[v].tolist(),'link_nodes':len(graph),'link_reachable':len(visited),'degrees':{str(n):len(ns) for n,ns in graph.items() if len(ns)!=2}})
  records.append({'id':part['id'],'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'vertices_tested':len(m.vertices),'nonmanifold_vertex_links':bad,'pass':len(bad)==0})
 report={'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'method':'Every merged vertex: incident opposite edges must form one connected degree-two link cycle. This supplements edge watertightness and triangle intersection tests by detecting pinched vertex fans.','parts':records,'all_pass':all(r['pass'] for r in records)}
 Path(args.output).write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'all_vertex_links_pass':report['all_pass'],'vertices_tested':sum(r['vertices_tested'] for r in records)}))
if __name__=='__main__':main()
