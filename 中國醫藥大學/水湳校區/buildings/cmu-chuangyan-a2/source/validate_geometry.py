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
levels=np.arange(.113,float(t.bounds[1,2]),.2);bad=[];summary=[];island_starts=[];prev=None
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
 for i,j in cKDTree(rawpoints[:,:2]).query_pairs(2e-6):
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
  q=Polygon(loop[:,:2]);assert q.is_valid and q.area>0
  polys.append(q)
 # Symmetric difference retains holes and disjoint columns; a union would fill holes.
 shape=polys[0]
 for q in polys[1:]:shape=shape.symmetric_difference(q)
 assert shape.is_valid and not shape.is_empty
 geoms=list(shape.geoms)if shape.geom_type=='MultiPolygon' else [shape]
 if prev is not None:
  starts=[g for g in geoms if g.intersection(prev.buffer(.02)).area<1e-5]
  if starts:island_starts.append({'z_display_mm':round(float(z),3),'islands':len(starts),'area_display_mm2':sum(g.area for g in starts),'component_xy_bounds_display_mm':[list(g.bounds)for g in starts]})
 prev=shape
 summary.append({'z_display_mm':round(float(z),3),'components':len(geoms),'area_display_mm2':round(float(shape.area),5),'minimum_component_area_display_mm2':round(min(q.area for q in geoms),5)})
