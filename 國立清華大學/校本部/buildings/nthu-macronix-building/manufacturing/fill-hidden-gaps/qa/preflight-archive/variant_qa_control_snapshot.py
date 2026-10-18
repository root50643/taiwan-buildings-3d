"""Read-only QA of the deliberately limited manufacturing variant.

All source-ray coordinates and heights are retained. Additional lines are
identified by fixed generator parameters, never substituted for old samples.
No mesh repairs, slicing, supports or print tests are performed.
"""
from pathlib import Path
import argparse, hashlib, json, math, platform, collections, time
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh64
from shapely.geometry import Polygon, LineString, box as box2
from shapely import wkt

ORIGINAL_SHA='00f6bbdd09196fba873d843bb9d50a1c3aad4e19e760978333dce6f49740627c'
GENERATOR_SHA='cff21ed128f2fa72d540e5894dc884f3a25db76c7657645477cf90a18bb5b66b'
BASE=Path(__file__).resolve().parent.parent
P=next((BASE/'candidate-repo').glob('*/**/nthu-macronix-building'))
VOLUME_TOL=1e-6
LINE_TOL=1e-5

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
 raw=p.read_bytes();n=int.from_bytes(raw[80:84],'little')
 if len(raw)!=84+50*n:raise ValueError('Not a supported binary STL.')
 rec=np.frombuffer(raw,offset=84,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]))
 tri=rec['v'].astype(float);verts,inv=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True);faces=inv.reshape(-1,3)
 mesh=trimesh.Trimesh(verts,faces,process=False)
 solid=Manifold(Mesh64(np.ascontiguousarray(verts),np.ascontiguousarray(faces,dtype=np.uint64)))
 return dict(path=p,sha=hashlib.sha256(raw).hexdigest(),raw=raw,tri=tri,verts=verts,faces=faces,mesh=mesh,solid=solid)
def solidstats(s):
 return dict(status=str(s.status()),empty=bool(s.is_empty()),volume_mm3=float(s.volume()),bounds_mm=None if s.is_empty() else list(s.bounding_box()),component_count=len(s.decompose()))
def metadata(a):
 m=a['mesh'];f=a['faces'];edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);uniq,cnt=np.unique(edges,axis=0,return_counts=True)
 return dict(stl_sha256=a['sha'],bytes=len(a['raw']),triangle_count=len(f),exact_vertex_count=len(a['verts']),exact_edge_count=len(uniq),edge_incidence_histogram={str(k):int((cnt==k).sum()) for k in np.unique(cnt)},watertight=bool(m.is_watertight),winding_consistent=bool(m.is_winding_consistent),signed_volume_mm3=float(m.volume),surface_area_mm2=float(m.area),bounds_mm=m.bounds.tolist(),manifold=solidstats(a['solid']))
def cube_bounds(lo,hi):return Manifold.cube(tuple(np.array(hi)-lo)).translate(tuple(lo))
def rotation(ang):
 t=math.radians(ang);return np.array([[math.cos(t),-math.sin(t),0],[math.sin(t),math.cos(t),0],[0,0,1.]])
def full_line(a,origin,direction):
 """All signed triangle intersections; no origin displacement or resampling."""
 o=np.asarray(origin,float);d=np.asarray(direction,float);tri=a['tri'];e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
 p=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,p);valid=np.abs(det)>1e-12
 inv=np.zeros_like(det);inv[valid]=1/det[valid];tv=o-tri[:,0];u=np.einsum('ij,ij->i',tv,p)*inv;q=np.cross(tv,e1);v=q@d*inv;t=np.einsum('ij,ij->i',e2,q)*inv
 valid&=(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)
 ids=np.where(valid)[0];ids=ids[np.argsort(t[ids])];hits=[]
 for i in ids:
  if hits and abs(t[i]-hits[-1]['t_mm'])<=1e-7:hits[-1]['faces'].append(int(i))
  else:hits.append(dict(t_mm=float(t[i]),faces=[int(i)]))
 return dict(global_origin_mm=o.tolist(),global_direction=d.tolist(),intersection_count=len(hits),even_hit_count=len(hits)%2==0,hits=hits,solid_intervals_mm=[[hits[i]['t_mm'],hits[i+1]['t_mm']] for i in range(0,len(hits)-1,2)])
