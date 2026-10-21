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
tests=[local('blue DISPLAY plinth NOT foundation',[-90,-90,0],[180,180,3],[.2,1,2.8]),local('front right paired rib foot',[58,-76,3],[15,13,20],[4,8,15,22]),local('front left integrated curling seat',[-117,-75,3],[48,48,35],[5,9,16,25,36]),local('rear transverse low bench',[-26,64,3],[82,13,9],[4,7,8.8]),local('upper milky film and bamboo band',[30,-15,79],[35,35,18],[80,86,92,95]),local('right side thin film',[66,-20,25],[25,30,30],[27,35,45,54]),local('front aperture expected empty',[-12,-75,20],[24,10,25],[22,30,40]),local('rear aperture above low bench expected empty',[2,66,14],[20,9,22],[16,25,34])]



mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Exact-weld raw STL; intersect isolated feature boxes then unrounded horizontal sections; erosion -0.4mm. Empty opening crops expected. No healing.',tests=tests,downward_faces_over_45deg_above_3mm=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),complete_visible_exterior_approximation=True,concealed_footings_included=0,actual_print_tested=False,support_free_certified=False,limitations='Curled shell, thin film, paired rib bands, reduced representative rungs and low seats require support/orientation assessment. No support-free claim. Every crop failure is retained; some crop edges and inclined member tips are thinner than 0.8 mm. Surface overhang count is a heuristic, not a slicer simulation. Geometric erosion is not full FFF simulation.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
