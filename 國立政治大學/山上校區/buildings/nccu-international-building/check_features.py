from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from qa_model import raw_read
A=Path(__file__).resolve().parent;r,v,f=raw_read(A/'model.stl');t=trimesh.Trimesh(v,f,process=False);S=2.5
probes=[('B1_left_solid',(10,2,2),True),('B1_front_slot_void',(12,-4,2),False),('1F_above_B1_slot_solid',(12,-4,6),True),('2F_full_back_core',(28,6,9),True),('3F_back_core_setback_air',(28,6,13),False),('right_rear_stair',(58,12,20),True),('1F_left_solid',(10,2,6),True),('2F_left_solid',(10,2,9),True),('3F_right_solid',(45,3,12),True),('right_below3F_terrain_support',(45,3,5),True),('5F_polygon_front',(10,-5,20),True),('6F_polygon_front_void',(10,-5,23),False),('6F_farleft_blank_bay_void',(4,5,23),False),('6F_610_band_solid',(13,5,23),True),('6F_right_solid',(45,3,23),True),('R_roof_air',(45,3,27),False),('R_roof_deck',(45,3,25.3),True),('candidate_central_core',(25,-2,28),True),('left_stair_projection',(-1,1,10),True),('platform_deck',(29,-8,11),True),('platform_undercroft',(29,-8,9),False),('platform_undergrade',(29,-8,6),True),('finite_portal_opening',(44,-7,4),False),('finite_portal_top',(44,-7,7.6),True),('front_grade',(10,-7.6,6),True),('platform_column',(28,-8.5,6),True),('right_stairs',(39.5,-5,4),True),('outside_main',(60,-5,18),False)]
got=t.contains(np.array([p for n,p,e in probes])*S);out=[]
for (name,p,expected),g in zip(probes,got):
 assert bool(g)==expected,(name,g,expected)
 out.append({'feature':name,'point_mm':(np.array(p)*S).tolist(),'expected_solid':expected,'actual_solid':bool(g)})
def ray(q,d):
 o=np.array(q)*S;d=np.array(d,dtype=float);d/=np.linalg.norm(d);loc,_,_=t.ray.intersects_location([o],[d],multiple_hits=True);ds=np.sort(np.dot(loc-o,d));result=[]
 for x in ds:
  if x>=-1e-5 and (not result or abs(x-result[-1])>1e-5):result.append(float(x))
 return result
roof=ray((10,-5,27),(0,0,-1));assert abs(roof[0]-(27-21.82)*S)<1e-4,roof
bay=ray((4,5,27),(0,0,-1));assert abs(bay[0]-(27-21.82)*S)<1e-4,bay
under=ray((29,-8,9),(0,0,1));assert abs(under[0]-(10.65-9)*S)<1e-4,under
ids=np.random.default_rng(20261024).choice(len(f),512,replace=False);norm=t.face_normals[ids];orig=t.triangles_center[ids]-norm*.0001
loc,ir,it=t.ray.intersects_location(orig,-norm,multiple_hits=True);mins=np.full(len(ids),np.inf)
for i,d in zip(ir,np.linalg.norm(loc-orig[ir],axis=1)):
 if d>1e-6:mins[i]=min(mins[i],d)
cavity_rays={}
for name,direction in [('left',(-1,0,0)),('right',(1,0,0)),('front',(0,-1,0)),('back',(0,1,0)),('down',(0,0,-1)),('up',(0,0,1))]:
 hits=ray((12.5,-3.7,2.4),direction);assert len(hits)>=2 and hits[1]>hits[0];cavity_rays[name]={'all_hits_mm':hits,'first_material_wall_segment_mm':hits[1]-hits[0]}
report={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'raw_mesh_contains_no_repair':out,'B1_slope_enclosed_proxy_six_axis_wall_rays':cavity_rays,'enclosed_cavity_manufacturing_risks':'SLA resin trapping and inaccessible FFF internal support; no drain invented, not print-ready','two_low_roof_downward_rays_mm':[roof,bay],'platform_undercroft_upward_ray_mm':under,'normal_thickness_samples':{'count':len(ids),'finite_hits':int(np.isfinite(mins).sum()),'minimum_sampled_mm':float(mins.min()),'below_0_8mm_count':int((mins<.8).sum()),'not_exhaustive':True},'nominal_frame_width_mm':.225,'nominal_parapet_thickness_mm':.55,'platform_solid_rim_mm':1.75,'note':'Thin window relief, platform rim and parapets require scale/material review. Platform soffit support needed; no physical print or guaranteed printability.'}
(A/'qa/feature-probes.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
