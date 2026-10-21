"""Sample actual unhealed STL regions; retain thin/marginal results, not a slicer."""
from pathlib import Path
import json,hashlib,numpy as np,manifold3d as md,trimesh
from shapely.geometry import Polygon,GeometryCollection
from qa_model import raw_read
A=Path(__file__).resolve().parent
_,v,f=raw_read(A/'model.stl');m=md.Manifold(md.Mesh(np.asarray(v,dtype=np.float32),np.asarray(f,dtype=np.uint32)))
def local(name,origin,size,levels,expected='solid'):
 s=m ^ md.Manifold.cube(size).translate(origin); rows=[]
 for z in levels:
  g=GeometryCollection()
  for p in s.slice(float(z)).to_polygons():
   if len(p)>2:g=g.symmetric_difference(Polygon(p))
  ps=list(g.geoms) if g.geom_type=='MultiPolygon' else ([] if g.is_empty else [g])
  erosions=[p.buffer(-.4,quad_segs=16) for p in ps]
  rows.append(dict(plane_mm=float(z),components=len(ps),valid=g.is_valid,area_mm2=g.area,failed_0_8mm=sum(p.is_empty for p in erosions),eroded_areas_mm2=[p.area for p in erosions],expected_occupancy_met=(not ps if expected=='air' else bool(ps))))
 return dict(feature=name,crop_origin=origin,crop_size=size,expected=expected,rows=rows)
tests=[]
for x in [-48,48]:
 for y in [-48,48]:tests.append(local('principal post',[x-2,y-2,12],[4,4,62],[14,35,60,72]))
tests.append(local('front central approach',[-20,-51,7],[40,6,50],[8,16,25,45],'air'))
tests.append(local('front left ladder upright',[-38,-49,30],[2,2,30],[35,48,58]))
tests.append(local('ladder open rectangle',[-44,-49,27],[4,2,10],[30,32,36],'air'))
tests.append(local('side low baluster',[47.2,-42.8,19],[1.6,1.6,8],[20,23,26]))
tests.append(local('left bench',[-46,-8,15],[4,16,2],[15.2,16,16.8]))
tests.append(local('main ring beam',[-8,-49,75],[16,2,5],[75.2,77,79]))
tests.append(local('roof eave',[-3,-62.8,74],[6,2,4],[74.5,75.5,76.5]))
tests.append(local('roof upper cap',[-.5,-.5,95],[1,1,3],[95.2,97,97.9]))
tests.append(local('blank plaque',[-7,-50.3,66],[14,1.5,6],[66.5,69,71.5]))
tests.append(local('display ground',[-10,-10,0],[20,20,3],[.2,1.5,2.8]))
mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Raw STL exact-coordinate weld only. Actual mesh crop intersections and unrounded horizontal sections; exact -0.4mm erosion; no thin exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),downward_faces_over_45deg_above_base=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),nominal_baluster_width_mm=1.7,roof_nominal_vertical_thickness_mm=3.2,thin_warning='Horizontal sections can become thin near roof courses and sloping raft/truss ends. Global connected-section erosion can conceal narrow attached details. Retain every failure.',actual_print_tested=False,support_free_certified=False,limitations='Broad roof soffit, benches, lintels, lattice crossbars and overhangs require slicer support/orientation planning. No exhaustive normal wall thickness/strength/FFF simulation; no physical print.')

(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:q for k,q in report.items() if k!='tests'},indent=2))
assert report['occupancy_mismatches']==0, 'Actual crop occupancy differs from model definition'
assert all(r['valid'] for t in tests for r in t['rows']), 'Invalid local section'