assert not bad
# Exterior stair landings can begin as unsupported slice islands. Preserve and report
# them honestly: a connected manifold is not a support-free print certificate.
unsupported_start_requires_support=bool(island_starts)
normals=t.face_normals;cent=t.triangles_center
mask=(normals[:,2]<-math.cos(math.radians(45)))&(cent[:,2]>.05)
overhang_area=float(t.area_faces[mask].sum())
# Actual segment/triangle intersections, without optional ray accelerator packages.
def segment_hits(start,end):
 start=np.array(start,float);direction=np.array(end,float)-start;tri=t.triangles;e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(np.broadcast_to(direction,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h);valid=np.abs(det)>1e-10;inv=np.divide(1.,det,out=np.zeros_like(det),where=valid);ss=start-tri[:,0];uu=inv*np.einsum('ij,ij->i',ss,h);q=np.cross(ss,e1);vv=inv*np.einsum('j,ij->i',direction,q);tt=inv*np.einsum('ij,ij->i',e2,q);sel=valid&(uu>=-1e-9)&(vv>=-1e-9)&(uu+vv<=1+1e-9)&(tt>1e-8)&(tt<1-1e-8);return sorted(set(np.round(tt[sel],8)))
P=json.loads((root/'parameters.json').read_text());ZS=P['base']['thickness'];E=P['eye'];ecx=E['center_x'];ecz=E['center_z']+ZS
segments=[{'name':'ground through-passage middle','start':[8,-50,8],'end':[8,55,8],'expect':'clear'}, {'name':'upper ground arch clearance','start':[8,-50,22],'end':[8,55,22],'expect':'clear'}, {'name':'eye mouth into actual concave recess','start':[ecx,-45,ecz],'end':[ecx,-17,ecz],'expect':'clear'}, {'name':'eye has backwall not whole-building tunnel','start':[ecx,-45,ecz],'end':[ecx,45,ecz],'expect':'blocked'}, {'name':'western oval foyer support retained','start':[-29,-50,9],'end':[-29,55,9],'expect':'blocked'}, {'name':'right offset core retained','start':[32,-50,9],'end':[32,55,9],'expect':'blocked'}, {'name':'rear surface at eye elevation is not mirrored opening','start':[ecx,50,ecz],'end':[ecx,20,ecz],'expect':'blocked'}]
for seg in segments:
 hits=segment_hits(seg['start'],seg['end']);seg['intersection_distinct_t']=hits;seg['pass']=(len(hits)==0)if seg['expect']=='clear'else(len(hits)>0);assert seg['pass'],seg
# Different actual delivered horizontal slices: ground, roof, and high double lobe.
slices=[]
for name,z in [('ground',9.2),('upper_envelope',89.5),('roof',171.7),('raised_double_lobed_screen',181.2)]:
 lines=trimesh.intersections.mesh_plane(t,plane_origin=[0,0,z],plane_normal=[0,0,1]);assert len(lines)>0
 bounds=np.array([lines.reshape(-1,3).min(axis=0),lines.reshape(-1,3).max(axis=0)])
 north_samples=[]
 for x in[-63,0,62]:
  ys=[]
  for aa,bb in lines:
   if max(aa[0],bb[0])<x-4 or min(aa[0],bb[0])>x+4:continue
   if abs(bb[0]-aa[0])<1e-9:ys.extend([float(aa[1]),float(bb[1])]);continue
   f0=max(0,min((x-4-aa[0])/(bb[0]-aa[0]),(x+4-aa[0])/(bb[0]-aa[0])));f1=min(1,max((x-4-aa[0])/(bb[0]-aa[0]),(x+4-aa[0])/(bb[0]-aa[0])))
   if f0<=f1:ys.extend([float(aa[1]+f*(bb[1]-aa[1]))for f in[f0,f1]])
  north_samples.append({'x':x,'sampling_strip_half_width_mm':4,'max_north_y':max(ys)if ys else None})
 slices.append({'name':name,'z_display_mm':z,'segment_count':len(lines),'bounds_display_mm':bounds.tolist(),'north_samples':north_samples})
assert slices[2]['north_samples'][0]['max_north_y']>slices[2]['north_samples'][1]['max_north_y']+3
assert slices[2]['north_samples'][2]['max_north_y']>slices[2]['north_samples'][1]['max_north_y']+3
assert slices[3]['north_samples'][0]['max_north_y']>slices[3]['north_samples'][1]['max_north_y']+3
assert slices[3]['north_samples'][2]['max_north_y']>slices[3]['north_samples'][1]['max_north_y']+3
(root/'qa/feature-validation.json').write_text(json.dumps({'method':'Delivered STL triangle intersections, not construction labels','segments':segments,'separate_slices':slices,'all_pass':True,'limitations':'Sampled lines verify modeled voids and retained masses only; not building circulation or safety certification.'},indent=2)+'\n')
report={'reload_source':'model.stl','stl_sha256':hashlib.sha256((root/'model.stl').read_bytes()).hexdigest(),'stl_triangle_order_and_coordinates_exact_to_authoritative_mesh':True,'vertices_after_weld':len(t.vertices),'triangles':len(t.faces),'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'edge_manifold_all_incidence_2':True,'vertex_manifold_all_links_single_cycles':True,'connected_components':len(parts),'degenerate_triangles':0,'duplicate_triangles':0,'minimum_triangle_area_display_mm2':float(t.area_faces.min()),'euler_number':int(t.euler_number),'positive_volume_display_mm3':float(t.volume),'bounds_display_mm':t.bounds.tolist(),'slice_preflight':{'layer_height_scenario_mm':.2,'first_plane_mm':.113,'layers_checked':len(summary),'closed_valid_sections':len(summary),'new_unattached_component_starts':island_starts,'unsupported_start_requires_support':unsupported_start_requires_support,'max_slice_components':max(x['components']for x in summary),'minimum_component_area_display_mm2':min(x['minimum_component_area_display_mm2']for x in summary),'method':'Decimal-centered planes at 0.113 + n*0.2 mm avoid exact tangencies at analytic construction vertices; triangle-plane intersections; endpoint weld 2e-6 mm; closed Shapely polygons with odd-even rings, not extrusion toolpaths'},'overhang_preflight':{'criterion':'down-facing >45 degrees from vertical excluding buildplate bottom','area_display_mm2':overhang_area,'triangle_count':int(mask.sum()),'support_warning':True},'practical_features':P['manufacturing'],'physical_print_test':False,'limitations':['Not support-free or a qualified toolpath. Thin paired bands, eye recess, passage arch and roof screen require support/fragility assessment.','Opaque glazing and simplified upper rear screen, PV mounting heights, room filling and normalized dimensions are not measured as-built detail.','Manufacturing dimensions do not guarantee a lower bound on all small color patches created at intersections.']}
(root/'qa/geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n');(root/'qa/layer-sections.json').write_text(json.dumps(summary,separators=(',',':'))+'\n');print(json.dumps(report,indent=2))
