"""Actual exported-mesh negative-space, local section, membrane thickness and support checks."""
from pathlib import Path
import json,hashlib,struct
import numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,Point,GeometryCollection,box
A=Path(__file__).resolve().parent
b=(A/'model.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0];r=np.frombuffer(b,dtype=[('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')],offset=84,count=n);v,inv=np.unique(r['v'].reshape(-1,3),axis=0,return_inverse=True);f=inv.reshape(-1,3);m=trimesh.Trimesh(v,f,process=False);assert m.is_watertight
S=2.7
def cv(p):return (np.array(p)-[40,23,0])*np.array([-S,S,S])
probes=[('B1_open_court',(48,22,3),False),('B1_floor',(48,22,1.2),True),('ground_not_court',(31,22,4),True),('oneF_bridge',(63.5,20,5.25),True),('under_oneF_bridge',(63.5,20,3.5),False),('twoF_bridge',(51.5,20,10.25),True),('under_twoF_bridge',(51.5,20,8),False),('threeF_west_bridge',(28.5,20,14.25),True),('under_threeF_west_bridge',(28.5,20,12),False),('threeF_east_bridge',(63.5,20,14.25),True),('north_3F_terrace',(54,4,17),False),('north_terrace_floor',(54,4,14.6),True),('south_5F_terrace',(50,30,25),False),('south_5F_back_wall',(50,35,25),True),('south_7F_step',(50,31,32),False),('south_8F_step',(32,32,36),False),('south_9F_step',(32,34,40),False),('rear_upper_notch',(31,47,36),False),('west_stair_slot',(1,42,12),False),('east_stair_slot',(65.5,42,12),False),('round_hall_solid',(9,6,8),True),('round_roof_no_glass_dome',(9,6,12),False)]
actual=m.contains(np.array([cv(p) for _,p,_ in probes]));pr=[]
for (name,p,expect),a in zip(probes,actual):pr.append(dict(name=name,point_mm=cv(p).tolist(),expected_solid=expect,actual_solid=bool(a),passed=bool(a)==expect))
assert all(x['passed'] for x in pr),[x for x in pr if not x['passed']]
raw=md.Manifold(md.Mesh(v.astype(np.float32),f.astype(np.uint32)))
# Actual horizontal local slices: retain every resulting polygon, no rounding or repairs.
local=[]
for name,z,rect in [('bridge1_section',5.25,(61.8,11.8,65.2,28.6)),('bridge2_section',10.25,(49.8,11.8,53.2,28.6)),('bridge3_section',14.25,(26.8,11.8,30.2,28.6)),('low_terrace',17,(44.8,-.2,63.2,9.2)),('high5_terrace',25,(44.8,28,63.2,32.9)),('B1_void',3,(35,14.4,63,28.0))]:
 geom=GeometryCollection()
 for c in raw.slice(z*S).to_polygons():
  p=Polygon(c);assert p.is_valid;geom=geom.symmetric_difference(p)
 x0,y0,x1,y1=rect;region=box((40-x1)*S,(y0-23)*S,(40-x0)*S,(y1-23)*S);g=geom.intersection(region)
 local.append(dict(name=name,z_mm=z*S,rectangle_mm=list(region.bounds),solid_area_mm2=g.area,air_area_mm2=region.area-g.area,valid=g.is_valid,contours=[list(p.exterior.coords) for p in (list(g.geoms) if g.geom_type=='MultiPolygon' else [g]) if p.geom_type=='Polygon']))
 assert g.is_valid
# Normal thickness measured by two ray intersections on actual membrane triangles.
thickness=[]
for name,x0,x1,y0,y1,base,amp,t in [('main',9,67,11.9,28.5,20.5,1.6,.5),('small',26.8,36.2,41.3,49.7,43.2,1.1,.45)]:
 for u,w in [(.22,.35),(.45,.5),(.72,.65)]:
  skew=4.5 if name=='main' else 0
  x=x0+(x1-x0)*u+skew*w+1.1*np.sin(np.pi*w)*(1 if u<.5 else -1)*(abs(2*u-1)**3);y=y0+(y1-y0)*w;z=base+amp*(2*u-1)*(2*w-1)+.7*np.sin(3*np.pi*u)*np.sin(np.pi*w)
  # Use the actual nearest upper-membrane triangle normal, not an analytic approximation.
  _,_,face=trimesh.proximity.closest_point(m,[cv((x,y,z+t))]);normal=m.face_normals[int(face[0])].copy()
  if normal[2]<0:normal=-normal
  center=cv((x,y,z+t/2));orig=center+normal*4
  loc,_,_=m.ray.intersects_location([orig],[-normal],multiple_hits=True);ds=np.dot(loc-orig,-normal);ds=np.sort(ds[(ds>1)&(ds<7)])
  assert len(ds)==2,(name,ds.tolist());val=float(ds[1]-ds[0]);assert val>.8,(name,val)
  thickness.append(dict(membrane=name,u=u,v=w,normal_thickness_mm=val,ray_origin_mm=orig.tolist(),ray_direction=(-normal).tolist()))
# Down-facing real triangle area: indication only, not physical-print or full slicer certification.
normal=m.face_normals;cent=m.triangles_center;areas=m.area_faces;sel=(normal[:,2]<-.5)&(cent[:,2]>.15)
support=dict(downward_face_threshold_z=-.5,downward_facing_surface_area_mm2=float(areas[sel].sum()),downward_face_count=int(sel.sum()),support_required=True,critical_regions=['large curved membrane','small roof membrane','1–3F suspended bridges','terrace lintels and roof edges','projecting stair landings'],physical_print_tested=False,warning='Global positive slice-component erosion is not a complete minimum-wall or support analysis. Opaque glazing fins may be finer than a nozzle; inspect chosen slicer, orient/support manually.')
rpt=dict(stl_sha256=hashlib.sha256(b).hexdigest(),negative_space_probes=pr,local_slices=local,membrane_normal_thickness=thickness,support=support,all_probes_passed=True)
(A/'qa/feature-validation.json').write_text(json.dumps(rpt,ensure_ascii=False,indent=2)+'\n');print('NFU CMA LOCAL NEGATIVE SPACE / MEMBRANE THICKNESS PASS',min(x['normal_thickness_mm'] for x in thickness))