def line_compare(a,b,origin,direction,source):
 x,y=full_line(a,origin,direction),full_line(b,origin,direction)
 same=len(x['hits'])==len(y['hits']) and all(abs(p['t_mm']-q['t_mm'])<=LINE_TOL for p,q in zip(x['hits'],y['hits']))
 return dict(source=source,original=x,variant=y,equal_within_1e_5_mm=same)
def filled_between(result,lo,hi):
 return any(a<=lo+LINE_TOL and b>=hi-LINE_TOL for a,b in result['solid_intervals_mm'])
def section(a,z):
 contours=a['solid'].slice(float(z)).to_polygons();region=Polygon();good=True
 for c in contours:
  p=Polygon(np.asarray(c));good&=p.is_valid;region=region.symmetric_difference(p)
 if not good or not region.is_valid:raise ValueError('Invalid slice; no repair used.')
 return region
def cropdelta(a,b,planes):
 for normal,offset in planes:a,b=a.trim_by_plane(normal,offset),b.trim_by_plane(normal,offset)
 add,remove=b-a,a-b
 return dict(halfspaces=[dict(normal=n,offset_mm=d) for n,d in planes],original=solidstats(a),variant=solidstats(b),added=solidstats(add),removed=solidstats(remove),symmetric_difference_volume_mm3=float(add.volume()+remove.volume()),equal_within_1e_6_mm3=bool(add.volume()+remove.volume()<=VOLUME_TOL))
