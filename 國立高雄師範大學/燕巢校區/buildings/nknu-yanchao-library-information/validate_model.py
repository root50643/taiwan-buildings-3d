#!/usr/bin/env python3
"""Exported geometry, section, clearance and determinism checks; not a physical print certificate."""
import argparse,pathlib,json,tempfile,subprocess,sys,hashlib
from collections import Counter,defaultdict
import numpy as np,trimesh,manifold3d as mf
from shapely.geometry import Polygon,GeometryCollection
ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);a=ap.parse_args();root=a.out;(root/'qa').mkdir(exist_ok=True)
D=np.load(root/'mesh-data.npz');m=trimesh.load_mesh(root/'nknu-yanchao-library-information.stl',process=True)
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
r={'artifact':'nknu-yanchao-library-information.stl','vertices':len(m.vertices),'triangles':len(m.faces),'closed_shells':len(m.split(only_watertight=False)),'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'positive_volume_mm3':float(m.volume),'edge_incidence_histogram':dict(Counter(edges.values())),'nonmanifold_edges':sum(n!=2 for n in edges.values()),'nonmanifold_vertex_links':len(bad),'degenerate_triangles':int((m.area_faces<1e-9).sum()),'duplicate_triangles':len(m.faces)-len(np.unique(np.sort(m.faces,axis=1),axis=0)),'size_model_mm':m.extents.tolist(),'bounds_model_mm':m.bounds.tolist(),'euler_characteristic':m.euler_number}
assert r['closed_shells']==1 and r['watertight']and r['winding_consistent']and r['positive_volume_mm3']>0
assert not any(r[k]for k in ['nonmanifold_edges','nonmanifold_vertex_links','degenerate_triangles','duplicate_triangles'])
(root/'qa/mesh-validation.json').write_text(json.dumps(r,indent=2)+'\n')
s=mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)));assert s.status()==mf.Error.NoError
records=[];prev=None
for z in np.arange(m.bounds[0,2]+.1,m.bounds[1,2],.2):
 g=GeometryCollection()
 for poly in s.slice(float(z)).to_polygons():
  if len(poly)>2:g=g.symmetric_difference(Polygon(poly))
 assert g.is_valid and not g.is_empty
 c=list(g.geoms)if hasattr(g,'geoms')else[g]
 records.append({'z_mm':round(float(z),3),'area_mm2':round(g.area,4),'regions':len(c),'morphological_loss_at_0_8mm_mm2':round(g.difference(g.buffer(-.4).buffer(.4)).area,4),'morphological_loss_at_1_2mm_mm2':round(g.difference(g.buffer(-.6).buffer(.6)).area,4),'growth_beyond_previous_plus_0_4mm_mm2':0 if prev is None else round(g.difference(prev.buffer(.4)).area,4)})
 prev=g
q={'type':'horizontal geometric section screen, NOT a slicer/toolpath/physical print','step_mm':.2,'valid_nonempty_sections':len(records),'maximum_regions':max(d['regions']for d in records),'maximum_growth_beyond_previous_plus_0_4mm_mm2':max(d['growth_beyond_previous_plus_0_4mm_mm2']for d in records),'minimum_representative_pale_member_diameter_mm':.60,'warnings':['Entrance underpass, roof perimeter canopy and circular rooflight overhang need explicit support/bridging review. Do not fill the passage to avoid supports.','Pale small members approximately 0.60–0.75 mm are fragile and scale/nozzle sensitive; this model is not certified FFF-print-ready.','Stair undersides and exterior-envelope internals are filled for fabrication; no interior, basement or structural detail is claimed.','245 by 215 mm display support is not terrain or a measured plinth. Verify build-plate capacity.','Colour 3MF carries per-triangle base materials, not filament or extruder presets.','Morphological losses include corner erosion and are not a global minimum-wall-thickness proof.'],'records':records}
(root/'qa/slice-thickness-screen.json').write_text(json.dumps(q,indent=2)+'\n')
# Independent reloaded-STL segment rays, using architectural-metre-equivalent probes.
S=2.5
checks=[
 ('front_underpass_cross_route',[-10,-32,2.5],[1,0,0],32,True),
 ('front_underpass_below_slab',[5,-32,2.5],[0,0,1],1.8,True),
 ('front_terrace_slab_occupied_control',[5,-32,2.5],[0,0,1],3.0,False),
 ('front_open_upper_terrace',[5,-32,5.6],[0,0,1],9.5,True),
 ('front_glazed_entry',[5,-28,7.0],[0,1,0],7,False),
 ('rear_lowest_1F_glazed_doors',[0,20,2.2],[0,-1,0],8,False),
 ('rear_upper_glazed_band',[0,20,7.5],[0,-1,0],8,False),
 ('rear_terrace_above_shallow_steps',[0,19,1.0],[0,0,1],8,True),
 ('rear_curved_canopy',[0,15.1,3],[0,0,1],2.2,False),
 ('right_roof_canopy_open_gap',[40,0,14.0],[1,0,0],4,True),
 ('right_roof_canopy_band_present',[40,0,14.55],[1,0,0],4,False),
 ('circular_rooflight_recess_open_above_glazing',[0,0,13.4],[0,0,1],4,True),
 ('circular_rooflight_glazed_closure',[0,0,13.4],[0,0,-1],1,False),
 ('left_full_skewed_roof_field',[-30,-10,16],[0,0,-1],4,False),
 ('right_full_roof_field',[25,0,16],[0,0,-1],4,False),
 ('right_external_escape_stair',[42.6,-15,8],[0,0,-1],8,False),
 ('rear_external_escape_stair',[28,24.75,8],[0,0,-1],8,False),
 ('left_paired_entrance_stair',[-4.15,-47.8,6],[0,0,-1],6,False),
 ('right_paired_entrance_stair',[20.6,-43.7,6],[0,0,-1],6,False)]
