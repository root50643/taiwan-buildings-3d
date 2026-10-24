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
from scipy.spatial import cKDTree
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
 z=float(round(z,7)) # exact decimal layer centers, avoid cumulative arange noise
 segments=trimesh.intersections.mesh_plane(t,plane_origin=[0,0,float(z)],plane_normal=[0,0,1])
 if len(segments)==0:bad.append(float(z));continue
 # Weld computed segment endpoints by Euclidean tolerance rather than decimal
 # rounding: a point near a rounding half-bin can otherwise split into two nodes.
 rawpoints=segments.reshape(-1,3);parent=np.arange(len(rawpoints))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i,j in cKDTree(rawpoints[:,:2]).query_pairs(1e-7):
  ii,jj=find(i),find(j)
  if ii!=jj:parent[max(ii,jj)]=min(ii,jj)
 ids=np.array([find(i)for i in range(len(rawpoints))]);graph=collections.defaultdict(set);points={}
 for k in range(len(segments)):
  u,v=int(ids[2*k]),int(ids[2*k+1])
  if u==v:continue
  graph[u].add(v);graph[v].add(u);points[u]=rawpoints[u];points[v]=rawpoints[v]
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
  q=Polygon(loop[:,:2]);assert q.is_valid and q.area>0, (z, q.area, __import__('shapely.validation',fromlist=['explain_validity']).explain_validity(q))
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
# Actual segment/triangle tests prove the through-route was not replaced by a
# solid facade. Numpy Moller-Trumbore, not visual inference or extra dependencies.
def segment_hits(start,end):
 start=np.array(start,float);end=np.array(end,float);direction=end-start
 tri=t.triangles;e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
 h=np.cross(np.broadcast_to(direction,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h)
 valid=np.abs(det)>1e-10;inv=np.divide(1.,det,out=np.zeros_like(det),where=valid)
 ss=start-tri[:,0];uu=inv*np.einsum('ij,ij->i',ss,h);q=np.cross(ss,e1)
 vv=inv*np.einsum('j,ij->i',direction,q);tt=inv*np.einsum('ij,ij->i',e2,q)
 mask=valid&(uu>=-1e-9)&(vv>=-1e-9)&(uu+vv<=1+1e-9)&(tt>1e-8)&(tt<1-1e-8)
 return int(mask.sum())
segments=[{'name':'front porch open between columns before glazing','start':[44,-2,50],'end':[44,6.5,50]},{'name':'front low entry canopy approach','start':[60,-24,29],'end':[60,6.5,29]},{'name':'terrace balustrade aperture','start':[16,-29,24.2],'end':[16,-25.4,24.2]}]
for seg in segments:seg['triangle_hits']=segment_hits(seg['start'],seg['end']);assert seg['triangle_hits']==0,seg
# Closed neutral rear tested to prevent facade-fragment release.
closed=[{'name':'main rear exists','start':[60,95,50],'end':[60,80,50]},{'name':'lower front projection exists','start':[60,-34,18],'end':[60,-20,18]}]
for seg in closed:seg['triangle_hits']=segment_hits(seg['start'],seg['end']);assert seg['triangle_hits']>0,seg
(root/'qa'/'feature-validation.json').write_text(json.dumps({'method':'Actual delivered STL segment/triangle intersections','open_segments':segments,'closed_mass_segments':closed,'source_rule_triangles':{str(i):int((D['rule_indices']==i).sum())for i in range(11)},'all_pass':True,'limitations':'Sampled clear lines verify modeled openings, not building circulation, safety or structural certification.'},indent=2)+'\n')
report={'reload_source':'model.stl','stl_sha256':hashlib.sha256((root/'model.stl').read_bytes()).hexdigest(),'stl_triangle_order_and_coordinates_exact_to_authoritative_mesh':True,'vertices_after_weld':len(t.vertices),'triangles':len(t.faces),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'edge_manifold_all_incidence_2':True,'vertex_manifold_all_links_single_cycles':True,'connected_components':len(parts),'degenerate_triangles':0,'duplicate_triangles':0,'minimum_triangle_area_display_mm2':float(t.area_faces.min()),'euler_number':int(t.euler_number),'positive_volume_display_mm3':float(t.volume),'bounds_display_mm':t.bounds.tolist(),'maximum_stl_vs_npz_abs_coordinate_drift':float(np.max(np.abs(raw.triangles-D['vertices'][D['faces']]))),'slice_preflight':{'layer_height_scenario_mm':.2,'first_plane_mm':.1,'layers_checked':len(summary),'closed_valid_sections':len(summary),'new_unattached_component_starts':island_starts,'max_slice_components':max(x['components']for x in summary),'minimum_component_area_display_mm2':min(x['minimum_component_area_display_mm2']for x in summary),'method':'Exact decimal-centered triangle-plane intersection; endpoint weld tolerance 1e-7 mm; Shapely closed polygons with odd-even rings; not extrusion toolpaths'},'overhang_preflight':{'criterion':'down-facing triangles >45 degrees from vertical, excluding build-plate bottom','area_display_mm2':overhang_area,'triangle_count':int(mask.sum()),'support_warning':True},'practical_features':json.loads((root/'parameters.json').read_text())['manufacturing'],'physical_print_test':False,'limitations':['Numerical mesh/slice checks do not guarantee adhesion, strength or support-free printing.','Supports need assessment under front fascia, entrance canopies, terraces and balustrades.','Color-only window and trim boundaries are actual face assignments, not holes. Fine features may require enlargement or resin; frames and rails are model-thickened.','Whole connected aboveground 2021–2022 installed-PV representative exterior; no interior, basement, surveyed grading or structural simulation. No real-world scale established.']}
(root/'qa'/'geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n');(root/'qa'/'layer-sections.json').write_text(json.dumps(summary,separators=(',',':'))+'\n');print(json.dumps(report,indent=2))
