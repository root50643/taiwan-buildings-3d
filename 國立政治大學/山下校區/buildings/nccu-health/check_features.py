from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;r,v,f=raw_read(A/'model.stl');t=trimesh.Trimesh(v,f,process=False);S=4
probes=[('main_1F_solid',(10,6,2),True),('deep_1F_triangle_void',(21,7,2.5),False),('middle_1F_triangle_void',(22,7.5,2.5),False),('triangle_landing',(21,7,1.0),True),('2F_diagonal_enclosure',(22,7.5,5),True),('3F_diagonal_enclosure',(22,7.5,9),True),('4F_diagonal_enclosure',(22,7.5,12),True),('pointed_wing',(31,12,6),True),('outside_point',(31,10,6),False),('roof_terrace_air',(17,8,15.8),False),('roof_terrace_deck',(17,8,14.45),True),('R_access_strip',(7,2,16),True),('no_B1_inset_roof',(25,11,16),False),('small_1F_stair_projection',(3,11.6,2),True),('small_3F_stair_projection',(3,11.6,9),True),('no_4F_small_projection',(3,11.6,12),False),('no_roof_small_projection',(3,11.6,16),False)]
pts=np.array([p for n,p,e in probes])*S;got=t.contains(pts);out=[]
for (name,p,expected),g in zip(probes,got):
 assert bool(g)==expected,(name,g,expected)
 out.append({'feature':name,'point_mm':(np.array(p)*S).tolist(),'expected_solid':expected,'actual_solid':bool(g)})
def ray(q,d):
 o=np.array(q)*S;d=np.array(d,dtype=float);d/=np.linalg.norm(d);loc,_,_=t.ray.intersects_location([o],[d],multiple_hits=True);ds=np.sort(np.dot(loc-o,d));result=[]
 for x in ds:
  if x>=-1e-5 and (not result or abs(x-result[-1])>1e-5):result.append(float(x))
 return result
rh=ray((22,7.5,2.5),(0,0,1));assert abs(rh[0]-4.6)<1e-4,rh
rr=ray((17,8,18),(0,0,-1));assert abs(rr[0]-13.6)<1e-4,rr
ids=np.random.default_rng(20261023).choice(len(f),512,replace=False);norm=t.face_normals[ids];orig=t.triangles_center[ids]-norm*.0001
loc,ir,it=t.ray.intersects_location(orig,-norm,multiple_hits=True);mins=np.full(len(ids),np.inf)
for i,d in zip(ir,np.linalg.norm(loc-orig[ir],axis=1)):
 if d>1e-6:mins[i]=min(mins[i],d)
report={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'raw_mesh_contains_no_repair':out,'deep_1F_triangle_retained':True,'ray_entry_void_to_2F_soffit_mm':rh,'ray_open_terrace_down_to_deck_mm':rr,'normal_thickness_samples':{'count':len(ids),'finite_hits':int(np.isfinite(mins).sum()),'minimum_sampled_mm':float(mins.min()),'below_0_8mm_count':int((mins<.8).sum()),'not_exhaustive':True},'nominal_frame_width_mm':.4,'nominal_louver_height_mm':.4,'nominal_parapet_thickness_mm':.8,'note':'Backed relief and nosings contain sub0.8mm details. Slices/rays not exhaustive wall or manufacturing certification. Deep entry soffit and projecting cap require support review; no physical print.'}
(A/'qa/feature-probes.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
