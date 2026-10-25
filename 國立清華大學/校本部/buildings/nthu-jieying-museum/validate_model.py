#!/usr/bin/env python3
"""Exported geometry, section, clearance and determinism checks; not a physical print certificate."""
import argparse,pathlib,json,tempfile,subprocess,sys,hashlib
from collections import Counter,defaultdict
import numpy as np,trimesh,manifold3d as mf
from shapely.geometry import Polygon,GeometryCollection
ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);a=ap.parse_args();root=a.out;(root/'qa').mkdir(exist_ok=True)
D=np.load(root/'mesh-data.npz');m=trimesh.load_mesh(root/'nthu-jieying-museum.stl',process=True)
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
r={'artifact':'nthu-jieying-museum.stl','vertices':len(m.vertices),'triangles':len(m.faces),'closed_shells':len(m.split(only_watertight=False)),'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'positive_volume_mm3':float(m.volume),'edge_incidence_histogram':dict(Counter(edges.values())),'nonmanifold_edges':sum(n!=2 for n in edges.values()),'nonmanifold_vertex_links':len(bad),'degenerate_triangles':int((m.area_faces<1e-9).sum()),'duplicate_triangles':len(m.faces)-len(np.unique(np.sort(m.faces,axis=1),axis=0)),'size_model_mm':m.extents.tolist(),'bounds_model_mm':m.bounds.tolist(),'euler_characteristic':m.euler_number}
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
q={'type':'horizontal geometric section screen, NOT a slicer/toolpath/physical print','step_mm':.2,'valid_nonempty_sections':len(records),'maximum_regions':max(d['regions']for d in records),'maximum_growth_beyond_previous_plus_0_4mm_mm2':max(d['growth_beyond_previous_plus_0_4mm_mm2']for d in records),'rail_width_model_mm':.85,'rail_post_diameter_model_mm':.88,'mullion_diameter_model_mm':.86,'warnings':['The large open passage, upper overhang and gallery soffit require explicit slicer support/bridging review. Do not fill the passage just to avoid supports.','Terrace rails and window relief are delicate: 0.85–0.88 mm, scale and nozzle sensitive.','Straight exterior stair underside is filled down to the supporting base for robustness; not the exact structural slab underneath.','Display-only base is 200 by 168 mm. Confirm build-plate clearance and supports.','Watertightness does not certify printer settings, toolpaths, adhesion or a successful physical print.','Colour 3MF uses per-triangle base materials, not filament/extruder presets.','Morphological losses include corner erosion and are not a global minimum wall-thickness proof.'],'records':records}
(root/'qa/slice-thickness-screen.json').write_text(json.dumps(q,indent=2)+'\n')
# Explicit segment rays: do not count a hit beyond the named clearance segment.
checks=[
 ('true_passage_street_to_courtyard',[-12,86,14],[1,0,0],118,True),
 ('passage_clear_below_soffit',[32,86,15],[0,0,1],10,True),
 ('passage_has_upper_building',[32,86,15],[0,0,1],22,False),
 ('north_core_glazed_boundary',[36,80,12],[0,1,0],23,False),
 ('lower_irregular_core_boundary',[45,-8,12],[0,1,0],30,False),
 ('gallery_courtyard_glazing',[115,90,12],[0,1,0],28,False),
 ('courtyard_remains_outside',[120,50,12],[0,1,0],40,True),
 ('detached_farmhouse_context_excluded',[140,20,12],[0,1,0],35,True),
 ('oval_roof_aperture_open_above_recess',[48,36,51],[0,0,1],65,True),
 ('oval_aperture_has_disclosed_deep_closure',[48,36,51],[0,0,-1],4,False),
 ('first_roof_slit_open_above_recess',[30,51,53],[0,0,1],45,True),
 ('terminal_stair_present',[130,145,35],[0,0,-1],30,False),
 ('street_end_shoulder_free_above_lower_rim',[40,5,70],[0,0,-1],10,True),
 ('street_end_lower_roof_present',[40,5,70],[0,0,-1],20,False),
 ('setback_tall_end_rise_present',[40,24,110],[0,0,-1],30,False),
 ('second_roof_slit_remains_open',[67,82,52],[0,0,1],60,True)]

rr=[]
for name,start,direction,length,clear in checks:
 loc,idx,tri=m.ray.intersects_location([start],[direction],multiple_hits=True);dist=np.linalg.norm(np.asarray(loc).reshape((-1,3))-np.array(start),axis=1);hits=dist[(dist>1e-5)&(dist<length)]
 actual=len(hits)==0;assert actual==clear,(name,hits)
 rr.append({'name':name,'start_mm':start,'direction':direction,'segment_length_mm':length,'expected_clear':clear,'actual_clear':actual,'hits_within_segment':len(hits)})
(root/'qa/open-ray-validation.json').write_text(json.dumps({'all_expected_outcomes':True,'method':'Independent reloaded STL ray/triangle segment checks, including occupied controls','checks':rr},indent=2)+'\n')
# Independent vertical rays verify the separate main-roof stair rises inboard.
step_samples=[]
for x in [5.,12.,20.]:
 start=np.array([x,70.,110.]);loc,idx,tri=m.ray.intersects_location([start],[[0,0,-1]],multiple_hits=True);heights=loc[:,2];z=float(heights.max());step_samples.append({'x_mm':x,'y_mm':70.,'top_hit_z_mm':z})
assert all(step_samples[i+1]['top_hit_z_mm']>step_samples[i]['top_hit_z_mm']+2 for i in range(2))
assert 49<step_samples[0]['top_hit_z_mm']<60 and 62<step_samples[-1]['top_hit_z_mm']<68
(root/'qa/main-roof-sector-validation.json').write_text(json.dumps({'inboard_rising_step_profile_confirmed':True,'samples':step_samples,'scope':'Checks authored upper terrace continuity/profile, not measured real-world dimensions'},indent=2)+'\n')
with tempfile.TemporaryDirectory(prefix='nthu-rebuild-')as tmp:
 subprocess.run([sys.executable,str(pathlib.Path(__file__).with_name('build_model.py')),'--out',tmp],check=True,capture_output=True)
 E=np.load(pathlib.Path(tmp)/'mesh-data.npz');same={k:bool(np.array_equal(D[k],E[k]))for k in ['vertices','faces','materials']};stl=(root/'nthu-jieying-museum.stl').read_bytes()==(pathlib.Path(tmp)/'nthu-jieying-museum.stl').read_bytes();assert all(same.values())and stl
(root/'qa/rebuild-validation.json').write_text(json.dumps({'fresh_process':True,'geometry_arrays_identical':same,'stl_byte_identical':stl},indent=2)+'\n')
print(json.dumps(r,indent=2));print('sections',len(records));print('rays',rr)
