"""Actual STL XZ mid-screen section; no repair. Audit every aperture ligament."""
from pathlib import Path
import numpy as np,trimesh,json,math
from shapely.geometry import Polygon,LineString
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',process=False)
y=-(12.1-4.1)*2.8
adj={}
for tri in m.triangles:
 hit=[]
 for a,b in [(tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])]:
  if tuple(a)>tuple(b):a,b=b,a
  if min(a[1],b[1])<y<max(a[1],b[1]):
   p=a+(b-a)*(y-a[1])/(b[1]-a[1]);hit.append(tuple(np.round(p[[0,2]],6)))
 if len(hit)==2 and hit[0]!=hit[1]:
  a,b=hit;adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
assert all(len(v)==2 for v in adj.values())
remaining=set(adj);loops=[]
while remaining:
 seed=next(iter(remaining));a=seed;last=None;loop=[]
 while True:
  loop.append(a);remaining.discard(a);opts=adj[a];b=opts[0] if opts[0]!=last else opts[1];last,a=a,b
  if a==seed:break
 p=Polygon(loop);assert p.is_valid;loops.append(p)
# Diamond holes are small inner loops above the lower screen edge.
holes=[p for p in loops if p.area<2 and p.bounds[1]>10]
assert len(holes)==104, len(holes)
bottom=2.4+(2.68-.001)*2.8
rows=[]
for i,p in enumerate(holes):
 nearest=min(p.distance(q) for j,q in enumerate(holes) if i!=j)
 bottom_margin=p.bounds[1]-bottom
 rows.append({'hole':i,'bounds_xz_mm':p.bounds,'area_mm2':p.area,'nearest_other_hole_ligament_mm':nearest,'above_screen_bottom_mm':bottom_margin})
assert min(r['nearest_other_hole_ligament_mm'] for r in rows)>=1.0
assert min(r['above_screen_bottom_mm'] for r in rows)>=1.0
report={'passed':True,'method':'Canonical actual STL section XZ at screen mid-depth; closed degree-2 loops, individual valid polygons; no repair. Hole-to-hole shortest Euclidean distance including diagonal neighbours. Bottom margin compared with original modeled panel lower edge.','apertures':104,'min_hole_ligament_mm':min(r['nearest_other_hole_ligament_mm'] for r in rows),'min_bottom_margin_mm':min(r['above_screen_bottom_mm'] for r in rows),'screen_depth_mm':1.3216,'checks':{'all_104_apertures_audited':True,'all_ligaments_at_least_1mm':True,'bottom_strip_at_least_1mm':True,'closed_valid_raw_section':True},'holes':rows}
(R/'screen-check.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='holes'})
