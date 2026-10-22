"""Raw-STL occupancy/thickness audits, not a printability certificate.
All positive components retained. Local crops are explicitly bounded samples,
not a proof of minimum wall thickness everywhere. No repairs or exemptions.
"""
from pathlib import Path
import hashlib,json
import numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection,Point
from qa_model import raw_read
A=Path(__file__).resolve().parent;_,v,f=raw_read(A/'model.stl');mesh=trimesh.Trimesh(v,f,process=False)
m=md.Manifold(md.Mesh(np.asarray(v,dtype=np.float32),np.asarray(f,dtype=np.uint32)))
features=json.loads((A/'qa/design-features.json').read_text());fm=json.loads((A/'mesh.json').read_text());materials=np.asarray(fm['face_materials']);palette=json.loads((A/'palette.json').read_text())['materials']
assert np.array_equal(np.asarray(fm['vertices'])[np.asarray(fm['faces'])],v[f])
def audit_crop(name,crop,levels,expected='solid',description=None,note=''):
 rows=[]
 for z in levels:
  geom=GeometryCollection();invalid=0
  for contour in crop.slice(float(z)).to_polygons():
   if len(contour)<3:continue
   p=Polygon(contour);invalid+=not p.is_valid;geom=geom.symmetric_difference(p)
  polys=list(geom.geoms) if geom.geom_type=='MultiPolygon' else ([] if geom.is_empty else [geom]);eroded=[p.buffer(-.4,quad_segs=16) for p in polys]
  rows.append(dict(plane_mm=float(z),components=len(polys),valid=bool(geom.is_valid and not invalid),area_mm2=float(geom.area),component_areas_mm2=[float(p.area) for p in polys],component_bounds_mm=[list(p.bounds) for p in polys],failed_0_8mm=sum(p.is_empty for p in eroded),expected_occupancy_met=(not polys if expected=='air' else bool(polys))))
 vol=float(crop.volume());return dict(feature=name,description=description,expected=expected,crop_intersection_volume_mm3=vol,air_volume_is_zero=bool(vol==0) if expected=='air' else None,note=note,rows=rows)
def local(name,origin,size,levels,expected='solid',note=''):
 return audit_crop(name,m^md.Manifold.cube(size).translate(origin),levels,expected,dict(origin_mm=origin,size_mm=size),note)
width=lambda x:28+x/12
roof=lambda x:108.25+69.5*x/168
T=[];rays=[]
for s in [-1,1]:
 for i,x in enumerate(features['ground_column_x_mm']):
  y=s*width(x);T.append(local(f'ground_column_{s}_{i}',[x-1.5,y-1.5,20],[3,3,35],[20.1,37,54.9]))
  T.append(local(f'footing_{s}_{i}',[x-3,y-3,.1],[6,6,4.8],[.2,2.5,4.8]))
 # Broad open bays below horizontal frame, not walls.
 for x in [-40,48]:T.append(local(f'open_side_bay_{s}_{x}',[x-4,s*width(x)-4,20],[8,8,40],[20.1,40,59.9],'air'))
for x in [-85,82]:T.append(local(f'open_short_end_{x}',[x-1,-12,20],[2,24,40],[20.1,40,59.9],'air'))
for x in [-60,-20,40,65]:T.append(local(f'underdeck_air_{x}',[x-3,-9,.1],[6,18,9],[.2,4,9],'air'))
T.append(local('taper_narrow_side_outside_deck',[-72,28,11.1],[4,4,2.3],[11.2,12,13.3],'air'))
T.append(local('taper_broad_deck_at_same_y',[68,28,11.1],[4,4,2.3],[11.2,12,13.3]))
T.append(local('oblique_connection_panel',[-113,-5,11.1],[3,6,2.1],[11.2,12,13.1]))
T.append(local('outside_slanted_connection_cut',[-122,16,11.1],[3,3,2],[11.2,12,13],'air'))
for i,(x,z) in enumerate([(102,1.5),(97,4.5),(92,7.5),(89,10.5)]):T.append(local(f'high_end_step_{i}',[x-1,-5,z-.5],[2,10,1],[z-.4,z,z+.4]))
# Inverted triangular timber web holes. Crop centre follows the same convergent plane.
U=np.asarray(features['truss_upper_nodes']);L=np.asarray(features['truss_lower_nodes'])
for s in [-1,1]:
 for i in [1,2,4,5]:
  pts=[U[i],U[i+1],L[i]] if i<3 else [U[i-1],U[i],L[i]]
  p=np.mean(pts,axis=0);x,z=map(float,p);y=s*width(x)
  T.append(local(f'truss_{s}_triangular_opening_{i}',[x-.5,y-.5,z-.5],[1,1,1],[z-.4,z,z+.4],'air'))
