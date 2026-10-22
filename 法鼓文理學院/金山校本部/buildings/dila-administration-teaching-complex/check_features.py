"""Raw exported STL local air/solid probes, exact sections, two-sided ray thickness and support evidence."""
from pathlib import Path
import json,hashlib,struct
import numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection,box
A=Path(__file__).resolve().parent;b=(A/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0]
r=np.frombuffer(b,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n);v,inv=np.unique(r['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3);m=trimesh.Trimesh(v,f,process=False);assert m.is_watertight
S=2.1
def cv(p):return (np.array(p)-[55,40,0])*S
probes=[('front_court_air',(67,20,5),False),('front_court_floor',(67,20,2.8),True),('GC_link_8m_deck',(49,25,7.8),True),('under_GC_link_8m',(49,25,5),False),('GC_link_12_5m_deck',(49,35,12.3),True),('under_GC_link_12_5m',(49,35,10),False),('court_no_invented_crossbridge_front',(67,25,7.8),False),('court_no_invented_crossbridge_upper',(67,55,12.3),False),('GB_upper_link_deck',(84,45,12.3),True),('under_GB_upper_link',(84,45,10),False),('GA_top_frame_gap',(49,76,24),False),('GA_top_short_roof',(37,77,26),True),('GA_top_long_roof',(80,77,26),True),('GA_recessed_gallery_air',(80,70,19),False),('GA_deep_inner_wall',(80,76,19),True),('GA_ground_transverse_opening',(50,76,14),False),('GC_first_slot',(34,22,14),False),('GC_second_slot',(34,44,14),False),('GC_GA_slot',(34,65,14),False),('GC_roof_slot_open',(34,22,17.1),False),('GC_classroom_solid',(34,10,14),True),('GB_tall_hall',(95,25,16),True),('closed_buried_GB_not_cutaway',(95,25,2.5),True),('lower_ground_terrace',(67,35,4.5),True),('higher_ground_terrace',(67,53,8.3),True)]
for i in range(3):
 y=3.8+21.4*i;probes += [(f'lecture_sector_{i}',(8,y+5,10),True),(f'outside_sector_corner_{i}',(16,y+13,10),False),(f'sunken_lightwell_{i}',(22,y+8,10),False),(f'well_planted_bottom_{i}',(22,y+8,6.3),True),(f'rooflight_cap_{i}',(19,y+11.2,13.35),True),(f'rooflight_inner_void_{i}',(19,y+11.2,12.7),False),(f'well_crossbridge_{i}',(22,y+16,12),True)]
actual=m.contains(np.array([cv(p) for _,p,_ in probes]));pr=[]
for (name,p,e),a in zip(probes,actual):pr.append(dict(name=name,point_mm=cv(p).tolist(),expected_solid=e,actual_solid=bool(a),passed=bool(a)==e))
assert all(x['passed'] for x in pr),[x for x in pr if not x['passed']]
raw=md.Manifold(md.Mesh(v.astype(np.float32),f.astype(np.uint32)));local=[]
for name,z,rect in [('GC_lower_link',7.8,(46,23,52,28)),('under_GC_lower_link',5,(46,23,52,28)),('GC_upper_link',12.3,(46,33,52,38)),('GA_top_gap',24,(46,70,52,84)),('GC_slot_1',14,(27,19,44,25)),('lecture_lightwell',10,(19.5,4.3,24.4,18.6)),('lecture_quarter_sector',10,(3,3.5,18,18.5))]:
 geom=GeometryCollection()
 for c in raw.slice(z*S).to_polygons():
  p=Polygon(c);assert p.is_valid;geom=geom.symmetric_difference(p)
 x0,y0,x1,y1=rect;region=box((x0-55)*S,(y0-40)*S,(x1-55)*S,(y1-40)*S);g=geom.intersection(region)
 local.append(dict(name=name,z_mm=z*S,rectangle_mm=list(region.bounds),solid_area_mm2=g.area,air_area_mm2=region.area-g.area,valid=g.is_valid,contours=[list(p.exterior.coords) for p in (list(g.geoms) if g.geom_type=='MultiPolygon' else [g]) if p.geom_type=='Polygon']));assert g.is_valid
thickness=[]
for name,pt,normal in [('lower_bridge_slab',(49,30,7.725),(0,0,1)),('upper_bridge_slab',(49,35,12.225),(0,0,1)),('GC_gallery_slab',(46,10,12.2),(0,0,1)),('rooflight_cap',(19.4,15.4,13.37),(0,0,1)),('rooflight_crossbar',(19.9,15,13.5),(0,1,0)),('bridge_top_rail',(50.8,35,13.55),(1,0,0))]:
 center=cv(pt);normal=np.array(normal,dtype=float);origin=center+normal*3
 loc,_,_=m.ray.intersects_location([origin],[-normal],multiple_hits=True);ds=np.sort(np.dot(loc-origin,-normal));ds=ds[(ds>1)&(ds<5)]
 assert len(ds)==2,(name,ds.tolist());val=float(ds[1]-ds[0]);thickness.append(dict(name=name,actual_two_surface_thickness_mm=val,ray_origin_mm=origin.tolist(),ray_direction=(-normal).tolist()))
normal=m.face_normals;sel=(normal[:,2]<-.5)&(m.triangles_center[:,2]>.15)
support=dict(downward_face_threshold_z=-.5,downward_facing_surface_area_mm2=float(m.area_faces[sel].sum()),downward_face_count=int(sel.sum()),support_required=True,critical_regions=['GA projecting deep upper frames','multilevel courtyard bridges','lecture podiums over lightwells','gallery slabs and external stair flights'],physical_print_tested=False,warning='Thin rooflight glass proxy, crossbars, glazing mullions and fins may merge/disappear in FFF. Sampling and horizontal erosion are not universal minimum-wall certification.')
rpt=dict(stl_sha256=hashlib.sha256(b).hexdigest(),negative_space_probes=pr,local_slices=local,local_ray_thickness=thickness,support=support,all_probes_passed=True)
(A/'qa/feature-validation.json').write_text(json.dumps(rpt,ensure_ascii=False,indent=2)+'\n');print('DILA LOCAL NEGATIVE SPACE / ACTUAL RAY THICKNESS PASS',json.dumps(thickness))
