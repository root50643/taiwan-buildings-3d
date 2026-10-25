#!/usr/bin/env python3
"""Exported geometry, section, clearance and determinism checks; not a physical print certificate."""
import argparse,pathlib,json,tempfile,subprocess,sys,hashlib
from collections import Counter,defaultdict
import numpy as np,trimesh,manifold3d as mf
from shapely.geometry import Polygon,GeometryCollection
ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);a=ap.parse_args();root=a.out;(root/'qa').mkdir(exist_ok=True)
D=np.load(root/'mesh-data.npz');m=trimesh.load_mesh(root/'tcu-daxi-gymnasium.stl',process=True)
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
r={'artifact':'tcu-daxi-gymnasium.stl','vertices':len(m.vertices),'triangles':len(m.faces),'closed_shells':len(m.split(only_watertight=False)),'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'positive_volume_mm3':float(m.volume),'edge_incidence_histogram':dict(Counter(edges.values())),'nonmanifold_edges':sum(n!=2 for n in edges.values()),'nonmanifold_vertex_links':len(bad),'degenerate_triangles':int((m.area_faces<1e-9).sum()),'duplicate_triangles':len(m.faces)-len(np.unique(np.sort(m.faces,axis=1),axis=0)),'size_model_mm':m.extents.tolist(),'bounds_model_mm':m.bounds.tolist(),'euler_characteristic':m.euler_number}
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
q={'type':'horizontal geometric section screen, NOT a slicer/toolpath/physical print','step_mm':.2,'valid_nonempty_sections':len(records),'maximum_regions':max(d['regions']for d in records),'maximum_growth_beyond_previous_plus_0_4mm_mm2':max(d['growth_beyond_previous_plus_0_4mm_mm2']for d in records),'minimum_isolated_post_diameter_model_mm':1.2,'parking_roof_skin_model_mm':1.0,'rooflight_cap_vertical_thickness_model_mm':1.0,'minimum_attached_frame_relief_width_model_mm':.35,'warnings':['Support and bridging assessment required under track arch bays, upper galleries, entrance portico, external stair and parking canopies.','Canopy posts are 1.2 model mm diameter; roof strips and raised cap are 1.0 mm thick, intentionally thickened. Do not downscale without new section and slicer tests.','Fine attached mullion relief is not a structural wall and may disappear with coarse nozzles.','Display base is 118 by 248 mm; check build-plate clearance, adhesion and support accessibility.','Watertightness does not certify printer settings, toolpaths or a physical print. No external slicer or printer was used.','Colour 3MF uses per-triangle base materials, not filament/extruder presets.','Morphological losses include corner erosion and are not a global minimum wall-thickness proof.'],'records':records}
(root/'qa/slice-thickness-screen.json').write_text(json.dumps(q,indent=2)+'\n')
# Explicit segment rays: do not count a hit beyond the named clearance segment.
checks=[
 ('track_arcade_true_open_approach',[-42,-84,12],[1,0,0],10,True),
 ('track_arcade_setback_backing',[-42,-84,12],[1,0,0],13,False),
 ('track_arcade_upper_arch_void',[-42,-84,21],[1,0,0],10,True),
 ('track_arcade_arch_spandrel_solid',[-42,-79,21],[1,0,0],6,False),
 ('road_arch_is_closed_glazing',[42,-84,18],[-1,0,0],7,False),
 ('road_low_rectangle_is_closed',[42,-84,8],[-1,0,0],7,False),
 ('road_upper_gallery_open_approach',[42,-80,36],[-1,0,0],9,True),
 ('road_upper_gallery_setback_glazing',[42,-80,36],[-1,0,0],13,False),
 ('track_upper_gallery_open_approach',[-42,-80,36],[1,0,0],9,True),
 ('canopy_central_aisle_open_to_sky',[48.5,-47,4],[0,0,1],30,True),
 ('canopy_central_aisle_open_longitudinally',[48.5,-103,7],[0,1,0],124,True),
 ('inner_parking_bay_open_under_roof',[41,-103,7],[0,1,0],121,True),
 ('outer_parking_bay_open_under_roof',[55,-103,7],[0,1,0],121,True),
 ('inner_parking_roof_present',[41,-47,5],[0,0,1],10,False),
 ('outer_parking_roof_present',[55,-47,5],[0,0,1],10,False),
 ('portico_open_approach',[0,140,15],[0,-1,0],35,True),
 ('portico_recessed_glazed_closure',[0,140,15],[0,-1,0],38,False),
 ('entrance_ramp_track_side',[-30,127,10],[0,0,-1],8,False),
 ('no_mirrored_road_side_entrance_ramp',[30,127,10],[0,0,-1],5,True),
 ('external_stair_daylight_beneath',[-50,50,8],[1,0,0],10,True),
 ('broad_roof_is_closed',[25,-35,80],[0,0,-1],20,False),
 ('narrow_cap_above_broad_roof',[0,-30,80],[0,0,-1],10,False),
 ('air_beside_narrow_cap',[18,-30,80],[0,0,-1],10,True)]
rr=[]
for name,start,direction,length,clear in checks:
 loc,idx,tri=m.ray.intersects_location([start],[direction],multiple_hits=True);dist=np.linalg.norm(np.asarray(loc).reshape((-1,3))-np.array(start),axis=1);hits=dist[(dist>1e-5)&(dist<length)]
 actual=len(hits)==0;assert actual==clear,(name,hits)
 rr.append({'name':name,'start_mm':start,'direction':direction,'segment_length_mm':length,'expected_clear':clear,'actual_clear':actual,'hits_within_segment':len(hits)})
(root/'qa/open-ray-validation.json').write_text(json.dumps({'all_expected_outcomes':True,'method':'Independent reloaded STL ray/triangle segment checks, including occupied controls','checks':rr},indent=2)+'\n')
# Independent occupied-point structural chord tests and a whole-surface normal screen.
def nearest(origin,direction):
 loc,idx,tri=m.ray.intersects_location([origin],[direction],multiple_hits=True)
 ds=np.linalg.norm(np.asarray(loc).reshape((-1,3))-np.asarray(origin),axis=1);ds=ds[ds>1e-5]
 return float(ds.min())if len(ds)else None
local=[]
for name,point,direction,minimum in [
 ('outer_canopy_post',[59.2,-98,7],[1,0,0],1.19),
 ('inner_canopy_roof',[41,-47,12.5],[0,0,1],.99),
 ('outer_canopy_roof',[55,-47,12.5],[0,0,1],.99),
 ('track_arcade_pier',[-35,-79,13],[0,1,0],2.99),
 ('upper_gallery_round_column',[-36.5,-71,36],[1,0,0],2.49),
 ('entrance_round_column',[33,115.6363636364,15],[1,0,0],2.69),
 ('external_stair_parapet',[-47,54,17.5],[1,0,0],.89)]:
 assert bool(m.contains([point])[0]),(name,'not inside structural solid')
 d=np.array(direction);left=nearest(point,d);right=nearest(point,-d);chord=left+right
 assert chord>=minimum,(name,chord,minimum)
 local.append({'feature':name,'inside_point_mm':point,'axis':direction,'measured_chord_mm':chord,'minimum_expected_mm':minimum,'pass':True})
# Sample evenly across final triangle IDs, not just selected construction components.
ids=np.unique(np.linspace(0,len(m.faces)-1,min(3000,len(m.faces))).astype(int));samples=[]
for i in ids:
 origin=m.triangles_center[i]-m.face_normals[i]*.0001;d=-m.face_normals[i];distance=nearest(origin,d)
 if distance is not None:samples.append(distance+.0001)
assert len(samples)==len(ids)
th={'method':'Reloaded STL: bidirectional chords at seven occupied structural points, plus inward face-normal rays from 3000 evenly distributed triangle centroids. A numerical screen, not an exact medial-axis global minimum thickness proof.', 'structural_chords':local,'global_surface_samples':len(samples),'global_chord_mm_percentiles':{str(p):float(np.percentile(samples,p))for p in [0,1,5,50,95,100]},'sampled_chords_under_0_8mm':sum(x<.8 for x in samples),'limitations':'Short chords can be attached trim, corners or near-grazing facets; hidden interior is a solid exterior abstraction. Print orientation, support removal and material limits still require a real slicer and printer test.'}
(root/'qa/thickness-ray-screen.json').write_text(json.dumps(th,indent=2)+'\n')
with tempfile.TemporaryDirectory(prefix='daxi-rebuild-')as tmp:
 subprocess.run([sys.executable,str(pathlib.Path(__file__).with_name('build_model.py')),'--out',tmp],check=True,capture_output=True)
 E=np.load(pathlib.Path(tmp)/'mesh-data.npz');same={k:bool(np.array_equal(D[k],E[k]))for k in ['vertices','faces','materials']};stl=(root/'tcu-daxi-gymnasium.stl').read_bytes()==(pathlib.Path(tmp)/'tcu-daxi-gymnasium.stl').read_bytes();assert all(same.values())and stl
(root/'qa/rebuild-validation.json').write_text(json.dumps({'fresh_process':True,'geometry_arrays_identical':same,'stl_byte_identical':stl},indent=2)+'\n')
print(json.dumps(r,indent=2));print('sections',len(records));print('rays',rr)
