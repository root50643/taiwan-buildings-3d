"""Original STL triangle ray controls; no repair or substituted mesh."""
from pathlib import Path
import numpy as np,trimesh,json,hashlib
R=Path(__file__).resolve().parent;raw=(R/'model.stl').read_bytes();m=trimesh.load(R/'model.stl',process=False);S=2.6;B=1.6;rows=[]
def T(x,y,h):return np.array([x*S,y*S,B+h*S])
def hit(o,d):
 d=np.array(d,float);q,_,_=m.ray.intersects_location([o],[d],multiple_hits=True)
 return sorted(set(round(float(np.dot(v-o,d)),6) for v in q if np.dot(v-o,d)>1e-5))
def check(name,p,d,fn,**data):
 o=T(*p);q=hit(o,d);ok=bool(fn(q));rows.append(dict(name=name,origin_mm=o.tolist(),direction=d,hits_mm=q,passed=ok,**data));assert ok,(name,q,data)
def width(name,p,d,minimum,**data):
 o=T(*p);d=np.array(d);a=hit(o,d);b=hit(o,-d);w=a[0]+b[0] if a and b else 0;ok=bool(a and b and w>=minimum-2e-4)
 rows.append(dict(name=name,origin_mm=o.tolist(),direction=d.tolist(),positive_hits_mm=a,negative_hits_mm=b,continuous_width_mm=w,minimum_mm=minimum,passed=ok,**data));assert ok,(name,a,b)
def down(name,x,y,h=25):check(name,(x,y,h),[0,0,-1],lambda q:len(q)==2 and abs(q[-1]-(B+h*S))<.0003,continuous_to_base=True)
# Four original high cylindrical portico pillars are rooted at lower slab and ceiling.
for i,x in enumerate([-5.7,-1.9,1.9,5.7]):
 for h in [1.1,4.2,8.4]:width(f'front_high_column_{i}_{h}',(x,-24.2,h),[1,0,0],.66*S)
 check(f'front_high_column_{i}_lower_root',(x,-24.2,4),[0,0,-1],lambda q:len(q)==1 and abs(q[0]-(B+4*S))<.0002)
 check(f'front_high_column_{i}_upper_root',(x,-24.2,8.4),[0,0,1],lambda q:q and q[0]>=.75*S-.0002)
 check(f'front_high_column_{i}_balcony_root',(x,-24.2,8.9),[0,1,0],lambda q:q and q[0]>1.4*S)
for i,x in enumerate([-7.6,-3.8,0,3.8,7.6]):
 check(f'five_portico_bay_{i}_clear',(x,-28,4.1),[0,1,0],lambda q:q and abs(q[0]-9*S)<.0003,actual_clear_depth_mm=5.2*S)
# All highest gallery pillars, including railing intersections, width and both roots.
cols=[(x,y) for y in [-22.35,22.35] for x in np.linspace(-11.7,11.7,7)]+[(x,y) for x in [-22.3,22.3] for y in np.linspace(-10.5,10.5,8)]
for i,(x,y) in enumerate(cols):
 for h in [13.8,15.3]:width(f'upper_gallery_column_{i}_{h}',(x,y,h),[1,0,0],.48*S)
 check(f'upper_gallery_column_{i}_lower_root',(x,y,13.9),[0,0,-1],lambda q:q and q[0]>(13.9-12.6)*S)
 check(f'upper_gallery_column_{i}_upper_root',(x,y,15.3),[0,0,1],lambda q:q and q[0]>.85*S)
# Recreate only control locations, not geometry. Actual surface remains original STL.
rails=[]
for y in [-22.35,22.35]:rails.append(((-12.5,y),(12.5,y),12.9))
for x in [-22.35,22.35]:rails.append(((x,-11.6),(x,11.6),12.9))
for x0,x1 in [(-24.5,-9.5),(9.5,24.5)]:
 for y0,y1 in [(-25.5,-10),(10,25.5)]:
  rails.extend([(a,b,9) for a,b in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]])
