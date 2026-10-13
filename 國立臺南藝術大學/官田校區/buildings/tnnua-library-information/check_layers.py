"""0.2 mm geometric contour and thin-feature screening, not G-code slicing.
Run beside model.stl: python check_layers.py
Requires numpy, trimesh, shapely. Does not alter model geometry.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
from shapely.geometry import Polygon
ROOT=Path(__file__).resolve().parent
mesh=trimesh.load(ROOT/'model.stl',force='mesh',process=True)
rows=[];bad=[];thin=[]
# 0.000013 mm offset avoids coplanar edges on designed 0.1mm heights.
for z in np.arange(.100013,mesh.bounds[1,2],.2):
 seg=trimesh.intersections.mesh_plane(mesh,[0,0,1],[0,0,float(z)])
 from scipy.spatial import cKDTree
 pts=seg[:,:,:2].reshape(-1,2)
 parent=list(range(len(pts)))
 def find(i):
  while parent[i]!=i: parent[i]=parent[parent[i]];i=parent[i]
  return i
 for aa,bb in cKDTree(pts).query_pairs(1e-4):
  aa,bb=find(aa),find(bb)
  if aa!=bb:parent[bb]=aa
 adj={};edges=set()
 for i in range(0,len(pts),2):
  a=tuple(pts[find(i)]);b=tuple(pts[find(i+1)])
  if a==b:continue
  edges.add(tuple(sorted([a,b])))
 for a,b in edges:adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a)
 closed=bool(edges) and all(len(v)==2 for v in adj.values())
 region=Polygon();loops=0
 if closed:
  unused=set(edges)
  while unused:
   a,b=next(iter(unused));start=a;points=[a];prev=a;cur=b;unused.remove(tuple(sorted([a,b])))
   while cur!=start:
    points.append(cur);nxt=next(x for x in adj[cur] if x!=prev)
    e=tuple(sorted([cur,nxt]));unused.discard(e);prev,cur=cur,nxt
   poly=Polygon(points)
   if not poly.is_valid:closed=False;break
   region=region.symmetric_difference(poly);loops+=1
 if not closed:bad.append(float(z))
 area=float(region.area)
 # A local 0.8mm XY width screen, mitred to avoid flagging square corners.
 # Narrow roof tips, relief ribs or tapering fin ends can be flagged legitimately.
 opened=region.buffer(-.4,join_style=2).buffer(.4,join_style=2) if area else Polygon()
 lost=max(0,float(region.difference(opened).area))
 if lost>.2:thin.append({'z_mm':round(float(z),5),'opening_loss_area_mm2':round(lost,5)})
 rows.append({'z_mm':round(float(z),5),'closed':closed,'loops':loops,'area_mm2':round(area,5),'xy_0_8mm_opening_loss_mm2':round(lost,5)})
report={'stl_sha256':hashlib.sha256((ROOT/'model.stl').read_bytes()).hexdigest(),'method':'Original STL horizontal triangle-plane intersections every 0.2 mm; endpoints clustered within 0.0001mm numerical tolerance; graph degrees must all equal 2; every contour polygon must be valid. Closed loop regions use even-odd nesting.','layer_spacing_mm':.2,'first_height_mm':.100013,'layers':len(rows),'all_sampled_contours_closed':not bad,'bad_contour_heights_mm':bad,'thin_screen':{'xy_screen_width_mm':.8,'area_warning_threshold_mm2':.2,'flagged_layers':len(thin),'maximum_opening_loss_area_mm2':max((a['xy_0_8mm_opening_loss_mm2'] for a in rows),default=0),'flagged_heights':thin,'interpretation':'Screening flags narrow XY protrusions, isolated small contour islands and tapering roof tips. Not a full 3D wall-thickness proof, not automatic unprintability.'},'formal_slicer_run':False,'physical_print_test':False,'limitations':['Geometric sections only: no nozzle paths, extrusion width, support generation, bridge quality or G-code was validated.','Sample planes do not cover every possible Z and do not prove minimum wall thickness.','Compare flagged layers and source dimensions in the printing notes before production.'],'sections':rows}
(ROOT/'layer-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['sections','thin_screen']},ensure_ascii=False));print('thin layers',len(thin));assert not bad
