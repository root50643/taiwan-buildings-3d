"""Raw STL air/solid probes, exact local slices, ray thickness and support evidence."""
from pathlib import Path
import json,hashlib,struct
import numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection,box
A=Path(__file__).resolve().parent;b=(A/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0]
r=np.frombuffer(b,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n);v,inv=np.unique(r['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3);m=trimesh.Trimesh(v,f,process=False);assert m.is_watertight
S=3.5
def cv(p):return (np.array(p)-[27,19.85,0])*S
probes=[('west_open_porch',(1.5,11,5),False),('west_porch_floor',(1.5,11,3.1),True),('west_recessed_glass',(3.25,11,5),True),('west_entrance_approach_air',(-.5,20,5),False),('west_stair_underflight_air',(-3.5,20,1.6),False),('main_hall_solid_omitted_interior',(20,20,5),True),('west_basement_recess_air',(.3,10,1.7),False),('west_basement_glass',(.9,10,1.7),True),('north_porch_air',(20,38,5),False),('south_porch_air',(20,1.5,5),False),('chamfer_corner_air',(.8,.8,5),False),('north_entrance_stair',(20.1,43,2.3),True),('north_nonentrance_air',(11.3,43,2.3),False),('south_entrance_stair',(11.3,-3,2.3),True),('south_nonentrance_air',(20.1,-3,2.3),False),('main_rooflight_solid',(19.85,19.85,12.3),True),('above_rooflight_air',(19.85,19.85,12.8),False),('service_central_gray_roof',(47,20,6.6),True),('service_above_gray_roof_air',(47,20,7.3),False),('service_below_gray_roof_solid_kitchen',(47,20,5),True),('service_north_high_wall',(47,25.15,8),True),('service_north_high_clerestory',(47,24.98,7.4),True),('service_east_high_clerestory',(52.02,20,7.4),True),('service_north_west_slope_end_closed',(42.75,26,6.85),True),('service_south_west_slope_end_closed',(42.75,14,6.85),True),('east_half_south_base_solid',(30,.3,1.7),True),('east_half_north_base_solid',(30,39.4,1.7),True),('south_entrance_door_low',(10.2,3.2,3.45),True),('north_entrance_door_low',(20,36.5,3.45),True),('west_entrance_door_low',(3.2,20,3.45),True),('service_first_ground_door',(60.5,15.5,3.2),True),('service_second_ground_door',(60.5,24.2,3.2),True),('north_yard_no_invented_object',(50,37,4),False),('south_yard_no_invented_object',(50,2,4),False)]
actual=m.contains(np.array([cv(p) for _,p,_ in probes]));pr=[]
for (name,p,e),a in zip(probes,actual):pr.append(dict(name=name,point_mm=cv(p).tolist(),expected_solid=e,actual_solid=bool(a),passed=bool(a)==e))
assert all(x['passed'] for x in pr),[x for x in pr if not x['passed']]
raw=md.Manifold(md.Mesh(v.astype(np.float32),f.astype(np.uint32)));local=[]
for name,z,rect in [('west_porch',5,(-.5,6,4,14)),('west_basement_recess',1.7,(-.2,8,1.5,13)),('west_stair_underside',1.6,(-5,17,-2,23)),('north_asymmetric_entry',2.3,(8,41,23,45)),('south_asymmetric_entry',2.3,(8,-5,23,-1.5)),('service_gray_roof',6.6,(43,15,52,25)),('air_above_covered_service_center',7.3,(43,15,52,25)),('central_rooflight',12.3,(16,16,24,24))]:
 geom=GeometryCollection()
 for c in raw.slice(z*S).to_polygons():
  p=Polygon(c);assert p.is_valid;geom=geom.symmetric_difference(p)
 x0,y0,x1,y1=rect;region=box((x0-27)*S,(y0-19.85)*S,(x1-27)*S,(y1-19.85)*S);g=geom.intersection(region)
 local.append(dict(name=name,z_mm=z*S,rectangle_mm=list(region.bounds),solid_area_mm2=g.area,air_area_mm2=region.area-g.area,valid=g.is_valid,contours=[list(p.exterior.coords) for p in (list(g.geoms) if g.geom_type=='MultiPolygon' else [g]) if p.geom_type=='Polygon']));assert g.is_valid
thickness=[]
for name,pt,normal in [('west_porch_guard',(0,10,3.7),(1,0,0)),('west_window_mullion',(3.12,5.4,5),(0,1,0)),('main_roof_slab',(7,19.85,9.153),(0,0,1)),('stair_slab',(-3.4,20,2.15),(0,0,1))]:
 center=cv(pt);normal=np.array(normal,dtype=float);origin=center+normal*5
 loc,_,_=m.ray.intersects_location([origin],[-normal],multiple_hits=True);ds=np.sort(np.dot(loc-origin,-normal));ds=ds[(ds>0)&(ds<10)]
 # retain all crossings and the closest bracketing pair; no invented analytic thickness.
 assert len(ds)>=2,(name,ds.tolist());mid=np.argmin(abs((ds[:-1]+ds[1:])/2-5));val=float(ds[mid+1]-ds[mid]);thickness.append(dict(name=name,actual_two_surface_thickness_mm=val,ray_distances_mm=ds.tolist(),ray_origin_mm=origin.tolist(),ray_direction=(-normal).tolist()))
normal=m.face_normals;sel=(normal[:,2]<-.5)&(m.triangles_center[:,2]>.15)
support=dict(downward_face_threshold_z=-.5,downward_facing_surface_area_mm2=float(m.area_faces[sel].sum()),downward_face_count=int(sel.sum()),support_required=True,critical_regions=['main open perimeter porch and square eaves','external stair slab undersides','service roof overhangs'],physical_print_tested=False,warning='0.56mm window mullions and hip ridges may merge/disappear in FFF. Local rays and global erosion are not universal minimum-wall certification; supports and slicer review required.')
rpt=dict(stl_sha256=hashlib.sha256(b).hexdigest(),negative_space_probes=pr,local_slices=local,local_ray_thickness=thickness,support=support,all_probes_passed=True)
(A/'qa/feature-validation.json').write_text(json.dumps(rpt,ensure_ascii=False,indent=2)+'\n');print('NPUST LOCAL SPACE / ACTUAL RAY THICKNESS PASS',json.dumps(thickness))
