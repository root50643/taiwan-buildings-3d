"""Read-only rays on original saved STL triangles; no processing or repair."""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
r=Path(__file__).resolve().parent;p=r/'model.stl';raw=p.read_bytes();m=trimesh.load(p,force='mesh',process=False);rows=[]
def T(x,y,z):return np.array([(x+17)*1.5,(y+2)*1.5,z*1.5])
def hits(o,d):
 h,_,_=m.ray.intersects_location([o],[d],multiple_hits=True)
 d=np.array(d,dtype=float);o=np.array(o);a=sorted(set(round(float(np.dot(v-o,d)),5) for v in h if np.dot(v-o,d)>1e-6));return a

def first(name,point,d,expected):
 o=T(*point);a=hits(o,d);assert a,name
 ok=abs(a[0]-expected)<1e-4;rows.append({'name':name,'origin_mm':o.tolist(),'direction':d,'forward_intersections_mm':a,'expected_first_distance_mm':expected,'passed':ok});assert ok,(name,a,expected)
# Positive recessed spaces and control faces, not a generic flat window grid.
first('west_balcony_clear_recess',(-11.5,-80,10.7),(0,1,0),(80-26.6)*1.5)
first('west_central_window_recess',(0,-80,15),(0,1,0),(80-27.9)*1.5)
first('west_top_clerestory_open_bay',(0,-80,25.3),(0,1,0),(80-26.6)*1.5)
first('west_top_dividing_pier',(9.0,-80,25.3),(0,1,0),(80-29)*1.5)
first('north_wing_platform_open_air',(-42,-19,70),(0,0,-1),(70-12.8)*1.5)
first('north_wing_platform_parapet',(-62,-19,70),(0,0,-1),(70-13.6)*1.5)
first('east_upper_terrace_open_air',(6,35,70),(0,0,-1),(70-23)*1.5)
first('roof_metal_cover_backed_rib',(0,2,70),(0,0,-1),(70-32.08)*1.5)
first('west_balcony_rail_is_recessed',(-11.5,-80,9.4),(0,1,0),(80-28.4)*1.5)
first('north_tall_window_recess',(-80,0,18),(1,0,0),(80-21.5)*1.5)
first('north_window_guard_is_recessed',(-80,0,16.8),(1,0,0),(80-22.2)*1.5)
# Backing/root continuity: original ray has only an outer entry and exit, no tiny gap.
for name,point,d in [('entrance_fine_mullion_root',(2,-80,6),(0,1,0)),('metal_cover_rib_vertical_root',(0,2,70),(0,0,-1))]:
 a=hits(T(*point),d);ok=len(a)==2;rows.append({'name':name,'origin_mm':T(*point).tolist(),'direction':d,'forward_intersections_mm':a,'continuous_solid_intersections':2,'passed':ok});assert ok,(name,a)
# All eight pavilion posts connect through solid roof and base, not free floating bars.
for side in [-1,1]:
 for dx in [-2.5,2.5]:
  for dy in [-2.5,2.5]:
   x=side*27+dx;y=-41+dy;a=hits(T(x,y,70),(0,0,-1));ok=len(a)==2 and abs(a[-1]-105)<1e-4
   rows.append({'name':f'pavilion_{side}_{dx}_{dy}_vertical_root','origin_mm':T(x,y,70).tolist(),'direction':[0,0,-1],'forward_intersections_mm':a,'post_section_mm':[2.25,2.25],'passed':ok});assert ok,(x,y,a)
# Finite glass-pyramid peak: verify 1.89mm square plateau, not zero-width apex.
for side in [-1,1]:
 x=side*27;a=hits(T(x,-80,7.59),(0,1,0));near=[v for v in a if 45<v<70]
 width=near[1]-near[0] if len(near)==2 else -1;ok=width>=1.89
 rows.append({'name':f'pavilion_{side}_finite_peak_width','forward_intersections_mm':near,'width_mm':width,'passed':ok});assert ok,(side,a)
# Every thin roof rib and corridor post is checked against the original mesh.
for y in np.linspace(-19.5,23.5,9):
 a=hits(T(0,float(y),70),(0,0,-1));ok=len(a)==2 and abs(a[-1]-105)<1e-4
 rows.append({'name':f'backed_metal_roof_rib_top_{y}_root','origin_mm':T(0,float(y),70).tolist(),'forward_intersections_mm':a,'minimum_rib_xy_width_mm':1.2,'passed':ok});assert ok,(y,a)
a=hits(T(0,-80,32.07),(0,1,0));assert len(a)==18,a
widths=[a[i+1]-a[i] for i in range(0,18,2)];ok=min(widths)>1.1999
rows.append({'name':'all_nine_rib_tips_original_surface_width','origin_mm':T(0,-80,32.07).tolist(),'forward_intersections_mm':a,'rib_widths_mm':widths,'passed':ok});assert ok,widths
for side in [-1,1]:
 for y in [-29,-35,-41]:
  x=side*27;a=hits(T(x,y,70),(0,0,-1));ok=len(a)%2==0 and abs(a[-1]-105)<1e-4 and a[-1]-a[-2]>=8.1
  rows.append({'name':f'attached_corridor_post_{side}_{y}_root','origin_mm':T(x,y,70).tolist(),'forward_intersections_mm':a,'post_width_mm':2.25,'root_continuous_from_base_to_mm':a[-1]-a[-2],'required_root_top_mm':8.1,'note':'Higher low-wing window recesses may occur above the post/beam; the complete post root interval must be solid.','passed':ok});assert ok,(x,y,a)
for x in [-10,10]:
 a=hits(T(x,34,70),(0,0,-1));ok=len(a)==2 and abs(a[-1]-105)<1e-4
 rows.append({'name':f'rear_terrace_finite_roof_cap_{x}_root','origin_mm':T(x,34,70).tolist(),'forward_intersections_mm':a,'peak_rectangle_mm':[3.15,2.7],'passed':ok});assert ok,(x,a)
assert p.read_bytes()==raw
j={'passed':all(q['passed'] for q in rows),'checks':{q['name']:q['passed'] for q in rows},'method':'Original STL process=False, positive ray intersections; no repair; sampled feature/root checks, not exhaustive all-direction wall analysis.','stl_sha256':hashlib.sha256(raw).hexdigest(),'rays':rows}
(r/'recess-root-check.json').write_text(json.dumps(j,ensure_ascii=False,indent=2));print('passed',j['passed'],'rays',len(rows))
