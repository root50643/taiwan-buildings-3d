"""Fail-closed canonical STL XY contour and 0.8mm morphological-opening screen.
Derived from the canonical edge method in thin_canonical_v2.py. No buffer(0)
repair, no invalid-loop omission, and no post hoc mesh repair is performed.
Every effective 0.2mm layer uses z=0.071+0.2*n millimetres.
This is neither slicer toolpath simulation nor an exhaustive wall thickness test.
"""
from pathlib import Path
import json,sys,traceback,hashlib
import numpy as np
import trimesh
from shapely.geometry import Polygon
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',force='mesh',process=True)
rows=[]
checks={'every_effective_0p2mm_layer_sampled':False,'all_nodes_degree_two':True,'all_individual_polygons_valid':True,'all_composite_polygons_valid':True,'no_contour_repair':True,'no_invalid_contours_discarded':True,'all_opened_geometries_valid':True,'no_section_component_erased_by_0p8mm_opening':True,'max_opening_loss_below_one_percent':False}
error=None
try:
 zs=np.arange(.071,m.bounds[1,2],.2);tri=m.triangles
 for z in zs:
  mask=(tri[:,:,2].min(axis=1)<z)&(tri[:,:,2].max(axis=1)>z)
  segments=[]
  for f in tri[mask]:
   hit=[]
   for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
    if tuple(a)>tuple(b):a,b=b,a
    if a[2]<z<b[2] or b[2]<z<a[2]:hit.append(a+(b-a)*(z-a[2])/(b[2]-a[2]))
   assert len(hit)==2, f'Intersection count at {z}: {len(hit)}'
   segments.append(hit)
  adj={}
  for seg in segments:
   a,b=[tuple(np.round(q[:2],6)) for q in seg]
   if a==b:continue # collapsed under 1e-6mm interpolation tolerance; not a polygon filter.
   adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
  if not adj or any(len(v)!=2 for v in adj.values()):checks['all_nodes_degree_two']=False;raise ValueError(f'Degree error at z={z}')
  remaining=set(adj);shape=Polygon();loops=0
  while remaining:
   seed=min(remaining);a=seed;last=None;loop=[]
   while True:
    loop.append(a);remaining.discard(a)
    opts=adj[a];b=opts[0] if opts[0]!=last else opts[1];last,a=a,b
    if a==seed:break
    assert len(loop)<=len(adj), f'Unclosed loop at z={z}'
   p=Polygon(loop)
   if len(loop)<3 or not p.is_valid or p.area<=0:checks['all_individual_polygons_valid']=False;raise ValueError(f'Invalid/degenerate polygon z={z}')
   shape=shape.symmetric_difference(p);loops+=1
  if not shape.is_valid or shape.is_empty:checks['all_composite_polygons_valid']=False;raise ValueError(f'Invalid composite z={z}')
  opened=shape.buffer(-.4).buffer(.4)
  if not opened.is_valid:checks['all_opened_geometries_valid']=False;raise ValueError(f'Invalid opening z={z}')
  polys=[shape] if shape.geom_type=='Polygon' else list(shape.geoms)
  if any(p.buffer(-.4).is_empty for p in polys):checks['no_section_component_erased_by_0p8mm_opening']=False
  lost=shape.difference(opened).area
  rows.append({'z_mm':round(float(z),3),'loops':loops,'area_mm2':float(shape.area),'opening_loss_mm2':float(lost),'opening_loss_fraction':float(lost/shape.area)})
 checks['every_effective_0p2mm_layer_sampled']=len(rows)==len(zs)
 checks['max_opening_loss_below_one_percent']=bool(max(x['opening_loss_fraction'] for x in rows)<.01)
except Exception as e:
 error=str(e)
report={'passed':error is None and all(checks.values()),'checks':checks,'error':error,'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'method':'Canonical shared-edge interpolation; 1e-6mm XY node quantization; fixed z=.071+.2*n; every contour/individual polygon/composite asserted valid; no repair. Opening radius .4mm.','pitch_mm':.2,'z_offset_mm':.071,'reference_width_mm':.8,'sampled_layers':len(rows),'maximum_opening_loss_fraction':max([x['opening_loss_fraction'] for x in rows],default=None),'limitations':['Digital section screening only, no Cura/Prusa toolpath or physical print tested.','Opening does not establish a global minimum wall thickness and includes corner rounding.'],'layers':rows}
(R/'section-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='layers'},indent=2));sys.exit(0 if report['passed'] else 1)
