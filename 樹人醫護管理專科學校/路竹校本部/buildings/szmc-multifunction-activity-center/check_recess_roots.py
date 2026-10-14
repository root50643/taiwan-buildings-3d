"""Original STL process=False feature rays; no mesh editing or repair."""
from pathlib import Path
import numpy as np,trimesh,json,hashlib
R=Path(__file__).resolve().parent;raw=(R/'model.stl').read_bytes();m=trimesh.load(R/'model.stl',process=False);rows=[];P=1.18/22.9
T=lambda x,y,z:np.array([(x-2000)*P,(1400-y)*P,1.6+z*1.18])
def hits(o,d):
 h,_,_=m.ray.intersects_location([o],[d],multiple_hits=True);return sorted(set(round(float(np.dot(v-o,d)),6) for v in h if np.dot(v-o,d)>1e-6))
def check(name,p,d,fn,**extra):
 o=T(*p);h=hits(o,np.array(d));ok=bool(fn(h));rows.append(dict(name=name,origin_mm=o.tolist(),direction=d,intersections_mm=h,passed=ok,**extra));assert ok,(name,h,extra)
def first_root(name,p,d,expected,minimum,**extra):check(name,p,d,lambda h:len(h)>=2 and abs(h[0]-expected)<2e-4 and h[1]-h[0]>=minimum,expected_first_distance_mm=expected,minimum_continuous_solid_interval_mm=minimum,**extra)
# Every fine curtain-wall frame is backed along its whole vertical extent.
# Three heights per frame test near its bottom, midpoint and near its top.
for i,y in enumerate(np.linspace(1320,1720,11)):
 top=5.1+(y-1300)*4.9/445
 for fraction in [.1,.5,.9]:
  z=4.4+(top-4.4)*fraction
  first_root(f'grass_frame_{i}_{fraction}',(1025,float(y),z),[1,0,0],44*P,1.0,frame_width_mm=16*P,root_overlap_mm=2*P)
for kind,xs,z0,height in [('upper_band',np.linspace(1640,2360,13),6.0,2.2),('lower_band',np.linspace(1320,1870,10),.55,2.1)]:
 for i,x in enumerate(xs):
  for f in [.1,.5,.9]:first_root(f'{kind}_frame_{i}_{f}',(float(x),2130,z0+height*f),[0,1,0],81*P,1.0,frame_width_mm=16*P,root_overlap_mm=2*P)
for i,x in enumerate(np.linspace(2490,3200,15)):
 top=min(8.15,1.9+(3220-x)*6.25/230)
 for f in [.1,.5,.9]:check(f'right_curtain_frame_{i}_{f}',(float(x),1930,.55+(top-.55)*f),[0,-1,0],lambda h:h and h[0]>=49*P-2e-4,minimum_continuous_back_to_frame_tip_mm=49*P,frame_width_mm=16*P,root_overlap_mm=2*P,note='Ray starts inside backing; attached exterior stairs may extend the continuous interval beyond the frame tip.')
first_root('right_curtain_horizontal_frame',(2700,2010,4.5),[0,1,0],31*P,1.0,horizontal_frame_height_mm=.85)
# Positive shallow glazing controls between frames; these are continuous bands.
check('upper_band_clear_glazing',(1670,2130,7.1),[0,1,0],lambda h:abs(h[0]-90*P)<2e-4,expected_recess_back_plane_paper_y=2040)
check('right_curtain_clear_glazing',(2515,2010,6.2),[0,1,0],lambda h:abs(h[0]-40*P)<2e-4,expected_recess_back_plane_paper_y=1970)
# Actual open passage, with back wall far behind the facade rather than a token recess.
check('foyer_open_undercroft',(2140,2130,2.0),[0,1,0],lambda h:abs(h[0]-340*P)<2e-4,clear_open_depth_mm=340*P)
for x in [2010,2280]:
 check(f'foyer_post_{x}_root',(x,1947,30),[0,0,-1],lambda h:len(h)%2==0 and abs(h[-1]-37)<2e-4 and h[-1]-h[-2]>=6.5,post_xy_mm=[28*P,35*P],continuous_from_base_to_mm=6.5)
# Finite folded corner roots, not isolated unsupported small plates.
check('low_roof_corner_fold_thickness',(2360,750,8),[1,0,0],lambda h:len(h)>=2 and abs(h[1]-h[0]-33*P)<2e-4,fold_width_mm=33*P)
check('campus_end_fold_thickness',(3400,1700,10),[-1,0,0],lambda h:len(h)>=2 and abs(h[1]-h[0]-5.2)<2e-4,fold_width_mm=5.2)
check('grass_fold_minimum_backed_plate',(900,750,12),[1,0,0],lambda h:len(h)>=2 and h[1]-h[0]>=5.999,fold_width_mm=6.0)
check('field_fold_minimum_backed_plate',(1500,2130,9.5),[0,1,0],lambda h:len(h)>=2 and h[1]-h[0]>=5.369,fold_width_mm=5.37)
check('pond_fold_minimum_backed_plate',(2500,1450,8),[-1,0,0],lambda h:len(h)>=2 and h[1]-h[0]>=3.829,fold_width_mm=3.83)
check('field_fold_vertical_base_root',(1500,2020,30),[0,0,-1],lambda h:len(h)%2==0 and abs(h[-1]-37)<2e-4 and h[-1]-h[-2]>12,minimum_solid_from_base_mm=12)
# Every roof opening crossbeam has a finite section and overlaps the enclosing roof.
for x in [1790,2180,2570,2960]:
 z=18-3.5*(x-890)/1540
 check(f'roof_opening_crossbeam_{x}',(x,1850,30),[0,0,-1],lambda h:len(h)>=2 and h[1]-h[0]>=1.149,beam_width_mm=26*P,roof_thickness_mm=1.15)
# Open equipment well first hit is the lower wing, while the gym remains roofed.
check('equipment_well_is_open_above_lower_floor',(2000,1850,30),[0,0,-1],lambda h:1.6+30*1.18-h[0]<12.0)
check('gym_roof_not_cut_through',(1700,1300,30),[0,0,-1],lambda h:1.6+30*1.18-h[0]>15.0)
# Both backed external stair flights remain continuous to the base.
for name,a,b,n in [('grass_stair',(990,2170),(1160,1860),14),('campus_stair',(3340,2145),(3070,1990),12)]:
 for i in range(n):
  t=(i+.5)/n;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
  check(f'{name}_tread_{i}',(x,y,30),[0,0,-1],lambda h:len(h)%2==0 and abs(h[-1]-37)<2e-4 and h[-1]-h[-2]>1.8,backed_stair_width_mm=80*P)
assert (R/'model.stl').read_bytes()==raw
j=dict(passed=True,checks={r['name']:r['passed'] for r in rows},stl_sha256=hashlib.sha256(raw).hexdigest(),method='Original saved STL process=False; all 49 vertical frames at three heights, horizontal frame, two structural posts, five folded plate roots, open undercroft/glazing/equipment well, four roof beams and each external stair tread. Sampled surfaces, not universal wall-thickness certification.',rays=rows)
(R/'recess-root-check.json').write_text(json.dumps(j,ensure_ascii=False,indent=2));print('PASS',len(rows),'original mesh rays')
