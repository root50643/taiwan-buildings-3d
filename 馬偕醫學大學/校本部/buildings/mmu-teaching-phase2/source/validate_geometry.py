#!/usr/bin/env python3
"""Independent STL combinatorial/slice/open-ray screens, not printer certification."""
from pathlib import Path
import argparse,json
from collections import Counter,defaultdict
import numpy as np,trimesh,manifold3d as mf
from shapely.geometry import Polygon,GeometryCollection
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=a.out;(root/'qa').mkdir(exist_ok=True)
t=trimesh.load_mesh(root/'model.stl',process=True);edges=Counter(tuple(sorted((int(f[i]),int(f[(i+1)%3]))))for f in t.faces for i in range(3));links=defaultdict(list)
for f in t.faces:
 for i in range(3):links[int(f[i])].append((int(f[(i+1)%3]),int(f[(i+2)%3])))
bad=[]
for v,es in links.items():
 adj=defaultdict(set)
 for x,y in es:adj[x].add(y);adj[y].add(x)
 seen=set();todo=[next(iter(adj))]
 while todo:
  x=todo.pop()
  if x in seen:continue
  seen.add(x);todo.extend(adj[x]-seen)
 if len(seen)!=len(adj)or any(len(x)!=2 for x in adj.values()):bad.append(v)
s=mf.Manifold(mf.Mesh(np.asarray(t.vertices,dtype=np.float32),np.asarray(t.faces,dtype=np.uint32)));assert s.status()==mf.Error.NoError
above=s-mf.Manifold.cube([600,600,2.05]).translate([-300,-300,0]);above_components=len(above.decompose())
r={'artifact':'model.stl','vertices':len(t.vertices),'triangles':len(t.faces),'watertight':bool(t.is_watertight),'consistent_winding':bool(t.is_winding_consistent),'positive_volume_model_mm3':float(t.volume),'connected_shells':len(t.split(only_watertight=False)),'connected_shells_after_removing_display_base':above_components,'nonmanifold_edges':sum(n!=2 for n in edges.values()),'nonmanifold_vertex_links':len(bad),'degenerate_triangles':int((t.area_faces<1e-9).sum()),'duplicate_triangles':len(t.faces)-len(np.unique(np.sort(t.faces,axis=1),axis=0)),'bounds_model_mm':t.bounds.tolist(),'size_model_mm':t.extents.tolist(),'edge_incidence_histogram':dict(Counter(edges.values()))}
assert all(r[k]==0 for k in('nonmanifold_edges','nonmanifold_vertex_links','degenerate_triangles','duplicate_triangles'));assert r['connected_shells']==above_components==1 and r['watertight']and r['consistent_winding']and t.volume>0
(root/'qa/mesh-validation.json').write_text(json.dumps(r,indent=2)+'\n')
records=[];prev=None
for z in np.arange(.1,float(t.bounds[1,2]),.2):
 g=GeometryCollection()
 for poly in s.slice(float(z)).to_polygons():
  if len(poly)>2:g=g.symmetric_difference(Polygon(poly))
 assert g.is_valid and not g.is_empty
 regions=len(g.geoms)if hasattr(g,'geoms') else 1
 records.append({'z_model_mm':round(float(z),3),'area_model_mm2':round(g.area,5),'separate_regions':regions,'erosion_loss_at_0_8mm':round(g.difference(g.buffer(-.4).buffer(.4)).area,5),'erosion_loss_at_1_2mm':round(g.difference(g.buffer(-.6).buffer(.6)).area,5),'growth_outside_previous_plus_0_4mm':0 if prev is None else round(g.difference(prev.buffer(.4)).area,5)});prev=g
report={'type':'Geometric sections only; not a toolpath/physical print','section_step_model_mm':.2,'valid_nonempty_sections':len(records),'min_area_model_mm2':min(x['area_model_mm2']for x in records),'max_regions':max(x['separate_regions']for x in records),'max_growth_outside_previous_plus_0_4mm':max(x['growth_outside_previous_plus_0_4mm']for x in records),'minimum_designed_freestanding_section_model_mm':1.0,'minimum_trellis_section_model_mm':1.05,'material_relief_note':'0.26–0.35 mm attached glazing relief is not an isolated printable wall; color-boundary resolution is printer dependent','cautions':['Not support-free: D trellis, exposed lower galleries, rooftop cross beams, connectors and external stairs need slicer/bridging/support review.','265 × 161 mm display base may exceed common beds. Split in a slicer or use a larger bed; downscaling thins 1.0–1.4 mm rails.','No measured architectural scale; mm denotes this print object only.','3MF base-material colors require manual printer/extruder mapping; STL is monochrome.','No physical print or printer-specific toolpath was tested.'], 'records':records}
(root/'qa/slice-thickness-screen.json').write_text(json.dumps(report,indent=2)+'\n')
# Actual delivered STL raycasts through every major void and open rooftop system.
params=json.loads((root/'parameters.json').read_text());scale=params['plan_to_model']['scale'];ox,oy=params['plan_to_model']['origin']
def xy(x,y):return[(x-ox)*scale,(oy-y)*scale]
def hits(origin,direction):
 loc,_,_=t.ray.intersects_location(np.array([origin]),np.array([direction]),multiple_hits=True);return sorted(float(np.dot(q-np.array(origin),direction))for q in loc if np.dot(q-np.array(origin),direction)>1e-5)
checks=[]
for name,pt,maxz in [('main court',(260,300),2.01),('G–F slot',(150,150),2.01),('F–E lightwell',(375,90),2.01),('E–D open recess',(555,80),2.01),('E open roof bay',(450,240),58),('F framed setback',(190,120),59),('G framed setback',(17,160),59)]:
 x,y=xy(*pt);hh=hits([x,y,90],[0,0,-1]);assert hh;first=90-hh[0];ok=first<=maxz;assert ok,(name,first,maxz);checks.append({'opening':name,'ray_origin_model_mm':[x,y,90],'direction':[0,0,-1],'first_surface_z_model_mm':first,'allowed_max_surface_z':maxz,'pass':ok})
ang=np.radians(params['footprints']['D_rotation_degrees']);u=np.array([np.cos(ang),np.sin(ang)]);v=np.array([np.sin(ang),-np.cos(ang)]);origin=np.array(xy(*params['footprints']['D_origin']));du=params['footprints']['D_size'][0]
start=origin+u*(du+8)+v*9;hh=hits([*start,43],[-u[0],-u[1],0]);assert hh and hh[0]>5;checks.append({'opening':'D trellis mesh aperture','ray_origin_model_mm':[*start,43],'direction':[-u[0],-u[1],0],'first_hit_distance_model_mm':hh[0],'minimum_clear_distance_model_mm':5,'pass':True})
(root/'qa/opening-ray-validation.json').write_text(json.dumps({'input':'actual reloaded STL','all_pass':True,'checks':checks},indent=2)+'\n')
print(json.dumps(r,indent=2));print('Slices and all major opening rays PASS')
