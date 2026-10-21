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
tests.append(local('filled main exterior envelope',[-2,-2,6],[4,4,80],[8,30,50,80]))
tests.append(local('rear wing two storeys',[96,54,6],[4,4,58],[10,40,60]))
tests.append(local('rear terrace open above 3F floor',[94,52,73],[8,8,20],[75,83,90],'air'))
tests.append(local('front raised turret',[82,-21,95],[4,4,16],[96,103,110]))
tests.append(local('front turret wide cap',[104,-20,112],[1.4,2,1.7],[112.2,112.8,113.5]))
tests.append(local('rectilinear canopy',[60,-50,31.8],[8,2,1.1],[32,32.4,32.8]))
tests.append(local('air below front canopy',[60,-51,10],[8,2,15],[12,20,24],'air'))
tests.append(local('rear terrace rim',[121.5,54,67],[3,4,4],[67.5,69,70.5]))
tests.append(local('main roof rim',[-2,49.2,95],[4,2.2,4],[96,97,98]))
tests.append(local('display plinth',[-2,-2,0],[4,4,3],[.2,1.5,2.8]))
mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Raw STL exact-coordinate weld only. Actual mesh crop intersections and unrounded horizontal sections; exact -0.4mm erosion; no thin exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),downward_faces_over_45deg_above_base=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),nominal_glazing_bar_diameter_mm=1.24,nominal_balcony_wall_mm=1.15,minimum_local_crop_can_be_narrower_than_feature=True,thin_warning='Horizontal sections can become thin near arc stair treads, curved mullions and bracket ends. Global connected-section erosion can conceal narrow attached details. Retain every failure.',actual_print_tested=False,support_free_certified=False,limitations='Broad roof soffits, canopy, stair treads, balcony ledges and circular cap require slicer support/orientation planning. No exhaustive normal wall thickness/strength/FFF simulation; no physical print.')

(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:q for k,q in report.items() if k!='tests'},indent=2))
assert report['occupancy_mismatches']==0, 'Actual crop occupancy differs from model definition'
assert all(r['valid'] for t in tests for r in t['rows']), 'Invalid local section'
