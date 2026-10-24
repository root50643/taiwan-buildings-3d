from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;r,v,f=raw_read(A/'model.stl');t=trimesh.Trimesh(v,f,process=False);S=4
probes=[('central_hall2F',(-10,15,7),True),('central_hall3F',(-10,15,11),True),('central_lower_roof_air4F',(-10,15,14),False),('left_front4F_projection',(-20,.8,14),True),('left_under4F_air_between_columns',(-17,.8,11),False),('left_projection_column',(-14.3,.8,11),True),('main_tower',(1,1,18),True),('tower_above_roof_air',(1,1,20),False),('right4F',(8,10,14),True),('rear_right_terrain',(8,22,3),True),('main_entry_ground',(-1,-1,1),True),('main_stairs_outer_air',(-1,-4,1),False),('B1_wide_west',(-26,12,1),True),('foreground_gate_absent',(0,-10,5),False),('adjacent_brick_absent',(25,15,8),False)]
got=t.contains(np.array([p for n,p,e in probes])*S);out=[]
for (name,p,expected),g in zip(probes,got):
 assert bool(g)==expected,(name,g,expected)
 out.append({'feature':name,'point_mm':(np.array(p)*S).tolist(),'expected_solid':expected,'actual_solid':bool(g)})
def ray(q,d):
 o=np.array(q)*S;d=np.array(d,dtype=float);d/=np.linalg.norm(d);loc,_,_=t.ray.intersects_location([o],[d],multiple_hits=True);ds=np.sort(np.dot(loc-o,d));result=[]
 for x in ds:
  if x>=-1e-5 and (not result or abs(x-result[-1])>1e-5):result.append(float(x))
 return result
roof=ray((-10,15,20),(0,0,-1));assert abs(roof[0]-(20-13.2)*4)<.02,roof
void=ray((-17,.8,11),(0,0,1));assert abs(void[0]-8)<.01,void
ids=np.random.default_rng(20261024).choice(len(f),768,replace=False);norm=t.face_normals[ids];orig=t.triangles_center[ids]-norm*.0001
loc,ir,it=t.ray.intersects_location(orig,-norm,multiple_hits=True);mins=np.full(len(ids),np.inf)
for i,d in zip(ir,np.linalg.norm(loc-orig[ir],axis=1)):
 if d>1e-6:mins[i]=min(mins[i],d)
report={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'raw_mesh_contains_no_repair':out,'ray_central_lower_roof_down_mm':roof,'ray_projection_air_to_soffit_mm':void,'normal_thickness_samples':{'count':len(ids),'finite_hits':int(np.isfinite(mins).sum()),'minimum_sampled_mm':float(mins.min()),'below_0_8mm_count':int((mins<.8).sum()),'not_exhaustive':True},'nominal_frame_width_mm':.36,'nominal_parapet_thickness_mm':.72,'note':'Thin frames and projecting bay/parapets require slicer review; cantilever soffits need support evaluation. No physical print; no support-free/global minimum wall claim.'}
(A/'qa/feature-probes.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
