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
for i,(x,y) in enumerate([(19.0919,19.0919),(-19.0919,19.0919),(-19.0919,-19.0919),(19.0919,-19.0919)]):
 tests.append(local('column '+str(i+1),[x-2,y-2,11],[4,4,125],[12,30,70,100,130]))
for z in [48,52,88,92]:tests.append(local('ring rail '+str(z),[25,-2,z-1.3],[4,4,2.6],[z-.8,z,z+.8]))
tests.append(local('reinforced bell suspension',[-2,-2,126.5],[4,4,4],[127,129,130]))
tests.append(local('bell body',[-4,-4,111],[8,8,14],[112,118,124]))
tests.append(local('shallow bell recess',[-3,-3,108],[6,6,2],[109.2,109.8],'air'))
tests.append(local('disc connected waist',[-3,-3,131],[6,6,5],[132,133.5,135]))
tests.append(local('open centre below bell',[-8,-8,11],[16,16,96],[20,50,90,105],'air'))
for a,z in [(47,3),(43,5),(39,7),(32,9)]:tests.append(local('radial tread level '+str(z),[a-.5,-3,z-.2],[1,6,.4],[z]))
for i,(sx,sy) in enumerate([(1,1),(-1,1),(-1,-1),(1,-1)]):
 tests.append(local('upper curved arm '+str(i+1),[5 if sx>0 else -21,5 if sy>0 else -21,138],[16,16,17],[140,148,152,154.8,154.85448400878906]))
for a0 in [0,90,180,270]:
 for da in [-23,23]:
  a=np.radians(a0+da);x,y=32*np.cos(a),32*np.sin(a)
  tests.append(local('rounded stone post '+str(a0+da),[x-5,y-5,11],[10,10,17],[15,23,26]))
tests.append(local('display support',[-3,-3,0],[6,6,2],[.2,1,1.8]))
mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Raw STL exact-coordinate weld only. Actual mesh crop intersections and unrounded horizontal sections; exact -0.4mm erosion; no thin exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),downward_faces_over_45deg_above_base=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),nominal_column_diameter_mm=2.9,nominal_ring_rail_diameter_mm=2.3,minimum_local_crop_can_be_narrower_than_feature=True,thin_warning='Horizontal sections can become thin near curved arm apexes and rounded post tops. Global connected-section erosion can conceal narrow attached details. Retain every failure.',actual_print_tested=False,support_free_certified=False,limitations='Hanging bell, disc underside, brace rings and inward-curving arms require slicer support/orientation planning. Tall narrow rods remain fragile. No exhaustive normal wall thickness/strength/FFF simulation; no physical print.')

(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:q for k,q in report.items() if k!='tests'},indent=2))
assert report['occupancy_mismatches']==0, 'Actual crop occupancy differs from model definition'
assert all(r['valid'] for t in tests for r in t['rows']), 'Invalid local section'
