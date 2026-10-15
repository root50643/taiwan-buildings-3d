from pathlib import Path
import json,numpy as np
from shapely import wkt
from shapely.geometry import Point
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;d=json.loads((R/'layer-component-check.json').read_text());out=[]
for r in d['original_component_checks']:
 if r['opening_loss_fraction']<=.01:continue
 p=wkt.loads(r['original_polygon_wkt']);b=p.bounds;cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2
 if cy>36:family='north_entry_pier' if abs(cx)<15 else 'north_colonnade_pier'
 elif b[1]<-17 and (b[0]>43 or b[2]<-40):family='south_stair_tower'
 elif b[1]<-14:family='south_open_slot_pier'
 else:family='unclassified'
 corners=[]
 for ring in [p.exterior,*p.interiors]:
  co=np.array(ring.coords)[:-1];n=len(co)
  # Find genuine direction changes, skipping only consecutive collinear sample vertices.
  for i in range(n):
   a=co[i]-co[i-1];bb=co[(i+1)%n]-co[i];la=np.linalg.norm(a);lb=np.linalg.norm(bb)
   if la<1e-8 or lb<1e-8:continue
   angle=np.arccos(np.clip(a@bb/(la*lb),-1,1))
   if angle>np.deg2rad(10):corners.append(co[i].tolist())
 zones=unary_union([Point(v).buffer(.41)for v in corners]);loss=p.difference(p.buffer(-.4).buffer(.4));outside=loss.difference(zones)
 out.append({**r,'family':family,'true_corner_points_mm':corners,'true_corner_radius_mm':.41,'loss_outside_true_corner_mm2':outside.area,'loss_outside_true_corner_fraction':outside.area/p.area,'loss_outside_true_corner_wkt':outside.wkt})
groups={}
for name in sorted({r['family']for r in out}):
 rs=[r for r in out if r['family']==name];groups[name]={'samples':len(rs),'distinct_plan_bounds':len({tuple(r['bounds_xy_mm'])for r in rs}),'maximum_component_loss':max(r['opening_loss_fraction']for r in rs),'maximum_outside_true_corner_mm2':max(r['loss_outside_true_corner_mm2']for r in rs),'z_range':[min(r['z_mm']for r in rs),max(r['z_mm']for r in rs)]}
report={'stl_sha256':d['stl_sha256'],'reference_width_mm':.8,'warning_samples':len(out),'families':groups,'method':'Original Polygon and original opening retained. Corners are >10 degree direction changes in original ring; 0.41mm disks, never replace original polygon by rectangle. Tiny numerical remnants are recorded nonzero. Counts are section samples, not physical component counts.','exception_approved':False,'samples':out};(R/'component-loss-evidence.json').write_text(json.dumps(report,indent=2));print(groups)
