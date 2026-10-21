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
# Front pair of piers checked at their actual rotated centers.
for a in [-105,-75]:
 import math
 x=48*math.cos(math.radians(a));y=48*math.sin(math.radians(a))
 tests.append(local('broad pier '+str(a),[x-1.5,y-1.5,12.2],[3,3,49],[13,27,40,57,61]))
tests.append(local('front lower portal air',[-8,-47.3,13],[16,2,27],[14,27,40],'air'))
tests.append(local('front deep spandrel',[-8,-47.6,41.3],[16,2.4,17],[42,50,58]))
tests.append(local('opaque front clerestory backing',[-8,-47.05,58.6],[16,1.4,4.5],[59,60.5,62.5]))
tests.append(local('inner pavilion air',[-10,-10,13],[20,20,50],[15,35,58,62],'air'))
tests.append(local('shallow central roof shell',[-5,-5,65.5],[10,10,2.0],[65.6,66.5,67.4]))
tests.append(local('outer round eave',[-4,-59.5,63.1],[8,1.0,2],[63.2,64,65]))
tests.append(local('lowest stair tread',[-16,-79.5,0],[32,2,1.1],[.2,.8,1.05]))
tests.append(local('upper stair tread',[-16,-52.2,0],[32,1.2,12],[10.5,11.5]))
tests.append(local('simplified terrain support',[-10,-10,0],[20,20,10],[.2,5,9.9]))
mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>12.21)
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Raw STL exact-coordinate weld only. Actual mesh crop intersections and unrounded horizontal sections; exact -0.4mm erosion; no thin exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),downward_faces_over_45deg_above_base=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),nominal_roof_shell_mm=2.2,nominal_main_pier_mm=[4.8,4.6],nominal_glazing_proxy_mm=1.6,thin_warning='Roof rim endpoints and curved top approach tangencies; finite sections do not certify every feature. Stair vertical rise 1.1mm. Opaque glazing is strengthened display adaptation, not actual window glass.',actual_print_tested=False,support_free_certified=False,limitations='Broad roof underside, 12 lintel spans and cantilever eaves need support/orientation planning in a slicer. Solid terrain proxy uses material and may warp. No exhaustive wall-thickness, strength or FFF simulation; no actual print.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:q for k,q in report.items() if k!='tests'},indent=2))
assert report['occupancy_mismatches']==0, 'Actual crop occupancy differs from model definition'
assert all(r['valid'] for t in tests for r in t['rows']), 'Invalid local section'
