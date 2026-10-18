"""Separate supplement to retained variant-qa.json; no earlier output edited.

Measures strict failed equality residues, and adds spatially narrower crops
when broad crops also include the intended rear sill fills. Saved float32
coordinate changes are quantified, never silently relabelled as zero.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json
import numpy as np
import trimesh

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('variant_qa',HERE/'variant_qa.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)

def proximity_bound(residual,target):
 if residual.is_empty():return dict(empty=True,surface_triangle_count=0,upper_bound_mm=0.)
 m=residual.to_mesh64();v=np.asarray(m.vert_properties)[:,:3];f=np.asarray(m.tri_verts);tri=v[f]
 centers=tri.mean(axis=1);near,dist,face=trimesh.proximity.closest_point(target['mesh'],centers)
 selected=target['tri'][face]
 queries=tri.reshape(-1,3);against=np.repeat(selected,3,axis=0)
 points=trimesh.triangles.closest_point(against,queries);d=np.linalg.norm(points-queries,axis=1).reshape(-1,3)
 return dict(empty=False,surface_triangle_count=len(tri),centroid_nearest_surface_distance_max_mm=float(dist.max()),triangle_to_one_target_face_convex_distance_upper_bound_mm=float(d.max()),worst_residual_triangle=int(np.argmax(d.max(axis=1))),worst_residual_triangle_vertices_mm=tri[np.argmax(d.max(axis=1))].tolist(),chosen_target_face=int(face[np.argmax(d.max(axis=1))]),method='For each residual triangle choose the nearest target triangle at its centroid. Compute distances from all three residual vertices to that same finite target triangle. Distance to a convex triangle is convex, hence its maximum over the residual triangle is bounded by the largest vertex distance; the bound applies to every point on that triangle, subject to floating-point closest-point arithmetic. This is a directed proximity bound, not a statement that residual volume is zero.')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--variant',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
 if args.output.exists():raise FileExistsError('Existing evidence not overwritten.')
 oldreportpath=HERE/'variant-qa.json';r=json.loads(oldreportpath.read_text());a,b=qa.load(qa.P/'model.stl'),qa.load(args.variant)
 assert a['sha']==qa.ORIGINAL_SHA and b['sha']==r['variant']['stl_sha256']
 fills=[]
 for row in r['boolean_delta']['source_parameter_ledger']:
  s=row['source_parameters']
  if s['frame']=='global XYZ':m=qa.cube_bounds(s['min_mm'],s['max_mm'])
  else:m=qa.cube_bounds(s['local_min_mm'],s['local_max_mm']).rotate((0,0,s['rotation_Z_deg'])).translate(tuple(s['global_translation_mm']))
  fills.append(m)
 from manifold3d import Manifold,OpType
 union=Manifold.batch_boolean(fills,OpType.Add);added=b['solid']-a['solid'];removed=a['solid']-b['solid'];outside=added-union;missing=union-b['solid'];res=[]
 for name,s in [('all_actual_removed_material',removed),('actual_added_outside_source_fill_union',outside),('unfilled_prescribed_fill_volume',missing)]:
  res.append(dict(id=name,strict_raw_solid=qa.solidstats(s),proximity_to_original=proximity_bound(s,a),proximity_to_variant=proximity_bound(s,b)))
 narrow=dict(
  actual_connector_grille_X16_to34_Y_le5=qa.cropdelta(a['solid'],b['solid'],[([1,0,0],16),([-1,0,0],-34),([0,-1,0],-5)]),
  front_roof_cap_Zge51_2_Xle16_Yle5=qa.cropdelta(a['solid'],b['solid'],[([0,0,1],51.2),([-1,0,0],-16),([0,-1,0],-5)]),
 )
 sills=[]
 for center,ang in [(-30,-14),(30,14)]:
  for z in [18,29,40,51]:
   crop=qa.cube_bounds([-32,-13.01,z-1], [32,-9.82,z+.1]).rotate((0,0,ang)).translate((center,30,0));x=added^crop;y=removed^crop
   sills.append(dict(rear_wing_center_X_mm=center,rotation_Z_deg=ang,Z_level_mm=z,unchanged_target_local_bounds_mm=[[-32,-13.01,z-1],[32,-9.82,z+.1]],added=qa.solidstats(x),removed=qa.solidstats(y),symmetric_difference_mm3=float(x.volume()+y.volume()),equal_at_original_1e_6_mm3_tolerance=abs(x.volume()+y.volume())<=qa.VOLUME_TOL))
 noexit=r['original_49_no_straight_exit_points_same_Z'];groups={}
 for name in sorted({x['component_group'] for x in noexit}):
  rows=[x for x in noexit if x['component_group']==name]
  groups[name]=dict(retained_original_no_exit_count=len(rows),old_air_points_now_solid=sum(x['variant_airpoint_now_solid'] for x in rows),still_air_points=sum(not x['variant_airpoint_now_solid'] for x in rows),some_tested_zero_radius_straight_exit_found=sum(x['variant_some_zero_radius_straight_route_clear'] for x in rows),original_faces=[x['original_face'] for x in rows])
 report=dict(schema_version=1,original_stl_sha256=a['sha'],variant_stl_sha256=b['sha'],script_sha256=qa.sha(Path(__file__)),supplement_to_report_sha256=qa.sha(oldreportpath),original_strict_volume_tolerance_mm3=qa.VOLUME_TOL,retained_initial_failed_equalities=['removed material is 5.245242e-6 mm3, not zero','actual added outside source fill union is 1.258535e-5 mm3, not zero','broad Z>=51.2 crop also includes rear surfaces and has a nonzero residue','broad connector X=16..34 crop also includes intended rear sill fill, with 0.3710188 mm3 difference'],residual_proximity_bounds=res,additional_narrow_crop_checks=narrow,rear_projecting_sill_front_edge_crop_checks=sills,original_49_no_exit_same_point_classification=groups,interpretation=['The original strict 1e-6 mm3 equality failures remain failures. Separate proximity bounds quantify their thin spatial extent; they are not erased, retoleranced, or called exactly zero.','The original broad connector crop difference includes the intended rear sill infill. This separate X16..34 AND Y<=5 crop tests only the connector region; it does not replace the broad result.','The original broad Z>=51.2 crop includes rear wing surfaces above the fills. The separate front-specific crop excludes those surfaces and tests the unchanged front clerestory cap.','When an old airpoint is now solid there is no cavity at that point for support to occupy. Remaining airpoints with no tested straight exit are unresolved access risks; a clear zero-radius ray alone never proves full support removal.','No new universal printability conclusion follows from this supplement.'],formal_slicer_run=False,support_generation_performed=False,physical_print_test=False)
 args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(dict(variant=b['sha'],narrow_crops={k:v['symmetric_difference_volume_mm3'] for k,v in narrow.items()},sill_crops=[x['symmetric_difference_mm3'] for x in sills],residual_bound_variant_mm={x['id']:x['proximity_to_variant'].get('triangle_to_one_target_face_convex_distance_upper_bound_mm',0) for x in res},original49=groups),indent=2))

if __name__=='__main__':main()