rails.append(((-9.2,-24.3),(9.2,-24.3),9))
for i,(a,b,h) in enumerate(rails):
 n=max(2,int(np.linalg.norm(np.array(b)-a)/2.5)+1);normal=np.array([-(b[1]-a[1]),b[0]-a[0],0.]);normal/=np.linalg.norm(normal)
 for j,p in enumerate(np.linspace(a,b,n)):
  width(f'rail_{i}_post_{j}',(*p,h+.5),[1,0,0],1.144)
  width(f'rail_{i}_post_{j}_y',(*p,h+.5),[0,1,0],1.144)
  check(f'rail_{i}_post_{j}_lower_root',(*p,h+.5),[0,0,-1],lambda q:q and q[0]>.60*S)
  check(f'rail_{i}_post_{j}_upper_root',(*p,h+.5),[0,0,1],lambda q:q and q[0]>=.54*S-.0002)
 p=np.array(a)*.63+np.array(b)*.37
 width(f'rail_{i}_top_band',(*p,h+.9),normal.tolist(),1.04)
# Five front middle panes and backed thin frames; no fragile independent mullions.
for i,x in enumerate(np.linspace(-8.9,5.6,5)):
 check(f'front_middle_pane_{i}',(x+.5,-28,10.6),[0,1,0],lambda q:q and abs(q[0]-(28-23.48)*S)<.0003,recess_depth_mm=.32*S)
 check(f'front_middle_vertical_frame_{i}',(x+1.5,-28,10.6),[0,1,0],lambda q:len(q)>=2 and abs(q[0]-(28-23.66)*S)<.0003 and q[1]-q[0]>1,frame_width_mm=.2*S,back_overlap_mm=.18*S)
 check(f'front_middle_horizontal_frame_{i}',(x+.6,-28,11.4),[0,1,0],lambda q:len(q)>=2 and abs(q[0]-(28-23.65)*S)<.0003 and q[1]-q[0]>1,frame_height_mm=.15*S)
# Each side has eight explicit broad shallow panes in three rows. Small mullions omitted.
for side in [-1,1]:
 for j,y in enumerate(np.linspace(-10.6,8.1,8)):
  for h in [2.8,5,10.5]:check(f'side_{side}_bay_{j}_row_{h}',(side*28,y+1,h),[-side,0,0],lambda q:q and abs(q[0]-(28-20.72)*S)<.0003,backing_recess_mm=.28*S)
# Real rear round recess, backed cross, outside corner lower windows differ from front.
check('rear_round_window_back',(0.5,28,6.4),[0,-1,0],lambda q:q and abs(q[0]-(28-22.65)*S)<.0003)
check('rear_round_cross_root',(0,28,6.6),[0,-1,0],lambda q:len(q)>=2 and abs(q[0]-(28-22.85)*S)<.0003 and q[1]-q[0]>1)
check('rear_round_window_opaque_surround',(2,28,5.9),[0,-1,0],lambda q:q and abs(q[0]-5*S)<.0003)
# Court is genuinely open above solid lecture-room roof and reaches the base.
down('court_floor_root',0,0);check('court_floor_height',(0,0,25),[0,0,-1],lambda q:q and abs(q[0]-(25-9.15)*S)<.0003)
# Roof finite eaves and ridge widths at normal directions, plus supported attic roots.
for i,(x,y,h) in enumerate([(0,-24.5,16.1),(-24.6,0,16.1),(24.6,0,16.1),(0,25,16.1)]):width(f'roof_eave_vertical_thickness_{i}',(x,y,h),[0,0,1],1.1)
for i,(x,y,h,d) in enumerate([(0,-16.5,19.45,[0,1,0]),(-18.1,0,18.95,[1,0,0]),(18.1,0,18.95,[1,0,0])]):width(f'roof_ridge_plateau_{i}',(x,y,h),d,.44*S)
# Two rear rolled-roof end caps at high slices retain a finite normal width.
for side in [-1,1]:width(f'rolled_roof_end_{side}',(side*10.7,18, (50.671-B)/S),[1,0,0],2.6)
assert raw==(R/'model.stl').read_bytes()
r=dict(passed=True,checks={v['name']:v['passed'] for v in rows},stl_sha256=hashlib.sha256(raw).hexdigest(),rays=rows,method='Original STL process=False triangle intersections. Sampled normal widths, backing and roots; no exhaustive minimum-thickness, slicing or print claim.')
(R/'recess-root-check.json').write_text(json.dumps(r,indent=2));print('PASS',len(rows),'original STL controls')
