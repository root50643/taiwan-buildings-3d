"""Source-linked raw STL occupancy, rays and sections: no geometry repair."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,manifold3d as md
from qa_model import raw_read
A=Path(__file__).resolve().parent;rec,v,f=raw_read(A/'model.stl');m=trimesh.Trimesh(v,f,process=False)
# Normalized model units; outputs and geometry inmm.
probes=[('ground_corridor_air',(-7,-4,2),False),('ground_rear_wall',(-7,-1,2),True),('far_end_display_room_closure',(12,-4,2),True),('left_stair_open_above_steps',(-13,-1,3.8),False),('upper_glass_corridor_air',(-7,-4,6),False),('upper_front_glass',(-7,-5.40,6),True),('short_corner_glass',(-14.91,-4,6),True),('left_white_shortwall',(-14.8,0,6),True),('left_stair_void_2F',(-13,0,6),False),('no_third_floor',(0,0,10),False),('neutral_rear_room',(0,5.3,6),True),('front_steps_connected',(-11,-5.8,.2),True),('left_steps_connected',(-15.3,-4,.2),True),('outside_fullsite',(-17,-7,.2),False)]
xyz=np.array([p for _,p,_ in probes])*4;got=m.contains(xyz);rows=[]
for (name,p,want),actual in zip(probes,got):assert bool(actual)==want,(name,actual,want);rows.append(dict(name=name,point_mm=(np.array(p)*4).tolist(),expected_solid=want,actual_solid=bool(actual)))
rays=[]
for name,origin,direction,expected in [('ground_open_portal',(-7,-8,2),(0,1,0),(-7,-2.3,2)),('right_closed_display',(12,-8,2),(0,1,0),(12,-5.5,2)),('upper_glazed_front',(-7,-8,6),(0,1,0),(-7,-5.5,6)),('short_white_notglass',(-18,0,6),(1,0,0),(-15.035,0,6))]:
 hit,_,_=m.ray.intersects_location(np.array([origin])*4,[direction]);assert len(hit);dist=np.linalg.norm(hit-np.array(origin)*4,axis=1);first=hit[np.argmin(dist)];err=float(np.linalg.norm(first-np.array(expected)*4));assert err<.02,(name,first,expected);rays.append(dict(name=name,origin_mm=(np.array(origin)*4).tolist(),first_hit_mm=first.tolist(),expected_mm=(np.array(expected)*4).tolist(),error_mm=err))
raw=md.Manifold(md.Mesh(v.astype(np.float32),f.astype(np.uint32)));sections=[]
for z in [2,6]:
 polys=raw.slice(z*4).to_polygons();sections.append({'z_mm':z*4,'loops':len(polys),'contours_mm':[np.asarray(p).tolist() for p in polys]})
# Local face-normal approximate thickness: sampled double sided rayexit from knownmaterial points.
thickness=[]
for name,origin,axis in [('front_glass_away_frames',(-7,-5.4,6),(0,1,0)),('roof_flat_center',(0,0,8.52),(0,0,1)),('column_core',(-10.4,-5.26,2),(1,0,0))]:
 distances=[]
 for sign in [-1,1]:
  hit,_,_=m.ray.intersects_location(np.array([origin])*4,[np.array(axis)*sign]);distance=np.linalg.norm(hit-np.array(origin)*4,axis=1);distances.append(float(distance.min()))
 thickness.append({'name':name,'through_thickness_mm':sum(distances),'method':'twoopposedrawSTLrayexitsfromsolidpoint','under_0_8_mm':sum(distances)<.8})
# Finite-width upper landing and side route: sampled center and +/-0.4 unit width.
# Stair top -> landing -> east side lane -> front corridor, with solid floor beneath.
route=[]
for x,y in [(-13.6,1.98),(-12.3,1.98),(-12.3,1),(-12.3,0),(-12.3,-1),(-12.3,-2),(-12.3,-3.3),(-10,-3.3),(-7,-3.3)]:
 for dx,dy in [(0,0),(-.4,0),(.4,0),(0,-.35),(0,.35)]:
  p=np.array([x+dx,y+dy,4.30])*4;q=np.array([x+dx,y+dy,4.75])*4
  assert bool(m.contains([p])[0]),('route_missing_floor',p)
  assert not bool(m.contains([q])[0]),('route_blocked_above_floor',q)
  route.append({'floor_mm':p.tolist(),'air_mm':q.tolist()})
report={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'finite_width_upper_stair_exit_route':route,'probes':rows,'first_hit_rays':rays,'raw_sections':sections,'local_thickness_samples':thickness,'support_warning':'True colonnade, ceiling, hollow upper glazed corridor and stairwell require slicer-specific supports/orientation. Upper corridor cavity communicates with real left stairwell and open1F, not filled for topology. Thin opaque glass panels and roofcrest tip require scale/material review. No physical print test; not printready certified.'}
(A/'qa/feature-probes.json').write_text(json.dumps(report,indent=2));print('feature probes/rays/sections pass; print warnings retained')
