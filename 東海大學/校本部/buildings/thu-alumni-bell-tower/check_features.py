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
design=json.loads((A/'qa/design-features.json').read_text());slabs=design['slab_centers_mm'];zt=slabs[-1];zb=slabs[-2]
for x in [-10,10]:tests.append(local('two deep wall blades',[x-2,-6,3],[4,12,149],[10,60,120,150]))
for z in slabs:tests.append(local('eleven deep cross slab',[-6,-6,z-1.1],[12,12,2.2],[z-.9,z,z+.9]))
for low,high in zip(slabs[:-2],slabs[1:-1]):tests.append(local('nine empty interspaces',[-6,-5,low+1.2],[12,10,high-low-2.4],[(low+high)/2],'air'))
tests.append(local('bell bay side open',[-7,-5,zb+1.2],[2,10,zt-zb-2.4],[(zb+zt)/2],'air'))
tests.append(local('bottom tall passage',[-7,-6,3],[14,12,slabs[0]-4.2],[5,15,25],'air'))
tests.append(local('upper wall tips',[-12,-5,zt+1.2],[4,10,152.5-zt-1.2],[145,151]))
tests.append(local('bell annular body',[-5,-5,zt-13.8],[10,10,10],[zt-13.5,zt-12,zt-10,zt-8]))
tests.append(local('strengthened stem',[-1,-1,zt-4],[2,2,3],[zt-3.5,zt-2]))
tests.append(local('clapper',[-1,-1,zt-14.8],[2,2,7],[zt-14.5,zt-14,zt-12]))
tests.append(local('small lower mechanism',[-.7,-.9,zb+1.1],[1.4,1.8,2.9],[zb+1.5,zb+3.5]))
tests.append(local('platform',[-40,-10,0],[80,20,2.5],[.2,1,2.3]))
mesh=trimesh.Trimesh(v,f,process=False);norm=mesh.face_normals;cen=mesh.triangles_center;down=(norm[:,2]<-.70710678)&(cen[:,2]>3.01)
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Raw STL exact-coordinate weld only. Actual mesh crop intersections and unrounded horizontal sections; exact -0.4mm erosion; no thin exemptions.',tests=tests,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),downward_faces_over_45deg_above_base=int(down.sum()),downward_area_mm2=float(mesh.area_faces[down].sum()),slab_thickness_mm=2.2,wall_width_mm=5,thin_warning='Bell annular wall horizontal sections can become thin. Global connected-section erosion can conceal narrow attached details. Retain every failure.',actual_print_tested=False,support_free_certified=False,limitations='Eleven cross slabs, suspended bell, thin annular bell wall and clapper require slicer support/orientation planning. No exhaustive normal wall thickness/strength/FFF simulation; no physical print.')

(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:q for k,q in report.items() if k!='tests'},indent=2))
assert report['occupancy_mismatches']==0, 'Actual crop occupancy differs from model definition'
assert all(r['valid'] for t in tests for r in t['rows']), 'Invalid local section'
