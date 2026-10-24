"""Actual raw STL probes; finite stair width/headheight and turning grids. No mesh repair."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,manifold3d as md
from qa_model import raw_read
A=Path(__file__).resolve().parent;_,v,f=raw_read(A/'model.stl');m=trimesh.Trimesh(v,f,process=False);S=2.5
rows=[]
def sample(label,p,w):rows.append({'label':label,'point_mm':(np.array(p)*S).tolist(),'expected_solid':w})
def route(label,x,y,h):
 sample(label+'_floor',(x,y,h-.06),True)
 for rise in [.04,.6,1.2,1.8,2.2]:sample(label+'_head_'+str(rise),(x,y,h+rise),False)
for k in range(4):
 z=.5+k*3.3
 for name,p,w in [('corridor',(0,-3,z+1.4),False),('room',(-7,2,z+1.4),False),('left_wall',(-29.85,2,z+1.4),True),('front_spandrel',(0,-4.35,z+.3),True)]:sample(str(k+1)+'F_'+name,p,w)
for k in range(3):
 z=.5+k*3.3
 for flight in [0,1]:
  for i in range(9):
   y=(-1.8+i*.5+.25) if flight==0 else (2.2-i*.5+.25)
   h=z+(i+1)*3.3/18+(1.65 if flight else 0)
   for x in ([2.48,3.28,4.08] if flight==0 else [4.92,5.72,6.52]):route(f'{k}_flight{flight}_tread{i}',x,y,h)
 for label,xs,ys,h in [('midlanding',np.arange(2.48,6.53,.25),np.arange(2.85,3.36,.15),z+1.65),('upperturn',np.arange(4.92,6.53,.25),np.arange(-2.9,-1.44,.15),z+3.3),('lowerstart',np.arange(2.48,4.09,.25),np.arange(-2.9,-1.94,.15),z)]:
  for x in xs:
   for y in ys:route(f'{k}_{label}',x,y,h)
for i in range(18):
 y=-6-(i+1)*.33+.15;h=max(.2,3.8-(i+1)*3.62/18)
 for x in [2.6,4.5,6.4]:
  sample(f'external_{i}_floor',(x,y,h-.03),True)
  for r in [.05,.5,1.2,2.2]:sample(f'external_{i}_head',(x,y,h+r),False)
for name,p,w in [('roof',(0,0,13.8),True),('no_tower',(4.5,0,15),False),('lower_landing',(4.5,-12.4,.10),True),('lower_landing_air',(4.5,-12.4,.35),False),('beyond_local_grade',(4.5,-13.2,.1),False),('entry_landing',(4.5,-5.3,3.65),True),('entry_air',(4.5,-5.3,4.2),False)]:sample(name,p,w)
# Ramp walking top, endpoint continuity and full-width dense landing transitions.
for x in np.arange(6.85,27.66,.13):
 h=3.8 if x<7 else (.4 if x>27 else 3.8-(x-7)*.17)
 for y in [-5.75,-5.25,-4.75]:
  sample('ramp_transition_floor',(x,y,h-.04),True)
  for rise in [.04,.5,1.2,2.2]:sample('ramp_transition_head',(x,y,h+rise),False)
for x in np.arange(2.5,6.61,.25):
 for y in np.arange(-5.8,-3.91,.15):
  sample('entry_fullwidth_floor',(x,y,3.74),True)
  for rise in [.1,1.0,2.2]:sample('entry_fullwidth_head',(x,y,3.8+rise),False)
got=[]
for i in range(0,len(rows),256):got.extend(m.contains(np.array([r['point_mm'] for r in rows[i:i+256]])).tolist())
failed=[]
for r,a in zip(rows,got):
 r['actual_solid']=a
 if r['expected_solid']!=a:failed.append(r)
raw=md.Manifold(md.Mesh(v.astype(np.float32),f.astype(np.uint32)));sections=[{'floor':k+1,'z_mm':(.5+k*3.3+1.55)*S,'contours_mm':[np.asarray(p).tolist() for p in raw.slice((.5+k*3.3+1.55)*S).to_polygons()]} for k in range(4)]
rays=[]
for name,o,d,e in [('front_window',(-28,-8,2),(0,1,0),(-28,-4.4,2)),('right_end',(34,2,6),(-1,0,0),(30,2,6)),('entry_landing',(4.5,-5.3,6),(0,0,-1),(4.5,-5.3,3.8)),('lower_landing',(4.5,-12.4,2),(0,0,-1),(4.5,-12.4,.18))]:
 hit,_,_=m.ray.intersects_location([np.array(o)*S],[d]);assert len(hit),name;first=hit[np.linalg.norm(hit-np.array(o)*S,axis=1).argmin()];err=float(np.linalg.norm(first-np.array(e)*S));assert err<.01,(name,first,np.array(e)*S);rays.append({'name':name,'origin_mm':(np.array(o)*S).tolist(),'first_hit_mm':first.tolist(),'expected_mm':(np.array(e)*S).tolist(),'error_mm':err})
for x in [6.85,6.95,7.05,7.15,26.85,26.95,27.05,27.15,27.5]:
 for y in [-5.75,-5.25,-4.75]:
  top=3.8 if x<7 else (.4 if x>27 else 3.8-(x-7)*.17)
  o=np.array([x,y,top+.4])*S;hit,_,_=m.ray.intersects_location([o],[[0,0,-1]]);assert len(hit);first=hit[np.linalg.norm(hit-o,axis=1).argmin()];err=float(abs(first[2]-top*S));assert err<.003,('ramp_actual_top',x,y,first,top)
  rays.append({'name':'ramp_endpoint_top','origin_mm':o.tolist(),'first_hit_mm':first.tolist(),'expected_top_mm':top*S,'error_mm':err})
r={'stl_sha256':hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),'first_hit_rays':rays,'sample_count':len(rows),'failed':failed,'probes':rows,'raw_sections':sections,'limits':'Normalized heights not humanaccess or code certification. No physical printtest. Thin rails frames glazing plates and supportremoval risks retained.'}
(A/'qa/feature-probes.json').write_text(json.dumps(r,indent=2));print('samples',len(rows),'failed',len(failed));assert not failed,failed[:8]
