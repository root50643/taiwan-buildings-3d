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
tests=[local('left glazing isolated far from posts',[-71,0,35],[3,10,25],[35.1,40,50,59.9]),local('notice backing isolated from frame',[-50,18,35],[10,4,20],[35.1,40,50,54.9]),local('seat center away from leg',[-40,1,19],[10,16,5],[20.1,21,22.3]),local('center bench leg',[-2,6,4],[4,6,15],[4.1,10,18.9]),local('left bracket tip',[ -69.25,15,13],[4,2,7],[13.2,13.4,13.8,15,19]),local('roof leading edge only',[-20,-28,89],[40,2,5],[90.2,92,93.8,93.999]),local('rear upper opening empty proof',[-60,17,72],[120,6,13],[72.1,78,84.9]),local('rear lower opening excluding leg',[-60,17,5],[50,6,13],[5.1,10,17.9])]
mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Exact-weld raw STL; intersect isolated feature boxes then unrounded horizontal sections; erosion -0.4mm. Empty opening crops expected. No healing.',tests=tests,downward_faces_over_45deg_excluding_plinth=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),roof_clear_transverse_span_estimate_mm=136.8,seat_half_span_estimate_mm=65.75,actual_print_tested=False,support_free_certified=False,limitations='Long roof and seat spans require slicer support/orientation assessment. Sloping roof leading top wedge and bracket tips can lose thin cross sections; do not represent as blanket thin-wall pass. Geometric erosion is not full FFF simulation.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
