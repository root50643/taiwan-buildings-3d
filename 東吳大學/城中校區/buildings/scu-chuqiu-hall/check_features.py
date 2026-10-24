"""Actual raw STL solid/air probes, local slices, ray thickness and support disclosure.
Probe positions use the builder's archival coordinate interpretation; not a survey.
"""
from pathlib import Path
import json,hashlib,struct
import numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection,box
A=Path(__file__).resolve().parent
b=(A/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0];assert len(b)==84+50*n
r=np.frombuffer(b,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n)
v,inv=np.unique(r['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3);m=trimesh.Trimesh(v,f,process=False);assert m.is_watertight
S=3.;RF=24.5
def cv(p):return (np.asarray(p)-[39.7675,6,0])*S
probes=[('main_enclosed_interior',(30,12,15),True),('T_wing_interior',(74,-5,15),True),('T_south_notch_air',(60,-5,15),False),('T_north_notch_air',(60,20,15),False),('no_full_above_ground_B1',(40,-3,2.5),False),('east_entry_recess_air',(78.9,5.5,3),False),('east_entry_glass_proxy',(78.41,5.5,3),True),('east_outside_under_canopy',(80,5.5,5),False),('east_canopy_slab',(80,5.5,8.5),True),('east_portal_pier',(79.7,3.55,12),True),('north_entry_recess_air',(48.85,17.5,2.5),False),('north_entry_outside_air',(50.8,17.72,2.5),False),('north_entry_double_door',(48.85,16.95,2.5),True),('north_lintel',(48.8,18.2,4.9),True),('south_entry_recess_air',(20,.2,2.5),False),('south_entry_front_air',(20,-.12,2.5),False),('roof_flat_slab',(40,6,24.62),True),('no_pitched_roof',(40,6,27.22),False),('west_roof_stair',(2,3,25.22),True),('central_lower_room',(32,7,26.22),True),('central_high_machine',(27,3,28.62),True),('central_high_upper_volume',(32,7,28.62),True),('east_L_stem',(67,6,26.22),True),('east_L_north_return',(63.4,11,26.22),True),('east_L_notch_air',(63.4,6,26.22),False),('west_low_water_tank',(8,10.8,25.52),True),('east_low_water_tank',(52,10.8,25.52),True),('between_water_tanks_air',(40,10.8,25.52),False),('water_tank_low_not_tower',(8,10.8,27.22),False),('7F_slight_outward_wrap',(40,-.52,23),True),('below7F_outside_body',(40,-.52,20),False)]
probes.extend([
('east_3F_recess_air',(79.2,5.5,10),False),('east_3F_recess_backsolid',(78.0,5.5,10),True),
('east_4F_recess_air',(79.2,5.5,13),False),('east_4F_recess_backsolid',(78.0,5.5,13),True),
('east_5F_recess_air',(79.2,5.5,16),False),('east_5F_recess_backsolid',(78.0,5.5,16),True),
('east_6F_outward_band_solid',(79.2,5.5,19.5),True),('east_6F_soffit_solid',(80,5.5,17.8),True),('east_6F_under_soffit_air',(80,5.5,17.5),False),
('west_bottom_door_recess_air',(.15,10.15,3),False),('west_bottom_door_glazing',(.4,10.15,3),True),
('central_east_low_stair_solid',(35,5,26),True),('central_east_low_stair_above_air',(35,5,28),False),
('central_high_lift_solid',(28,5,28),True),('central_high_lift_above_air',(28,5,29),False),
('east_L_high_machine_solid',(67,5,28),True),('east_north_low_stair_solid',(67,11,26),True),('east_north_low_stair_above_air',(67,11,28),False),
('west_275_roof_stair_top_solid',(2,3,27),True),('west_275_roof_stair_above_air',(2,3,27.5),False)])
actual=m.contains(np.array([cv(p) for _,p,_ in probes]));pr=[]
for (name,p,expect),a in zip(probes,actual):pr.append(dict(name=name,point_mm=cv(p).tolist(),expected_solid=expect,actual_solid=bool(a),passed=bool(a)==expect))
raw=md.Manifold(md.Mesh(v.astype(np.float32),f.astype(np.uint32)));assert raw.status().name=='NoError'
local=[]
for name,z,rect in [('east_entry',3,(78.1,3.7,80,10.8)),('north_entry',2.5,(44.3,16.7,53.4,18.3)),('south_entry',2.5,(17.4,-.5,22.9,.8)),('east_canopy',8.5,(78,3,82,11.5)),('roof_tanks_and_groups',25.52,(0,0,79.5,21.5)),('7F_T_outline',24,(-1,-10,80,22)),('east3_recess',10,(78,-2.7,80,16.7)),('east4_recess',13,(78,-2.7,80,16.7)),('east5_recess',16,(78,-2.7,80,16.7)),('roof_high_low_step',28.1,(23,0,70,14)),('west_bottom_door',3,(-.4,8.7,.8,11.6))]:
 geom=GeometryCollection()
 for c in raw.slice(z*S).to_polygons():
  p=Polygon(c);assert p.is_valid;geom=geom.symmetric_difference(p)
 x0,y0,x1,y1=rect;region=box((x0-39.7675)*S,(y0-6)*S,(x1-39.7675)*S,(y1-6)*S);g=geom.intersection(region)
 polys=list(g.geoms) if hasattr(g,'geoms') else [g]
 local.append(dict(name=name,z_mm=z*S,rectangle_mm=list(region.bounds),solid_area_mm2=g.area,air_area_mm2=region.area-g.area,valid=g.is_valid,polygons=[dict(exterior=list(p.exterior.coords),holes=[list(r.coords) for r in p.interiors]) for p in polys if p.geom_type=='Polygon']))
 assert g.is_valid
# Two nearest intersections measure actual exposed slab/member thickness.
thickness=[]
for name,origin,direction,expected in [('east_canopy_vertical',(81,5.5,10),(0,0,-1),1.65),('west_water_tank_north_south',(8,14,25.52),(0,-1,0),4.8),('roof_parapet_north_south',(20,-2,25.02),(0,1,0),1.14)]:
 o=cv(origin);d=np.array(direction,float);loc,_,_=m.ray.intersects_location([o],[d],multiple_hits=True);dist=np.dot(loc-o,d);dist=np.unique(np.round(dist[dist>1e-6],7));dist.sort();assert len(dist)>=2,(name,dist)
 val=float(dist[1]-dist[0]);passed=abs(val-expected)<.002
 thickness.append(dict(name=name,origin_mm=o.tolist(),direction=d.tolist(),first_two_distance_mm=dist[:2].tolist(),thickness_mm=val,expected_approx_mm=expected,passed=passed))
normal=m.face_normals;cent=m.triangles_center;areas=m.area_faces;sel=(normal[:,2]<-.5)&(cent[:,2]>.15)
support=dict(downward_face_threshold_z=-.5,downward_facing_surface_area_mm2=float(areas[sel].sum()),downward_face_count=int(sel.sum()),support_review_required=True,critical_regions=['east projecting canopy and underside ribs','east 6F projecting soffit and ribs','north entry lintel','seventh-floor small outward wrap','facade projecting frames'],physical_print_tested=False,toolpath_generated=False,warning='Global component erosion does not certify minimum wall thickness. Nominal window mullions 0.45 mm and transoms 0.39 mm at this scale may be below a chosen nozzle/toolpath width; local slicer-specific treatment and supports required. Opaque glass panels are closed proxies, not glazing apertures.')
rpt=dict(probe_design_revision='v12: former west x=-0.1m 7F probe sampled a projecting window, not the building envelope. Replaced by paired south-long-face probes (40,-0.52,23) solid and (40,-0.52,20) air, correctly testing documented north/south 7F outward wrapping; west main wall remains x=0. Earlier probe is not evidence of a westward structural wrap.',stl_sha256=hashlib.sha256(b).hexdigest(),negative_space_probes=pr,local_slices=local,actual_mesh_ray_thickness=thickness,support=support,all_probes_passed=all(x['passed'] for x in pr),all_ray_thickness_passed=all(x['passed'] for x in thickness))
(A/'qa/feature-validation.json').write_text(json.dumps(rpt,ensure_ascii=False,indent=2)+'\n')
assert rpt['all_probes_passed'],[x for x in pr if not x['passed']]
assert rpt['all_ray_thickness_passed'],thickness
print('SCU CHUQIU ACTUAL MESH FEATURE/SLICES/THICKNESS PASS',len(pr),len(local),len(thickness))
