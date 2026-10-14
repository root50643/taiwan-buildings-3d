"""Sample actual STL sections for XY features below a 0.8 mm reference width.
A geometric screening only, not a nozzle toolpath simulation or full wall analysis.
"""
from pathlib import Path
import json,ast,hashlib
import numpy as np
import trimesh
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',force='mesh',process=True)
source=ast.parse((R/'build_model.py').read_text()); buildings=next(ast.literal_eval(n.value) for n in source.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='BUILDINGS' for t in n.targets))
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
  center=component.centroid; nearest=min(buildings,key=lambda b:(center.x-b['model_center_mm'][0])**2+(center.y-b['model_center_mm'][1])**2)
  loss=component.difference(restored); span=[component.bounds[2]-component.bounds[0],component.bounds[3]-component.bounds[1]]
  corners=[]
  for ring in [component.exterior,*component.interiors]:
   q=np.array(ring.coords[:-1]);u=q-np.roll(q,1,axis=0);v=np.roll(q,-1,axis=0)-q;turn=np.arccos(np.clip(np.sum(u*v,axis=1)/(np.linalg.norm(u,axis=1)*np.linalg.norm(v,axis=1)),-1,1))
   corners.extend(Point(*xy).buffer(.60) for xy,t in zip(q,turn) if t>.10)
  corner_region=unary_union(corners);outside=loss.difference(corner_region).area
  if loss.area/component.area>.01:assert outside<.0002,(z,component.bounds,outside)
  kind='1.1mm diameter porch column' if component.area<1.1 else 'roof/ridge' if z>[1.70,2.55,3.60,4.60][nearest['level']]+3.3 else 'body with window recesses / porch ends or integral terrace'
  component_rows.append({'building_nearest':nearest['id'],'feature_class':kind,'bounds_xy_mm':list(component.bounds),'span_xy_mm':span,'eroded_area_mm2':eroded.area,'opened_area_mm2':restored.area,'lost_area_mm2':loss.area,'corner_turn_threshold_radians':.10,'corner_region_radius_mm':.60,'loss_outside_corner_regions_mm2':outside,'outside_corner_loss_fraction':outside/component.area,'assessment':'Each original Polygon remains one nonempty eroded and opened component; rounded convex window/porch/end corners account for local area loss. Narrow-feature survival is tested independently, not waived by this percentage.','z_mm':round(float(z),3),'original_component_index':ci,'original_area_mm2':component.area,'eroded_components':ec,'opened_components':oc,'opening_loss_fraction':component.difference(restored).area/component.area})
  assert ec==1 and oc==1, f'Original component {ci} bounds {component.bounds} at {z} vanishes or splits: eroded {ec}, opened {oc}'
 opened=shape.buffer(-.4).buffer(.4)
 lost=shape.difference(opened).area
 rows.append({'z_mm':round(float(z),3),'section_area_mm2':float(shape.area),'area_not_retained_by_0_8mm_opening_mm2':float(lost),'fraction':float(lost/max(shape.area,1e-9))})
report={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'original_components_over_one_percent':sum(r['opening_loss_fraction']>.01 for r in component_rows),'all_over_one_percent_loss_outside_0_6mm_corner_regions_below_0_0002_mm2':all(r['loss_outside_corner_regions_mm2']<.0002 for r in component_rows if r['opening_loss_fraction']>.01),'maximum_original_component_loss':max(r['opening_loss_fraction'] for r in component_rows),'method':'Actual STL XY sections with canonical edge interpolation and closed-loop assertions at 0.2mm pitch, z offset .071mm; morphological opening radius 0.4mm. Narrow tips and sharp corners also contribute.','reference_width_mm':.8,'sampled_layers':len(rows),'layers_over_one_percent_opening_loss':sum(r['fraction']>.01 for r in rows),'maximum_opening_loss_fraction':max(r['fraction'] for r in rows),'not_a_slicer':True,'not_exhaustive_wall_thickness':True,'judgment':'Review fine roof/rim/corner regions and use supports where needed; no automatic printability claim.','layers':rows,'original_component_checks':component_rows,'checks':{'over_one_percent_corner_residual_below_0_0002_mm2':all(r['loss_outside_corner_regions_mm2']<.0002 for r in component_rows if r['opening_loss_fraction']>.01),'all_original_components_survive_0_8mm_opening':True,'no_original_component_splits_after_erosion_or_opening':True},'passed':True}
(R/'layer-component-check.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k not in ['layers','original_component_checks']})
