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
tests=[local('broad curved leg lower front',[54,-45,0],[12,12,12],[.2,2,5,9,11]),local('curved leg mid-height',[51,-34,18],[12,20,12],[19,22,25,28]),local('leg to shared beam junction',[48,-7,40],[14,14,12],[41,44,47,50]),local('shared low diameter beam center',[-5,-5,41],[10,10,12],[42.9,44,48,50]),local('parallel roof rib at center',[-1,-26,59],[2,8,12],[60,62,64,66,68]),local('roof field between ribs',[4,-26,60],[4,5,12],[62,64,65,66,67]),local('outer high curved rim',[-6,-50,78],[12,6,8],[79,81,83,83.9,83.959]),local('inner curved crossrib',[3,-30,62],[6,7,10],[63,65,67,69]),local('open undercroft no invented central floor',[-35,-25,0],[70,50,35],[.2,10,20,34.9])]

mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Exact-weld raw STL; intersect isolated feature boxes then unrounded horizontal sections; erosion -0.4mm. Empty opening crops expected. No healing.',tests=tests,downward_faces_over_45deg_above_3mm=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),half_oval_leaves=2,curved_legs=4,actual_print_tested=False,support_free_certified=False,limitations='Rising half-oval roofs and broad splayed legs require support/orientation assessment. No support-free claim. Every crop failure is retained; some crop edges and curved rim tips are thinner than 0.8 mm. Surface overhang count is a heuristic, not a slicer simulation. Geometric erosion is not full FFF simulation.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
