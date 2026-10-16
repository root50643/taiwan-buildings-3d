"""Fail-closed binding of current geometry, raw evidence, scene and preview gates.
Does not replace independent review, measurement or physical printing.
"""
from pathlib import Path
import gzip,hashlib,json,struct,sys
from verification.qa_common import open_compressed_csv
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
REQUIRED_FLAG_NAMES={'raw': ['binary_length_exact', 'finite_original_data', 'all_original_faces_nondegenerate', 'no_duplicate_original_faces', 'original_stored_normals_unit', 'original_stored_normals_agree_with_directed_faces', 'exact_coordinate_edges_two_faces', 'exact_coordinate_consistent_winding', 'exact_coordinate_vertex_links_single_cycles', 'single_surface_no_internal_shell', 'positive_signed_volume', 'requested_longest_extent_mm'], 'sections': ['all_three_offsets_have_layers', 'all_original_sections_valid_without_repair', 'every_original_polygon_checked', 'all_original_polygons_survive_erosion_and_opening', 'no_original_polygon_splits_after_erosion_or_opening', 'all_opened_and_eroded_polygons_valid', 'all_individual_polygon_losses_le_one_percent'], 'dense': ['every_original_face_exactly_ten_samples', 'stored_normals_agree_with_original_directed_faces', 'all_original_ray_intervals_and_controls_valid', 'all_first_original_chords_ge_0p8mm'], 'controls': ['positive_box_passes_all_gates_both_modes', 'all_negative_controls_rejected_for_expected_reason_both_modes', 'all_controls_have_reports', 'both_python_modes_tested'], 'aggregate': ['all_gates_explicitly_pass', 'all_gate_check_flags_true', 'original_stl_unchanged', 'all_geometry_reports_bound_to_current_stl', 'checker_sources_unchanged_during_run', 'all_reports_bound_to_current_checkers', 'three_required_layer_offsets', 'every_original_face_has_ten_rays', 'zero_short_or_flagged_dense_samples', 'all_full_detail_artifact_hashes_current', 'dense_lossless_csv_hash_current'], 'scene': ['one_mesh_object', 'triangle_count_same', 'all_oriented_coordinates_exact', 'no_modifiers', 'identity_transforms', 'source_hash_recorded', 'no_embedded_text_blocks', 'no_linked_libraries', 'no_external_images', 'no_image_texture_nodes', 'relative_saved_render_path', 'no_other_renderable_object_types', 'no_hidden_unlinked_objects', 'no_parent_or_instances', 'mesh_world_matrix_identity', 'mesh_render_visible', 'single_scene_no_compositor', 'no_external_blend_resource_paths', 'no_external_media_datablocks', 'no_linked_datablocks', 'no_private_datablock_or_custom_property_paths', 'no_packed_resources']}
REQUIRED_FEATURE_NAMES=['N lower south half of double-height aperture', 'N upper north half of double-height aperture', 'N upper south open bay', 'N north-third internal support', 'N continuous north-end concrete strip', 'N ground colonnade opening', 'N ground north glass/core mass', 'M undercroft between columns', 'M recessed backing wall', 'M V-column central open space', 'M north platform underside open zone', 'Courtyard raised lawn mass', 'West court shallow descending entry void', 'N narrow roof slot lies below parapet', 'M south lower annex', 'M southwest stair projection', 'Lawn skylight 1 body', 'Lawn skylight 2 body', 'Lawn skylight 3 body', 'Lawn skylight 4 body', 'Lawn skylight 5 body', 'Lawn skylight 6 body']
def inspect(root=R):
 root=Path(root);stl=root/'model.stl';h=sha(stl);raw=stl.read_bytes();triangles=struct.unpack_from('<I',raw,80)[0]
 gates={'raw':'qa/current/raw/raw-mesh-check.json','sections':'qa/current/sections/section-check.json','dense':'qa/current/dense/dense-check.json','controls':'qa/current/controls/control-check.json','aggregate':'qa/current/qa-summary.json','exact_invocation':'exact-invocation.json','intersections':'qa/current/intersections/original-intersections.json','intersection_controls':'qa/current/intersection-controls/controls-summary.json','features':'architectural-features.json','reproducibility':'reproducibility.json','scene':'scene-check.json'}
 reports={};checks={};details={}
 for name,rel in gates.items():
  p=root/rel
  try:
   q=json.loads(p.read_text());reports[name]=q;checks[name+'_passed']=q.get('passed') is True
   if name not in ['controls','intersection_controls']:checks[name+'_current_stl']=q.get('stl_sha256')==h
   if name in REQUIRED_FLAG_NAMES:
    flags=q.get('checks')
    checks[name+'_required_flag_schema']=isinstance(flags,dict) and set(flags)==set(REQUIRED_FLAG_NAMES[name])
    checks[name+'_every_flag_true']=isinstance(flags,dict) and bool(flags) and all(v is True for v in flags.values())
   if name in ['raw','sections','dense','controls','aggregate','intersections']: checks[name+'_strict_passed']=q.get('strict_passed') is True
   details[name]={'path':rel,'sha256':sha(p),'reported_passed':q.get('passed')}
  except Exception as e:checks[name+'_readable']=False;details[name]={'path':rel,'error':str(e)}
 fq=reports.get('features',{}); checks['features_all_probe_flags_true']=isinstance(fq.get('checks'),list) and bool(fq['checks']) and all(row.get('passed') is True for row in fq['checks'])
 checks['features_complete_expected_probes']=isinstance(fq.get('checks'),list) and len(fq['checks'])==22 and [row.get('name') for row in fq['checks']]==REQUIRED_FEATURE_NAMES and all(isinstance(row.get('expected_solid'),bool) and row.get('observed_solid') is row.get('expected_solid') for row in fq['checks'])
 checks['features_current_source']=fq.get('checker_source_sha256')==sha(root/'check_architectural_features.py')
 dense=reports.get('dense',{});sections=reports.get('sections',{});inter=reports.get('intersections',{});rawq=reports.get('raw',{})
 checks['raw_expected_extent']=rawq.get('expected_longest_mm')==200 and abs(max(rawq.get('extents_mm',[0]))-200)<1e-5
 checks['raw_count_matches_bytes']=rawq.get('triangles')==triangles and len(raw)==84+50*triangles
 checks['dense_required_width_unrelaxed']=dense.get('minimum_required_chord_mm')==.8
 checks['dense_all_original_samples']=dense.get('samples')==triangles*10 and dense.get('samples_per_original_face')==10
 checks['dense_zero_short_or_flagged']=dense.get('under_0p8mm_count')==0 and dense.get('flagged_sample_count')==0 and dense.get('minimum_first_chord_mm',0)>=.8
 checks['sections_required_schedule']=sections.get('pitch_mm')==.2 and sections.get('offsets_from_z_min_mm')==[.031,.071,.137]
 checks['sections_required_opening']=sections.get('opening_reference_width_mm')==.8 and sections.get('per_polygon_loss_limit')==.01
 checks['sections_zero_failures']=sections.get('failed_layer_count')==0 and sections.get('failed_polygon_count')==0
 checks['exact_intersections_completed_clear']=inter.get('completed') is True and inter.get('bad_pair_count')==0 and inter.get('strict_passed') is True
 evidence=[('sections','detail_file','detail_sha256'),('sections','failure_file','failure_sha256'),('dense','csv_file','csv_compressed_sha256'),('dense','short_chords_file','short_chords_sha256'),('dense','flagged_samples_file','flagged_samples_sha256')]
 for name,key,hkey in evidence:
  q=reports.get(name,{});file=q.get(key);p=root/'qa/current'/name/file if isinstance(file,str) else None
  checks[name+'_'+key+'_hash']=bool(p and p.is_file() and sha(p)==q.get(hkey))
  if p and p.is_file() and key in ['failure_file','short_chords_file','flagged_samples_file']:
   try:checks[name+'_'+key+'_empty']=json.load(gzip.open(p))==[]
   except Exception:checks[name+'_'+key+'_empty']=False
 # Bind the aggregate's four raw report records and both compressed/lossless ray hashes.
 ag=reports.get('aggregate',{}).get('gate_reports')
 checks['aggregate_exact_gate_records']=isinstance(ag,list) and len(ag)==4 and [row.get('gate') for row in ag]==['raw','sections','dense','controls']
 if isinstance(ag,list):
  for name in ['raw','sections','dense','controls']:
   rows=[row for row in ag if row.get('gate')==name]; expected=gates[name].removeprefix('qa/current/')
   checks['aggregate_'+name+'_report_binding']=len(rows)==1 and rows[0].get('report_file')==expected and rows[0].get('report_sha256')==sha(root/gates[name]) and rows[0].get('returncode')==0 and rows[0].get('passed') is True and rows[0].get('failed_checks')==[]
 csv=root/'qa/current/dense'/str(dense.get('csv_file','missing'))
 try:
  with open_compressed_csv(csv,dense.get('csv_compression')) as handle:
   dig=hashlib.sha256();size=0
   while block:=handle.read(1024*1024):dig.update(block);size+=len(block)
   checks['dense_lossless_csv_hash']=dig.hexdigest()==dense.get('uncompressed_csv_sha256') and size==dense.get('uncompressed_csv_bytes')
  checks['dense_declared_container_bytes']=csv.stat().st_size==dense.get('csv_compressed_bytes')
 except Exception:checks['dense_lossless_csv_hash']=False;checks['dense_declared_container_bytes']=False
 # Bind all generic checker scripts, not just the primary STL hash.
 inventory={p.name:sha(p) for p in sorted((root/'verification').iterdir()) if p.suffix in ['.py','.cpp'] and p.is_file()}
 for name in ['raw','sections','dense','controls','aggregate']:checks[name+'_current_checker_inventory']=reports.get(name,{}).get('checker_sources_sha256')==inventory
 ic=reports.get('intersection_controls',{})
 checks['exact_controlled_source']=ic.get('checker_sha256')==sha(root/'verification/check_original_intersections.py')
 iq=reports.get('exact_invocation',{})
 checks['exact_current_source']=iq.get('checker_source_sha256')==sha(root/'verification/check_original_intersections.py') and iq.get('wrapper_source_sha256')==sha(root/'run_exact_intersections.py')
 checks['exact_invocation_bound_to_report']=iq.get('report_sha256')==sha(root/'qa/current/intersections/original-intersections.json') and iq.get('exit_code')==0 and iq.get('sources_unchanged_during_run') is True
 contacts=inter.get('all_actual_intersections',{}); cp=root/'qa/current/intersections'/str(contacts.get('path','missing'))
 checks['exact_contacts_bound']=cp.is_file() and contacts.get('sha256')==sha(cp) and contacts.get('record_count')==inter.get('actual_intersection_pair_count')
 checks['exact_controls_current_source']=ic.get('controls_source_sha256')==sha(root/'verification/check_intersection_controls.py')
 rq=reports.get('reproducibility',{});checks['repro_current_source']=rq.get('build_source_sha256')==sha(root/'build_model.py') and rq.get('parameters_sha256')==sha(root/'parameters.json') and rq.get('rebuilt_stl_sha256')==h
 sq=reports.get('scene',{});checks['scene_current_blend']=sq.get('blend_sha256')==sha(root/'scene.blend') if (root/'scene.blend').is_file() else False
 try:
  render=json.loads((root/'render-manifest.json').read_text());checks['render_bound_to_current_stl']=render.get('stl_sha256')==h;checks['render_current_source']=render.get('render_source_sha256')==sha(root/'render_preview.py');checks['render_current_blend']=render.get('blend_sha256')==sha(root/'scene.blend')
  for name in ['front','rear','north','east','west','south','top','n-west-detail','m-east-detail']:
   p=root/'previews'/(name+'.png');checks['preview_'+name+'_hash']=p.is_file() and render.get('views',{}).get(name,{}).get('png_sha256')==sha(p)
 except Exception:checks['render_manifest_readable']=False
 return {'python_optimization_level':sys.flags.optimize,'passed':all(checks.values()),'strict_passed':all(checks.values()),'stl_sha256':h,'checks':checks,'gate_reports':details,'failed_checks':[k for k,v in checks.items() if not v],'limits':'Finite raw-STL geometric screens and source/preview bindings only. No independent review approval, exact survey fidelity, global all-direction thickness proof or physical print claim.'}
if __name__=='__main__':
 try:q=inspect()
 except Exception as e:q={'passed':False,'strict_passed':False,'error_type':type(e).__name__,'error':str(e)}
 (R/'validation.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));raise SystemExit(0 if q['passed'] else 1)
