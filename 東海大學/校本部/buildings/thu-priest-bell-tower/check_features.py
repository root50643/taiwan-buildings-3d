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
for x in [-23,23]:
 for y in [-15,15]:tests.append(local('thick wall '+str((x,y)),[x-4,y-10,3],[8,20,120],[4,40,80,122]))
 tests.append(local('side slit '+str(x),[x-4,-1.5,4],[8,3,76],[5,40,79],'air'))
 tests.append(local('bearing block '+str(x),[x-5,-3,85],[10,6,10],[85.2,90,94.8]))
 tests.append(local('tile shallow relief '+str(x),[x+5.02,-20,10],[.42,5,105],[20,40,60,110]))
tests.append(local('central passage',[-15,-20,4],[30,40,70],[5,35,70],'air'))
tests.append(local('bell mouth rim',[13.5,-1,79.5],[2,2,4],[79.7,80,80.5]))
tests.append(local('clapper',[-3,-3,76],[6,6,16],[76.2,78,79.8,84,90]))
tests.append(local('axle',[16,-2,90],[2,4,4],[90.5,92,93.5]))
tests.append(local('yoke crown',[-4,-2,103],[8,4,5],[103.3,104,105,106.7]))
tests.append(local('artificial paving',[-10,-10,0],[20,20,3.5],[.2,2,3.4]))
mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Raw STL exact-coordinate weld only. Actual mesh crop intersections and unrounded horizontal sections; exact -0.4mm erosion; no thin exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),downward_faces_over_45deg_above_base=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),nominal_wall_thickness_mm=10,nominal_tile_relief_mm=.45,thin_warning='Shallow diamond relief and curved hardware/rim extrema may fail 0.8mm erosion; retain all failures. Sample crops are not exhaustive normal wall-thickness tests.',actual_print_tested=False,support_free_certified=False,limitations='Bell mouth, clapper, axle, bearing blocks and curved yoke need slicer support/orientation planning. Paving is simplified. No strength or actual print test.')

(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:q for k,q in report.items() if k!='tests'},indent=2))
assert report['occupancy_mismatches']==0, 'Actual crop occupancy differs from model definition'
assert all(r['valid'] for t in tests for r in t['rows']), 'Invalid local section'
