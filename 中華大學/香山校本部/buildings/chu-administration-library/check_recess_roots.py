"""Original STL only: local roots, through apertures, backed relief, finite crowns.
No rebuilding, repair, processing, or global minimum/printability certification.
Coordinates in authored metres are controls only; all measurements use STL facets.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
R=Path(__file__).resolve().parent
raw=(R/'model.stl').read_bytes();m=trimesh.load(R/'model.stl',process=False)
S=1.75;B=1.6;rows=[]
def T(x,y,z):return np.array([x*S,y*S,B+z*S],float)
def unit(d):d=np.array(d,float);return d/np.linalg.norm(d)
def raw_hits(o,d):
 d=unit(d);loc,_,ids=m.ray.intersects_location([o],[d],multiple_hits=True)
 return sorted([(float(np.dot(p-o,d)),int(i),p)for p,i in zip(loc,ids)if np.dot(p-o,d)>1e-6],key=lambda q:q[0])
def hits(o,d):
 q=raw_hits(o,d)
 # Coincident triangle-edge intersections represent one crossing, not a skin.
 out=[]
 for v in q:
  if not out or abs(v[0]-out[-1][0])>1e-7:out.append(v)
 return out
def ds(o,d):return [round(q[0],7)for q in hits(o,d)]
def inside(o):return bool(len(ds(o,[.173,.329,1]))%2)
def rec(name,ok,**kw):rows.append(dict(name=name,passed=bool(ok),**kw))
def root(name,o,d,minimum):
 d=unit(d);q=ds(o,d);r=ds(o,-d)
 rec(name,len(q)%2 and len(r)%2 and q[0]>=minimum-.0003,origin_mm=o.tolist(),direction=d.tolist(),hits_mm=q,reverse_hits_mm=r,minimum_continuous_root_mm=minimum)
def width(name,o,d,minimum):
 d=unit(d);q=ds(o,d);r=ds(o,-d);w=q[0]+r[0]if q and r else 0
 rec(name,len(q)%2 and len(r)%2 and w>=minimum-.0003,origin_mm=o.tolist(),direction=d.tolist(),positive_hits_mm=q,negative_hits_mm=r,continuous_width_mm=w,minimum_mm=minimum)
def clear(name,o,d,length):
 q=ds(o,d);rec(name,len(q)%2==0 and (not q or q[0]>=length-.0003),origin_mm=o.tolist(),direction=unit(d).tolist(),hits_mm=q,minimum_clear_mm=length)
def normal(name,o,d,minimum=.8):
 d=unit(d);q=hits(o,d)
 if not q:rec(name,False,error='No original surface');return
 t,f,p=q[0];tri=m.triangles[f];n=unit(np.cross(tri[1]-tri[0],tri[2]-tri[0]));start=p+n*.001;a=hits(start,-n);dist=[v[0]for v in a];w=dist[1]-dist[0]if len(a)>=2 else 0
 pts=[start-n*(dist[0]-.0001),start-n*((dist[0]+dist[1])/2),start-n*(dist[1]+.0001)]if len(a)>=2 else []
 states=[inside(v)for v in pts]
 rec(name,len(a)>=2 and abs(dist[0]-.001)<.0003 and w>=minimum-.0003 and states==[False,True,False],raw_probe_hits=[dict(distance_mm=v[0],triangle_id=v[1],point_mm=v[2].tolist())for v in raw_hits(o,d)],raw_normal_hits=[dict(distance_mm=v[0],triangle_id=v[1],point_mm=v[2].tolist())for v in raw_hits(start,-n)],probe_origin_mm=o.tolist(),probe_direction=d.tolist(),original_triangle_id=f,original_triangle=tri.tolist(),surface_mm=p.tolist(),original_outward_normal=n.tolist(),normal_origin_mm=start.tolist(),normal_hits_mm=dist,first_solid_mm=w,minimum_mm=minimum,control_points_mm=[v.tolist()for v in pts],before_mid_after_inside=states,first_exit_mm=a[1][2].tolist()if len(a)>=2 else None)
def rotate(p,angle):
 a=np.deg2rad(angle);p=np.array(p,float);return np.array([p[0]*np.cos(a)-p[1]*np.sin(a),p[0]*np.sin(a)+p[1]*np.cos(a),p[2]])
def RT(x,y,z,a):p=rotate([x,y,z],a);return T(*p)
# Each ear: aperture above 30.8-m screens, both legs into screens, annulus.
for a,y in [(0,-16.2),(180,-16.2),(90,-29.7),(270,-29.7)]:
 for z in [31.3,31.65,32.0]:clear(f'ear_{a}_through_{z}',RT(0,y-1,z,a),rotate([0,1,0],a),2*S)
 for x in [-2.75,2.75]:
  width(f'ear_{a}_leg_{x}_depth',RT(x,y,31.2,a),rotate([0,1,0],a),1.1*S)
  width(f'ear_{a}_leg_{x}_breadth',RT(x,y,30.9,a),rotate([1,0,0],a),1.20*S)
  root(f'ear_{a}_leg_{x}_screen_root',RT(x,y,31.2,a),[0,0,-1],.6*S)
 for t in [.25,.65,np.pi/2,2.5,2.9]:
  normal(f'ear_{a}_outer_arc_{t}',RT(4*np.cos(t),y,31+4*np.sin(t),a),rotate([-np.cos(t),0,-np.sin(t)],a),1.1*S)
  normal(f'ear_{a}_inner_arc_{t}',RT(1.8*np.cos(t),y,31+1.8*np.sin(t),a),rotate([np.cos(t),0,np.sin(t)],a),1.1*S)
 normal(f'ear_{a}_ring_front',RT(0,y-2,33.7,a),rotate([0,1,0],a),1.1*S)
# Barrel crown original normals, solid interior and support below shallow arch.
for x in [-20,0,20]:
 for t in [.18,.5,1.,1.57,2.15,2.7,2.96]:
  normal(f'barrel_normal_x{x}_t{t}',T(x,5*np.cos(t),28.2+4*np.sin(t)),[0,-np.cos(t),-np.sin(t)])
 root(f'barrel_root_x{x}',T(x,0,29),[0,0,-1],1.2*S)
 width(f'barrel_near_top_x{x}',T(x,0,31.05),[0,1,0],1.0)
# Dome y=0 is an original shared-triangle seam; deliberately offset controls
# avoid exact edge ambiguity, without moving geometry or thickness thresholds.
# Both half-domes: surface-normal first chords, cap width and direct rear roots.
for side in [-1,1]:
 for h in [24.2,25,26,27,28,28.6]:
  for t in [-1.3,-.7,.013,.7,1.3]:
   f=np.sqrt(1-((h-24)/5)**2)
   normal(f'dome_{side}_z{h}_t{t}',T(side*(29.8+(6.5*f+.25)*np.cos(t)),(8*f+.25)*np.sin(t),h),[-side*np.cos(t),-np.sin(t),0])
 for yy in [-1,.037,1]:
  normal(f'dome_{side}_finite_top_y{yy}',T(side*30.8,yy,30),[0,0,-1])
  root(f'dome_{side}_rear_root_y{yy}',T(side*30.2,yy,27.5),[-side,0,0],1*S)
 root(f'dome_{side}_base_root',T(side*34,.037,24.2),[0,0,-1],1*S)
 width(f'dome_{side}_truncated_top',T(side*30.5,.037,28.69),[0,1,0],3*S)
 # 3F/4F/5-6F solid curved backing and EACH bowed mullion, three heights.
 for rx,ry,lo,hi in [(4.7,7.8,8.1,11.45),(6.5,9,11.6,15.7),(8.7,10.3,15.8,24)]:
  levels=[(lo+.65,hi-.55)]if hi-lo<5 else [(16.5,19.55),(20.35,23.45)]
  for aa,bb in levels:
   for i,t in enumerate(np.linspace(-np.pi/2+.12,np.pi/2-.12,13)):
    for h in [aa+.05,(aa+bb)/2,bb-.05]:
     o=T(side*(30+(rx-.15)*np.cos(t)),(ry-.15)*np.sin(t),h)
     root(f'bow_{side}_{lo}_{aa}_mullion{i}_z{h}_back',o,[-side*np.cos(t),-np.sin(t),0],.30*S)
   for t in [-1.35,-.9,-.4,.2,.7,1.25]:
    normal(f'bow_{side}_{lo}_{aa}_back_normal_{t}',T(side*(30+(rx+1)*np.cos(t)),(ry+1)*np.sin(t),(aa+bb)/2),[-side*np.cos(t),-np.sin(t),0],1.)
  for h in [lo+.4,(lo+hi)/2,hi-.1]:root(f'bow_{side}_{lo}_rear_wall_z{h}',T(side*30.1,0,h),[-side,0,0],1*S)
 # Single column enters 4F underside, while 3F projection stops short of column.
 for h in [1,6,11.4]:
  for d in [[1,0,0],[0,1,0]]:width(f'column_{side}_z{h}_{d}',T(side*36.1,0,h),d,1.40*S)
 root(f'column_{side}_bottom_root',T(side*36.1,0,1),[0,0,-1],B+S)
 root(f'column_{side}_top_into_4F',T(side*36.1,0,11.4),[0,0,1],.65*S)
 root(f'4F_plate_{side}_onto_column',T(side*36.1,0,11.7),[0,0,-1],2*S)
 clear(f'3F_column_{side}_gap',T(side*35.05,0,10),[side,0,0],.30*S)
# New terrace parapet: EACH of 48 original straight arc facets, both faces,
# continuous downward roots and inner clear terrace ending at the inset crown.
for side in [-1,1]:
 for i,t in enumerate((np.linspace(-np.pi/2,np.pi/2,49)[:-1]+np.linspace(-np.pi/2,np.pi/2,49)[1:])/2):
  d=np.array([side*np.cos(t),np.sin(t),0]);o=T(side*(30+8.52*np.cos(t)),10.12*np.sin(t),24.35)
  for sign in [-1,1]:normal(f'terrace_{side}_segment{i}_face{sign}',o+d*1.2*sign,-d*sign,1.35)
  root(f'terrace_{side}_segment{i}_base_root',T(side*(30+8.4*np.cos(t)),10*np.sin(t),24.35),[0,0,-1],.7*S)
 for t in [-1.25,-.75,.013,.75,1.25]:
  # Centre of terrace floor, between crown and inner parapet, rests on main bow.
  o=T(side*(30+7.4*np.cos(t)),8.9*np.sin(t),23.95)
  root(f'terrace_{side}_floor_t{t}_backed',o,[0,0,-1],1*S)
  clear(f'terrace_{side}_open_air_t{t}',T(side*(30+7.4*np.cos(t)),8.9*np.sin(t),24.4),[0,0,1],3*S)
# Every central arch vertical and horizontal frame backed into the main wall.
for face in [-1,1]:
 for x in [-9,-6,-3,0,3,6,9]:
  top=10.6+np.sqrt(11.08**2-x*x)
  for h in [4.4,(4.2+top)/2,top-.25]:root(f'glass_{face}_vertical_x{x}_z{h}_back',T(x,face*16.9,h),[0,-face,0],.4*S)
 for h in [7.9,11.9,15.9,19.9]:
  extent=11.08 if h<=10.6 else np.sqrt(11.08**2-(h+.11-10.6)**2)
  for x in [-extent*.90,0,extent*.90]:root(f'glass_{face}_horizontal_{h}_x{x}_back',T(x,face*16.9,h+.11),[0,-face,0],.4*S)
for lo,hi in [(1.1,3.5),(4.5,7.35)]:
 for x in np.linspace(-10.8,10.8,9):
  if lo<2 and abs(x)<2.5:continue
  for h in [lo+.06,(lo+hi)/2,hi-.06]:root(f'entry_vertical_{lo}_x{x}_z{h}_back',T(x,-22.72,h),[0,1,0],.30*S)
root('entry_recess_back',T(0,-21.7,2),[0,1,0],1*S)
# Revised south six/three-pane groups and upper central grouped windows;
# every authored thin mullion receives three depth-root controls.
for lo,hi,groups in [(24.3,27.65,[(-29,-20.8),(-19.2,-14.7),(-9.3,-3.7),(-2.9,2.9),(3.7,9.3),(14.7,19.2),(20.8,29)]),(20.5,23.6,[(-29,-20.8),(-19.2,-14.7),(14.7,19.2),(20.8,29)]),(18.3,19.5,[(-29,-20.8),(-19.2,-14.7),(14.7,19.2),(20.8,29)]),(13.5,15.5,[(-29,-20.8),(-19.2,-14.7),(14.7,19.2),(20.8,29)]),(9.2,11.5,[(-29,-20.8),(-19.2,-14.7),(14.7,19.2),(20.8,29)]),(4.7,7.4,[(-29,-20.8),(-19.2,-14.7),(14.7,19.2),(20.8,29)])]:
 for xa,xb in groups:
  count=6 if abs(xa)>20 or abs(xb)>20 else 3 if min(abs(xa),abs(xb))>12 else 5
  for x in np.linspace(xa,xb,count+1)[1:-1]:
   for h in [lo+.05,(lo+hi)/2,hi-.05]:root(f'south_group_{lo}_{xa}_{xb}_x{x}_z{h}_back',T(x,-16.94,h),[0,1,0],.4*S)
  if hi-lo>2.5:
   for x in [xa+.1,(xa+xb)/2,xb-.1]:root(f'south_transom_{lo}_{xa}_x{x}_back',T(x,-16.94,hi-.82),[0,1,0],.4*S)
 if lo>=9:
  for x in [-25.2,-16.3,16.3,25.2]:clear(f'north_plain_recess_{lo}_x{x}',T(x,17.04,(lo+hi)/2),[0,1,0],.5*S)
for side in [-1,1]:
 for lo,hi in [(1.3,2.5),(4.7,7.4)]:
  for yy in np.linspace(-10,10,11):
   for h in [lo+.05,(lo+hi)/2,hi-.05]:root(f'side_short_frame_{side}_{lo}_y{yy}_z{h}',T(side*29.75,yy,h),[-side,0,0],.3*S)
# 0.7-m finite red strip crest across both long sides and original slope normals.
for side in [-1,1]:
 for x in [-25,-10,10,25]:
  width(f'red_{side}_crest_x{x}',T(x,side*13.45,30.79),[0,1,0],.7*S)
  normal(f'red_{side}_crest_top_normal_x{x}',T(x,side*13.45,32),[0,0,-1],1*S)
  for y in [14.2,15.2,16.2]:normal(f'red_{side}_slope_x{x}_y{y}',T(x,side*y,32),[0,0,-1],1*S)
# Same dome seam locations tested to BOTH sides, retaining unclustered hits.
for side in [-1,1]:
 for h in [24.2,27.5,28,28.6,28.69]:
  for yy in [-.0001,.0001]:normal(f'dome_seam_offset_{side}_{h}_{yy}',T(side*37.0,yy,h),[-side,0,0])
# Current raw rectangular section arithmetic flags: consume actual public source,
# never a stale six-component whitelist. Bounds select probes only, not geometry.
from shapely import wkt
rectangle_raw=(R/'rectangle-boundary-diagnostics.json').read_bytes()
rectangle_source=json.loads(rectangle_raw);rectangles=[]
for item in rectangle_source:
 shape=wkt.loads(item['original_polygon_wkt']);assert shape.is_valid
 x0,y0,x1,y1=shape.bounds
 rectangles.append((item['z_mm'],item['original_component_index'],(x0+x1)/2,(y0+y1)/2))
for z,i,x,y in rectangles:
 o=np.array([x,y,z]);name=f'original_rectangle_z{z}_component{i}'
 for axis in [[1,0,0],[0,1,0]]:
  width(name+f'_XY_{axis}',o,axis,1.924999)
  for sign in [-1,1]:
   d=unit(axis)*sign;normal(name+f'_face_{axis}_{sign}',o+d*3,-d,1.924999)
 root(name+'_down_into_original_screen_or_roof',o,[0,0,-1],2.)
from shapely.geometry import Polygon
def raw_section(zheight):
 tri=m.triangles;segs=[];ids=np.where((tri[:,:,2].min(axis=1)<zheight)&(tri[:,:,2].max(axis=1)>zheight))[0]
 for fid in ids:
  f=tri[fid];pts=[]
  for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
   if tuple(a)>tuple(b):a,b=b,a
   if a[2]<zheight<b[2] or b[2]<zheight<a[2]:pts.append(a+(b-a)*(zheight-a[2])/(b[2]-a[2]))
  if len(pts)==2:segs.append(pts)
 adj={}
 for seg in segs:
  a,b=[tuple(np.round(q[:2],6))for q in seg]
  if a==b:continue
  adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
 assert adj and all(len(v)==2 for v in adj.values()),('nonclosed raw section',zheight)
 remaining=set(adj);shape=Polygon()
 while remaining:
  seed=next(iter(remaining));a=seed;last=None;loop=[]
  while True:
   loop.append(a);remaining.discard(a);opts=adj[a];b=opts[0] if opts[0]!=last else opts[1];last,a=a,b
   if a==seed:break
   assert len(loop)<=len(adj)
  p=Polygon(loop);assert p.is_valid
  if p.area>1e-8:shape=shape.symmetric_difference(p)
 assert shape.is_valid
 return shape,ids.tolist()
def polys(p):return []if p.is_empty else [p]if p.geom_type=='Polygon'else list(p.geoms)

from shapely.geometry import box as roi_box
section_checks=[]
for label,zu,zl in [('crown_and_parapet_base',43.8,43.4),('parapet_middle',44.5,44.1),('parapet_embed_bottom',43.3625,42.9625)]:
 upper,ui=raw_section(zu);lower,li=raw_section(zl);overlap=upper.intersection(lower)
 item=dict(name=label,upper_z_mm=zu,lower_z_mm=zl,central_z_mm=(zu+zl)/2,upper_lower_offsets_mm=.2,upper_original_triangle_ids=ui,lower_original_triangle_ids=li,upper_original_polygon_wkt=upper.wkt,lower_original_polygon_wkt=lower.wkt,intersection_original_polygon_wkt=overlap.wkt,upper_components=len(polys(upper)),lower_components=len(polys(lower)),intersection_components=len(polys(overlap)),local_sides=[])
 for side in [-1,1]:
  roi=roi_box(30.3*S,-20*S,41*S,20*S)if side>0 else roi_box(-41*S,-20*S,-30.3*S,20*S)
  u=upper.intersection(roi);l=lower.intersection(roi)
  if label=='parapet_embed_bottom':
   # Actual higher raw section identifies crown and ring footprints independently.
   mask,maskids=raw_section(43.8);u=u.intersection(mask);item['original_exposed_mask_z_mm']=43.8;item['original_exposed_mask_wkt']=mask.wkt;item['original_exposed_mask_triangle_ids']=maskids
  inter=u.intersection(l);components=[]
  for j,piece in enumerate(polys(u)):
   support=piece.intersection(l);eroded=support.buffer(-.4)
   components.append(dict(component=j,upper_area_mm2=piece.area,upper_original_clipped_wkt=piece.wkt,support_area_mm2=support.area,support_fraction=support.area/piece.area,support_intersection_wkt=support.wkt,support_components=len(polys(support)),support_eroded_0_4mm_components=len(polys(eroded)),support_eroded_area_mm2=eroded.area,passed=len(polys(support))==1 and len(polys(eroded))==1 and eroded.area>0))
  ok=len(components)==2 and all(c['passed']for c in components)
  rec(f'original_sections_{label}_side{side}_crown_and_ring_support',ok,upper_z_mm=zu,lower_z_mm=zl,local_upper_components=len(components),local_upper_components_details=components)
  item['local_sides'].append(dict(side=side,roi_bounds_mm=list(roi.bounds),upper_components=len(polys(u)),lower_components=len(polys(l)),intersection_components=len(polys(inter)),components=components,passed=ok))
 section_checks.append(item)
assert raw==(R/'model.stl').read_bytes(),'STL changed during check'
r=dict(passed=all(v['passed']for v in rows),stl_sha256=hashlib.sha256(raw).hexdigest(),original_triangle_count=len(m.faces),checks_count=len(rows),failed_count=sum(not v['passed']for v in rows),method='Original STL loaded process=False; triangle rays, original triangle normals, first solid interval and outside/inside/outside controls. No repaired geometry or idealized mesh substitution. Authored coordinates define probes only. Rays are local sampled controls, not exhaustive minimum thickness or printability certification.',rays=rows)
r['original_section_support']=section_checks
r['rectangle_diagnostic_source']=dict(filename='rectangle-boundary-diagnostics.json',sha256=hashlib.sha256(rectangle_raw).hexdigest(),components=len(rectangle_source),probes_per_component=7,all_original_controls=[dict(z_mm=z,component_index=i,center_xy_mm=[x,y])for z,i,x,y in rectangles])
r['section_method']='Original STL triangle-plane canonical edge interpolation; six-decimal endpoint graph must close at degree two, every original Polygon must be valid. No simplify, buffer(0), repair, or ideal-shape replacement. Two original levels at central z +/-0.2 mm are intersected. Side ROI x beyond +/-30.3m separates crown and parapet; each actual support must retain one nonempty 0.4mm erosion core. Erosion is diagnostic only, never replacement geometry.'
r['normal_minimum_first_solid_mm']=min(v['first_solid_mm']for v in rows if 'first_solid_mm'in v)
r['normal_group_minima_mm']={group:min(v['first_solid_mm']for v in rows if v['name'].startswith(group) and 'first_solid_mm'in v)for group in ['ear_', 'barrel_', 'dome_', 'bow_', 'red_', 'terrace_']}
r['first_gap_assessment']={
 'terrace_first_solid_minimum_mm':min(v['first_solid_mm']for v in rows if v['name'].startswith('terrace_')and 'first_solid_mm'in v),
 'classification':'Parapet first exit is its opposite original arc face at the same height; the following void is the intentionally open terrace between parapet and inset crown. Both inward/outward normal probes verify outside/inside/outside parity, and independent upward terrace probes verify opening to sky. Not a hidden cavity under a thin surface.',
 'first_gap_after_minimum_normal_mm':(lambda v:v['normal_hits_mm'][2]-v['normal_hits_mm'][1])(min([v for v in rows if v['name'].startswith('terrace_')and 'first_solid_mm'in v],key=lambda v:v['first_solid_mm']))}
r['numerical_controls']='Coincident triangle-edge hit distances within 1e-7 mm are one crossing. Dome normals avoid the y=0 shared-facet seam using predeclared theta .013 and root y .037 m. Thickness thresholds are unchanged. This de-duplicates intersections only; the original STL is never modified.'
(R/'recess-root-check.json').write_text(json.dumps(r,indent=2,ensure_ascii=False))
print('PASS'if r['passed']else'FAIL',r['checks_count'],'checks',r['failed_count'],'failures','minimum normal',r['normal_minimum_first_solid_mm'])
for v in rows:
 if not v['passed']:print(json.dumps(v,ensure_ascii=False))
raise SystemExit(not r['passed'])
