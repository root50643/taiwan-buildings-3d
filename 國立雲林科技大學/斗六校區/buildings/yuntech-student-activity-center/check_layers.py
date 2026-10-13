"""Fail-closed canonical 0.2 mm geometric sections. No repair and no slicer claims."""
from pathlib import Path
import json
import numpy as np
import trimesh
from shapely.geometry import Polygon
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',force='mesh',process=True)
tri=m.triangles;rows=[];issues=[]
for z in np.arange(.071,m.bounds[1,2],.2):
 try:
  adj={};mask=(tri[:,:,2].min(axis=1)<z)&(tri[:,:,2].max(axis=1)>z)
  for f in tri[mask]:
   hit=[]
   for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
    if tuple(a)>tuple(b):a,b=b,a
    if a[2]<z<b[2] or b[2]<z<a[2]:hit.append(tuple(np.round((a+(b-a)*(z-a[2])/(b[2]-a[2]))[:2],6)))
   if len(hit)==2 and hit[0]!=hit[1]:
    a,b=hit;adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
  assert adj and all(len(v)==2 for v in adj.values()), 'Each contour node must have degree two'
  todo=set(adj);shape=Polygon();count=0
  while todo:
   seed=min(todo);a=seed;last=None;loop=[]
   while True:
    loop.append(a);todo.discard(a);opts=adj[a];b=opts[0] if opts[0]!=last else opts[1];last,a=a,b
    if a==seed:break
    assert len(loop)<=len(adj), 'Loop did not close'
   p=Polygon(loop);assert p.is_valid and not p.is_empty and p.area>0, 'Invalid individual polygon'
   shape=shape.symmetric_difference(p);assert shape.is_valid, 'Invalid combined polygon';count+=1
  assert shape.is_valid and not shape.is_empty,'Invalid or empty final shape'
  rows.append({'z_mm':round(float(z),3),'closed_loops':count,'area_mm2':float(shape.area),'individual_polygons_valid':True,'combined_polygon_valid':True})
 except Exception as e:issues.append({'z_mm':round(float(z),3),'error':str(e)})
checks={'all_layers_nonempty':len(rows)>0 and not issues,'all_nodes_degree2':not issues,'all_contours_closed':not issues,'all_individual_polygons_valid':not issues,'all_combined_polygons_valid':not issues,'no_polygon_repair_used':True}
r={'passed':all(checks.values()),'checks':checks,'method':'Original delivered STL, canonical shared-edge interpolation, endpoint rounding 1e-6 mm; every 0.2 mm layer from z=0.071 mm; rejects invalid individual or combined polygons without repair.','sampled_layers':len(rows)+len(issues),'valid_layers':len(rows),'issues':issues,'not_a_slicer':True,'not_a_physical_print_test':True,'layers':rows}
(R/'layer-check.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items() if k!='layers'});raise SystemExit(0 if r['passed'] else 1)
