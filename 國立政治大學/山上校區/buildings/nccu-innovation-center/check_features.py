from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;r,v,f=raw_read(A/'model.stl');t=trimesh.Trimesh(v,f,process=False);S=2.2
probes=[('left2F_hall_void',(-12,-6,7),False),('left3F_X_void',(-12,-6,11),False),('left4F_room_caps_X',(-12,-6,14),True),('left_low_roof_no5F',(-20,3,19),False),('right2F_hall_void',(16,3,7),False),('right3F_X_void',(16,3,11),False),('right4F_X_void',(16,3,15),False),('right5F_635sqm_occupied_slab',(16,3,17.2),True),('right5F_exchange_solid',(16,3,19),True),('R_high_roof_solid',(16,3,21.05),True),('R_no_sixth_occupied_floor',(16,3,23),False),('classroom425_occupied',(-12,-20,14),True),('adjacent_low_terrace_not4F',(9,-20,15),False),('adjacent_low_terrace_roof',(9,-20,13.05),True),('1F_left_attached_auditorium',(-45,3,3),True),('1F_auditorium_low_not2F',(-45,3,7),False),('shared_lift_R_head',(-3,-7,23),True),('high_end_stair_R_head',(38,12,21.8),True),('low_stair_head',(-31,1,15.6),True),('low_stair_no_highhead',(-31,1,21.8),False),('entry_red_canopy',(41,-4,9),True),('entry_canopy_overhang_open_below',(41,-4,3),False)]
probes += [('south_skirt_contact',(-25,-20,2),True),('south_skirt_below_projecting_2F',(10,-18,4),True),('outside_bounded_skirt',(10,-26,3),False),('1F_lower_entry_edge_solid',(38,-13.3,3),True),('entry_low_projection_not_extra2F',(38,-13.3,7),False),('entry_recess_open_front',(39.4,-4,7),False),('entry_recess_glazing_back',(38.9,-4,7),True)]
got=t.contains(np.array([p for n,p,e in probes])*S);rows=[]
for (name,p,expected),g in zip(probes,got):
 assert bool(g)==expected,(name,g,expected)
 rows.append(dict(feature=name,point_mm=(np.array(p)*S).tolist(),expected_solid=expected,actual_solid=bool(g)))
ids=np.unique(np.linspace(0,len(f)-1,600,dtype=int));orig=t.triangles_center[ids]-t.face_normals[ids]*1e-4;direc=-t.face_normals[ids]
loc,rids,tris=t.ray.intersects_location(orig,direc,multiple_hits=True);dist=np.einsum('ij,ij->i',loc-orig[rids],direc[rids]);width=np.full(len(ids),np.inf)
for k,d in zip(rids,dist):
 if d>1e-5:width[k]=min(width[k],d+1e-4)
valid=np.isfinite(width);assert valid.all()
ray=dict(method='600 evenly indexed raw face centroids, inward normal first exit. Local sampled chords NOT exhaustive minimum wall',sample_count=len(ids),valid_exits=int(valid.sum()),minimum_mm=float(width.min()),under_0_8mm=int((width<.8).sum()),samples=[dict(face=int(i),thickness_mm=float(w)) for i,w in zip(ids,width)])
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),raw_mesh_contains_no_repair=rows,inward_ray_thickness=ray,note='1 exterior and2 enclosed finite hall cavity boundaries; closed cavities may trap resin/powder/support. No physical print or support-free guarantee.')
(A/'qa/feature-probes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print({k:v for k,v in ray.items() if k!='samples'});print('all',len(rows),'solid/void probes match')
