"""Original STL surface-ray controls: no repair, no substituted mesh."""
from pathlib import Path
import numpy as np,trimesh,json,hashlib
R=Path(__file__).resolve().parent;raw=(R/'model.stl').read_bytes();m=trimesh.load(R/'model.stl',process=False);P=.248;S=2.;rows=[]
def T(x,y,h):return np.array([(x-485)*P,(320-y)*P,1.6+h*S])
def hit(o,d):
 q,_,_=m.ray.intersects_location([o],[d],multiple_hits=True);return sorted(set(round(float(np.dot(v-o,d)),6) for v in q if np.dot(v-o,d)>1e-5))
def check(name,p,d,fn,**data):
 o=T(*p);q=hit(o,np.array(d));ok=bool(fn(q));rows.append(dict(name=name,origin_mm=o.tolist(),direction=d,hits_mm=q,passed=ok,**data));assert ok,(name,q,data)
def width(name,p,d,minimum,**data):
 o=T(*p);a=hit(o,np.array(d));b=hit(o,-np.array(d));w=a[0]+b[0] if a and b else 0;ok=bool(a and b and w>=minimum-2e-4);rows.append(dict(name=name,origin_mm=o.tolist(),direction=d,positive_hits_mm=a,negative_hits_mm=b,continuous_width_mm=w,minimum_mm=minimum,passed=ok,**data));assert ok,(name,a,b)
def base(name,x,y):check(name,(x,y,35),[0,0,-1],lambda q:len(q)==2 and abs(q[-1]-71.6)<.0002,continuous_to_base=True)
# All west glass divisions are backed shallow relief, not independent fragile rods.
a=np.array([218.,245.]);b=np.array([235.,325.]);v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v);d=np.array([-n[0],n[1],0.])
for i,t in enumerate(np.linspace(.05,.95,10)):
 p=a+v*t+n*10
 for h in [4.5,8.5,12.5]:check(f'west_glass_frame_{i}_root_{h}',(*p,h),d.tolist(),lambda q:len(q)>=2 and abs(q[0]-10.15*P)<.001 and q[1]-q[0]>1,relief_frame_width_mm=2*P,recess_back_depth_mm=1.2*P)
for h in [3.5,7.25,10.35,13.85]:
 p=a+v*.12+n*10;check(f'west_horizontal_backed_frame_{h}',(*p,h),d.tolist(),lambda q:len(q)>=2 and abs(q[0]-10.15*P)<.001 and q[1]-q[0]>1,frame_height_mm=.3)
p=a+v*.1+n*10
check('west_continuous_shallow_glass_backing',(*p,8.5),d.tolist(),lambda q:q and abs(q[0]-11.2*P)<.001,backing_recess_mm=1.2*P)
# Two retained door divisions plus centre are also rooted in the continuous facade.
for t in [.25,.5,.75]:
 p=a+v*t+n*10;check(f'west_door_root_{t}',(*p,1.5),d.tolist(),lambda q:len(q)>=2 and abs(q[0]-10.15*P)<.001 and q[1]-q[0]>1)
# South B207 opaque wall must be complete and rooted along its whole length.
for x in np.linspace(315,500,8):
 base(f'south_horizontal_wall_base_{x}',float(x),404.5)
 width(f'south_horizontal_wall_width_{x}',(float(x),404.5,3),[0,1,0],5*P)
check('south_wall_horizontal_top',(350,404.5,35),[0,0,-1],lambda q:abs(q[0]-(35-5.4)*2)<.0002)
# Eastern entry is a gap above the landing, rather than a central hole in the main wall.
check('east_stair_access_open',(520,404.5,8),[0,0,-1],lambda q:abs(q[0]-(8-5)*2)<.0002)
# Southern long corridor recess and its continuous canopy are genuine original surfaces.
check('south_corridor_depth',(420,410,7.5),[0,1,0],lambda q:q and abs(q[0]-45*P)<.0002,clear_depth_mm=45*P)
width('south_canopy_minimum_plate',(400,388,8.2),[0,0,1],.9)
# East wing glass frame roots, all on a continuous lower wall.
for y in np.linspace(252,315,7):
 for h in [1,2,3.4]:check(f'east_glass_frame_{y}_{h}',(780,float(y),h),[-1,0,0],lambda q:len(q)>=2 and abs(q[0]-9*P)<.0002 and q[1]-q[0]>2,frame_width_mm=4*P,backing_overlap_mm=2*P)
