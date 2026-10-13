"""Sample actual STL sections for XY features below a 0.8 mm reference width.
A geometric screening only, not a nozzle toolpath simulation or full wall analysis.
"""
from pathlib import Path
import json
import numpy as np
import trimesh
from shapely.geometry import Polygon
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',force='mesh',process=True)
rows=[]
for z in np.arange(.071,m.bounds[1,2],1.0):
 # Canonical edge direction gives bitwise-consistent shared-edge intersections.
 tri=m.triangles
 mask=(tri[:,:,2].min(axis=1)<z)&(tri[:,:,2].max(axis=1)>z)
 segments=[]
 for f in tri[mask]:
  hit=[]
  for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
   if tuple(a)>tuple(b):a,b=b,a
   if a[2]<z<b[2] or b[2]<z<a[2]:hit.append(a+(b-a)*(z-a[2])/(b[2]-a[2]))
  if len(hit)==2:segments.append(hit)
 adj={}
 for seg in segments:
  a,b=[tuple(np.round(q[:2],6)) for q in seg]
  if a==b:continue
  adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
 assert adj and all(len(v)==2 for v in adj.values()), f'Unclosed section at {z}: reject thin screening'
 remaining=set(adj);shape=Polygon()
 while remaining:
  seed=next(iter(remaining));a=seed;last=None;loop=[]
  while True:
   loop.append(a);remaining.discard(a)
   if len(adj[a])!=2:break
   opts=adj[a];b=opts[0] if opts[0]!=last else opts[1];last,a=a,b
   if a==seed or len(loop)>len(adj):break
  if len(loop)>2:
   p=Polygon(loop)
   assert a==seed and p.is_valid, f'Invalid closed loop at {z}'
   if p.area>1e-8:shape=shape.symmetric_difference(p)
 assert shape.is_valid, f'Invalid combined section at {z}: reject thin screening without repair'

 components=list(shape.geoms) if shape.geom_type=='MultiPolygon' else [shape]
 component_rows=[]
 for component in components:
  shrunk=component.buffer(-.4); retained=shrunk.buffer(.4)
  rect=list(component.minimum_rotated_rectangle.exterior.coords)
  widths=[float(np.linalg.norm(np.array(rect[i])-np.array(rect[i+1]))) for i in range(4)]
  component_rows.append({'area_mm2':float(component.area),'minimum_rotated_rectangle_width_mm':min(widths),'opening_retained_area_mm2':float(retained.area),'opening_retained_fraction':float(retained.area/component.area),'eroded_core_components':len(shrunk.geoms) if shrunk.geom_type=='MultiPolygon' else (0 if shrunk.is_empty else 1),'component_survives':not shrunk.is_empty})
 assert all(c['component_survives'] and c['eroded_core_components']==1 for c in component_rows),f'Component disappears/splits at {z}'
 rows.append({'z_mm':round(float(z),3),'components':component_rows,'section_wkt':shape.wkt})
report={'method':'Per-connected-Polygon check on every canonical v3 1mm sample (z=.071+n); no repair; opening radius .4mm. Minimum rotated rectangle is a bounding-box width, not exhaustive wall thickness.','checks':{'every_component_survives':all(c['component_survives'] for row in rows for c in row['components']),'no_eroded_component_splits':all(c['eroded_core_components']==1 for row in rows for c in row['components'])},'layers':rows}
(R/'component-thin-audit.json').write_text(json.dumps(report,indent=2));print(report['checks'])
