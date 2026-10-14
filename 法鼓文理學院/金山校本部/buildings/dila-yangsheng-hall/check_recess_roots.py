"""Sample original STL surfaces process=False, without editing or repair."""
from pathlib import Path
import numpy as np,trimesh,json,hashlib
R=Path(__file__).resolve().parent;raw=(R/'model.stl').read_bytes();m=trimesh.load(R/'model.stl',process=False);P=.10251;S=1.7;rows=[]
def T(x,y,h):return np.array([(x-550)*P,(850-y)*P,1.6+h*S])
def hit(o,d):
 q,_,_=m.ray.intersects_location([o],[d],multiple_hits=True)
 return sorted(set(round(float(np.dot(v-o,d)),6) for v in q if np.dot(v-o,d)>1e-5))
def check(name,p,d,fn,**data):
 o=T(*p);v=hit(o,np.array(d));ok=bool(fn(v));rows.append(dict(name=name,origin_mm=o.tolist(),direction=d,hits_mm=v,passed=ok,**data));assert ok,(name,v,data)
def width(name,p,d,minimum,**data):
 o=T(*p);a=hit(o,np.array(d));b=hit(o,-np.array(d));ok=bool(a and b and a[0]+b[0]>=minimum-2e-4);rows.append(dict(name=name,origin_mm=o.tolist(),direction=d,positive_hits_mm=a,negative_hits_mm=b,continuous_width_mm=a[0]+b[0] if a and b else None,minimum_mm=minimum,passed=ok,**data));assert ok,(name,a,b)
def base(name,x,y):check(name,(x,y,35),[0,0,-1],lambda h:len(h)==2 and abs(h[-1]-61.1)<.0002,continuous_to_base=True)
# Each of 24 facade frames: sampled root at 3 heights, plus actual width.
for a,b in [(280,380),(402,503),(525,625)]:
 for x in np.linspace(a+15,b-15,4):
  for lo,hi in [(.65,3.5),(4.8,7.8)]:
   for f in [.1,.5,.9]:
    h=4+lo+(hi-lo)*f
    check(f'glazing_root_{x}_{lo}_{f}',(x,1010,h),[0,1,0],lambda q:len(q)>=2 and q[0]<=15*P+.0002 and q[1]-q[0]>1.0,frame_width_mm=8*P,root_overlap_mm=2*P)
   width(f'glazing_width_{x}_{lo}',(x,993,4+(lo+hi)/2),[1,0,0],8*P)
# Every western box, opaque outer face and actual side-return minimum border.
for y in [414,536,658,780,902]:
 for h in [14.3,18.0]:
  width(f'west_box_front_{y}_{h}',(242,y,h),[1,0,0],8*P)
  check(f'west_box_root_{y}_{h}',(245,y,h),[1,0,0],lambda q:q and q[0]>20*P,root_reaches_main_wall_x=270)
 for side in [-1,1]:width(f'west_box_return_{y}_{side}',(243,y+side*25,18),[1,0,0],8*P)
width('south_box_opaque_front',(350,1036,18),[0,1,0],8*P)
for x in [319,388]:width(f'south_box_return_{x}',(x,1000,18),[0,1,0],10*P)
# Corridor structural end piers; rails are rooted into each floor slab.
F=[0,4.1,8.6,13.3,17.9,22.7];B=[395,480,596,718,838,958,1100,1223,1344,1380]
for i,(lo,hi) in enumerate(zip(F[:-1],F[1:])):
 end=1330 if i<3 else 1380
 for a,b in zip(B[:-1],B[1:]):
  b=min(b,end)
  if a>=end or b-a<35:continue
  width(f'corridor_pier_{i}_{a}',(712,a+5,4+(lo+hi)/2),[0,1,0],12*P)
  width(f'corridor_rail_{i}_{a}',(692,(a+b)/2,4+lo+.8),[1,0,0],9*P)
  check(f'corridor_rail_floor_root_{i}_{a}',(692,(a+b)/2,4+lo+.8),[0,0,-1],lambda q:q and q[0]>.5*S,minimum_root_down_mm=.85)
