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
for sign in [-1,1]:
 x=sign*48;y=-sign*39
 tests.append(local('flared low support '+str(sign),[x-2,y-2,3],[4,4,26],[4,12,20,24]))
 tests.append(local('raised free tip '+str(sign),[sign*54-1 if sign>0 else -55,sign*44-1 if sign>0 else -45,80],[2,2,5],[82,83,83.8,84.2,84.59]))
tests.append(local('continuous central shell',[-2,-2,48],[4,4,5],[49.2,50,51]))
tests.append(local('inset edge rib',[48,-2,42],[2,4,12],[45,46,48]))
tests.append(local('front opening air',[-10,-30,4],[20,10,20],[5,12,22],'air'))
tests.append(local('rear opening air',[-10,20,4],[20,10,20],[5,12,22],'air'))
tests.append(local('table top',[-6,-4,12],[12,8,2],[12.2,13,13.8]))
tests.append(local('table horizontal slot',[-10,-3,10.6],[2,6,1.3],[10.8,11.2,11.8],'air'))
tests.append(local('artificial display base',[-10,-10,0],[20,20,3],[.2,1.5,2.8]))
mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Raw STL exact-coordinate weld only. Actual mesh crop intersections and unrounded horizontal sections; exact -0.4mm erosion; no thin exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),downward_faces_over_45deg_above_base=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),nominal_vertical_shell_mm=2.6,nominal_inset_rib_width_mm=3.4,nominal_inset_rib_depth_mm=5.2,thin_warning='Free high tips terminate tangentially. Global and local 0.8mm erosion failures are retained. Vertical shell thickness is not the true minimum normal wall thickness.',actual_print_tested=False,support_free_certified=False,limitations='Broad continuous saddle soffit and cantilever high corners need slicer support/orientation planning. Display base bridges two supports and is not surveyed paving. No exhaustive normal wall-thickness, strength or FFF simulation; no actual print.')

(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:q for k,q in report.items() if k!='tests'},indent=2))
assert report['occupancy_mismatches']==0, 'Actual crop occupancy differs from model definition'
assert all(r['valid'] for t in tests for r in t['rows']), 'Invalid local section'
