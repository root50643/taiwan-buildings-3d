#!/usr/bin/env python3
"""Reload delivered STL, check edge AND vertex manifoldness, slice all 0.2 mm layers.
This is numerical preflight, not a slicer qualification or physical print test.
"""
import argparse,json,hashlib,collections,math
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=a.out;(root/'qa').mkdir(exist_ok=True)
D=np.load(root/'mesh-data.npz');raw=trimesh.load_mesh(root/'model.stl',process=False)
assert len(raw.faces)==len(D['faces']);assert np.array_equal(raw.triangles,np.asarray(D['vertices'])[D['faces']])
t=trimesh.load_mesh(root/'model.stl',process=True)
assert t.is_watertight and t.is_winding_consistent and t.volume>0
parts=t.split(only_watertight=False);assert len(parts)==1
counts=np.bincount(t.edges_unique_inverse);assert np.all(counts==2)
canonical=np.sort(t.faces,axis=1);assert len(np.unique(canonical,axis=0))==len(t.faces)
assert np.all(t.area_faces>1e-10)
links=[[]for _ in t.vertices]
for f in t.faces:
 for i in range(3):links[f[i]].append((int(f[(i+1)%3]),int(f[(i+2)%3])))
for edges in links:
 graph=collections.defaultdict(set)
 for u,v in edges:graph[u].add(v);graph[v].add(u)
 assert all(len(n)==2 for n in graph.values())
 seen=set();stack=[next(iter(graph))]
 while stack:
  n=stack.pop()
  if n in seen:continue
  seen.add(n);stack.extend(graph[n]-seen)
 assert len(seen)==len(graph)
# World XY polygons from independently recomputed intersections, not GPU preview.
levels=np.arange(.1,float(t.bounds[1,2]),.2);bad=[];summary=[];island_starts=[];prev=None
for z in levels:
 segments=trimesh.intersections.mesh_plane(t,plane_origin=[0,0,float(z)],plane_normal=[0,0,1])
 if len(segments)==0:bad.append(float(z));continue
 graph=collections.defaultdict(set);points={}
 for seg in segments:
  u,v=[tuple(np.round(q[:2],5))for q in seg]
  if u==v:continue
  graph[u].add(v);graph[v].add(u);points[u]=seg[0];points[v]=seg[1]
 assert all(len(q)==2 for q in graph.values()), ('section branch',z)
 loops=[];unused=set(graph)
 while unused:
  start=min(unused);seq=[start];previous=None;current=start
  while True:
   unused.discard(current);nxt=next(q for q in sorted(graph[current])if q!=previous)
   seq.append(nxt)
   if nxt==start:break
   previous,current=current,nxt
  loops.append(np.array([points[q]for q in seq]))
 polys=[]
 for loop in loops:
  assert np.linalg.norm(loop[0]-loop[-1])<1e-5
  q=Polygon(loop[:,:2]);assert q.is_valid and q.area>0
  polys.append(q)
 # Symmetric difference retains holes and disjoint columns; a union would fill holes.
 shape=polys[0]
 for q in polys[1:]:shape=shape.symmetric_difference(q)
 assert shape.is_valid and not shape.is_empty
 geoms=list(shape.geoms)if shape.geom_type=='MultiPolygon' else [shape]
 if prev is not None:
  starts=[g for g in geoms if g.intersection(prev.buffer(.02)).area<1e-5]
  if starts:island_starts.append({'z_display_mm':round(float(z),3),'islands':len(starts),'area_display_mm2':sum(g.area for g in starts)})
 prev=shape
 summary.append({'z_display_mm':round(float(z),3),'components':len(geoms),'area_display_mm2':round(float(shape.area),5),'minimum_component_area_display_mm2':round(min(q.area for q in geoms),5)})
assert not bad
# Columns intentionally appear as separate slice components but begin connected to body below.
assert not island_starts, island_starts
normals=t.face_normals;cent=t.triangles_center
mask=(normals[:,2]<-math.cos(math.radians(45)))&(cent[:,2]>.05)
overhang_area=float(t.area_faces[mask].sum())
report={'reload_source':'model.stl','stl_sha256':hashlib.sha256((root/'model.stl').read_bytes()).hexdigest(),'stl_triangle_order_and_coordinates_exact_to_authoritative_mesh':True,'vertices_after_weld':len(t.vertices),'triangles':len(t.faces),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'edge_manifold_all_incidence_2':True,'vertex_manifold_all_links_single_cycles':True,'connected_components':len(parts),'degenerate_triangles':0,'duplicate_triangles':0,'minimum_triangle_area_display_mm2':float(t.area_faces.min()),'euler_number':int(t.euler_number),'positive_volume_display_mm3':float(t.volume),'bounds_display_mm':t.bounds.tolist(),'maximum_stl_vs_npz_abs_coordinate_drift':float(np.max(np.abs(raw.triangles-D['vertices'][D['faces']]))),'slice_preflight':{'layer_height_scenario_mm':.2,'first_plane_mm':.1,'layers_checked':len(summary),'closed_valid_sections':len(summary),'new_unattached_component_starts':island_starts,'max_slice_components':max(x['components']for x in summary),'minimum_component_area_display_mm2':min(x['minimum_component_area_display_mm2']for x in summary),'method':'Exact triangle-plane intersection + Shapely closed polygons, odd-even rings; not actual extrusion toolpaths'},'overhang_preflight':{'criterion':'down-facing triangles >45 degrees from vertical, excluding build-plate bottom','area_display_mm2':overhang_area,'triangle_count':int(mask.sum()),'support_warning':True},'practical_features':json.loads((root/'parameters.json').read_text())['manufacturing'],'physical_print_test':False,'limitations':['Numerical mesh/slice checks do not guarantee adhesion, strength or support-free printing.','Use supports under the long curved gallery, tower lantern lintels, central lantern cap and overhangs; tune orientation, support removal and material.','Color-only window and trim boundaries are actual face assignments, not holes. Fine features may require enlargement or resin; lantern posts are model-thickened.','Solid massing model; no interior halls, basement, site grading, structural simulation or exact real-world scale.']}
(root/'qa'/'geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n');(root/'qa'/'layer-sections.json').write_text(json.dumps(summary,separators=(',',':'))+'\n');print(json.dumps(report,indent=2))