# Common south frame, thin intermediate slab and recessed rails/posts.
width('south_intermediate_slab',(790,1350,21.85),[0,0,1],.55*S)
for floor,r0,r1 in [(13,13.55,14.05),(18.15,18.65,19.15)]:
 width(f'south_rail_height_{floor}',(770,1372,4+(r0+r1)/2),[0,0,1],.5*S)
 width(f'south_rail_depth_{floor}',(770,1372,4+(r0+r1)/2),[0,1,0],9*P)
 width(f'south_post_width_{floor}',(789,1372,4+floor+.25),[1,0,0],10*P)
 check(f'south_post_floor_root_{floor}',(789,1372,4+floor+.25),[0,0,-1],lambda q:q and q[0]>.3*S)
 for x in [751,827]:check(f'south_rail_side_root_{floor}_{x}',(x,1372,4+(r0+r1)/2),[-1,0,0] if x<780 else [1,0,0],lambda q:q and q[0]>3*P)
for h in [19,24.2]:check(f'south_frame_clear_depth_{h}',(770,1400,h),[0,1,0],lambda q:q and abs(q[0]-75*P)<.0002,clear_recess_depth_mm=55*P)
width('south_common_frame_west_partition',(741,1350,19),[1,0,0],13*P)
width('lower_second_level_central_pier',(790,1320,10),[1,0,0],12*P)
# Finite low roof bands, connected continuously to the gym mass.
for y in [360,485,610,735,860]:base(f'roof_band_base_root_{y}',450,y)
# Each rooftop perimeter is >=10px; finite parapet heights are simplified.
for a,b in [(430,590),(610,770),(790,950),(980,1140),(1160,1330)]:
 width(f'office_roof_rim_{a}',(720,(a+b)/2,26.3),[1,0,0],10*P)
for x,y in [(685,1000),(895,1000),(790,395),(790,1380)]:width(f'outer_parapet_{x}_{y}',(x,y,26.5),[1,0,0] if x!=790 else [0,1,0],10*P)
# Backed stair treads and bounded bridge endpoints.
for y0,y1,x,n in [(1520,1348,450,12),(1352,1098,450,24)]:
 for i in range(n):base(f'external_tread_{y0}_{i}',x,y0-(y0-y1)*(i+.5)/n)
for x,y in [(780,190),(997,650)]:base(f'bridge_stub_root_{x}',x,y)
for x,y,d in [(781,250,[1,0,0]),(816,250,[1,0,0]),(950,634,[0,1,0]),(950,671,[0,1,0])]:width(f'bridge_guard_{x}_{y}',(x,y,13.1),d,8*P)
width('north_stair_upper_backing',(790,400,17),[0,1,0],11*P)
# Inter-mass gap stays open above the connecting third-floor platform.
check('inter_mass_clear_above_platform',(665,650,30),[0,0,-1],lambda q:q and abs(q[0]-(30-12.6)*S)<.0002)
# Every additional over-1% family has an original-surface root/width control.
for x,y,h in [(212,1365,2.1),(292,1115,6.3)]:
 width(f'sloped_flank_finite_cap_{x}',(x,y,h),[1,0,0],15*P)
 base(f'sloped_flank_base_{x}',x,y)
width('south_lower_corner_pier',(698,1324,7),[0,1,0],12*P)
width('north_west_roof_corner',(700,400,26.2),[0,1,0],17*P)
assert (R/'model.stl').read_bytes()==raw
j=dict(passed=True,stl_sha256=hashlib.sha256(raw).hexdigest(),checks={q['name']:q['passed'] for q in rows},rays=rows,method='Original STL process=False sampled surface rays. Finite roots/widths and genuine recesses; no repair and no universal thickness or printability guarantee.')
(R/'recess-root-check.json').write_text(json.dumps(j,ensure_ascii=False,indent=2));print('PASS',len(rows),'surface ray controls')
