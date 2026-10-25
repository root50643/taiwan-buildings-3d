#!/usr/bin/env python3
"""Delivered STL topology, geometric sections and public explicit gap probes.

No physical printing or global minimum wall thickness is claimed. Probe coordinates
are model millimetres and are public, independently reloaded-STL checks.
"""
import argparse,pathlib,json,tempfile,subprocess,sys,hashlib
import numpy as np,trimesh,manifold3d as mf
from shapely.geometry import Polygon,GeometryCollection
from mesh_topology import check_topology

ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent)
ap.add_argument('--probes',type=pathlib.Path,default=pathlib.Path(__file__).with_name('qa-probes.json'))
a=ap.parse_args();root=a.out;(root/'qa').mkdir(exist_ok=True)
probes=json.loads(a.probes.read_text());D=np.load(root/'mesh-data.npz')
path=root/'xiangshan-whole-2010.stl';sha=hashlib.sha256(path.read_bytes()).hexdigest()
m=trimesh.load_mesh(path,process=True);r=check_topology(m.vertices,m.faces,path.name)
r['stl_sha256']=sha;r['reloaded_stl_triangles_match_public_arrays']=bool(np.array_equal(m.triangles,D['vertices'][D['faces']]))
assert r['all_pass'] and r['reloaded_stl_triangles_match_public_arrays'],r
assert len(D['materials'])==len(D['faces'])
palette=json.loads((root/'editable-parts.json').read_text())['palette']
assert set(map(int,D['materials']))==set(range(len(palette))),'Every declared colour must be present; indices must be valid'
(root/'qa/mesh-validation.json').write_text(json.dumps(r,indent=2)+'\n')
s=mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)));assert s.status()==mf.Error.NoError
records=[];prev=None;step=float(probes.get('section_step_mm',.2));assert 0<step<=.4
for z in np.arange(m.bounds[0,2]+step/2,m.bounds[1,2],step):
 g=GeometryCollection()
 for poly in s.slice(float(z)).to_polygons():
  if len(poly)>2:g=g.symmetric_difference(Polygon(poly))
 assert g.is_valid and not g.is_empty
 c=list(g.geoms)if hasattr(g,'geoms')else[g]
 records.append({'z_mm':round(float(z),5),'area_mm2':round(g.area,5),'regions':len(c),
  'morphological_loss_at_0_8mm_mm2':round(g.difference(g.buffer(-.4).buffer(.4)).area,5),
  'morphological_loss_at_1_2mm_mm2':round(g.difference(g.buffer(-.6).buffer(.6)).area,5),
  'growth_beyond_previous_plus_0_4mm_mm2':0 if prev is None else round(g.difference(prev.buffer(.4)).area,5)})
 prev=g
q={'stl_sha256':sha,'type':'Horizontal geometric section screen, NOT a slicer/toolpath/physical print',
 'step_mm':step,'valid_nonempty_sections':len(records),'maximum_regions':max(d['regions']for d in records),
 'maximum_growth_beyond_previous_plus_0_4mm_mm2':max(d['growth_beyond_previous_plus_0_4mm_mm2']for d in records),
 'warnings':probes['print_warnings']+['Morphological losses include corner erosion and are not a global minimum-wall-thickness proof.'],
 'records':records}
(root/'qa/slice-thickness-screen.json').write_text(json.dumps(q,indent=2)+'\n')

def segment(mesh,start,direction,length):
 start=np.asarray(start,float);direction=np.asarray(direction,float);direction/=np.linalg.norm(direction)
 loc,idx,tri=mesh.ray.intersects_location([start],[direction],multiple_hits=True)
 distance=np.linalg.norm(np.asarray(loc).reshape((-1,3))-start,axis=1)
 hits=distance[(distance>1e-5)&(distance<length-1e-5)]
 occupied=mesh.contains([start+direction*1e-4,start+direction*length*.5,start+direction*(length-1e-4)])
 return bool(len(hits)==0 and not occupied.any()),len(hits),int(occupied.sum())

rr=[];checks=probes['gap_rays'];assert len(checks)>=8
assert any(q['expected_clear']for q in checks) and any(not q['expected_clear']for q in checks)
for c in checks:
 actual,hits,inside=segment(m,c['start_model_mm'],c['direction'],c['segment_length_model_mm'])
 assert actual==c['expected_clear'],(c['name'],actual,hits,inside)
 rr.append(dict(c,actual_clear=actual,hits_within_segment=hits,occupied_sample_points=inside))
neg=probes['injected_gap_blocker'];control=next(q for q in checks if q['name']==neg['ray_name']);assert control['expected_clear']
block=trimesh.creation.box(extents=neg['box_extents_model_mm']);block.apply_translation(neg['box_center_model_mm'])
mutant=trimesh.util.concatenate([m,block]);clear,hits,inside=segment(mutant,control['start_model_mm'],control['direction'],control['segment_length_model_mm'])
assert not clear and (hits>0 or inside>0)
(root/'qa/open-ray-validation.json').write_text(json.dumps({'stl_sha256':sha,'all_expected_outcomes':True,
 'method':'Independent reloaded-STL segment ray intersections plus interior point checks; occupied controls and actual injected-blocker negative fixture',
 'checks':rr,'negative_control':{'injected_underpass_blocker_detected':True,'ray_name':control['name'],
 'hits':hits,'occupied_sample_points':inside,'deliverable_modified':False}},indent=2)+'\n')