# Roof-normal rays: one deliberate transverse-rib sample plus five sheet-only samples.
slope=69.5/168;normal=np.array([-slope,0,1]);normal/=np.linalg.norm(normal)
for x,y in [(-72,8),(-65,7),(-43,-8),(7,7),(41,-9),(70,11)]:
 p=np.array([x,y,roof(x)+.45]);origin=p-normal*4
 locations,_,_=mesh.ray.intersects_location([origin],[normal],multiple_hits=True);vals=np.sort((locations-origin)@normal)
 assert len(vals)%2==0
 intervals=[[float(a),float(b)] for a,b in zip(vals[::2],vals[1::2])];hit=[ab for ab in intervals if ab[0]<4<ab[1]];assert len(hit)==1
 thick=hit[0][1]-hit[0][0];rays.append(dict(feature=f'roof_normal_{x}_{y}',intersects_transverse_grid_rib=(x==-72),origin_mm=origin.tolist(),direction=normal.tolist(),all_solid_intervals_mm=intervals,thickness_mm=thick,nominal_mm=.9/(1+slope*slope)**.5,below_0_8mm=thick<.8))
 # Rotate plane so roof normal is local Z; examine actual finite patch around ray.
 xx=np.array([0.,1.,0.]);yy=np.cross(normal,xx);R=np.vstack([xx,yy,normal]);oriented=m.transform(np.column_stack([R,-R@p]))
 crop=oriented^md.Manifold.cube((3,3,2)).translate((-1.5,-1.5,-1))
 T.append(audit_crop(f'roof_normal_patch_{x}_{y}',crop,[-.3,0,.3],description=dict(world_center=p.tolist(),normal=normal.tolist(),local_crop_size=[3,3,2])))
# Cross-sections normal to representative narrow diagonal wood members.
for member in features['timber_members']:
 if 'diagonal_web' not in member['name']:continue
 a=np.array(member['a']);b=np.array(member['b']);d=(b-a)/np.linalg.norm(b-a);p=(a+b)/2
 q=np.array([0.,0.,1.]);xx=np.cross(q,d);xx/=np.linalg.norm(xx);yy=np.cross(d,xx);R=np.vstack([xx,yy,d]);oriented=m.transform(np.column_stack([R,-R@p]));crop=oriented^md.Manifold.cube((4,4,2)).translate((-2,-2,-1))
 T.append(audit_crop(member['name']+'_normal',crop,[-.8,0,.8],description=dict(world_center=p.tolist(),axis=d.tolist(),local_crop_size=[4,4,2])))
# Thin sign stroke, bolt and drain local samples are not waived.
T.append(local('sign_front_and_metal_back_stroke',[38.5,-35.5,88.5],[3,4,1],[88.6,89,89.4],note='Tiny cropped sign fragments count even if an adjacent thicker member exists.'))
T.append(local('drain_pipe',[-84.7,22.3,25],[1.4,1.4,3],[25.1,26.5,27.9]))
T.append(local('under_roof_mid_void',[-2,-5,90],[4,10,10],[90.1,95,99.9],'air'))
centers=mesh.triangles_center;mask=(mesh.face_normals[:,2]<-np.sqrt(.5))&(centers[:,2]>.0001)
solid=[r for t in T if t['expected']=='solid' for r in t['rows']];air=[r for t in T if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest(),method='Raw STL exact welding; finite-volume actual-mesh occupancy intersections, even-odd local slices with all components and -0.4mm erosion; actual roof-normal rays (one grid-rib sample distinguished from five sheet-only samples). No repairs or thin exemptions.',tests=T,solid_samples=len(solid),air_samples=len(air),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in T for r in t['rows']),air_volume_mismatches=sum(not t['air_volume_is_zero'] for t in T if t['expected']=='air'),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solid),failed_0_8mm_components=sum(r['failed_0_8mm'] for r in solid),roof_normal_ray_checks=rays,axis_thickness_below_0_8mm_samples=sum(r['below_0_8mm'] for r in rays),downward_faces_over_45deg_above_base=int(mask.sum()),downward_area_mm2=float(mesh.area_faces[mask].sum()),overhang_by_material={p['id']:dict(triangles=int((mask&(materials==i)).sum()),area_mm2=float(mesh.area_faces[mask&(materials==i)].sum())) for i,p in enumerate(palette)},thin_warning='0.83mm normal PC sheet, sign strokes, bolts, drain and grazing sections remain fragile. Elevated deck, roof, beams and truss webs require support planning; translucent display alpha does not alter solid STL.',actual_print_tested=False,support_free_certified=False,limitations='Finite samples only, not a global minimum thickness/strength/bridge-span/slicer/support-removal or physical-print certification.')
(A/'qa/local-features.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['tests','roof_normal_ray_checks']},indent=2))
assert report['occupancy_mismatches']==0 and report['air_volume_mismatches']==0,[(t['feature'],t['expected']) for t in T if any(not r['expected_occupancy_met'] for r in t['rows'])]
assert all(r['valid'] for t in T for r in t['rows'])
assert all((r['thickness_mm']>=r['nominal_mm'] if r['intersects_transverse_grid_rib'] else abs(r['thickness_mm']-r['nominal_mm'])<.002) for r in rays)
