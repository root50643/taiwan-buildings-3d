"""Sample actual STL sections for XY features below a 0.8 mm reference width.
A geometric screening only, not a nozzle toolpath simulation or full wall analysis.
"""
from pathlib import Path
import json, hashlib
import numpy as np
import trimesh
from shapely.geometry import Polygon
R=Path(__file__).resolve().parent
before=(R/'model.stl').read_bytes()
m=trimesh.load(R/'model.stl',force='mesh',process=True)
rows=[]
component_rows=[]
for z in np.arange(.071,m.bounds[1,2],.2):
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
 opened=shape.buffer(-.4).buffer(.4)
 components=list(shape.geoms) if shape.geom_type=='MultiPolygon' else [shape]
 for ci,c in enumerate(components):
  op=c.buffer(-.4).buffer(.4)
  nout=0 if op.is_empty else len(op.geoms) if op.geom_type=='MultiPolygon' else 1
  assert nout==1, f'Component vanishes or splits at z={z}, component={ci}'
  retained=float(c.intersection(op).area/c.area)
  rect=np.asarray(c.minimum_rotated_rectangle.exterior.coords)[:4]
  dims=np.linalg.norm(np.roll(rect,-1,axis=0)-rect,axis=1)
  component_rows.append({'z_mm':round(float(z),3),'component':ci,'area_mm2':float(c.area),'retained_fraction':retained,'opening_components':nout,'minimum_rotated_rectangle_width_mm':float(min(dims))})
 lost=shape.difference(opened).area
 rows.append({'z_mm':round(float(z),3),'section_area_mm2':float(shape.area),'area_not_retained_by_0_8mm_opening_mm2':float(lost),'fraction':float(lost/max(shape.area,1e-9))})
report={'method':'Actual STL XY sections with canonical edge interpolation and closed-loop assertions at 0.2mm pitch, z offset .071mm; morphological opening radius 0.4mm. Narrow tips and sharp corners also contribute.','reference_width_mm':.8,'sampled_layers':len(rows),'layers_over_one_percent_opening_loss':sum(r['fraction']>.01 for r in rows),'maximum_opening_loss_fraction':max(r['fraction'] for r in rows),'not_a_slicer':True,'not_exhaustive_wall_thickness':True,'judgment':'Review fine roof/rim/corner regions and use supports where needed; no automatic printability claim.','layers':rows}
report['checks']={'all_raw_section_loops_valid':True,'all_combined_sections_valid':True,'pitch_0_2mm':True,'no_component_vanishes_or_splits_under_opening':True};report['component_min_retained_fraction']=min(x['retained_fraction'] for x in component_rows);report['components']=component_rows;report['passed']=True
assert (R/'model.stl').read_bytes()==before
report['stl_sha256']=hashlib.sha256(before).hexdigest()
(R/'component-opening-check.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k not in ('layers','components')})
