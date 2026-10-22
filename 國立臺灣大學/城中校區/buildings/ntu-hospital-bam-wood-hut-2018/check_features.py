"""Bounded raw-STL checks for NTUH 2018 Bam-Wood Hut.
Exact coordinate welding only. No mesh repairs, contour rounding, island deletion
or thin-feature exemptions. These samples are not a global normal-thickness proof.
"""
from pathlib import Path
import hashlib,json
import numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,GeometryCollection,Point
from qa_model import raw_read
A=Path(__file__).resolve().parent
raw_hash=hashlib.sha256((A/'model.stl').read_bytes()).hexdigest()
_,v,f=raw_read(A/'model.stl')
mesh=trimesh.Trimesh(v,f,process=False)
assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
m=md.Manifold(md.Mesh(np.asarray(v,dtype=np.float32),np.asarray(f,dtype=np.uint32)))
assert m.status().name=='NoError'
features=json.loads((A/'qa/design-features.json').read_text())
fm=json.loads((A/'mesh.json').read_text())
assert np.array_equal(np.asarray(fm['vertices'])[np.asarray(fm['faces'])],v[f]),'Material manifest geometry mismatch'
materials=np.asarray(fm['face_materials']);palette=json.loads((A/'palette.json').read_text())['materials']
assert len(materials)==len(f)

def audit_crop(name,crop,levels,expected='solid',note='',description=None,reference_xy=None):
 rows=[]
 for z in levels:
  geom=GeometryCollection();invalid=0
  for contour in crop.slice(float(z)).to_polygons():
   if len(contour)<3:continue
   p=Polygon(contour);invalid+=not p.is_valid;geom=geom.symmetric_difference(p)
  polys=list(geom.geoms) if geom.geom_type=='MultiPolygon' else ([] if geom.is_empty else [geom])
  eroded=[p.buffer(-.4,quad_segs=16) for p in polys]
  row=dict(plane_mm=float(z),components=len(polys),valid=bool(geom.is_valid and invalid==0),area_mm2=float(geom.area),component_areas_mm2=[float(p.area) for p in polys],component_bounds_mm=[list(p.bounds) for p in polys],failed_0_8mm=sum(p.is_empty for p in eroded),eroded_areas_mm2=[float(p.area) for p in eroded],expected_occupancy_met=(not polys if expected=='air' else bool(polys)))
  if reference_xy is not None:
   indices=[i for i,p in enumerate(polys) if p.covers(Point(*reference_xy))]
   row.update(target_axis_component_count=len(indices),target_axis_component_failed_0_8mm=sum(eroded[i].is_empty for i in indices),off_axis_component_count=len(polys)-len(indices))
  rows.append(row)
 volume=float(crop.volume())
 return dict(feature=name,description=description or {},expected=expected,crop_intersection_volume_mm3=volume,air_volume_is_zero=bool(volume==0) if expected=='air' else None,note=note,rows=rows)

def local(name,origin,size,levels,expected='solid',note='',reference_xy=None):
 crop=m ^ md.Manifold.cube(size).translate(origin)
 return audit_crop(name,crop,levels,expected,note,dict(shape='axis-aligned box',origin_mm=origin,size_mm=size),reference_xy)

tests=[];frames=features['frames'];assert len(frames)==20 and features['bay_count']==19
# Every post row is tested in the raw STL, preserving adjacent bamboo fragments.
for fr in frames:
 for k,p in enumerate(fr['posts']):
  x,y,z=p
  tests.append(local(f"timber post {fr['number']:02} side {k+1}",[x-1.05,y-.65,7],[2.1,1.3,14],[7.1,11,16,20.9],reference_xy=[x,y],note='Complete post width and depth with all adjacent bamboo/shoe fragments retained. Nominal strengthened section1.8×1.0mm; not real measured timber.'))
# Actual local intersections, not expected primitive-only tests. Tangent sections
# remain in the results and are not excluded when they fail the .8mm core test.
def auto_patch(name,origin,size,note):
 crop=m ^ md.Manifold.cube(size).translate(origin)
 cv=np.asarray(crop.to_mesh64().vert_properties)[:,:3];assert len(cv),name
 lo,hi=float(cv[:,2].min()),float(cv[:,2].max());dz=hi-lo
 tests.append(audit_crop(name,crop,[lo+.001,lo+dz*.15,lo+dz*.5,hi-dz*.15,hi-.001],note=note,description=dict(shape='axis-aligned box',origin_mm=origin,size_mm=size,actual_solid_z_bounds_mm=[lo,hi])))
for fi in [0,9,19]:
 fr=frames[fi]
 for k,(a,b) in enumerate(zip(fr['bamboo_nodes'],fr['bamboo_nodes'][1:])):
  q=(np.array(a)+np.array(b))/2
  auto_patch(f'bamboo frame{fi+1} segment{k+1}',(q-[1.5,.6,1.6]).tolist(),[3,1.2,3.2],'Entire local bamboo diameter around segment midpoint, including any steel/other surfaces entering the crop. Near tangent slices deliberately retained; horizontal erosion is not normal rod diameter.')
 for k,n in enumerate(fr['bamboo_nodes'][1:-1],1):
  roof=fr['roof'];x,y,z=n;l,ridge,r=roof
  rz=l[2]+(ridge[2]-l[2])*(x-l[0])/(ridge[0]-l[0]) if x<=ridge[0] else ridge[2]+(r[2]-ridge[2])*(x-ridge[0])/(r[0]-ridge[0])
  q=np.array([x,y,(rz+z)/2])
  auto_patch(f'steel stand-off frame{fi+1} node{k}',(q-[.8,.85,.7]).tolist(),[1.6,1.7,1.4],'Strengthened .55×.65mm paired galvanized support; this is intentionally below .8mm in one normal direction. All failed erosion cores are real warnings, not exemptions.')
