"""Reconstruct warning polygons and quantify loss outside four actual post corners.
Original section vertices are not all called true corners. No repair or exception approval.
"""
from pathlib import Path
import json,hashlib,numpy as np,trimesh
from shapely.geometry import Polygon,MultiPoint
R=Path(__file__).parent;m=trimesh.load(R/'model.stl',process=False)
def section(z):
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
  a,b=[tuple(q[:2]) for q in seg]
  assert a!=b, f'Degenerate original section edge at {z}'
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
   assert a==seed and p.is_valid, f'Invalid closed loop at {z}: {__import__("shapely").is_valid_reason(p)}'
   assert p.area>0, f'Zero-area original polygon at {z}'
   shape=shape.symmetric_difference(p)
 assert shape.is_valid, f'Invalid combined section at {z}: reject thin screening without repair'
 return shape

a=json.loads((R/'component-detail.json').read_text());warnings=[v for v in a['original_component_checks']if v['opening_loss_fraction']>.01];rows=[]
for z in sorted(set(v['z_mm']for v in warnings)):
 shape=section(z);parts=[shape]if shape.geom_type=='Polygon'else list(shape.geoms)
 for p in parts:
  er=p.buffer(-.4);op=er.buffer(.4);loss=p.difference(op)
  if loss.area/p.area<=.01:continue
  # Canopy square post is rotated rectangular; hull returns only exact original convex corners.
  # Float32 triangulation can add microscopic collinear turns. Fit only actual extreme points
  # in known two construction axes; distances to these original extrema are published.
  A=np.array([[-np.sqrt(3)/2,-.5],[.5,-np.sqrt(3)/2]])
  vs=np.asarray(p.exterior.coords)[:-1];local=vs@A;lo=local.min(0);hi=local.max(0)
  corners=[]
  for q in [lo,[lo[0],hi[1]],hi,[hi[0],lo[1]]]:
   k=int(np.argmin(np.linalg.norm(local-q,axis=1)));corners.append(vs[k].tolist())
  original_corner_deviation=max(float(np.min(np.linalg.norm(local-q,axis=1)))for q in [lo,[lo[0],hi[1]],hi,[hi[0],lo[1]]])
  assert original_corner_deviation<1e-5
  dims=hi-lo;assert np.allclose(dims,[1.2*.86*1.209283792097708,1.2*1.209283792097708],atol=1e-5)
  outside=loss.difference(MultiPoint(corners).buffer(.41)).area
  assert er.geom_type=='Polygon'and op.geom_type=='Polygon'and not er.is_empty
  rows.append(dict(z_mm=z,original_area_mm2=p.area,loss_mm2=loss.area,loss_percent=100*loss.area/p.area,retained_percent=100*(1-loss.area/p.area),normal_dimensions_mm=dims.tolist(),four_actual_extreme_corners_mm=corners,corner_fit_error_mm=original_corner_deviation,loss_outside_four_0p41mm_corners_mm2=outside))
assert len(rows)==len(warnings)
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),count=len(rows),families={'two_square_canopy_posts':len(rows)},z_range_mm=[min(v['z_mm']for v in rows),max(v['z_mm']for v in rows)],peak_loss_percent=max(v['loss_percent']for v in rows),minimum_retained_percent=min(v['retained_percent']for v in rows),maximum_loss_outside_four_true_corners_mm2=max(v['loss_outside_four_0p41mm_corners_mm2']for v in rows),checks={'all_warning_polygons_identified':len(rows)==len(warnings),'all_original_post_normal_widths_identified':True,'all_warnings_single_eroded_and_opened_core':True},rows=rows,limits='Evidence only; strict component check remains false. No automatic exception or global thickness guarantee.')
(R/'warning-families.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items()if k!='rows'})
