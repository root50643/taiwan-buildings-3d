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
# Three parallel visual profiles reach one common top, separated by backed grooves.
for i,(low,high) in enumerate([(-7.5,-3.1),(-1.9,1.9),(3.1,7.5)]):
 tests.append(local('equal-height profile %d top'%(i+1),[12,low,150],[4,high-low,3],[150.2,152,152.999]))
for x in [-1,1]:
 for y in [-2.5,2.5]:
  # Slightly inset into known empty groove, never cut across its closed back.
  tests.append(local('return groove air x%s y%s'%(x,y),[15.7 if x==1 else -16.4,y-.5,10],[.7,1,130],[20,75,120],'air'))
  tests.append(local('solid backing behind groove x%s y%s'%(x,y),[13.5 if x==1 else -15.5,y-.5,10],[2,1,130],[20,75,120]))
# Isolate exposed front lip from main core; global body thickness must not mask it.
for z in [47,49.1,96,98.1,143,145.1]:
 tests.append(local('molding isolated front projection z%s'%z,[-10,-8.3,z],[20,.8,1.1],[z+.1,z+.55,z+1]))
# Empty gaps are real, but only beyond body face; filled center is intended.
for z in [48.1,97.1,144.1]:
 tests.append(local('paired band external gap z%s'%z,[-10,-8.2,z+.1],[20,.6,.8],[z+.2,z+.5,z+.8],'air'))
tests.append(local('artificial display base',[-20,-14,0],[40,28,3],[.2,1.5,2.9]))
mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Raw STL exact-coordinate weld only. Intersection crops of exported mesh, unrounded horizontal sections, exact -0.4mm geometric erosion, no thin-feature exemptions. Crops isolate molding projection rather than including thick main body.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),downward_faces_over_45deg_above_base=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),nominal_molding_projection_mm=.8,nominal_molding_height_mm=1.1,nominal_molding_clear_gap_mm=1,nominal_groove_width_mm=1.2,nominal_groove_depth_mm=.9,marginal_width_warning='Molding projection is nominally exactly 0.8mm: zero process allowance. Exact crop erosion may collapse even though the attached solid lip is not an independent wall. Do not treat whole-body slice survival as all-feature minimum-width proof.',actual_print_tested=False,support_free_certified=False,limitations='Tall slender 150mm pillar above added base; tipping/adhesion and horizontal band underside support/orientation need target-slicer checks. Groove air/backing samples check approximation only, not real hidden connections. Finite crops are not exhaustive minimum-wall analysis, strength testing or FFF simulation; no physical print.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:q for k,q in report.items() if k!='tests'},indent=2))
assert report['occupancy_mismatches']==0, 'Actual crop occupancy differs from model definition'
assert all(r['valid'] for t in tests for r in t['rows']), 'Invalid local section'
