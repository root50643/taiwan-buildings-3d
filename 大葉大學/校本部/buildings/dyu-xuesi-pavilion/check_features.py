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
 for y in [-48,48]:tests.append(local('square red principal post',[x-2,y-2,7],[4,4,54],[8,25,44,58]))
tests.append(local('open front edge',[-20,-50,6],[40,4,35],[7,16,25,39],'air'))
tests.append(local('side rail upright',[47.2,-16.8,7],[1.6,1.6,18],[8,17,24]))
tests.append(local('rail opening',[47.3,-13,21],[1.4,8,3],[21.2,22,23.5],'air'))
tests.append(local('side bench top',[36,-7,13],[6,14,2.4],[13.2,14,15.2]))
tests.append(local('front bench undercroft',[-6,-35,6],[12,6,6],[7,10,12],'air'))
tests.append(local('stone pedestal',[-10,-3,6],[20,14,13],[7,12,18]))
tests.append(local('thick stone cap',[-15,-5,20],[30,18,11],[20.2,25,30.8]))
tests.append(local('lower red beam',[-8,-49,46],[16,2,3],[46.2,47,48.8]))
tests.append(local('upper red beam',[-8,-49,60],[16,2,7],[60.2,63,66.8]))
tests.append(local('roof slope',[20,-30,75],[4,3,8],[76,77,78]))
tests.append(local('opaque backed square hood',[-4,-4,91],[8,8,10],[92,96,100]))
tests.append(local('hood peak',[-1,-1,105],[2,2,2],[105.2,106,106.99]))
tests.append(local('display ground',[-10,-10,0],[20,20,2.5],[.2,1.5,2.4]))
mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Raw STL exact-coordinate weld only. Actual mesh crop intersections and unrounded horizontal sections; exact -0.4mm erosion; no thin exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),downward_faces_over_45deg_above_base=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),nominal_rail_width_mm=1.6,roof_nominal_vertical_thickness_mm=2.8,thin_warning='Horizontal sections can become thin near roof seams and hood peak. Global connected-section erosion can conceal narrow attached details. Retain every failure.',actual_print_tested=False,support_free_certified=False,limitations='Broad roof soffit, benches, lintels, horizontal rail crossbars and overhangs require slicer support/orientation planning. No exhaustive normal wall thickness/strength/FFF simulation; no physical print.')

(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:q for k,q in report.items() if k!='tests'},indent=2))
assert report['occupancy_mismatches']==0, 'Actual crop occupancy differs from model definition'
assert all(r['valid'] for t in tests for r in t['rows']), 'Invalid local section'
