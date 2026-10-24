from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;r,v,f=raw_read(A/'model.stl');t=trimesh.Trimesh(v,f,process=False);S=3
probes=[('1F_central_entry_void',(0,-12,2),False),('1F_recessed_back_wall',(0,-8.4,2),True),('2F_column',(-4.2,-14,5.8),True),('2F_colonnade_void',(0,-14,5.8),False),('718_front_recess_void',(0,14.1,2),False),('718_front_recess_back',(0,13.75,2),True),('718_warm_pier',(-4,14.3,2),True),('6F_hall_ceiling_mass',(0,0,21.4),True),('7F_X_left_void',(-8,1,23),False),('7F_X_center_void',(0,1,23),False),('8F_X_left_void',(-8,1,27),False),('8F_center_occupied_core',(0,1,27),True),('8F_front_setback',(0,-13,27),False),('9F_front_setback',(0,-13,30),False),('9F_rear_terrace_open',(0,9,30),False),('9F_terrace_floor',(0,9,28.5),True),('9F_central_mass_caps_X',(-8,1,30),True),('9F_end_wing_occupied',(-20,3,30),True),('R_platform_not_tenth_floor',(-15,0,34),False),('R_rear_terrace_air',(0,9,34),False),('R_left_stair',(-23,-4,34),True),('R_right_stair',(23,-4,34),True),('R_central_core',(0,-4,34),True)]
pts=np.array([p for n,p,e in probes])*S;got=t.contains(pts);rows=[]
for (name,p,expected),g in zip(probes,got):
 assert bool(g)==expected,(name,g,expected)
 rows.append({'feature':name,'point_mm':(np.array(p)*S).tolist(),'expected_solid':expected,'actual_solid':bool(g)})
# Deterministic inward normal probes on raw faces. Not a global wall certificate.
ids=np.unique(np.linspace(0,len(f)-1,600,dtype=int));orig=t.triangles_center[ids]-t.face_normals[ids]*1e-4;direc=-t.face_normals[ids]
loc,rids,tris=t.ray.intersects_location(orig,direc,multiple_hits=True)
dist=np.einsum('ij,ij->i',loc-orig[rids],direc[rids]);width=np.full(len(ids),np.inf)
for k,d in zip(rids,dist):
 if d>1e-5:width[k]=min(width[k],d+1e-4)
valid=np.isfinite(width);assert valid.all()
ray={'method':'600 deterministic evenly indexed raw face centroids, inward unit-normal rays; first positive exit; sampled local chord lengths, not exhaustive/global minimum wall','sample_count':len(ids),'valid_exits':int(valid.sum()),'minimum_mm':float(width.min()),'under_0_8mm':int((width<.8).sum()),'samples':[{'face':int(i),'thickness_mm':float(w)} for i,w in zip(ids,width)]}
report={'version':'官方PDF記錄之修繕前瓷磚外觀版，非2026修繕後現況','stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'raw_mesh_contains_no_repair':rows,'inward_ray_thickness':ray,'nominal_mullion_width_mm':.12*S,'nominal_terrace_parapet_mm':.35*S,'note':'Void classification and heights are source-relative simplified approximations. Two boundary shells are exterior and enclosed atrium void. No physical print/support-free certification.'}
(A/'qa/feature-probes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='inward_ray_thickness'},ensure_ascii=False));print({k:v for k,v in ray.items() if k!='samples'})
