from pathlib import Path
import json,gzip,hashlib,numpy as np,collections
from shapely import wkt
from shapely.geometry import Point
from shapely.ops import unary_union
R=Path(__file__).parent;M=R.parent;d=json.loads(gzip.decompress((M/'qa/layer-component-check.json.gz').read_bytes()));out=[]
for r in d['original_component_checks']:
 if r['opening_loss_fraction']<=.01:continue
 g=wkt.loads(r['original_polygon_wkt']);loss=g.difference(g.buffer(-.4).buffer(.4));corners=[]
 for ring in [g.exterior,*g.interiors]:
  p=np.array(ring.coords[:-1]);n=len(p)
  for i,b in enumerate(p):
   a=p[(i-1)%n];c=p[(i+1)%n];u=b-a;v=c-b
   if min(np.linalg.norm(u),np.linalg.norm(v))<1e-10:continue
   ang=np.arctan2(abs(np.cross(u,v)),u@v)
   if ang>np.radians(.1):corners.append(b.tolist())
 assert len(corners)>=3
 zones={str(rad):unary_union([Point(p).buffer(rad,resolution=64)for p in corners])for rad in [.41,.6]}
 x,y,X,Y=r['bounds_xy_mm'];family='north_frame'if x< -68 else 'colonnade_pole'
 out.append({**r,'family':family,'actual_vertex_corners':corners,'true_corner_outside_0_41_mm2':float(loss.difference(zones['0.41']).area),'outside_fixed_0_6_mm2':float(loss.difference(zones['0.6']).area),'corner_definition':'Original ring vertices whose adjacent nonzero edge turn exceeds0.1 degree; all original WKT opening/loss untouched; no substituted rectangles or repaired polygons'})
with gzip.open(R/'warning-corners-original.json.gz','wt')as f:json.dump({'stl_sha256':d['stl_sha256'],'not_approval':True,'rows':out},f)
s={}
for k in sorted(set(r['family']for r in out)):
 v=[r for r in out if r['family']==k];s[k]={'samples':len(v),'max_loss_fraction':max(r['opening_loss_fraction']for r in v),'max_true_corner_outside_0_41_mm2':max(r['true_corner_outside_0_41_mm2']for r in v),'max_fixed_0_6_outside_mm2':max(r['outside_fixed_0_6_mm2']for r in v),'nonzero_true_corner_outside_count':sum(r['true_corner_outside_0_41_mm2']>0 for r in v)}
(R/'warning-corners-summary.json').write_text(json.dumps({'stl_sha256':d['stl_sha256'],'families':s,'not_approval':True},indent=2));print(s)
