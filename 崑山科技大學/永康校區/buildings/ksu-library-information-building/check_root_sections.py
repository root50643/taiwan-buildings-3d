from pathlib import Path
import json,hashlib,numpy as np,trimesh
from shapely.geometry import Polygon,box
R=Path(__file__).resolve().parent;m=trimesh.load(R/'model.stl',process=False);tri=m.triangles;B=1.6;S=1.5

def section(z):
 adj={}
 for f in tri[(tri[:,:,2].min(1)<z)&(tri[:,:,2].max(1)>z)]:
  h=[]
  for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
   if tuple(a)>tuple(b):a,b=b,a
   if a[2]<z<b[2] or b[2]<z<a[2]:h.append(a+(b-a)*(z-a[2])/(b[2]-a[2]))
  if len(h)==2:
   a,b=[tuple(q[:2])for q in h]
   if a!=b:adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
 assert all(len(v)==2 for v in adj.values())
 rem=set(adj);shape=Polygon()
 while rem:
  seed=next(iter(rem));a=seed;last=None;pts=[]
  while True:
   pts.append(a);rem.discard(a);b=adj[a][0]if adj[a][0]!=last else adj[a][1];last,a=a,b
   if a==seed:break
  p=Polygon(pts);assert p.is_valid
  if p.area>1e-8:shape=shape.symmetric_difference(p)
 assert shape.is_valid
 return shape
regions=[]
def add(name,x0,y0,x1,y1,z):regions.append((name,box(x0*S,-y1*S,x1*S,-y0*S),B+z*S))
for x in [-41,-34,-27,-20,-13,13,20,27,34,41]:add('front_colonnade_pier',x-.7,-26,x+.7,-24.4,.65)
for x in [-8.2,6.7]:add('entry_pier',x,-29,x+1.5,-26,.65)
for x in [-29,31]:add('south_stair_base',x-1.9,12,x+1.9,16,.05)
for xa,xb in [(3,5),(11,13),(19,21),(26,28)]:add('south_slot_pier_lower_root',xa,24-.0088*(xb+5)**2-4.2,xb,24-.0088*(xa+5)**2+.1,32.31)
add('north_bow_bottom',-10.5,-17,20.5,-4,23.1)
add('intermediate_curved_band',-6.8,-13.1,20.8,-2.6,39.55)
add('upper_curved_cap',-5.3,-19,25.3,-2.8,44.55)
res=[]
for name,b,z in regions:
 upper=section(z).intersection(b);lower=section(z-.2).intersection(b);common=upper.intersection(lower)
 def n(q):return 0 if q.is_empty else 1 if q.geom_type=='Polygon' else len(q.geoms)
 res.append({'label':name,'upper_z_mm':z,'lower_z_mm':z-.2,'upper_original_section_wkt':upper.wkt,'lower_original_section_wkt':lower.wkt,'overlap_wkt':common.wkt,'upper_area_mm2':upper.area,'overlap_area_mm2':common.area,'supported_fraction':common.area/upper.area if upper.area else 0,'overlap_component_areas_mm2':sorted([g.area for g in getattr(common,'geoms',[common])],reverse=True),'overlap_component_count':n(common),'nonempty_single_root':n(common)==1})
r={'stl_sha256':hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),'method':'Original STL sections separated by 0.2mm, actual region intersection; upper/lower WKT retained. Curved cap can have partial supported plan area; no claim of full support or support-free printing.','samples':res,'passed':all(x['nonempty_single_root']for x in res)};(R/'root-section-check.json').write_text(json.dumps(r,indent=2));print([(x['label'],x['supported_fraction'],x['overlap_component_count'])for x in res])
