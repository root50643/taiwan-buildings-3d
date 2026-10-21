"""Local measurements of delivered raw STL, not nominal design alone."""
from pathlib import Path
import json,hashlib,numpy as np,manifold3d as md,trimesh
from shapely.geometry import Polygon,GeometryCollection
from qa_model import raw_read
A=Path(__file__).resolve().parent
_,v,f=raw_read(A/'model.stl');m=md.Manifold(md.Mesh(np.asarray(v,dtype=np.float32),np.asarray(f,dtype=np.uint32)))
def local(name,origin,size,levels,rotate=None):
 s=m ^ md.Manifold.cube(size).translate(origin)
 if rotate:s=s.rotate(rotate)
 rows=[]
 for z in levels:
  g=GeometryCollection()
  for p in s.slice(float(z)).to_polygons():
   if len(p)>2:g=g.symmetric_difference(Polygon(p))
  ps=list(g.geoms) if g.geom_type=='MultiPolygon' else ([] if g.is_empty else [g])
  rows.append(dict(plane_mm=float(z),components=len(ps),valid=g.is_valid,area_mm2=g.area,failed_0_8mm=sum(p.buffer(-.4).is_empty for p in ps)))
 return dict(feature=name,crop_origin=origin,crop_size=size,rotation=rotate,rows=rows)
tests=[local('center rear post rear half isolated from wall',[ -2,0.4,5],[4,1.6,10],[5.1,10,14.9]),local('first blank notice backing away from frame',[-32,-5,50],[6,7,25],[50.1,60,74.9]),local('timber seat away from rear wall',[-5,-20,19],[10,8,5],[20.1,21,22.5]),local('wall backed pale bench support',[-5,-18,16],[10,9,5],[16.6,18,19.9]),local('central diagonal brace lower transition excluding rear post',[-2,-8,69],[4,4,8],[70.1,70.2,70.4,72,75]),local('roof near free front edge',[-10,-52,89],[20,3,5],[90.1,92,93.499]),local('board to wall narrow horizontal slit',[-32,-5,40],[6,7,3],[40.1,41,42.9]),local('no front ground post proof',[-3,-48,4],[6,6,60],[4.1,20,40,63.9]),local('open triangular bracket void',[-1,-24,83],[2,8,4],[83.1,85,86.9])]

mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Exact-weld raw STL; intersect isolated feature boxes then unrounded horizontal sections; erosion -0.4mm. Empty opening crops expected. No healing.',tests=tests,downward_faces_over_45deg_excluding_plinth=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),roof_max_cantilever_estimate_mm=52,roof_between_rear_brackets_estimate_mm=54,seat_wall_backed_projection_estimate_mm=13,actual_print_tested=False,support_free_certified=False,limitations='Cantilever roof, elevated bench and board lower rails require slicer support/orientation assessment. Local brace root crops can expose thin triangular tips even when global layers pass; report every local failure. Geometric erosion is not full FFF simulation.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