def source_ray_tree(node,prefix=''):
 if isinstance(node,dict):
  if all(k in node for k in ('origin','direction','hits')):yield prefix,node
  else:
   for k,v in node.items():yield from source_ray_tree(v,prefix+'/'+k)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--variant',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();start=time.monotonic()
 if args.output.exists():raise FileExistsError('Evidence exists; refusing overwrite.')
 assert sha(P/'build_model.py')==GENERATOR_SHA
 a,b=load(P/'model.stl'),load(args.variant);assert a['sha']==ORIGINAL_SHA
 assert all(str(x['solid'].status())=='Error.NoError' for x in (a,b))
 added=b['solid']-a['solid'];removed=a['solid']-b['solid'];fillers=[]
 for x in [37,43,49,55]:
  for z in [25,34,43]:
   lo=[x-.5,-20.95,z];hi=[x+.5,-19.05,z+7];s=cube_bounds(lo,hi)
   fillers.append((dict(id=f'fin_{x}_z{z}',frame='global XYZ',min_mm=lo,max_mm=hi),s))
 for center,ang in [(-30,-14),(30,14)]:
  for z in [18,29,40,51]:
   lo=[-32,-9.81,z];hi=[32,-9.70,z+.1];s=cube_bounds(lo,hi).rotate((0,0,ang)).translate((center,30,0))
   fillers.append((dict(id=f'rear_{center}_z{z}',frame='local XYZ, rotate Z then translate',local_min_mm=lo,local_max_mm=hi,rotation_Z_deg=ang,global_translation_mm=[center,30,0]),s))
 union=Manifold.batch_boolean([x[1] for x in fillers],__import__('manifold3d').OpType.Add)
 ledger=[]
 for params,s in fillers:
  old_air=s-a['solid'];actual=added^s
  ledger.append(dict(source_parameters=params,raw_fill=solidstats(s),overlap_original_solid=solidstats(s^a['solid']),intended_old_air_fill=solidstats(old_air),actual_added_within=solidstats(actual),variant_unfilled_inside_prescribed_fill=solidstats(s-b['solid'])))
 expected=a['solid']+union
 bools=dict(added=solidstats(added),removed=solidstats(removed),net_volume_change_mm3=float(b['solid'].volume()-a['solid'].volume()),volume_balance_residual_mm3=float(b['solid'].volume()-a['solid'].volume()-added.volume()+removed.volume()),actual_added_outside_fill_union=solidstats(added-union),prescribed_fill_missing_in_variant=solidstats(union-b['solid']),variant_minus_expected=solidstats(b['solid']-expected),expected_minus_variant=solidstats(expected-b['solid']),source_parameter_ledger=ledger)
 accesspath=P/'qa/risk-followup-e45f8d6/support_access_review.json';access=json.loads(accesspath.read_text());assert access['stl_sha256']=='9c90c8b6b6f99076f2096783e78b793404fb81df88ee270d2eb02f21290e24b8'
 oldrays=[]
 for group in ['entrance','rear']:
  for path,row in source_ray_tree(access[group],group):
   origin=np.array(row['origin']);d=np.array(row['direction']);source=dict(report_file='qa/risk-followup-e45f8d6/support_access_review.json',source_report_STL_sha256=access['stl_sha256'],source_report_version='e45f8d6; coordinates replayed independently into fixed R2 and variant; source face IDs are not transferred',json_path=path,unmodified_origin=row['origin'],unmodified_direction=row['direction'],source_stored_solid_intervals=row.get('solid_intervals'))
   if group=='rear':
    side=path.split('/')[1];R=np.array(access['rear'][side]['local_to_global']);shift=np.array(access['rear'][side]['translation_mm']);origin=R@origin+shift;d=R@d;source['coordinate_frame']=dict(rotation=R.tolist(),translation_mm=shift.tolist())
   rowout=line_compare(a,b,origin,d,source)
   oldstored=[q['range'] for q in row['solid_intervals']];rec=rowout['original']['solid_intervals_mm']
   rowout['original_recomputation_matches_retained_intervals_within_1e_5_mm']=len(oldstored)==len(rec) and all(max(abs(x-y) for x,y in zip(i,j))<=LINE_TOL for i,j in zip(oldstored,rec))
   oldrays.append(rowout)
 fixed=[]
 for x in [37,43,49,55]:
  for z in [28.5,37.5,46.5]:
   r=line_compare(a,b,[x,0,z],[0,1,0],dict(kind='additional_generator_parameter_line',location='entrance_fin_center',X_mm=x,Z_mm=z))
   r['target_air_interval_mm']=[-20.899999618530273,-19.100000381469727];r['original_target_interval_solid']=filled_between(r['original'],-20.8999,-19.1001);r['variant_target_interval_solid']=filled_between(r['variant'],-20.8999,-19.1001);fixed.append(r)
 for center,ang in [(-30,-14),(30,14)]:
  R=rotation(ang);shift=np.array([center,30,0])
  for z in [18.05,29.05,40.05,51.05]:
   origin=R@np.array([.123,0,z])+shift;d=R@np.array([0,1,0]);r=line_compare(a,b,origin,d,dict(kind='retained_support_access_generator_line',location='rear_microgap',local_origin_mm=[.123,0,z],local_direction=[0,1,0],rotation_Z_deg=ang,translation_mm=shift.tolist()))
   r['target_air_interval_local_Y_mm']=[-9.8,-9.75];r['original_target_interval_solid']=filled_between(r['original'],-9.79999,-9.75001);r['variant_target_interval_solid']=filled_between(r['variant'],-9.79999,-9.75001);fixed.append(r)
 # Full bay rectangles lie between unchanged fin X edges. These volume crops
 # verify no fill or removal intrudes into the opening, rather than relying
 # only on centre rays. The 0.01 mm inset excludes the intended shared edge.
 bays=[]
 for lo,hi in [(37.5,42.5),(43.5,48.5),(49.5,54.5),(55.5,60.0)]:
  for z in [25,34,43]:
   region=cube_bounds([lo+.01,-21.94,z+.01],[hi-.01,-19.11,z+6.99]);add=added^region;rem=removed^region
   bays.append(dict(X_opening_bounds_mm=[lo,hi],Z_opening_bounds_mm=[z,z+7],tested_inset_mm=.01,added=solidstats(add),removed=solidstats(rem),unchanged_within_1e_6_mm3=abs(add.volume())+abs(rem.volume())<=VOLUME_TOL))
 zs=sorted(set([18.05,29.05,40.05,51.05,25.123,28.123,31.999,31.999987,34.123,37.123,43.123,46.123]))
 sections=[]
 for z in zs:
  x,y=section(a,z),section(b,z);add=y-x;rem=x-y
  sections.append(dict(Z_mm=z,original_area_mm2=float(x.area),variant_area_mm2=float(y.area),added_area_mm2=float(add.area),removed_area_mm2=float(rem.area),added_section_WKT=wkt.dumps(add,rounding_precision=12,trim=True),removed_section_WKT=wkt.dumps(rem,rounding_precision=12,trim=True)))
 # All 18 original null backing measurements stay null in their original
 # report. Independently measure both meshes at the identical failed Z.
 supppath=P/'qa/risk-followup-e45f8d6/r2-support_analysis.json';supp=json.loads(supppath.read_text());nulls=[]
 for row in supp['face_measurements']:
  if row['horizontal_backing_distance_at_original_centroid_mm'] is not None:continue
  from shapely.geometry import Point
  z=row['horizontal_support_reference_z_mm'];q=Point(row['original_centroid_mm'][:2]);x,y=section(a,z),section(b,z)
  nulls.append(dict(original_face=row['face'],original_centroid_mm=row['original_centroid_mm'],original_failed_Z_mm=z,retained_original_backing_distance=None,original_independent_same_Z_point_distance_mm=float(q.distance(x)),variant_independent_same_Z_point_distance_mm=float(q.distance(y))))
 crops={
  'fin_front_global_Y_le_minus20_95':cropdelta(a['solid'],b['solid'],[([0,-1,0],20.95)]),
  'roof_and_cap_Z_ge_51_2':cropdelta(a['solid'],b['solid'],[([0,0,1],51.2)]),
  'front_oval_and_stair_X_le_16_Y_le_5':cropdelta(a['solid'],b['solid'],[([-1,0,0],-16),([0,-1,0],-5)]),
  'connector_grille_X_16_to34':cropdelta(a['solid'],b['solid'],[([1,0,0],16),([-1,0,0],-34)]),
 }
 report=dict(schema_version=1,original_fixed_commit='f15ccb3c0283fb302616a68146fb41f02b203d07',original=metadata(a),variant=metadata(b),original_generator_sha256=sha(P/'build_model.py'),script_sha256=sha(Path(__file__)),runtime=dict(python=platform.python_version(),numpy=np.__version__,trimesh=trimesh.__version__),method='Raw STL float32 promoted without change; exact coordinate vertex indexing, no repair. Numerical manifold Booleans retain full residuals. All retained signed source rays replayed without movement, source face IDs retained only as reference and not transferred to variant. Independent Manifold slice at precisely the same source Z, no offsets introduced.',tolerances=dict(volume_equality_mm3=VOLUME_TOL,line_intersection_comparison_mm=LINE_TOL,ray_hit_merge_mm=1e-7),boolean_delta=bools,retained_source_ray_report_sha256=sha(accesspath),retained_source_rays=oldrays,target_air_to_solid_lines=fixed,bay_opening_volume_checks=bays,same_Z_sections=sections,retained_null_backing_measurements_same_Z=nulls,limited_unchanged_crops=crops,visibility_changes=['Fin front plane Y=-21.95 and fin X widths are retained; backing infill replaces the air behind four fins with solid ribs, changing fin side/rear surfaces and oblique visibility of window recesses. It is a deliberate manufacturing simplification, not a claim of architectural accuracy.','Rear 0.05 mm-deep by 0.10 mm-high microgap is filled only behind original sill lower lip; 0.05 mm local-Y extension beyond cut backplane overlaps solid, and 0.01 mm overlap at sill avoids a coincident join. This changes microgap internal surfaces while leaving the projecting front sill edge/local Y=-13 unchanged.','Equal bounding boxes or limited crops do not prove all visible contour views are unchanged. Actual added/removed bounds, fixed rays, bay volume crops and prescribed source-parameter residuals are given above.'],formal_slicer_run=False,support_generation_performed=False,physical_print_test=False,limitations=['Finite fixed rays and slices do not certify a global thickness minimum or full support extraction.','Any nonzero float32 export/Boolean residual is retained, even if below the declared comparison tolerance.','This variant only removes the specified fin-back air and sill microgap. Remaining eaves, grille, arcade, windows, 0.8 mm details and roof edge support/toolpath risks persist.','No claim of success on arbitrary single-material FDM equipment; actual slicing, support strategy and test printing remain outstanding.'],elapsed_seconds=time.monotonic()-start)
 report['inputs_unchanged_at_end']=dict(original=sha(P/'model.stl')==a['sha'],variant=sha(args.variant)==b['sha'],original_generator=sha(P/'build_model.py')==GENERATOR_SHA)
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(dict(original=a['sha'],variant=b['sha'],topology=report['variant'],boolean_delta={k:v for k,v in bools.items() if k!='source_parameter_ledger'},retained_rays=len(oldrays),retained_ray_old_recomputations_match=sum(r['original_recomputation_matches_retained_intervals_within_1e_5_mm'] for r in oldrays),target_lines=len(fixed),target_lines_filled=sum(r['variant_target_interval_solid'] for r in fixed),bays_unchanged=sum(r['unchanged_within_1e_6_mm3'] for r in bays),nulls_retained=len(nulls),crops={k:v['symmetric_difference_volume_mm3'] for k,v in crops.items()},elapsed_seconds=report['elapsed_seconds']),indent=2))

if __name__=='__main__':main()
