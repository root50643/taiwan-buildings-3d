from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;r,v,f=raw_read(A/'model.stl');t=trimesh.Trimesh(v,f,process=False)
def point(q):x,y,z=q;return np.array([(x-75)/14,(310-y)/14,z])*4
probes=[('left2F_wing',(200,240,7),True),('right2F_wing',(700,240,7),True),('left3F_roof_terrace_air',(200,240,10),False),('right3F_roof_terrace_air',(700,240,10),False),('central3F_real_room',(430,260,11),True),('central3F_registered_stair_mass',(425,204,11),True),('3F_small_side_room',(550,240,11),True),('no_fullwidth3F',(650,240,11),False),('rear_foyer1F',(430,140,3),True),('rear_foyer_no2F',(430,140,7),False),('entry_recess1F_air',(430,280,3),False),('entry2F_room_above',(430,280,6),True),('entry_top_landing',(430,310,1.2),True),('entry_grounded_low_tread',(430,349,.2),True),('beyond_natural_steps_empty',(430,360,.2),False),('canopy_material',(430,325,5.1),True),('canopy_soffit_air',(430,325,4),False),('outside_foyer_empty',(500,140,3),False),('no_roof_tower',(425,204,14),False)]
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
for name,q,h in [('left_terrace',(200,240,15),8.95),('right_terrace',(700,240,15),8.95),('central3F_cap',(430,260,15),12.6),('small_room_cap',(550,240,15),12.6),('rear_foyer1F_cap',(430,140,15),5.36),('entry_canopy_top',(430,325,15),5.24)]:
 hits=ray(q,(0,0,-1));assert abs(hits[0]-(q[2]-h)*4)<1e-4,(name,hits);rays[name]={'hits_mm':hits,'expected_first_height_mm':h*4}
steps=[]
for i in range(6):
 q=(430,323+i*5,3);hits=ray(q,(0,0,-1));h=3-hits[0]/4;expected=1.6-(i+1)*.2
 assert abs(h-expected)<1e-5,(i,h,expected);steps.append({'i':i,'height_mm':h*4,'ray_hits_mm':hits})
# Entry recess clearance measured across the open1F porch, not repaired away.
hits=ray((430,340,3),(0,1,0));assert abs(hits[0]-(340-267.6)/14*4)<1e-4,hits
ids=np.random.default_rng(20261024).choice(len(f),512,replace=False);norm=t.face_normals[ids];orig=t.triangles_center[ids]-norm*.0001
loc,ir,it=t.ray.intersects_location(orig,-norm,multiple_hits=True);mins=np.full(len(ids),np.inf)
for i,d in zip(ir,np.linalg.norm(loc-orig[ir],axis=1)):
 if d>1e-6:mins[i]=min(mins[i],d)
report={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'raw_mesh_contains_no_repair':out,'roof_direct_rays':rays,'entry_stair_heights':steps,'entry_open_recess_first_backwall_distance_mm':hits[0],'normal_thickness_samples':{'count':len(ids),'finite_hits':int(np.isfinite(mins).sum()),'minimum_sampled_mm':float(mins.min()),'below_0_8mm_count':int((mins<.8).sum()),'not_exhaustive':True},'manufacturing_limits':'No physical print or toolpath. Fine frame and terrace rails under0.8mm; canopy/entry ceiling  may require support. No enclosed cavity shells; enclosed-room mass proxies are solid, not claimed surveyed interiors. No support-free/globalminimum-wall claim.'}
(A/'qa/feature-probes.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
