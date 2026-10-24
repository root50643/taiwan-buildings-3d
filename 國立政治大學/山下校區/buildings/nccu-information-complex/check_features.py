from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;r,v,f=raw_read(A/'model.stl');t=trimesh.Trimesh(v,f,process=False)
def point(q):x,y,z=q;return np.array([(x-120)/10,(375-y)/10,z])*3
probes=[('621_west1F_actual_room',(145,200,5),True),('621_east_broad_external_stair',(440,270,1),True),('621_east_broad_stair_above_treads_air',(440,270,5),False),('610_raised_short_cap',(210,360,25.5),True),('610_not_full_extra_roof_storey',(210,320,25.5),False),('low_1F_back_room',(400,70,5),True),('low_1F_X_recess_not_filled',(400,142,5),False),('upper_above1F_X_room',(400,142,9),True),('low_front_arcade_open',(310,120,8),False),('low_roof_open_frame_not_full_corridor',(400,142,19),False),('low_roof_bounded_end_room',(650,160,19),True),('5F_labelled_west_terrace_air',(145,200,19),False),('4F_below_west_terrace_solid',(145,200,15),True),('5F_south_main_room_not_deleted',(145,320,19),True),('6F_narrow_high_wing',(200,220,22),True),('high_RF_not_extended_to_low',(400,80,23),False),('614_west1F_entry_recess',(190,80,5),False),('614_above_entry2F_room',(190,80,8),True),('614_west_entry_ground_steps',(150,70,1),True),('621_south_underentry_air',(200,350,5),False),('621_south_entry_support_column',(175,362,5),True),('621_recessed1F_room',(200,320,5),True),('information_round_stair_pocket',(560,150,8),False),('information_round_stair_parapet',(560,159,7.4),True),('wide_flat_core_at_west_boundary',(200,130,25),True),('no_wrong_tall_core_at_stair_center',(245,130,26.5),False),('curved_high_core',(336,270,24),True),('outside_curved_core',(345,270,24),False)]
got=t.contains(np.array([point(p) for n,p,e in probes]));out=[]
for (name,p,expected),g in zip(probes,got):
 assert bool(g)==expected,(name,p,g,expected)
 out.append({'feature':name,'point_mm':point(p).tolist(),'expected_solid':expected,'actual_solid':bool(g)})
def ray(q,d):
 o=point(q);d=np.array(d,dtype=float);d/=np.linalg.norm(d);loc,_,_=t.ray.intersects_location([o],[d],multiple_hits=True);ds=np.sort(np.dot(loc-o,d));result=[]
 for x in ds:
  if x>=-1e-5 and (not result or abs(x-result[-1])>1e-5):result.append(float(x))
 return result
rays={}
for name,q,expected in [('low_frame_open_to_deck',(400,142,23),17.4),('5F_west_terrace_to4F_roof',(145,200,23),17.4),('high_RF_roof',(200,220,27),24.45)]:
 hits=ray(q,(0,0,-1));assert abs(hits[0]-(q[2]-expected)*3)<1e-4,(name,hits);rays[name]={'hits_mm':hits,'expected_first_roof_height_mm':expected*3}
ids=np.random.default_rng(20261024).choice(len(f),512,replace=False);norm=t.face_normals[ids];orig=t.triangles_center[ids]-norm*.0001
loc,ir,it=t.ray.intersects_location(orig,-norm,multiple_hits=True);mins=np.full(len(ids),np.inf)
for i,d in zip(ir,np.linalg.norm(loc-orig[ir],axis=1)):
 if d>1e-6:mins[i]=min(mins[i],d)
report={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'raw_mesh_contains_no_repair':out,'roof_separation_direct_rays':rays,'normal_thickness_samples':{'count':len(ids),'finite_hits':int(np.isfinite(mins).sum()),'minimum_sampled_mm':float(mins.min()),'below_0_8mm_count':int((mins<.8).sum()),'not_exhaustive':True},'nominal_window_frame_width_mm':.24,'nominal_high_parapet_thickness_mm':.66,'manufacturing_limits':'No physical print. Open gallery/entry and roof-beam soffits may need FFF support. Thin window relief/rails require scale/material review. No hidden drain or roof cap added to manufacture a topology pass. No global minimum-wall or support-free guarantee.'}
(A/'qa/feature-probes.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