profiles=[]
for p in probes['rising_surface_profiles']:
 samples=[]
 if 'sample_xy_model_mm' in p:
  xy_samples=[(i/(len(p['sample_xy_model_mm'])-1),np.asarray(xy,float))for i,xy in enumerate(p['sample_xy_model_mm'])]
 else:
  aa=np.array(p['start_xy_model_mm']);bb=np.array(p['end_xy_model_mm'])
  xy_samples=[(t,aa*(1-t)+bb*t)for t in p.get('sample_t',[.12,.32,.52,.72,.9])]
 for t,xy in xy_samples:
  start=[*xy,p['ray_top_z_model_mm']]
  loc,idx,tri=m.ray.intersects_location([start],[[0,0,-1]],multiple_hits=True);assert len(loc)
  samples.append({'t':t,'top_z_model_mm':float(loc[:,2].max())})
 assert len(samples)>=4 and all(samples[i+1]['top_z_model_mm']>samples[i]['top_z_model_mm']+.02 for i in range(len(samples)-1)),(p['name'],samples)
 profiles.append({'name':p['name'],'samples':samples})
assert profiles,'At least one attached curved-ramp or stair profile must be checked'
(root/'qa/surface-profile-validation.json').write_text(json.dumps({'stl_sha256':sha,'all_profiles_rise_monotonically':True,
 'profiles':profiles,'exact_architectural_risers_or_survey_slopes_not_claimed':True},indent=2)+'\n')
# The two inland roof terminations must really touch their thin local grade.
joins=[]
for probe in probes['grade_join_points']:
 occupied=m.contains(probe['points_model_mm']);assert occupied.all(),(probe,occupied)
 joins.append(dict(probe,inside_solid=occupied.tolist()))
lo=trimesh.creation.box([4,4,.18]);lo.apply_translation([0,0,.09]);hi=trimesh.creation.box([4,4,1.0]);hi.apply_translation([0,0,.72]);gap_fixture=trimesh.util.concatenate([lo,hi]);assert not gap_fixture.contains([[0,0,.20]])[0]
closed_fixture=trimesh.creation.box([4,4,1.22]);closed_fixture.apply_translation([0,0,.61]);assert closed_fixture.contains([[0,0,.20]])[0]
(root/'qa/grade-join-validation.json').write_text(json.dumps({'stl_sha256':sha,'all_expected_outcomes':True,'scope':'Explicit model-material contact samples at both inland ends; not a global terrain or surveyed construction certification.','checks':joins,'controls':{'known_0_04mm_separation_detected':True,'continuous_solid_control_detected':True,'deliverable_modified':False}},indent=2)+'\n')
# Roof access cuts must be genuinely depressed, not merely dark paint.
def roof_top(mesh,xy):
 loc,_,_=mesh.ray.intersects_location([[*xy,30]],[[0,0,-1]],multiple_hits=True)
 assert len(loc);return float(loc[:,2].max())
recesses=[]
for probe in probes['recess_depth_pairs']:
 floor=roof_top(m,probe['floor_xy_model_mm']);roof=roof_top(m,probe['adjacent_roof_xy_model_mm']);depth=roof-floor
 assert depth>probe['minimum_depth_model_mm'],(probe,depth)
 recesses.append(dict(probe,actual_floor_z_model_mm=floor,actual_adjacent_roof_z_model_mm=roof,actual_depth_model_mm=depth))
first=recesses[0];cap=trimesh.creation.box([2,2,1]);cap.apply_translation([*first['floor_xy_model_mm'],first['actual_adjacent_roof_z_model_mm']-.2])
filled=trimesh.util.concatenate([m,cap]);mutant_depth=first['actual_adjacent_roof_z_model_mm']-roof_top(filled,first['floor_xy_model_mm']);assert mutant_depth<first['minimum_depth_model_mm']
(root/'qa/recess-depth-validation.json').write_text(json.dumps({'stl_sha256':sha,'all_expected_outcomes':True,'method':'Downward rays on independently reloaded STL at public explicit points; depth is model millimetres, not surveyed architecture.','checks':recesses,'negative_control':{'injected_roof_return_cap_detected':True,'mutant_depth_model_mm':mutant_depth,'deliverable_modified':False}},indent=2)+'\n')
with tempfile.TemporaryDirectory(prefix='xiangshan-rebuild-')as tmp:
 subprocess.run([sys.executable,str(pathlib.Path(__file__).with_name('build_model.py')),'--out',tmp,
  '--params',str(pathlib.Path(__file__).with_name('parameters.json'))],check=True,capture_output=True)
 E=np.load(pathlib.Path(tmp)/'mesh-data.npz');same={k:bool(np.array_equal(D[k],E[k]))for k in ['vertices','faces','materials','groups']}
 stl=path.read_bytes()==(pathlib.Path(tmp)/path.name).read_bytes();assert all(same.values())and stl
assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
(root/'qa/rebuild-validation.json').write_text(json.dumps({'fresh_process':True,'geometry_arrays_identical':same,'stl_byte_identical':stl},indent=2)+'\n')
print(json.dumps(r,indent=2));print('sections',len(records));print('rays',len(rr));print('profiles',len(profiles))
