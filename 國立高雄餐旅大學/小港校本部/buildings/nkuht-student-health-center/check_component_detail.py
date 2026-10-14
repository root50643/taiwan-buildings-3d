"""Sample actual STL sections for XY features below a 0.8 mm reference width.
A geometric screening only, not a nozzle toolpath simulation or full wall analysis.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
from shapely.geometry import Polygon,MultiPoint
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',force='mesh',process=False)
rows=[];component_rows=[]
for z in np.arange(.071,m.bounds[1,2],0.2):
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
 # Test each original section component independently, including tiny ones.
 components=[shape] if shape.geom_type=='Polygon' else list(shape.geoms)
 for ci,component in enumerate(components):
  eroded=component.buffer(-.4);restored=eroded.buffer(.4)
  def count(q):return 0 if q.is_empty else 1 if q.geom_type=='Polygon' else len(q.geoms)
  ec=count(eroded);oc=count(restored)
  rect=list(component.minimum_rotated_rectangle.exterior.coords); widths=[float(np.linalg.norm(np.array(rect[i])-rect[i+1])) for i in range(4)]; loss=component.difference(restored); verts=list(component.exterior.coords)+[p for ring in component.interiors for p in ring.coords]
  component_rows.append({'bounds':list(component.bounds),'rotated_bbox_min_width':min(widths),'retained_fraction':1-loss.area/component.area,'loss_area_mm2':loss.area,'loss_outside_0p41_vertex_mm2':loss.difference(MultiPoint(verts).buffer(.41)).area,'z_mm':round(float(z),3),'original_component_index':ci,'original_area_mm2':component.area,'eroded_components':ec,'opened_components':oc,'opening_loss_fraction':component.difference(restored).area/component.area})
  assert ec==1 and oc==1, f'Original component {ci} at {z} vanishes or splits: eroded {ec}, opened {oc}'
 opened=shape.buffer(-.4).buffer(.4)
 lost=shape.difference(opened).area
 rows.append({'z_mm':round(float(z),3),'section_area_mm2':float(shape.area),'area_not_retained_by_0_8mm_opening_mm2':float(lost),'fraction':float(lost/max(shape.area,1e-9))})
report={'method':'Actual STL XY sections with canonical edge interpolation and closed-loop assertions at 0.2mm pitch, z offset .071mm; morphological opening radius 0.4mm. Narrow tips and sharp corners also contribute.','reference_width_mm':.8,'sampled_layers':len(rows),'layers_over_one_percent_opening_loss':sum(r['fraction']>.01 for r in rows),'maximum_opening_loss_fraction':max(r['fraction'] for r in rows),'not_a_slicer':True,'not_exhaustive_wall_thickness':True,'judgment':'Review fine roof/rim/corner regions and use supports where needed; no automatic printability claim.','layers':rows,'original_component_checks':component_rows,'checks':{'all_original_components_survive_0_8mm_opening':True,'no_original_component_splits_after_erosion_or_opening':True},'passed':True}
report['stl_sha256']=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest()
report['maximum_individual_polygon_loss_fraction']=max(r['opening_loss_fraction'] for r in component_rows)
report['individual_polygons_over_one_percent']=sum(r['opening_loss_fraction']>.01 for r in component_rows)
report['checks']['all_individual_polygon_losses_le_one_percent']=report['individual_polygons_over_one_percent']==0
report['passed']=all(report['checks'].values())
(R/'component-detail.json').write_text(json.dumps(report,indent=2))
assert report['checks']['all_individual_polygon_losses_le_one_percent'], 'Per-polygon warning: change source geometry or obtain a specific evidenced exception; no whole-layer averaging'
(R/'component-detail.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k not in ['layers','original_component_checks']})
