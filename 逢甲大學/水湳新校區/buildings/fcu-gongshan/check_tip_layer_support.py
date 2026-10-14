"""Original-STL tip sections, inscribed cores, and overlap with the preceding 0.2mm layer."""
from pathlib import Path
import numpy as np,trimesh,json,hashlib
from shapely.geometry import Polygon,Point
from shapely.ops import polylabel
R=Path(__file__).parent;m=trimesh.load(R/'model.stl',process=False)
def section(z):
 adj={}
 for f in m.triangles[(m.triangles[:,:,2].min(axis=1)<z)&(m.triangles[:,:,2].max(axis=1)>z)]:
  hit=[]
  for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
   if tuple(a)>tuple(b):a,b=b,a
   if a[2]<z<b[2] or b[2]<z<a[2]:hit.append(tuple((a+(b-a)*(z-a[2])/(b[2]-a[2]))[:2]))
  assert len(hit)==2 and hit[0]!=hit[1]
  a,b=hit;adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
 assert adj and all(len(v)==2 for v in adj.values());remaining=set(adj);out=Polygon()
 while remaining:
  seed=next(iter(remaining));a=seed;last=None;loop=[]
  while True:
   loop.append(a);remaining.discard(a);v=adj[a];b=v[0]if v[0]!=last else v[1];last,a=a,b
   if a==seed:break
   assert len(loop)<=len(adj)
  p=Polygon(loop);assert p.is_valid and p.area>0;out=out.symmetric_difference(p)
 assert out.is_valid;polys=[out]if out.geom_type=='Polygon'else list(out.geoms);selected=[p for p in polys if p.contains(Point(2.65,-60.55))];assert len(selected)==1
 return selected[0]
prev=section(19.871);rows=[]
for z in [20.071,20.271,20.471,20.671]:
 a=section(z);center=polylabel(a,tolerance=.0001);core=2*center.distance(a.boundary);overlap=a.intersection(prev).area;eroded=a.buffer(-.4);opened=eroded.buffer(.4);assert eroded.geom_type=='Polygon' and not eroded.is_empty and opened.geom_type=='Polygon' and not opened.is_empty;joint=a.intersection(prev);assert joint.geom_type=='Polygon' and not joint.is_empty; joint_core=2*polylabel(joint,tolerance=.0001).distance(joint.boundary);assert joint_core>=.8 and core>=.8
 rows.append(dict(z_mm=z,area_mm2=a.area,opening_loss_fraction=a.difference(opened).area/a.area,inscribed_core_diameter_mm=core,core_xy=list(center.coords)[0],overlap_previous_lower_layer_mm2=overlap,overlap_core_diameter_mm=joint_core,fraction_with_material_0p2mm_below=overlap/a.area));prev=a
r=dict(stl_sha256=hashlib.sha256((R/'model.stl').read_bytes()).hexdigest(),checks=dict(four_tip_layers_single_after_erosion_and_opening=True,all_tip_layers_have_core_diameter_ge_0p8mm=True,all_tip_layers_have_continuous_lower_overlap_core_ge_0p8mm=True),passed=True,samples=rows,limits='Inscribed core diameter is not a global minimum neck or wall thickness; area overlap is not a physical-print guarantee.');(R/'tip-layer-support.json').write_text(json.dumps(r,indent=2));print(r)
