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
import math
for a in [22.5,67.5,112.5,157.5,202.5,247.5,292.5,337.5]:
 x=46.5*math.cos(math.radians(a));y=46.5*math.sin(math.radians(a))
 tests.append(local('round column '+str(a),[x-2,y-2,12.5],[4,4,58],[14,30,50,65,68,70]))
ap=46.5*math.cos(math.pi/8)
tests.append(local('front pierced parapet opening',[7,-ap-.8,15.4],[3,1.6,5],[16.5,18,19.5],'air'))
tests.append(local('front parapet central web',[-1,-ap-1.2,12.5],[2,2.4,11],[13,16,20,23]))
tests.append(local('front parapet upper rail',[-14,-ap-1.7,22.8],[28,3.4,1.4],[23,24]))
tests.append(local('opposed bridge entry air',[ap-1,-6,13],[2,12,50],[14,24,45,62],'air'))
tests.append(local('central open interior',[-8,-8,13],[16,16,53],[15,30,50,65],'air'))
tests.append(local('front upper beam',[-7,-ap-2.8,70.5],[14,5.6,9.5],[71,74,77,79]))
tests.append(local('center roof shell',[-1,-1,99.8],[2,2,3],[100.2,101,102]))
tests.append(local('finial neck',[-1,-1,112.8],[2,2,2.4],[113,114,114.8]))
tests.append(local('roof tile end tangency',[-1.7,-58.3,78],[3.4,3.4,4],[81.1,81.2,81.3]))
tests.append(local('immediate platform',[-12,-12,8.4],[24,24,3.8],[9,10,12]))
tests.append(local('display support continuation',[-12,-12,0],[24,24,8],[.2,4,7.9]))
mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>12.41)
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Raw STL exact-coordinate weld only. Actual mesh crop intersections and unrounded horizontal sections; exact -0.4mm erosion; no thin exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),downward_faces_over_45deg_above_base=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),nominal_roof_vertical_shell_mm=3.2,nominal_round_shaft_diameter_mm=7.4,nominal_parapet_mm=3.3,thin_warning='Curved roof/rib/bead tangencies are submillimeter at endpoints. Finial and pierced rail bridges require slicer review; finite crops do not certify every feature.',actual_print_tested=False,support_free_certified=False,limitations='Large overhead roof, eight beam spans, finial bulb and eave cantilevers require support/orientation planning. Single-shell display model, not certified print-ready; no actual print or exhaustive wall-thickness/strength simulation.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:q for k,q in report.items() if k!='tests'},indent=2))
assert report['occupancy_mismatches']==0, 'Actual crop occupancy differs from model definition'
assert all(r['valid'] for t in tests for r in t['rows']), 'Invalid local section'
