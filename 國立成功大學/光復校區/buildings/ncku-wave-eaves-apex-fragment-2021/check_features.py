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
tests=[local('blue display plinth NOT source building',[-45,-10,0],[90,30,3],[.2,1,2.8]),local('left blue cut support NOT real footing',[-50,-2,3],[10,18,16],[5,10,18]),local('paired left boundary midsection',[-31,-10,41],[15,20,14],[43,47,51,54]),local('upper transverse timber',[-20,-10,49],[32,16,14],[51,55,59,62]),local('offset Y junction',[-3,-10,36],[25,16,30],[39.4,44,50,59]),local('dark apex simplified connector',[-2,-14,94],[14,12,8],[95,97,99,100,100.6,100.702]),local('large upper opening expected empty',[-5,-10,65],[6,16,12],[66,70,75]),local('open space between cut supports expected empty',[-20,-8,5],[40,18,9],[6,10,13])]


mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Exact-weld raw STL; intersect isolated feature boxes then unrounded horizontal sections; erosion -0.4mm. Empty opening crops expected. No healing.',tests=tests,downward_faces_over_45deg_above_3mm=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),complete_pavilion=False,actual_footings_included=0,actual_print_tested=False,support_free_certified=False,limitations='Inclined rectangular lattice, short cut members, paired boundary slit and apex require support/orientation assessment. No support-free claim. Every crop failure is retained; some crop edges and inclined member tips are thinner than 0.8 mm. Surface overhang count is a heuristic, not a slicer simulation. Geometric erosion is not full FFF simulation.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
