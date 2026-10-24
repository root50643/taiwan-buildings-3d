from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;r,v,f=raw_read(A/'model.stl');t=trimesh.Trimesh(v,f,process=False);S=3
probes=[('right_upper_corner_post',(30.05,-.11,12),True),('porch_true_air',(5,-5,2),False),('porch_1F_landing',(5,-5,.85),True),('porch_canopy',(5,-7,3.9),True),('upper_entry_body',(5,-5,6),True),('screen_lattice_hole',(4.75,-7,4.73),False),('screen_horizontal_bar',(4.75,-7,5.05),True),('rear_upper_2F',(-12,12,5),True),('rear_upper_5F',(-12,12,16),True),('rear_ground_terrain_contact',(-12,12,2),True),('connector_4F',(5,9,12),True),('connector_no_5F',(5,9,16),False),('east_rear_lower_roof_no5F',(6,20,16),False),('rear_highest_roof_air',(-12,12,18.4),False),('rear_roof_deck',(-12,12,17.55),True),('low_annex_2F',(-6,-23,5),True),('low_annex_absent3F',(-6,-23,9),False),('front_long_diagonal3F',(-10,-17,9),True),('front_shortened4F_no_far_body',(-10,-17,12),False),('right_end_upper_open_frame',(29.5,-.8,12),False),('right_end_upper_solid_wall',(29.5,-5,12),True),('right_end_frame_cap',(29.5,-.8,13.6),True)]
pts=np.array([p for n,p,e in probes])*S;got=t.contains(pts);out=[]
for (name,p,expected),g in zip(probes,got):
 assert bool(g)==expected,(name,g,expected)
 out.append({'feature':name,'point_mm':(np.array(p)*S).tolist(),'expected_solid':expected,'actual_solid':bool(g)})
def ray(q,d):
 o=np.array(q)*S;d=np.array(d,dtype=float);d/=np.linalg.norm(d);loc,_,_=t.ray.intersects_location([o],[d],multiple_hits=True);ds=np.sort(np.dot(loc-o,d));result=[]
 for x in ds:
  if x>=-1e-5 and (not result or abs(x-result[-1])>1e-5):result.append(float(x))
 return result
rh=ray((5,-5,2),(0,0,1));assert abs(rh[0]-5.25)<1e-4,rh
rr=ray((-12,12,19),(0,0,-1));assert abs(rr[0]-3.78)<1e-4,rr
ids=np.random.default_rng(20261024).choice(len(f),768,replace=False);norm=t.face_normals[ids];orig=t.triangles_center[ids]-norm*.0001
loc,ir,it=t.ray.intersects_location(orig,-norm,multiple_hits=True);mins=np.full(len(ids),np.inf)
for i,d in zip(ir,np.linalg.norm(loc-orig[ir],axis=1)):
 if d>1e-6:mins[i]=min(mins[i],d)
report={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'raw_mesh_contains_no_repair':out,'ray_entry_void_to_canopy_mm':rh,'ray_highest_roof_down_to_deck_mm':rr,'normal_thickness_samples':{'count':len(ids),'finite_hits':int(np.isfinite(mins).sum()),'minimum_sampled_mm':float(mins.min()),'below_0_8mm_count':int((mins<.8).sum()),'not_exhaustive':True},'nominal_frame_width_mm':.33,'nominal_lattice_bar_width_mm':.45,'nominal_parapet_thickness_mm':.66,'note':'Thin relief/lattice/parapet needs slicer review; open canopy soffit and end frame overhang need support evaluation. No physical print; no support-free/global minimum wall claim.'}
(A/'qa/feature-probes.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
