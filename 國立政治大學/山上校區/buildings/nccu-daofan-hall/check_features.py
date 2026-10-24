from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;r,v,f=raw_read(A/'model.stl');t=trimesh.Trimesh(v,f,process=False)
def point(q):x,y,z=q;return np.array([(x-115)/16,(386-y)/16,z])*[4,4,3]
probes=[('north_4F_room',(380,120,15),True),('east_4F_room',(600,270,15),True),('south_3F_room',(380,350,11),True),('south_4F_absent_low_roof',(380,350,15),False),('south_low_roof',(380,350,13.6),True),('courtyard_ground_empty',(380,240,.3),False),('courtyard_upper_empty',(380,240,11),False),('north_grade_solid_not_B1_rooms',(380,120,1.5),True),('B1_south_room',(380,350,1.5),True),('B1_partial_east_room',(600,270,1.5),True),('upper_east_grade_solid_not_B1_rooms',(600,120,1.5),True),('north_gallery1F_air',(380,153,5),False),('north_gallery2F_air',(380,153,8),False),('north_gallery4F_air',(380,153,15),False),('east_gallery_air',(555,270,11),False),('south_gallery_air',(380,318,11),False),('south_round_core',(205,275,8),True),('east_round_core',(492,217,11),True),('north_stair_core',(315,130,15),True),('neck_first_floor_slab',(675,87,3.4),True),('neck_second_floor_slab',(675,87,6.8),True),('neck_roof_platform',(675,87,10.2),True),('neck_under_air',(675,87,2),False),('neck_1F_open_air',(675,87,5),False),('neck_2F_open_air',(675,87,8),False),('annex_1F_approx_interior_void',(820,40,5),False),('annex_2F_approx_interior_void',(820,40,8),False),('annex_2F_floor',(820,40,6.8),True),('annex_roof',(820,40,10.2),True),('annex_not_main_3F',(820,40,12),False),('annex_near_south_stair',(724,115,8),True),('annex_far_east_stair',(942,-14,8),True),('annex_local_mezzanine_slab',(725,60,5.1),True),('annex_local_mezzanine_below_void',(725,60,4.3),False),('annex_local_mezzanine_above_void',(725,60,5.7),False),('entry_recess_air',(640,220,5),False),('entry_recess_door',(620.5,220,5),True),('annex_1F_side_room',(695,35,5),True),('annex_no_side_room_2F',(695,35,8),False),('annex_1F_lower_room',(820,100,5),True),('annex_no_lower_room_2F',(820,100,8),False),('east_entry_steps',(680,220,1.2),True),('east_entry_above_air',(680,220,5),False),('screen_gap',(655,180,8.3),False),('screen_vertical',(658,183,8.3),True),('visible_roof_projection',(315,120,18),True),('799_south_landing',(220,400,3.4),True),('799_landing_below_air',(220,400,2),False),('799_south_gray_window',(300,388,8),True),('north_back_not_mirrored',(380,86,8),False),('no_arbitrary_roof_storey',(600,270,18),False)]
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
for name,q,expected in [('north_4F_roof',(380,120,20),17.14),('east_4F_roof',(600,270,20),17.14),('south_3F_low_roof',(380,350,20),13.74),('annex_2F_roof',(820,40,15),10.34),('neck_platform',(675,87,15),10.34),('bounded_roof_projection',(315,120,21),19.73)]:
 hits=ray(q,(0,0,-1));assert abs(hits[0]-(q[2]-expected)*3)<1e-4,(name,hits);rays[name]={'hits_mm':hits,'expected_first_height_mm':expected*3}
ids=np.random.default_rng(2026102460).choice(len(f),512,replace=False);norm=t.face_normals[ids];orig=t.triangles_center[ids]-norm*.0001
loc,ir,it=t.ray.intersects_location(orig,-norm,multiple_hits=True);mins=np.full(len(ids),np.inf)
for i,d in zip(ir,np.linalg.norm(loc-orig[ir],axis=1)):
 if d>1e-6:mins[i]=min(mins[i],d)
fm=np.array(json.loads((A/'mesh.json').read_text())['face_materials']);material_checks=[]
for name,q,d,expected in [('north_grade_not_basement_facade',(380,80,1.5),(0,-1,0),5),('south_local_basement_facade',(380,400,1.5),(0,1,0),0)]:
 loc,ir,it=t.ray.intersects_location([point(q)],[d],multiple_hits=True);order=np.argsort(np.linalg.norm(loc-point(q),axis=1));idx=int(it[order[0]]);actual=int(fm[idx]);assert actual==expected,(name,actual,expected)
 material_checks.append({'name':name,'triangle':idx,'expected_material':expected,'actual_material':actual})
report={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'partial_basement_vs_grade_material_rays':material_checks,'raw_mesh_contains_no_repair':out,'roof_and_platform_direct_rays':rays,'normal_thickness_samples':{'count':len(ids),'finite_hits':int(np.isfinite(mins).sum()),'minimum_sampled_mm':float(mins.min()),'below_0_8mm_count':int((mins<.8).sum()),'not_exhaustive':True},'nominal_screen_member_mm':[.5,.3],'nominal_roof_edge_thickness_mm':.8,'manufacturing_limits':'No physical print. Two approximate annex interior cavities retained; these are not evidenced whole-floor lightwells. Local mezzanine pocket is separately modeled. Resin drainage/venting and FFF internal soffit support unresolved. Open galleries, neck and thin lattice need orientation/scale/material review. No global minimumwall or supportfree certificate.'}
(A/'qa/feature-probes.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