# Six roof patches away from timber support planes. Alpha does not create air.
for bi in [0,9,18]:
 a,b=frames[bi:bi+2];y=(a['y']+b['y'])/2
 for side in [0,1]:
  p=(np.array(a['roof'][side])+np.array(a['roof'][side+1])+np.array(b['roof'][side])+np.array(b['roof'][side+1]))/4
  auto_patch(f'polycarbonate bay{bi+1} slope{side+1}',[p[0]-2,y-1.7,p[2]-.1],[4,3.4,3.2],'Physical translucent roof sheet, nominal .78mm vertical thickness; sloped tangent slices and trim intersections retained. This is solid in STL, NOT an open roof gap.')
# True negative spaces: all are full-volume intersections, not just sample rays.
tests.append(local('continuous clear tunnel core',[-13,-89,4],[26,178,19],[4.1,9,15,22.9],'air',note='Conservative through-passage under bamboo, both ends open. No side/end walls or solid tunnel core may fill this volume.'))
for side in [-1,1]:
 tests.append(local(f'open long side waist {side}',[35 if side==1 else -45,-12,5],[10,24,19],[5.1,12,20,23.9],'air',note='Conservative long-side air beyond the narrowed middle post row and below eave; full-volume occupancy must be zero.'))
for y,name in [(-89,'front'),(87,'rear')]:
 tests.append(local(f'open {name} end',[-29,y,4],[58,2,19],[4.1,10,16,22.9],'air',note='Core of open gable end below segmented bamboo. Not a full gable triangle, which contains real braces and remains unfilled elsewhere.'))
# The roof-to-bamboo cavity is sampled only at a proven safe centre node bay.
fr=frames[9];y=fr['y']
tests.append(local('gap between rafters and inner bamboo',[0,y-.8,39.1],[2,1.6,.45],[39.15,39.3,39.5],'air',note='Conservative small gap below the rafter underside and above the bamboo at x0–2. An initial z40–41 probe intersected the real rafter and was rejected; corrected probe is z39.1–39.55. No geometry removed. Does not claim entire roof underside is empty.'))
# Raw full-model overhang classification. Not a support-generation estimator.
centers=mesh.triangles_center;mask=(mesh.face_normals[:,2]<-np.sqrt(.5))&(centers[:,2]>3.5001)
by_material={p['id']:dict(triangles=int((mask&(materials==i)).sum()),area_mm2=float(mesh.area_faces[mask&(materials==i)].sum())) for i,p in enumerate(palette)}
solidrows=[r for t in tests if t['expected']=='solid' for r in t['rows']];airrows=[r for t in tests if t['expected']=='air' for r in t['rows']]
report=dict(stl_sha256=raw_hash,method='Raw binary STL exact-coordinate weld only; whole-mesh crop intersections, unrounded sections and even-odd nesting; exact -0.4mm erosion on every positive component. No healing, rounding, island removal or thin exemption.',tests=tests,post_count_tested=40,solid_samples=len(solidrows),air_samples=len(airrows),occupancy_mismatches=sum(not r['expected_occupancy_met'] for t in tests for r in t['rows']),air_volume_mismatches=sum(not t['air_volume_is_zero'] for t in tests if t['expected']=='air'),solid_failed_0_8mm_samples=sum(r['failed_0_8mm']>0 for r in solidrows),failed_0_8mm_components=sum(r['failed_0_8mm'] for r in solidrows),post_axis_failed_0_8mm_samples=sum(r['target_axis_component_failed_0_8mm']>0 for t in tests if t['feature'].startswith('timber post') for r in t['rows']),downward_faces_over_45deg_above_deck=int(mask.sum()),downward_area_mm2=float(mesh.area_faces[mask].sum()),overhang_by_material=by_material,roof_translation='Alpha in Blend/3MF is not geometric air; opaque STL printing gives opaque roof. Roof patches are tested solid. Open sides and passage are tested as full empty volumes.',thin_warning='Steel .55×.65mm and longitudinal bamboo .76mm, roof .78mm, bamboo .86mm tangent slices, fine deck grooves and vent edges retain actual thin warnings. Scaling down can erase them. Horizontal erosion is not global normal thickness proof.',actual_print_tested=False,support_free_certified=False,limitations='Approximate display geometry; no structural, bridge, supports, slicer-linewidth, accessibility or fabrication validation. Downward triangle area is not support material area or volume.')
assert raw_hash==hashlib.sha256((A/'model.stl').read_bytes()).hexdigest()
(A/'qa/local-features.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:q for k,q in report.items() if k!='tests'},ensure_ascii=False,indent=2))
assert report['occupancy_mismatches']==0, 'Expected actual crop occupancy mismatch; diagnose instead of modifying QA'
assert report['air_volume_mismatches']==0,'Expected full air volume contains geometry'
assert all(r['target_axis_component_count']==1 for t in tests if t['feature'].startswith('timber post') for r in t['rows'])
assert all(r['valid'] for t in tests for r in t['rows'])
