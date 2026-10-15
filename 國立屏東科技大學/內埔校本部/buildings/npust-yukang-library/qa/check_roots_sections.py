from pathlib import Path
import json,hashlib,numpy as np,trimesh
from shapely.geometry import Polygon,box
R=Path(__file__).parent;M=R.parent;m=trimesh.load(M/'model.stl',process=False);T=m.triangles
cache={}
def section(z):
 if z in cache:return cache[z]
 adj={}
 for f in T[(T[:,:,2].min(axis=1)<z)&(T[:,:,2].max(axis=1)>z)]:
  h=[]
  for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
   if tuple(a)>tuple(b):a,b=b,a
   if (a[2]-z)*(b[2]-z)<0:h.append(tuple((a+(b-a)*(z-a[2])/(b[2]-a[2]))[:2]))
  assert len(h)==2
  a,b=h;adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
 assert all(len(v)==2 for v in adj.values())
 seen=set();shape=Polygon()
 for a in adj:
  if a in seen:continue
  start=a;prev=None;ring=[]
  while a not in seen:
   seen.add(a);ring.append(a);nxt=adj[a][0] if adj[a][0]!=prev else adj[a][1];prev,a=a,nxt
  assert a==start
  g=Polygon(ring);assert g.is_valid;shape=shape.symmetric_difference(g)
 assert shape.is_valid;cache[z]=shape;return shape

def pair(name,mask,upper,lower):
 a=section(upper).intersection(mask);b=section(lower).intersection(mask);c=a.intersection(b);assert a.is_valid and b.is_valid and a.area>0
 return {'name':name,'upper_z_mm':upper,'lower_z_mm':lower,'section_separation_mm':abs(upper-lower),'mask_wkt':mask.wkt,'upper_original_clipped_wkt':a.wkt,'lower_original_clipped_wkt':b.wkt,'upper_area_mm2':a.area,'intersection_area_mm2':c.area,'overlap_fraction':c.area/a.area,'direction':'downward'if upper>lower else 'upward'}
rows=[]
# 24 wing free poles and8 central free poles;4 central endpoints fuse into large piers.
for xc in [-36,36]:
 for x in np.linspace(xc-15,xc+15,6):
  for y in [-23.9,23.9]:
   xx=x*1.2;yy=y*1.2;mask=box(xx-.69001,yy-.69001,xx+.69001,yy+.69001)
   rows.append(pair(f'wing_column_{x}_{y}_base',mask,4.671,4.471));rows.append(pair(f'wing_column_{x}_{y}_head',mask,20.471,20.671))
for x in [-8.4,-2.8,2.8,8.4]:
 for y in [-24.1,24.1]:
  xx=x*1.2;yy=y*1.2;mask=box(xx-.69001,yy-.69001,xx+.69001,yy+.69001)
  rows.append(pair(f'central_column_{x}_{y}_base',mask,4.671,4.471));rows.append(pair(f'central_column_{x}_{y}_head',mask,20.771,20.821))
# Entire north steel assembly upper/lower faces; masks exclude adjacent end piers when possible.
rows.append(pair('north_frame_base_whole',box(-70.44001,-29.46001,-69.11999,29.46001),4.671,4.471))
rows.append(pair('north_frame_top_to_roof_partial',box(-70.44001,-29.46001,-69.11999,29.46001),20.471,20.671))
rows.append(pair('central_roof_to_body_and_porch_columns',box(-16.8,-30,16.8,30),20.371,20.071))
rows.append(pair('PV_north_cap_to_roof',box(-66.9,-27, -19.5,27),28.671,28.471))
rows.append(pair('PV_south_cap_to_roof',box(19.5,-27,66.9,27),28.671,28.471))
(R/'root-sections-original.json').write_text(json.dumps({'stl_sha256':hashlib.sha256((M/'model.stl').read_bytes()).hexdigest(),'method':'Exact canonical-edge original STL sections, every loop and composed Polygon validity asserted; local feature masks only select regions, no repair. Overlap is geometric support evidence, not slicer/support-free approval.','actual_free_columns':32,'parametric_central_endpoint_posts_fused_into_main_piers':4,'rows':rows},indent=2))
print([(r['name'],r['overlap_fraction'])for r in rows[-5:]]);print('column min',min(r['overlap_fraction']for r in rows[:-5]))
