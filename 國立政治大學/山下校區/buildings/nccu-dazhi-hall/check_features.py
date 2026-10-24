"""Source-linked raw STL occupancy, rays and sections. No healing or source-image embedding."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,manifold3d as md
from qa_model import raw_read
A=Path(__file__).resolve().parent;_,v,f=raw_read(A/'model.stl');m=trimesh.Trimesh(v,f,process=False);S=2.5
probes=[]
for k in range(4):
 z=.5+3.3*k
 probes.extend([(f'{k+1}F_corridor_air',(0,-4,z+1.5),False),(f'{k+1}F_room_air',(0,2,z+1.5),False),(f'{k+1}F_left_single_service_air',(-27.35,3,z+1.5),False),(f'{k+1}F_right_pair_partition',(27.35,3,z+1.5),True),(f'{k+1}F_right_sanitary_air',(28.7,3,z+1.5),False),(f'{k+1}F_left_short_wall',(-29.85,3,z+1.5),True),(f'{k+1}F_corridor_parapet',(0,-4.85,z+.4),True)])
probes += [('roof_closure',(0,0,13.8),True),('no_roof_tower',(0,0,15),False),('no_fourstorey_external_wing',(34,-4,8),False),('2F_finite_landing',(30.8,-4,3.65),True),('2F_landing_air',(30.8,-4,4.1),False),('stair_ground_footing',(36.9,-4,.1),True),('outside_bounded_site',(39,-4,.1),False),('outside_footing_width',(34,-6,.1),False)]
xyz=np.array([p for _,p,_ in probes])*S;got=m.contains(xyz);rows=[]
for (n,p,w),a in zip(probes,got):assert bool(a)==w,(n,p,bool(a),w);rows.append({'name':n,'point_mm':(np.array(p)*S).tolist(),'expected_solid':w,'actual_solid':bool(a)})
rays=[]
for name,o,d,e in [('classroom_window',(-26.6,8,2),(0,-1,0),(-26.6,4.91,2)),('right_short_end',(35,2,6),(-1,0,0),(30,2,6)),('2F_external_landing_top',(30.7,-4,7),(0,0,-1),(30.7,-4,3.8)),('no_extended_roof',(33,-4,16),(0,0,-1),(33,-4,.5+3.3-(6)*(3.62)/18))]:
 hit,_,_=m.ray.intersects_location([np.array(o)*S],[d]);assert len(hit),name;dist=np.linalg.norm(hit-np.array(o)*S,axis=1);first=hit[dist.argmin()];err=float(np.linalg.norm(first-np.array(e)*S));assert err<.01,(name,first,np.array(e)*S);rays.append({'name':name,'origin_mm':(np.array(o)*S).tolist(),'first_hit_mm':first.tolist(),'expected_mm':(np.array(e)*S).tolist(),'error_mm':err})
route=[]
for k in range(1,4):
 z=.5+3.3*k
 for x in [-26.2,28.8]:
  for y in [-2.7,-2.9,-3.1,-3.5,-4.0]:
   p=np.array([x,y,z-.08])*S;q=np.array([x,y,z+.3])*S
   assert bool(m.contains([p])[0]),('stair_exit_floor',p)
   assert not bool(m.contains([q])[0]),('stair_exit_air',q)
   route.append({'floor_mm':p.tolist(),'air_mm':q.tolist()})
# Entire internal stair flights: finite-width tread floor and head-air checks,
# including actual return lasttreads rather than only exit landings.
internal=[]
for k in range(3):
 z=.5+3.3*k
 for x0,x1 in [(-29.65,-25.25),(25.25,29.65)]:
  mid=(x0+x1)/2
  for flight in [0,1]:
   for i in range(9):
    y=(-3+i*.35+.175) if flight==0 else (-.2-i*.35+.175)
    height=z+(i+1)*3.3/18+(1.65 if flight else 0)
    xs=[x0+.5,(x0+mid)/2,mid-.5] if flight==0 else [mid+.5,(mid+x1)/2,x1-.5]
    for x in xs:
     ground=np.array([x,y,height-.06])*S;assert m.contains([ground])[0],('internal_tread_floor',k,flight,i,ground)
     for rise in [.04,.6,1.2,1.8,2.2]:
      air=np.array([x,y,height+rise])*S;assert not m.contains([air])[0],('internal_tread_headroom',k,flight,i,air)
      internal.append({'storey_from':k+1,'core_x':[x0,x1],'flight':flight,'tread':i,'floor_mm':ground.tolist(),'air_mm':air.tolist(),'tested_headrise_normalized':rise})
  for x in [x0+.5,mid,x1-.5]:
   floor=np.array([x,.5,z+1.65-.06])*S;assert m.contains([floor])[0]
   for rise in [.04,.6,1.2,1.8,2.2]:
    air=np.array([x,.5,z+1.65+rise])*S;assert not m.contains([air])[0],('midlanding_headroom',air)
    internal.append({'storey_from':k+1,'core_x':[x0,x1],'flight':'midlanding','floor_mm':floor.tolist(),'air_mm':air.tolist()})
# Dense finite-width turns across the whole midpoint landing and last-tread
# to upper exit/corridor, not endpoint-only clearance inference.
turn_grids=[]
for k in range(3):
 z=.5+3.3*k
 for x0,x1 in [(-29.65,-25.25),(25.25,29.65)]:
  mid=(x0+x1)/2
  regions=[('midlanding',np.arange(x0+.35,x1-.34,.25),np.arange(.25,.81,.15),z+1.65),('upperturn',np.arange(mid+.35,x1-.34,.25),np.arange(-3.75,-2.84,.15),z+3.3),('lowerstart',np.arange(x0+.35,mid-.34,.25),np.arange(-3.75,-3.09,.15),z)]
  for label,xs,ys,level in regions:
   for x in xs:
    for y in ys:
     ground=np.array([x,y,level-.06])*S;assert m.contains([ground])[0],('turn_grid_floor',label,ground)
     for rise in [.1,1.2,2.2]:
      air=np.array([x,y,level+rise])*S;assert not m.contains([air])[0],('turn_grid_headroom',label,air)
      turn_grids.append({'region':label,'storey_from':k+1,'floor_mm':ground.tolist(),'air_mm':air.tolist()})
# Verify external sequence has solid under each tread and open air above its centre.
steps=[]
for i in range(18):
 x=31.35+i*.3+.15;h=3.8-(i+1)*3.62/18
 p=np.array([x,-4,max(.2,h)-.03])*S;q=np.array([x,-4,max(.2,h)+.1])*S
 assert m.contains([p])[0] and not m.contains([q])[0],('external_step',i)
 steps.append({'step':i,'floor_mm':p.tolist(),'air_mm':q.tolist()})
raw=md.Manifold(md.Mesh(v.astype(np.float32),f.astype(np.uint32)));sections=[]
for k in range(4):
 z=(.5+k*3.3+1.55)*S;sections.append({'z_mm':z,'contours_mm':[np.asarray(p).tolist() for p in raw.slice(z).to_polygons()]})
(A/'qa/feature-probes.json').write_text(json.dumps({'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'probes':rows,'first_hit_rays':rays,'finite_upper_end_stair_exit_routes':route,'all_internal_treads_finite_width_floor_and_headair':internal,'dense_finite_width_stair_turn_grids':turn_grids,'external_stair_tread_air_and_ground_contacts':steps,'raw_sections':sections,'limits':'Interior partitions and exact stairs approximate; no sourcepixel textures. Hollow rooms communicate via doorway/corridor/endstairs, not filled for shellcount. Thin opaque windows, braces, rails, stair soffits and ceilings require scale/support/orientation review; no physical printtest or printready certification.'},indent=2));print('feature probes, rays, rawsections, stair exits and tread contact checks passed')
