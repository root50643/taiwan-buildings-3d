"""Supplementary actual-STL roof-frame section audit; no repairs, no geometry changes.
Each disconnected XY component at 70.071..73.071 mm is audited separately.
MRR short side is a component envelope width, NOT a whole-model minimum wall thickness.
The construction widths 1.55/1.60 mm refer to the standalone roof-frame posts.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',force='mesh',process=True)
def section(z):
 adj={}
 for f in m.triangles[(m.triangles[:,:,2].min(axis=1)<z)&(m.triangles[:,:,2].max(axis=1)>z)]:
  hits=[]
  for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
   if tuple(a)>tuple(b):a,b=b,a
   if a[2]<z<b[2] or b[2]<z<a[2]:hits.append(tuple((a+(b-a)*(z-a[2])/(b[2]-a[2]))[:2]))
  if len(hits)==2 and hits[0]!=hits[1]:
   a,b=hits;adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
 assert adj and all(len(q)==2 for q in adj.values())
 remain=set(adj);shape=Polygon()
 while remain:
  seed=next(iter(remain));a=seed;prev=None;loop=[]
  while True:
   loop.append(a);remain.discard(a);q=adj[a];b=q[0] if q[0]!=prev else q[1];prev,a=a,b
   if a==seed:break
   assert len(loop)<=len(adj)
  p=Polygon(loop);assert p.is_valid
  shape=shape.symmetric_difference(p)
 assert shape.is_valid
 return shape
rows=[]
for z in [70.071,71.071,72.071,73.071]:
 shape=section(z);components=list(shape.geoms) if hasattr(shape,'geoms') else [shape]
 components.sort(key=lambda p:(p.centroid.x,p.centroid.y));items=[]
 for i,p in enumerate(components,1):
  eroded=p.buffer(-.4);opened=eroded.buffer(.4)
  assert eroded.is_valid and opened.is_valid
  retained=p.intersection(opened);assert retained.is_valid
  q=np.array(p.minimum_rotated_rectangle.exterior.coords);sides=np.linalg.norm(q[1:]-q[:-1],axis=1)
  short=float(sides.min());long=float(sides.max())
  coords=np.array(p.exterior.coords[:-1]);corners=[]
  for j,v in enumerate(coords):
   a=v-coords[j-1];b=coords[(j+1)%len(coords)]-v
   if abs(a[0]*b[1]-a[1]*b[0])>1e-8:corners.append(tuple(v))
  near_corners=unary_union([Point(c).buffer(.41) for c in corners])
  outside_corner_loss=p.difference(opened).difference(near_corners).area
  items.append({'component':i,'corner_count':len(corners),'lost_area_outside_0_41mm_corner_neighbourhood_mm2':outside_corner_loss,'area_mm2':p.area,'bounds_mm':list(p.bounds),'mrr_short_side_mm':short,'mrr_long_side_mm':long,'is_rectangular_envelope':abs(p.area-short*long)<1e-5,'erosion_nonempty':not eroded.is_empty,'opened_nonempty':not opened.is_empty,'opened_components':len(opened.geoms) if hasattr(opened,'geoms') else (0 if opened.is_empty else 1),'area_retained_fraction':retained.area/p.area,'whole_component_disappeared':opened.is_empty,'outline_xy':[list(q) for q in p.exterior.coords],'opened_outline_xy':[[list(q) for q in g.exterior.coords] for g in (list(opened.geoms) if hasattr(opened,'geoms') else [opened])]})
 rows.append({'z_mm':z,'component_count':len(items),'minimum_component_mrr_short_side_mm':min(x['mrr_short_side_mm'] for x in items),'minimum_retained_area_fraction':min(x['area_retained_fraction'] for x in items),'whole_components_disappeared':sum(x['whole_component_disappeared'] for x in items),'items':items})
checks={'all_original_sections_valid':True,'all_opening_loss_within_original_corner_neighbourhoods':all(x['lost_area_outside_0_41mm_corner_neighbourhood_mm2']<1e-6 for r in rows for x in r['items']),'all_components_survive_0_8mm_opening':all(not x['whole_component_disappeared'] for r in rows for x in r['items']),'no_component_splits_after_opening':all(x['opened_components']==1 for r in rows for x in r['items']),'every_component_envelope_at_least_1_5mm':all(x['mrr_short_side_mm']>=1.5-1e-5 for r in rows for x in r['items'])}
report={'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'method':'Original STL, canonical shared-edge section interpolation; each input loop and composite asserted valid. Each component individually eroded/dilated radius0.4mm without repairs. MRR width is envelope only.','construction_cross_sections_mm':{'standalone_wing_roof_posts':[1.6,1.55],'standalone_core_roof_posts':[1.55,1.7],'end_frame_wall_width':1.6},'interpretation':'All section components remain. Corner rounding removes some area from rectangular posts and joined end-frame corners. The narrowest standalone roof-post design side is1.55mm; this does not certify every local corner, every model wall or nozzle toolpath. Supports/bridge checks and a physical print remain necessary.','sections':rows}
(R/'roof-component-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='sections'},ensure_ascii=False,indent=2));print([(r['z_mm'],r['component_count'],r['minimum_component_mrr_short_side_mm'],r['minimum_retained_area_fraction']) for r in rows]);raise SystemExit(0 if report['passed'] else 1)