for x in np.linspace(584,705,10):
 for h in [1,2,3.4]:check(f'low_wing_south_frame_{x}_{h}',(float(x),410,h),[0,1,0],lambda q:len(q)>=2 and abs(q[0]-9*P)<.0002 and q[1]-q[0]>2,frame_width_mm=4*P,backing_overlap_mm=2*P)
# Terrace perimeter, with finite angle junctions; no floating rail strips.
wing=[(548,203),(662,203),(677,231),(770,231),(770,325),(715,347),(735,400),(548,400)]
for i,(a0,b0) in enumerate(zip(wing,wing[1:]+wing[:1])):
 a0=np.array(a0,float);b0=np.array(b0,float);p=(a0+b0)/2;v=b0-a0;v/=np.linalg.norm(v);normal=[-v[1],-v[0],0]
 width(f'terrace_guard_{i}',(*p,5.4),normal,5*P)
# Both external flights have backed treads; footprint taper is retained on the south.
for i in range(25):
 x=397+94*(i+.5)/25;outer=448-(x-397)*34/94;y=(403+outer)/2;base(f'south_stair_tread_{i}',x,y)
for i in range(25):base(f'east_stair_tread_{i}',677+93*(i+.5)/25,224)
# Roof rim and its two equipment/light blocks remain connected to the full hall.
for x,y,direction in [(237.5,280,[1,0,0]),(547.5,280,[1,0,0]),(400,205.5,[0,1,0]),(400,372.5,[0,1,0])]:width(f'main_roof_rim_{x}_{y}',(x,y,14.85),direction,5*P)
for y in [226,351]:base(f'roof_light_root_{y}',313,y)
# Opaque crosses are reliefs fused to walls, never unsupported linework.
check('east_cross_root',(580,291,8.5),[-1,0,0],lambda q:len(q)>=2 and abs(q[0]-8*P)<.0002 and q[1]-q[0]>1)
check('south_cross_root',(530,402,7.5),[1,0,0],lambda q:len(q)>=2 and abs(q[0]-13*P)<.0002 and q[1]-q[0]>1)
base('tall_south_cross_wall_base',547.5,425)
# Tower slit and upper openings are geometric holes/recesses, not painted shapes.
check('tower_west_slit_backing',(190,379,8),[1,0,0],lambda q:q and abs(q[0]-28*P)<.0002)
check('tower_south_upper_opening',(250,420,21),[0,1,0],lambda q:q and q[0]>60*P,minimum_clear_depth_mm=60*P)
width('tower_cross_vertical_plate',(219.5,409,22),[1,0,0],5*P)
width('tower_cross_horizontal_plate',(225,409,24),[0,0,1],1)
# Short bridge is deliberately cut at model boundary; support and low guards rooted.
base('bridge_scope_end_support',295,476)
for x in [282,307]:width(f'bridge_guard_{x}',(x,450,5.5),[1,0,0],4*P)
# Small original slice families at the tower slit ends are still finite wall strips.
a0=np.array([217.,325.]);b0=np.array([208.,359.]);v0=b0-a0;p0=a0+v0*.92;n0=np.array([-v0[1],v0[0]])/np.linalg.norm(v0)
for h in [21.0,24.8]:width(f'tower_west_opening_end_strip_{h}',(*p0,h),[n0[0],-n0[1],0],1.24)
base('tower_west_end_strip_vertical_root',float(p0[0]+.5),float(p0[1]+.1))
check('tower_southwest_cross_back_root',(219.5,409,22),[0,1,0],lambda q:q and q[0]>=9*P,continuous_cross_to_wall_root=True)
assert (R/'model.stl').read_bytes()==raw
report=dict(passed=True,checks={r['name']:r['passed'] for r in rows},stl_sha256=hashlib.sha256(raw).hexdigest(),rays=rows,method='Original STL process=False actual triangle intersections. Sampled roots and widths, not an exhaustive wall-thickness or print certification.')
(R/'recess-root-check.json').write_text(json.dumps(report,indent=2));print('PASS',len(rows),'surface controls')
