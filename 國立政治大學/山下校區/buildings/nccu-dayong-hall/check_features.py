"""Every raw-STL stair tread, three width samples, five head heights and dense landings."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,manifold3d as md
from qa_model import raw_read
A=Path(__file__).resolve().parent;_,v,f=raw_read(A/'model.stl');m=trimesh.Trimesh(v,f,process=False);S=2.5;rows=[]
def sample(label,p,w):rows.append(dict(label=label,point_mm=(np.array(p)*S).tolist(),expected_solid=w))
def route(label,x,y,h):
 sample(label+'_floor',(x,y,h-.06),True)
 for rise in [.04,.6,1.2,1.8,2.2]:sample(label+'_head'+str(rise),(x,y,h+rise),False)
for k in range(4):
 z=.5+k*3.3
 for n,p,w in [('corridor',(0,2,z+1.3),False),('room',(0,-1,z+1.3),False),('back',(0,3.42,z+.5),True),('shortwall',(-29.9,0,z+1.2),True)]:sample(f'{k}_{n}',p,w)
for core,c in enumerate([-27.8,-10.7,11.4,27.8]):
 a=c-2.12;bb=c+2.12
 for k in range(3):
  z=.5+k*3.3
  for flight in [0,1]:
   xs=[a+.45,c-1.05,c-.35] if not flight else [c+.35,c+1.05,bb-.45]
   for i in range(9):
    y=(3.35+i*.34+.18) if not flight else (6.07-i*.34+.18)
    h=z+(i+1)*3.3/18+(1.65 if flight else 0)
    for x in xs:route(f'core{core}_floor{k}_flight{flight}_step{i}',x,y,h)
  for label,xs,ys,h in [('midlanding',np.arange(a+.4,bb-.3,.21),np.arange(6.49,6.96,.11),z+1.65),('upperturn',np.arange(c+.35,bb-.3,.19),np.arange(2.9,3.65,.11),z+3.3),('lowerstart',np.arange(a+.4,c-.2,.19),np.arange(2.9,3.28,.10),z)]:
   for x in xs:
    for y in ys:route(f'core{core}_floor{k}_{label}',x,y,h)
E=-10.5;G=1.85
for i in range(12):
 y=-5.3-(i+1)*.33+.16;h=max(G+.02,3.8-(i+1)*(3.8-G)/12)
 for x in [E-1.5,E,E+1.5]:route(f'external_step{i}',x,y,h)
for label,xs,ys,h in [('entry',np.arange(E-1.6,E+1.65,.23),np.arange(-5.13,-3.11,.17),3.8),('foot',np.arange(E-1.6,E+1.65,.23),np.arange(-10.0,-9.35,.12),G),('ramp_lower',np.arange(-29.0,-28.6,.13),np.arange(-5.05,-4.05,.20),1.88)]:
 for x in xs:
  for y in ys:route(label,x,y,h)
for x in np.arange(-28.95,-12.34,.12):
 h=1.88 if x<-28.5 else (3.8 if x>-12.5 else 1.88+(x+28.5)/16*1.92)
 for y in [-5.0,-4.6,-4.15]:route('ramp_and_both_endpoint_transitions',x,y,h)
for name,p,w in [('roof',(0,0,13.8),True),('no_tower',(-10.7,5,14.4),False),('second_gap',(11.3,-3.5,4.8),False),('no_second_canopy',(11.3,-5,6.5),False),('beyondgrade',(E,-10.5,1),True)]:sample(name,p,w)
# Exact old beyondgrade point retained: now intentionally inside the new terrain.
# V2 legacy expectation failure is preserved outside source ZIP; no test point dropped.
for y in np.arange(-15.05,-9.38,.13):
 h=1.85 if y>-10.9 else .18+(y+15.2)/4.3*1.67
 for x in [E-1.5,E,E+1.5]:route('new_foot_front_grade_transition',x,y,h)
for side in [-1,1]:
 for dx in np.arange(2.7,5.0,.13):
  h=1.85 if dx<2.9 else .18+(5.1-dx)/2.2*1.67
  for y in [-10.65,-10.15,-9.65]:route('new_foot_side_grade_transition',E+side*dx,y,h)
for x in np.arange(-33.35,-28.6,.13):
 h=1.88 if x>-29.55 else .18+(x+33.5)/3.95*1.70
 for y in [-5.2,-4.7,-4.2]:route('new_ramp_left_grade_transition',x,y,h)
for y in np.arange(-8.05,-5.35,.13):
 h=1.88 if y>-5.6 else .18+(y+8.2)/2.6*1.70
 for x in [-29.4,-29.0,-28.6]:route('new_ramp_front_grade_transition',x,y,h)
sample('outside_new_foot_grade',(E,-15.5,.1),False)
sample('outside_new_ramp_grade',(-33.8,-4.7,.1),False)
got=[]
for i in range(0,len(rows),64):got.extend(m.contains(np.array([r['point_mm'] for r in rows[i:i+64]])).tolist())
failed=[]
for r,a in zip(rows,got):
 r['actual_solid']=a
 if r['expected_solid']!=a:failed.append(r)
raw=md.Manifold(md.Mesh(v.astype(np.float32),f.astype(np.uint32)));sections=[dict(floor=k+1,z_mm=(.5+k*3.3+1.5)*S,contours_mm=[np.asarray(p).tolist() for p in raw.slice((.5+k*3.3+1.5)*S).to_polygons()]) for k in range(4)]
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),sample_count=len(rows),failed=failed,probes=rows,raw_sections=sections,limits='Raw STL model-unit sampled routes, not human or building-code clearances. All failures retained; no repairs.')
(A/'qa/feature-probes.json').write_text(json.dumps(report,indent=2));print('samples',len(rows),'failed',len(failed));assert not failed,failed[:12]
