"""Geometric horizontal cross-sections, NOT a printer slicer or printability proof.
Run: python check_layers.py. Does not repair or mutate model.stl.
"""
from pathlib import Path
import json
import numpy as np
import trimesh
R=Path(__file__).resolve().parent
m=trimesh.load(R/'model.stl',force='mesh',process=True);tri=m.triangles
zmax=float(m.bounds[1,2]);issues=[];rows=[]
# Offset avoids most vertex-aligned sections, which have ambiguous coplanar edges.
for z in np.arange(.071,zmax,.2):
 mask=(tri[:,:,2].min(axis=1)<z)&(tri[:,:,2].max(axis=1)>z)
 t=tri[mask];pairs=[]
 for f in t:
  hit=[]
  for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:
   if tuple(a)>tuple(b):a,b=b,a
   if (a[2]<z<b[2]) or (b[2]<z<a[2]):
    p=a+(b-a)*(z-a[2])/(b[2]-a[2]);hit.append(tuple(np.round(p[:2],6)))
  if len(hit)==2 and hit[0]!=hit[1]:pairs.append(hit)
 adj={}
 for a,b in pairs:adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
 bad=sum(len(v)!=2 for v in adj.values());todo=set(adj);loops=0;areas=[];spans=[]
 while todo:
  seed=next(iter(todo));stack=[seed];seen=set()
  while stack:
   a=stack.pop()
   if a in seen:continue
   seen.add(a);stack.extend(b for b in adj[a] if b not in seen)
  todo-=seen;loops+=1
  if len(seen)>2 and all(len(adj[a])==2 for a in seen):
   pts=[];last=None;a=seed
   while True:
    pts.append(a);opts=adj[a];b=opts[0] if opts[0]!=last else opts[1];last,a=a,b
    if a==seed:break
    if len(pts)>len(seen)+1:break
   p=np.array(pts);areas.append(abs(float(np.dot(p[:,0],np.roll(p[:,1],1))-np.dot(p[:,1],np.roll(p[:,0],1))))/2)
   spans.append(float(np.ptp(p,axis=0).min()))
 if bad or not adj:issues.append({'z_mm':float(z),'non_degree2_nodes':bad,'segments':len(pairs)})
 rows.append({'z_mm':round(float(z),3),'closed_loops':loops if not bad else None,'minimum_loop_bbox_span_mm':min(spans) if spans else None,'minimum_loop_area_mm2':min(areas) if areas else None})
normal=m.face_normals
# Regions steeper than 45deg below horizontal are only a geometric support indicator.
down=(normal[:,2]<-np.sqrt(.5))&(m.triangles_center[:,2]>.01)
report={'method':'Horizontal triangle-plane intersections, 0.2 mm pitch, first z=0.071 mm; welded endpoints rounded to 1e-6 mm','not_a_printer_slicer':True,'not_a_physical_print_test':True,'sampled_layers':len(rows),'all_sampled_contours_closed':not issues,'issues':issues,'downward_facing_area_45deg_mm2':float(m.area_faces[down].sum()),'nominal_min_added_relief_mm':.65,'nominal_nozzle_reference_mm':.4,'wall_thickness_exhaustively_measured':False,'limitations':['Closed contours do not establish extrusion continuity, adhesion, toolpaths, bridging, or support accessibility.','Tiny cross-sections near curved or pointed roofs are expected; minimum loop bbox is not a wall-thickness measurement.','Unseen elevations are simplified. Support settings must be reviewed in a real print slicer.'],'layers':rows}
(R/'layer-check.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='layers'},indent=2));raise SystemExit(0 if not issues else 1)
