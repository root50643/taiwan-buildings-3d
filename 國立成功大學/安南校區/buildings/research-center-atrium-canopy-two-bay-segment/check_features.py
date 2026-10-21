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
tests=[local('central frame web isolated midspan',[-61,-1.3,34],[4,2.6,9],[36,37,38,39,40,41,42]),local('central lower chord crown',[-5,-1.3,51],[10,2.6,4],[51.2,52,53,54]),local('longitudinal center purlin between frames',[-1.1,9,58],[2.2,10,5],[59,60,61]),local('roof field between purlins and frames',[5,8,57],[5,8,6],[59,60,61,62]),local('right fork lower stem',[70,-2,17],[7,4,10],[18,20,22,24,26]),local('right fork upper termination',[42,-2,40],[5,4,5],[42,43.2,43.4,44]),local('left short support',[-69,-2.3,27],[5,4.6,6],[28.2,29,30,31]),local('truss gap and upper-chord boundary crop',[-60,-1,39],[1,2,2],[39.1,40,40.9]),local('no center ground columns',[-40,-20,0],[80,40,20],[.2,5,15,19.9])]

mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Exact-weld raw STL; intersect isolated feature boxes then unrounded horizontal sections; erosion -0.4mm. Empty opening crops expected. No healing.',tests=tests,downward_faces_over_45deg_excluding_plinth=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),longitudinal_frame_spacing_mm=28,transverse_estimated_span_mm=130,actual_print_tested=False,support_free_certified=False,limitations='Raised arch roof and truss webs require support/orientation assessment. Blue side display blocks do not make the roof support-free. Every crop failure is retained; some crop edges and cylindrical tips are thinner than 0.8 mm. Surface overhang count is a heuristic, not a slicer simulation. Geometric erosion is not full FFF simulation.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
