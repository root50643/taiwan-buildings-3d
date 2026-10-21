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
for x in [-52,52]:
 for y in [-33,33]:tests.append(local('four substantial corner pillars',[x-2.2,y-1.8,8],[4.4,3.6,42],[10,20,40,49]))
 tests.append(local('stepped panel crown',[x-1.3,-10,46],[2.6,20,7],[47,49,52]))
 tests.append(local('moon gate center remains air',[x-2,-5,7],[4,10,27],[8,15,25,33],'air'))
 for y in [-29,29]:tests.append(local('stepped side negative space',[x-2.5,y-.55,15],[5,1.1,20],[16,25,34],'air'))
 tests.append(local('stepped upper negative space',[x-2.5,-6,54.4],[5,12,1],[54.6,55],'air'))
 tests.append(local('small gable oculus open',[x-2.8,-1,64.5],[5.6,2,3.4],[65,66.2,67.2],'air'))
 tests.append(local('moon rim horizontal crown',[x-1.3,-2,38.6],[2.6,4,3],[39,40]))
for y in [-33,33]:
 tests.append(local('two long sides open',[-45,y-1.5,8],[90,3,32],[10,25,39],'air'))
 tests.append(local('long lintels',[-40,y-2.2,51],[80,4.4,4.3],[52,54]))
for y in [-18,0,18]:tests.append(local('underside roof beams',[-40,y-.9,50],[80,1.8,30],[float(54+25*__import__('math').exp(-(y/19)**2)+4*(abs(y)/43)**8-4)]))
for x in [-63,63]:tests.append(local('white curved fascia apex',[x-1.2,-2,77],[2.4,4,3.4],[78,79.8,80.2]))
tests.append(local('roof shell near eave',[-40,40,54],[80,2,8],[56.3,57.5]))
tests.append(local('integral roof rib high tangent',[-.7,-1,78.7],[1.4,2,1],[79.1,79.4]))
tests.append(local('small plaque panel',[-9,-30.6,44.2],[18,.3,5],[45,48]))
tests.append(local('stepped platform',[-60,-36,0],[120,72,6.8],[.2,2.5,4.8,6.7]))
mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Raw STL exact-coordinate weld only. Actual mesh crop intersections and unrounded horizontal sections; exact -0.4mm erosion; no thin exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),downward_faces_over_45deg_above_base=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),panel_thickness_mm=2.8,roof_vertical_thickness_mm=2.5,thin_warning='Roof ribs, tile relief, near-tangent moon/oculus curves and plaque relief can be sub-0.8mm locally. Global connected-section erosion can conceal narrow attached details. Retain every failure.',actual_print_tested=False,support_free_certified=False,limitations='Broad roof soffit, curved eaves, moon-gate crowns, small oculi, beams and plaque require slicer support/orientation planning. No exhaustive normal wall thickness/strength/FFF simulation; no physical print.')

(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:q for k,q in report.items() if k!='tests'},indent=2))
assert report['occupancy_mismatches']==0, 'Actual crop occupancy differs from model definition'
assert all(r['valid'] for t in tests for r in t['rows']), 'Invalid local section'
