from pathlib import Path
import json,hashlib,math
import numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;r,v,f=raw_read(A/'model.stl');t=trimesh.Trimesh(v,f,process=False)
def point(q):x,y,z=q;return np.array([(x-50)/16,(365-y)/16,z])*4
probes=[('complete_left4F_room',(120,300,15),True),('complete_right4F_room',(750,300,15),True),('left_flat_roof',(120,300,16.55),True),('right_flat_roof',(750,300,16.55),True),('not_fifth_floor_left',(120,300,18),False),('back_room_band',(350,120,11),True),('front_court_empty',(350,300,1),False),('front_court_empty_upper',(350,300,11),False),('gallery1F_air',(350,202,4),False),('gallery2F_air',(350,202,8),False),('gallery3F_air',(350,202,11),False),('gallery4F_air',(350,202,15),False),('gallery_true_backwall',(350,175,11),True),('gallery_white_column',(319,222,11),True),('main_stair_core',(540,110,11),True),('west_stair_core',(80,200,11),True),('central_entry_steps',(450,249,1),True),('entry_steps_above_air',(450,249,4),False),('turning_entry_steps',(514,247,1),True),('east_entry_steps',(800,198,1),True),('north_entry_steps',(380,34,1),True),('attached_platform_solid',(540,232,5.7),True),('attached_platform_soffit_air',(540,232,4),False),('independent_bridge_excluded',(540,280,5.7),False),('roof_access',(540,90,17.5),True),('no_extra_roof_storey',(350,120,17.5),False)]
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
for name,q,expected in [('left_complete_roof',(120,300,20),16.62),('right_complete_roof',(750,300,20),16.62),('main_stair_roof_access',(540,90,20),18.23),('bridge_interface_top',(540,232,8),5.86)]:
 hits=ray(q,(0,0,-1));assert abs(hits[0]-(q[2]-expected)*4)<1e-4,(name,hits);rays[name]={'hits_mm':hits,'expected_first_height_mm':expected*4}
tread_samples=[]
for i in range(5):
 a=math.pi/2+(i+.5)*math.pi/10;q=(527+14*math.cos(a),255+14*math.sin(a),4)
 hits=ray(q,(0,0,-1));height=4-hits[0]/4;expected=.80+(i+1)*.08
 assert abs(height-expected)<1e-5,(i,height,expected)
 tread_samples.append({'kind':'fan','i':i,'point_px_z':q,'top_design_units':height})
for i in range(8):
 q=(513,254-i*3.4,4);hits=ray(q,(0,0,-1));height=4-hits[0]/4;expected=2.12 if q[1]<234 else 1.20+(i+1)*.115
 assert abs(height-expected)<1e-5,(i,height,expected)
 tread_samples.append({'kind':'upper_flight','i':i,'point_px_z':q,'top_design_units':height})
assert all(b['top_design_units']>=a['top_design_units']-1e-5 for a,b in zip(tread_samples,tread_samples[1:]))
ids=np.random.default_rng(20261024).choice(len(f),512,replace=False);norm=t.face_normals[ids];orig=t.triangles_center[ids]-norm*.0001
loc,ir,it=t.ray.intersects_location(orig,-norm,multiple_hits=True);mins=np.full(len(ids),np.inf)
for i,d in zip(ir,np.linalg.norm(loc-orig[ir],axis=1)):
 if d>1e-6:mins[i]=min(mins[i],d)
report={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'raw_mesh_contains_no_repair':out,'roof_and_platform_direct_rays':rays,'518_turning_treads_direct_ray_heights':tread_samples,'normal_thickness_samples':{'count':len(ids),'finite_hits':int(np.isfinite(mins).sum()),'minimum_sampled_mm':float(mins.min()),'below_0_8mm_count':int((mins<.8).sum()),'not_exhaustive':True},'nominal_frame_width_mm':.32,'nominal_roof_parapet_thickness_mm':.72,'manufacturing_limits':'No physical print. Open gallery and platform soffits may need FFF support. Thin relief/rails require scale/material review. No hidden drain or infill added to manufacture topology. No global minimum-wall/support-free guarantee.'}
(A/'qa/feature-probes.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
