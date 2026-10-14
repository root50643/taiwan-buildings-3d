from pathlib import Path
import json,numpy as np
from shapely import wkt
from shapely.geometry import Point,box
from shapely.ops import unary_union
r=Path(__file__).resolve().parent;q=r;j=json.loads((r/'layer-component-check.json').read_text());out=[]
for a in j['original_component_checks']:
 if a['opening_loss_fraction']<=.01 or a['over_one_percent_local_shape_proof']:continue
 p=wkt.loads(a['original_polygon_wkt']);loss=p.difference(p.buffer(-.4).buffer(.4));corners=[]
 for ring in [p.exterior,*p.interiors]:
  x=np.array(ring.coords[:-1]);u=x-np.roll(x,1,axis=0);v=np.roll(x,-1,axis=0)-x;t=np.arccos(np.clip(np.sum(u*v,axis=1)/(np.linalg.norm(u,axis=1)*np.linalg.norm(v,axis=1)),-1,1));corners.extend(Point(*pt).buffer(.41)for pt,tt in zip(x,t)if tt>.1)
 remainder=loss.difference(unary_union(corners));geoms=[remainder]if remainder.geom_type=='Polygon'else list(remainder.geoms);dist=max([Point(pt).distance(p.boundary)for g in geoms for pt in g.exterior.coords]or[0]);out.append(dict(z_mm=a['z_mm'],original_component_index=a['original_component_index'],original_polygon_wkt=p.wkt,original_loss_area_mm2=loss.area,true_corner_radius_mm=.41,loss_outside_true_corners_mm2=remainder.area,loss_outside_true_corners_wkt=remainder.wkt,maximum_remainder_vertex_distance_from_original_boundary_mm=dist,remaining_after_0_005mm_original_boundary_band_mm2=remainder.difference(p.boundary.buffer(.005)).area,original_rectangle_symmetric_difference_mm2=p.symmetric_difference(box(*p.bounds)).area,minimum_original_bbox_span_mm=min(a['span_xy_mm'])))
(q/'rectangle-boundary-diagnostics.json').write_text(json.dumps(out,indent=2));print([{k:v for k,v in a.items()if not k.endswith('wkt')}for a in out])
