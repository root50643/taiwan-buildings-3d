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
tests=[local('left outer coping strip',[-70,-10,58.5],[1.6,20,1.5],[58.6,59,59.999]),local('right front coping strip',[35,-17,58.5],[20,1.6,1.5],[58.6,59,59.999]),local('left rear coping strip',[-60,15.4,58.5],[20,1.6,1.5],[58.6,59,59.999]),local('central red side rim',[-22,-12,71.5],[4,20,1.5],[71.6,72,72.999]),local('central pier forward projection',[-22,-21.6,8],[4,1.2,50],[8.1,35,57.9]),local('white panel solid backing',[-10,-20.4,10],[20,4,40],[10.1,30,49.9]),local('left shallow top recess air',[-60,-10,58.5],[20,20,1.4],[58.6,59,59.8]),local('right shallow top recess air',[35,-10,58.5],[20,20,1.4],[58.6,59,59.8]),local('central shallow top recess air',[-10,-10,71.5],[20,20,1.4],[71.6,72,72.8])]
mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Exact-weld raw STL; isolated feature crops and unrounded horizontal sections; -0.4mm erosion. Three recess-air crops intentionally empty. No healing or thin exemptions.',tests=tests,downward_faces_over_45deg_excluding_plinth=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),white_panel_recess_top_lip_depth_mm=.6,actual_print_tested=False,support_free_certified=False,limitations='Shallow name-panel recess has an upper downward-facing lip; evaluate layer width and orientation in target slicer. Local crops are sampled tests, not a proof of every minimum width; erosion is not full FFF simulation. No physical print or strength test.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
