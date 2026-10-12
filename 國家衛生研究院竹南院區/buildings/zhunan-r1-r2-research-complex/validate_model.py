"""Validate a standalone, millimeter-unit architectural STL without changing it.
Usage: python validate_model.py model.stl --longest-edge 150 --output validation.json
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import trimesh
p=argparse.ArgumentParser();p.add_argument('stl',type=Path);p.add_argument('--longest-edge',type=float,default=150);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
mesh=trimesh.load(a.stl,force='mesh',process=True)
edges,counts=np.unique(np.sort(mesh.edges,axis=1),axis=0,return_counts=True)
bad_edges=int(np.sum(counts!=2));adj=[[] for _ in mesh.vertices]
for x,y,z in mesh.faces:adj[x].append((y,z));adj[y].append((x,z));adj[z].append((x,y))
bad_links=0
for pairs in adj:
 d={}
 for x,y in pairs:d.setdefault(int(x),set()).add(int(y));d.setdefault(int(y),set()).add(int(x))
 if not d or any(len(v)!=2 for v in d.values()):bad_links+=1;continue
 pending=[next(iter(d))];seen=set()
 while pending:
  v=pending.pop()
  if v in seen:continue
  seen.add(v);pending.extend(d[v]-seen)
 if len(seen)!=len(d):bad_links+=1
parts=mesh.split(only_watertight=False)
finite=bool(np.isfinite(mesh.vertices).all())
nondegenerate=bool((mesh.area_faces>1e-9).all())
bottom=np.isclose(mesh.triangles[:,:,2],mesh.bounds[0,2],atol=1e-5).all(axis=1)
checks={'finite_coordinates':finite,'nondegenerate_faces':nondegenerate,'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),'one_connected_body':len(parts)==1,'no_sealed_internal_cavity_shells':len(parts)==1,'each_surface_shell_positive_volume':all(c.volume>0 for c in parts),'no_duplicate_faces':len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces),'all_edges_two_faces':bad_edges==0,'all_vertex_links_single_cycles':bad_links==0,'positive_volume':bool(mesh.volume>0),'base_on_z_zero':abs(float(mesh.bounds[0,2]))<1e-4,'flat_contact_area':float(mesh.area_faces[bottom].sum())>1,'longest_edge_matches_target':abs(float(mesh.extents.max())-a.longest_edge)<.02}
report={'passed':all(checks.values()),'checks':checks,'dimensions_mm':mesh.extents.tolist(),'target_longest_edge_mm':a.longest_edge,'units':'mm','scale_note':'Standalone miniature; not a common scale across campus buildings.','triangles':len(mesh.faces),'vertices':len(mesh.vertices),'connected_components':len(parts),'surface_shells':len(parts),'sealed_internal_cavity_note':'A single closed surface shell excludes separate enclosed cavity shells; the open courtyard and open colonnade are exterior air.','volume_mm3':float(mesh.volume),'contact_area_mm2':float(mesh.area_faces[bottom].sum()),'nonmanifold_edges':bad_edges,'nonmanifold_vertex_links':bad_links,'stl_sha256':hashlib.sha256(a.stl.read_bytes()).hexdigest(),'limitations':['Digital mesh validation is not a physical print test.','Minimum feature thickness and support needs require design review and slicer inspection.','This check does not independently prove absence of all geometric self-intersections.']}
a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['passed'] else 1)
