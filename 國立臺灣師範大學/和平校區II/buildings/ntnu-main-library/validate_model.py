#!/usr/bin/env python3
"""Exported geometry, section, clearance and determinism checks; not a physical print certificate."""
import argparse,pathlib,json,tempfile,subprocess,sys,hashlib
from collections import Counter,defaultdict
import numpy as np,trimesh,manifold3d as mf
from shapely.geometry import Polygon,GeometryCollection
ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);a=ap.parse_args();root=a.out;(root/'qa').mkdir(exist_ok=True)
D=np.load(root/'mesh-data.npz');m=trimesh.load_mesh(root/'ntnu-main-library.stl',process=True)
edges=Counter(tuple(sorted((int(f[i]),int(f[(i+1)%3]))))for f in m.faces for i in range(3));links=defaultdict(list)
for f in m.faces:
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
 if len(seen)!=len(adj)or any(len(s)!=2 for s in adj.values()):bad.append(v)
r={'artifact':'ntnu-main-library.stl','vertices':len(m.vertices),'triangles':len(m.faces),'closed_shells':len(m.split(only_watertight=False)),'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'positive_volume_mm3':float(m.volume),'edge_incidence_histogram':dict(Counter(edges.values())),'nonmanifold_edges':sum(n!=2 for n in edges.values()),'nonmanifold_vertex_links':len(bad),'degenerate_triangles':int((m.area_faces<1e-9).sum()),'duplicate_triangles':len(m.faces)-len(np.unique(np.sort(m.faces,axis=1),axis=0)),'size_model_mm':m.extents.tolist(),'bounds_model_mm':m.bounds.tolist(),'euler_characteristic':m.euler_number}
assert r['closed_shells']==1 and r['watertight']and r['winding_consistent']and r['positive_volume_mm3']>0
assert not any(r[k]for k in ['nonmanifold_edges','nonmanifold_vertex_links','degenerate_triangles','duplicate_triangles'])
(root/'qa/mesh-validation.json').write_text(json.dumps(r,indent=2)+'\n')
s=mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)));assert s.status()==mf.Error.NoError
records=[];prev=None
for z in np.arange(.1,m.bounds[1,2],.2):
 g=GeometryCollection()
 for poly in s.slice(float(z)).to_polygons():
  if len(poly)>2:g=g.symmetric_difference(Polygon(poly))
 assert g.is_valid and not g.is_empty
 c=list(g.geoms)if hasattr(g,'geoms')else[g]
 records.append({'z_mm':round(float(z),3),'area_mm2':round(g.area,4),'regions':len(c),'morphological_loss_at_0_8mm_mm2':round(g.difference(g.buffer(-.4).buffer(.4)).area,4),'morphological_loss_at_1_2mm_mm2':round(g.difference(g.buffer(-.6).buffer(.6)).area,4),'growth_beyond_previous_plus_0_4mm_mm2':0 if prev is None else round(g.difference(prev.buffer(.4)).area,4)})
 prev=g
q={'type':'horizontal geometric section screen, NOT a slicer/toolpath/physical print','step_mm':.2,'valid_nonempty_sections':len(records),'maximum_regions':max(d['regions']for d in records),'maximum_growth_beyond_previous_plus_0_4mm_mm2':max(d['growth_beyond_previous_plus_0_4mm_mm2']for d in records),'curved_mullion_relief_width_model_mm_approx':.365,'straight_mullion_width_model_mm':.44,'mullion_note':'Raised attached relief; not isolated structural walls. Colour skins overlap support mass.','warnings':['Support and bridging assessment required beneath north recessed soffit, rear pocket soffits and bookstore gate header.','Fine attached mullion relief is scale-sensitive and may disappear with coarse nozzles.','Display plinth is 230 by 151 model mm; check build-plate clearance or rescale with new slicer tests.','Watertightness does not certify printer settings, toolpaths, adhesion or a successful physical print.','Colour 3MF uses per-triangle base materials, not filament/extruder presets.','Morphological losses include corner erosion and are not a global minimum wall-thickness proof.'],'records':records}
(root/'qa/slice-thickness-screen.json').write_text(json.dumps(q,indent=2)+'\n')
# Explicit segment rays: do not count a hit beyond the named clearance segment.
checks=[
 ('west_pocket_open_approach',[-50,-49,12],[0,1,0],19,True),
 ('west_pocket_backing_closes_not_tunnel',[-50,-49,12],[0,1,0],24,False),
 ('west_pocket_open_below_soffit',[-50,-35,12],[0,0,1],7,True),
 ('west_pocket_closed_by_second_floor',[-50,-35,12],[0,0,1],10,False),
 ('east_pocket_setback_before_glass',[50,-39,12],[0,1,0],11,True),
 ('east_pocket_glazed_backing',[50,-39,12],[0,1,0],17,False),
 ('south_continuous_upper_bar',[-50,-49,30],[0,1,0],14,False),
 ('north_low_glazing_setback_clearance',[0,73,28],[0,-1,0],6,True),
 ('north_low_glazing_closure',[0,73,28],[0,-1,0],11,False),
 ('covered_atrium_not_open_exterior_court',[0,20,155],[0,0,-1],17,False),
 ('above_atrium_free_air',[0,20,155],[0,0,-1],10,True)]
rr=[]
for name,start,direction,length,clear in checks:
 loc,idx,tri=m.ray.intersects_location([start],[direction],multiple_hits=True);dist=np.linalg.norm(np.asarray(loc).reshape((-1,3))-np.array(start),axis=1);hits=dist[(dist>1e-5)&(dist<length)]
 actual=len(hits)==0;assert actual==clear,(name,hits)
 rr.append({'name':name,'start_mm':start,'direction':direction,'segment_length_mm':length,'expected_clear':clear,'actual_clear':actual,'hits_within_segment':len(hits)})
(root/'qa/open-ray-validation.json').write_text(json.dumps({'all_expected_outcomes':True,'method':'Independent reloaded STL ray/triangle segment checks, including occupied controls','checks':rr},indent=2)+'\n')
with tempfile.TemporaryDirectory(prefix='ntnu-rebuild-')as tmp:
 subprocess.run([sys.executable,str(pathlib.Path(__file__).with_name('build_model.py')),'--out',tmp],check=True,capture_output=True)
 E=np.load(pathlib.Path(tmp)/'mesh-data.npz');same={k:bool(np.array_equal(D[k],E[k]))for k in ['vertices','faces','materials']};stl=(root/'ntnu-main-library.stl').read_bytes()==(pathlib.Path(tmp)/'ntnu-main-library.stl').read_bytes();assert all(same.values())and stl
(root/'qa/rebuild-validation.json').write_text(json.dumps({'fresh_process':True,'geometry_arrays_identical':same,'stl_byte_identical':stl},indent=2)+'\n')
print(json.dumps(r,indent=2));print('sections',len(records));print('rays',rr)