def segment(mesh,start,direction,length):
 start=np.array(start)*S;length*=S
 loc,idx,tri=mesh.ray.intersects_location([start],[direction],multiple_hits=True);dist=np.linalg.norm(np.asarray(loc).reshape((-1,3))-start,axis=1);hits=dist[(dist>1e-5)&(dist<length)];return len(hits)==0,len(hits)
rr=[]
for name,start,direction,length,clear in checks:
 actual,hits=segment(m,start,direction,length);assert actual==clear,(name,hits)
 rr.append({'name':name,'start_model_mm':(np.array(start)*S).tolist(),'direction':direction,'segment_length_model_mm':length*S,'expected_clear':clear,'actual_clear':actual,'hits_within_segment':hits})
# Deliberately insert a blocking plate into an independent disposable triangle fixture.
block=trimesh.creation.box(extents=[.5*S,4*S,3*S]);block.apply_translation([5*S,-32*S,2.5*S]);mutant=trimesh.util.concatenate([m,block]);negative_clear,negative_hits=segment(mutant,[-10,-32,2.5],[1,0,0],32);assert not negative_clear and negative_hits>=2
(root/'qa/open-ray-validation.json').write_text(json.dumps({'all_expected_outcomes':True,'method':'Independent reloaded STL ray/triangle segment checks with occupied controls and actual injected-underpass-blocker negative fixture','checks':rr,'negative_control':{'injected_underpass_blocker_detected':True,'hits':negative_hits,'deliverable_modified':False}},indent=2)+'\n')
# Actual stair-top ray profiles, with known display closure excluded from the samples.
profiles=[]
for name,a,b in [('left',[-5.9,-53.8],[-2.4,-41.8]),('right',[24.5,-48.9],[16.7,-38.5])]:
 samples=[]
 for t in [.12,.32,.52,.72,.90]:
  q=np.array(a)*(1-t)+np.array(b)*t;start=np.array([q[0]*S,q[1]*S,20*S]);loc,idx,tri=m.ray.intersects_location([start],[[0,0,-1]],multiple_hits=True);top=float(loc[:,2].max());samples.append({'t':t,'top_z_model_mm':top})
 assert all(samples[i+1]['top_z_model_mm']>samples[i]['top_z_model_mm']+.1 for i in range(4)),(name,samples)
 profiles.append({'name':name,'samples':samples})
(root/'qa/stair-profile-validation.json').write_text(json.dumps({'paired_entrance_stairs_rise_monotonically':True,'profiles':profiles,'exact_architectural_risers_not_claimed':True},indent=2)+'\n')
with tempfile.TemporaryDirectory(prefix='nknu-rebuild-')as tmp:
 subprocess.run([sys.executable,str(pathlib.Path(__file__).with_name('build_model.py')),'--out',tmp],check=True,capture_output=True)
 E=np.load(pathlib.Path(tmp)/'mesh-data.npz');same={k:bool(np.array_equal(D[k],E[k]))for k in ['vertices','faces','materials']};stl=(root/'nknu-yanchao-library-information.stl').read_bytes()==(pathlib.Path(tmp)/'nknu-yanchao-library-information.stl').read_bytes();assert all(same.values())and stl
(root/'qa/rebuild-validation.json').write_text(json.dumps({'fresh_process':True,'geometry_arrays_identical':same,'stl_byte_identical':stl},indent=2)+'\n')
print(json.dumps(r,indent=2));print('sections',len(records));print('rays',len(rr))
