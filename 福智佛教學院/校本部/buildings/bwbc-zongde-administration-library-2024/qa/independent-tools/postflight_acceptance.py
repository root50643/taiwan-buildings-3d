"""Read-only, failure-closed audit of completed v17 evidence and publication bindings.
This does not alter or upgrade the original numerical strict=false result.
"""
import argparse,collections,gzip,hashlib,json,lzma,sys
from fractions import Fraction
from pathlib import Path
STL='96481addb2b9ac4144cb5f012f19b57e047106021e93adb5c34df2c00770e1a3'
FREEZE='4c83b113598bff1053087caf4208d0382f80b9bc855aade37e27c347b73c1890'
VIEWS={'front','rear','local-plus-y','local-minus-y','local-plus-x','local-minus-x','top','court-open','court-high-wings','entry','court-stair'}
def require(value,message):
 if not value: raise RuntimeError(message)
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--qa',type=Path,required=True);ap.add_argument('--author',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
 require(not args.out.exists(),'Refuse existing postflight output');args.out.mkdir(parents=True)
 qa=args.qa.resolve();author=args.author.resolve();old=qa/'final-v17';run=qa/'resume-v17';frozen=old/'frozen';ver=frozen/'verification';ind=frozen/'independent-tools';tracked={};report={'bounded_verification_passed':False,'original_numerical_strict_passed':False,'stl_sha256':STL,'scope':'Completed-stage bindings, explicit normal/optimized gate inspection, exact flagged-ray proofs, source/Blend/image reproduction and publication-file integrity. No global wall-thickness or physical-print guarantee.','postflight_source_sha256':sha(__file__),'optimization_level':sys.flags.optimize}
 def key(p):
  p=Path(p).resolve()
  if p.is_relative_to(qa):return 'independent-qa/'+str(p.relative_to(qa))
  if p.is_relative_to(author):return 'author/'+str(p.relative_to(author))
  raise RuntimeError('Evidence path outside declared roots')
 def track(p,expected=None):
  p=Path(p);digest=sha(p);logical=key(p);row={'sha256':digest,'bytes':p.stat().st_size};require(expected is None or digest==expected,'SHA mismatch: '+logical);require(logical not in tracked or tracked[logical]==row,'Evidence changed since first read: '+logical);tracked[logical]=row;return digest
 def read(p):
  raw=Path(p).read_bytes();require(hashlib.sha256(raw).hexdigest()==track(p),'JSON changed during read: '+key(p));return json.loads(raw)
 def yes(d,keys,label):require(all(d.get(k) is True for k in keys),label+' lacks required true fields')
 def local(base,name):require(isinstance(name,str) and Path(name).name==name,'Evidence artifact must be basename');return base/name
 def decode_json(p):
  raw=Path(p).read_bytes();require(hashlib.sha256(raw).hexdigest()==track(p),'Compressed JSON changed during read: '+key(p));return json.loads(gzip.decompress(raw))
 try:
  track(old/'author-freeze-manifest.json',FREEZE);track(author/'frozen-inputs-v17.json',FREEZE);manifest=read(old/'author-freeze-manifest.json');require(manifest['stl_sha256']==STL and len(manifest['files'])==68,'Freeze identity/count')
  for row in manifest['files']:
   p=author/row['path'];require(p.stat().st_size==row['bytes'],'Frozen size differs');track(p,row['sha256'])
  for rel,digest in read(old/'frozen-input-inventory.json').items():
   p=frozen/rel
   if not p.is_file():p=frozen/'documentation'/rel
   track(p,digest)
  inv=read(old/'independent-tool-inventory.json');require(len(inv)==7,'Independent snapshot count')
  for name,digest in inv.items():track(ind/name,digest)
  sys.path[:0]=[str(ver),str(ind)]
  from run_qa import REQUIRED_CHECKS
  from qa_common import checker_inventory
  from png_exact_compare import parse as parse_png,compare as compare_png,SANITIZE_TEXT_KEYS
  inventory=checker_inventory();required={k:set(v) for k,v in REQUIRED_CHECKS.items()};required['raw'].add('requested_longest_extent_mm')
  resumed=read(run/'resumed-execution-summary.json');yes(resumed,['completed','all_frozen_inputs_and_tools_unchanged'],'Recovery execution');require(resumed['strict_passed'] is False,'Execution ledger falsely upgrades strict');track(qa/'independent-tools/resume_independent_candidate.py',resumed['resume_source_sha256']);require(all(resumed['author_input_rechecks'].values()),'Author recheck failure')
  expected_exits={'normal-dense':1,'optimized-standard':1}
  names={'normal-dense','normal-generic-controls','normal-exact-intersections','normal-intersection-controls','normal-exact-recorded-rays','optimized-standard','optimized-exact-intersections','optimized-intersection-controls','optimized-exact-recorded-rays','source-stl-reproduction','source-scene-state-reproduction','saved-blend-eleven-rerenders','public-png-metadata-cleanup'}
  require({r['name'] for r in resumed['executions']}==names and len(resumed['executions'])==len(names),'Execution inventory incomplete/duplicate')
  for row in resumed['executions']:require(row['returncode']==expected_exits.get(row['name'],0),'Unexpected child exit: '+row['name']);track(run/row['log_file'],row['log_sha256'])
  interruption=read(old/'interruption/interruption-status.json');references=read(run/'referenced-completed-stages.json');require(references['stl_sha256']==STL and {x['gate'] for x in references['stages']}=={'raw','sections'},'Recovered stage set')
  for row in references['stages']:
   gate=row['gate'];reportname={'raw':'raw-mesh-check.json','sections':'section-check.json'}[gate];require(row['original_report_sha256']==interruption['normal_'+gate+'_report_sha256'],'Recovery original binding')
   for name,digest in row['files_sha256'].items():track(old/'geometry/normal/standard'/gate/name,digest);track(run/'geometry/normal/standard'/gate/name,digest)
  modes={};mode_reports={}
  for mode,opt in [('normal',0),('optimized',1)]:
   base=run/'geometry'/mode;std=base/'standard';g={name:read(std/name/file) for name,file in [('raw','raw-mesh-check.json'),('sections','section-check.json'),('dense','dense-check.json'),('controls','control-check.json')]};mode_reports[mode]=g
   for gate,r in g.items():
    require('error' not in r and set(r['checks'])==required[gate] and r['checker_sources_sha256']==inventory,'Gate schema/inventory: '+mode+'/'+gate)
    if gate!='controls':require(r['stl_sha256']==STL,'Gate STL binding')
    if gate!='dense':yes(r,['passed','strict_passed'],mode+'/'+gate);require(all(v is True for v in r['checks'].values()),'False gate flag: '+mode+'/'+gate)
   raw,sec,dense,controls=(g[x] for x in ['raw','sections','dense','controls'])
   require(raw['triangles']==37330 and raw['surface_shells']==1 and raw['extents_mm']==[210.,187.5,54.625],'Raw dimensions/count')
   require(sec['sampled_layers']==819 and sec['original_polygon_count']==29220 and sec['failed_layer_count']==sec['failed_polygon_count']==0 and sec['pitch_mm']==.2 and sec['offsets_from_z_min_mm']==[.031,.071,.137] and sec['per_polygon_loss_limit']==.01 and sec['opening_reference_width_mm']==.8,'Section counts/thresholds')
   require(dense['passed'] is False and dense['strict_passed'] is False and {k for k,v in dense['checks'].items() if v is False}=={'all_original_ray_intervals_and_controls_valid'},'Numerical gate failure semantics changed')
   require(all(v is True for k,v in dense['checks'].items() if k!='all_original_ray_intervals_and_controls_valid'),'Unexpected numerical gate failure')
   require(dense['samples']==373300 and dense['original_triangles']==37330 and dense['samples_per_original_face']==10 and dense['under_0p8mm_count']==0 and dense['flagged_sample_count']==12 and dense['minimum_first_chord_mm']==1.0 and dense['minimum_required_chord_mm']==.8,'Numerical counts/thresholds')
   for gate,fk,hk in [('sections','detail_file','detail_sha256'),('sections','failure_file','failure_sha256'),('dense','csv_file','csv_compressed_sha256'),('dense','short_chords_file','short_chords_sha256'),('dense','flagged_samples_file','flagged_samples_sha256')]:track(local(std/gate,g[gate][fk]),g[gate][hk])
   csvpath=local(std/'dense',dense['csv_file']);require(dense['csv_compression']=='xz' and csvpath.name.endswith('.csv.xz'),'Dense container')
   with lzma.open(csvpath,'rb') as f:require(hashlib.file_digest(f,'sha256').hexdigest()==dense['uncompressed_csv_sha256'],'Decoded dense SHA mismatch')
   require(decode_json(std/'dense'/dense['short_chords_file'])==[] and decode_json(std/'sections'/sec['failure_file'])==[],'Nonempty original failed/short evidence')
   flags=decode_json(std/'dense'/dense['flagged_samples_file']);require(len(flags)==12,'Flag count')
   require(controls['control_runs']==30 and controls['fixtures']==12 and len(controls['controls'])==30,'Generic control count')
   for row in controls['controls']:
    require(row['expectation_verified'] is True,'Generic control expectation');childpath=std/'controls'/row['report_file'];track(childpath,row['report_sha256']);child=read(childpath);require(type(row['expected_pass']) is bool and child['passed'] is row['expected_pass'] and child['strict_passed'] is row['expected_pass'] and row['returncode']==(0 if row['expected_pass'] else 1),'Generic control child outcome');require(row['expected_false_check'] is None or child['checks'].get(row['expected_false_check']) is False,'Negative control reason differs')
   if mode=='optimized':
    aggregate=read(std/'qa-summary.json');require(aggregate['passed'] is False and aggregate['strict_passed'] is False and aggregate['optimized_python'] is True,'Optimized original aggregate semantics')
    expected_false={'all_gates_explicitly_pass','all_gate_check_flags_true','zero_short_or_flagged_dense_samples'};require({k for k,v in aggregate['checks'].items() if v is False}==expected_false and all(type(v) is bool for v in aggregate['checks'].values()),'Unexpected optimized aggregate failure')
    for row in aggregate['gate_reports']:track(std/row['report_file'],row['report_sha256']);require(row['returncode']==(1 if row['gate']=='dense' else 0),'Unexpected optimized gate exit')
   else:
    ledger=read(std/'recovered-stage-summary.json');require(ledger['passed'] is False and ledger['strict_passed'] is False and ledger['all_evidence_bindings_valid'] is True and all(v is True for v in ledger['binding_checks'].values()),'Recovery binding ledger')
   inter=read(base/'intersections.json');yes(inter,['passed','strict_passed','completed','input_unchanged_during_check'],'Exact intersections');require(inter['stl_sha256']==inter['stl_sha256_after_check']==STL and inter['bad_pair_count']==0 and inter['bad_pairs']==[] and inter['degenerate_original_faces']==[],'Exact geometry result')
   require(inter['broad_phase']['all_bbox_overlapping_pairs_completed'] is True and inter['broad_phase']['candidate_pairs_checked']==620769 and inter['tools']['source_sha256']==inventory['check_original_intersections.py'] and inter['tools']['optimization_level']==opt,'Exact intersection completeness/tool')
   contacts=inter['all_actual_intersections'];track(local(base,contacts['path']),contacts['sha256']);require(contacts['record_count']==inter['actual_intersection_pair_count']==324715,'Exact contact count')
   ic=read(base/'intersection-controls/controls-summary.json');yes(ic,['passed'],'Intersection controls');require(ic['checker_sha256']==inventory['check_original_intersections.py'] and ic['controls_source_sha256']==inventory['check_intersection_controls.py'] and ic['optimization_level']==opt and ic['predicate_case_count']==len(ic['predicate_cases'])==2736 and len(ic['broad_phase_bruteforce_cases'])==36 and ic['subprocess_execution_count']==len(ic['subprocess_executions'])==48,'Intersection control scope')
   require(all(r['matches_bruteforce'] is True for r in ic['broad_phase_bruteforce_cases']),'Broad phase control failure')
   for row in ic['subprocess_executions']:
    childpath=base/'intersection-controls'/row['report'];track(childpath,row['report_sha256']);child=read(childpath);require(type(row['expected_pass']) is bool and child['passed'] is row['expected_pass'] and child['strict_passed'] is row['expected_pass'] and row['exit_code']==(0 if row['expected_pass'] else 2 if 'error_type' in child else 1),'Intersection control child outcome')
   exactdir=base/'exact-recorded-rays';ex=read(exactdir/'exact-recorded-ray-summary.json');yes(ex,['completed','all_selected_rays_exactly_classified','all_selected_first_chords_ge_0p8mm','all_original_inputs_and_sources_unchanged','original_raw_and_exact_intersection_prerequisites_passed','full_original_csv_exact_face_sample_coverage','all_flagged_samples_selected','all_selected_descriptors_match_original_full_csv'],'Exact flagged rays')
   require(ex['optimization_level']==opt and ex['full_original_csv_rows_verified']==373300 and ex['total_flagged_samples']==ex['selected_samples']==12 and ex['original_numerical_strict_passed'] is False and 'error' not in ex,'Exact-ray scope/semantics')
   bind={'stl':frozen/'models/v17/model.stl','flags':std/'dense'/dense['flagged_samples_file'],'dense_report':std/'dense/dense-check.json','raw_report':std/'raw/raw-mesh-check.json','intersections_report':base/'intersections.json','exact_core_source':ind/'exact_ray_diagnosis.py','diagnostic_source':ind/'diagnose_recorded_cpp_rays.py','original_csv':csvpath}
   require(set(ex['input_and_tool_sha256'])==set(bind),'Exact-ray input set')
   for k,p in bind.items():track(p,ex['input_and_tool_sha256'][k])
   detail=local(exactdir,ex['detail_file']);track(detail,ex['detail_sha256'])
   with gzip.open(detail,'rt') as f:rows=[json.loads(line) for line in f]
   require(len(rows)==12 and {(r['original_face_index'],r['sample_index']) for r in rows}=={(r['original_face_index'],r['sample_index']) for r in flags},'Exact selected rows disagree with flags')
   for r in rows:
    yes(r,['exact_classification_completed','supplied_lossless_descriptor_line_classified','original_run_lossless_descriptor_used','conservative_first_solid_chord_ge_0p8mm'],'Exact detail')
    require(Fraction(r['conservative_first_solid_chord_squared_mm2_exact'])>=Fraction(16,25),'Exact detail short chord')
   modes[mode]={'triangles':raw['triangles'],'layers':sec['sampled_layers'],'polygons':sec['original_polygon_count'],'rays':dense['samples'],'flags':len(flags),'original_strict_passed':False,'minimum_numerical_chord_mm':dense['minimum_first_chord_mm'],'minimum_flagged_exact_chord_mm_approx':min(r['conservative_first_solid_chord_mm_approx'] for r in rows),'candidate_pairs':inter['broad_phase']['candidate_pairs_checked'],'bad_pairs':0,'dense_decoded_sha256':dense['uncompressed_csv_sha256'],'section_detail_sha256':sec['detail_sha256'],'flag_file_sha256':dense['flagged_samples_sha256'],'exact_detail_sha256':ex['detail_sha256'],'intersection_contacts_sha256':contacts['sha256'],'candidate_sequence_sha256':inter['broad_phase']['candidate_sequence_sha256']}
  require(modes['normal']==modes['optimized'],'Normal/optimized scientific evidence differs');report['geometry']=modes
  require(all(resumed['source_rebuild'].values()),'Source rebuild result')
  for name in ['model.stl','color-regions.json']:track(run/'reproduction/models/v17'/name,track(frozen/'models/v17'/name))
  source=read(run/'source-scene-reproduction/source-scene-audit.json');yes(source,['passed','all_eleven_camera_definitions_match','exact_scene_state_matches','source_unchanged','original_blend_unchanged','manifest_unchanged'],'Source scene reproduction');require(source['state_difference_count']==0 and source['state_differences']==[] and set(source['camera_definition_checks'])==VIEWS and all(source['camera_definition_checks'].values()),'Source state/cameras differ')
  track(ind/'compare_source_scene.py',source['checker_sha256']);track(frozen/'models/v17/render_preview.py',source['source_sha256']);track(frozen/'models/v17/scene.blend',source['original_blend_sha256']);track(frozen/'previews/v17/render-manifest.json',source['manifest_sha256'])
  track(run/'reproduction/models/v17/scene.blend',source['generated_blend_sha256']);require(read(run/'source-scene-reproduction/original-scene-state.json')==read(run/'source-scene-reproduction/source-scene-state.json'),'Source scene-state evidence differs')
  renderdir=run/'saved-blend-rerenders';render=read(renderdir/'blend-rerender-audit.json');yes(render,['passed','strict_passed'],'Saved Blend rerender');require(render['inspect_only'] is False and len(render['views'])==11 and {r['view'] for r in render['views']}==VIEWS and all(v is True for v in render['checks'].values()),'Incomplete render audit')
  for k,p in [('source_sha256',ind/'inspect_and_rerender_blend.py'),('png_comparator_source_sha256',ind/'png_exact_compare.py'),('original_blend_sha256',frozen/'models/v17/scene.blend'),('original_stl_sha256',frozen/'models/v17/model.stl'),('original_manifest_sha256',frozen/'previews/v17/render-manifest.json')]:track(p,render[k])
  public=run/'public-previews';pubman=read(public/'render-manifest.json');cleanup=read(public/'metadata-cleanup-binding.json');yes(cleanup,['passed'],'Public cleanup');require(set(pubman['views'])==set(cleanup['views'])==VIEWS and pubman['stl_sha256']==cleanup['stl_sha256']==STL and set(cleanup['removal_whitelist'])==set(SANITIZE_TEXT_KEYS),'Public view/policy binding');track(public/'render-manifest.json',cleanup['public_manifest_sha256']);track(ind/'png_exact_compare.py',cleanup['sanitizer_sha256']);track(ind/'sanitize_png_previews.py',cleanup['batch_source_sha256']);track(frozen/'previews/v17/render-manifest.json',cleanup['source_manifest_sha256'])
  png_results={}
  for row in render['views']:
   name=row['view'];m=pubman['views'][name];c=cleanup['views'][name];require(row['posed_world_directed_geometry_matches_stl'] is True,'Per-camera geometry mismatch');require(c==row['original_metadata_cleanup'],'Batch cleanup differs from rerender-original cleanup')
   track(public/(name+'.png'),m['sha256']);track(renderdir/'sanitized-original'/(name+'.png'),m['sha256']);track(frozen/'previews/v17'/(name+'.png'),m['original_raw_png_sha256']);track(renderdir/(name+'.png'),row['rerendered_raw_png_sha256']);track(renderdir/'sanitized-rerender'/(name+'.png'),row['rerendered_metadata_cleanup']['sanitized_png_sha256'])
   comparison=compare_png(public/(name+'.png'),renderdir/'sanitized-rerender'/(name+'.png'),m['sha256']);yes(comparison,['passed','decoded_rgba_bytes_identical','all_nonvolatile_metadata_identical'],'Public-vs-rerender pixels/metadata');require(m['decoded_rgba_sha256']==c['sanitized_rgba_sha256']==comparison['original_rgba_sha256']==comparison['rerendered_rgba_sha256'],'Public RGBA binding');require(m['sha256']==c['sanitized_png_sha256']==comparison['original_png_sha256'] and m['original_raw_png_sha256']==c['original_png_sha256']==row['original_raw_png_sha256'],'Public raw/clean SHA fields');require(comparison==row['sanitized_png_comparison'],'Recorded rerender comparison differs from postflight')
   png_results[name]={'public_png_sha256':m['sha256'],'original_raw_png_sha256':m['original_raw_png_sha256'],'decoded_rgba_sha256':m['decoded_rgba_sha256'],'decoded_rgba_bytes_identical':True,'all_surviving_metadata_identical':True,'cleaned_file_bitwise_identical':comparison['whole_png_file_bytes_identical'],'raw_file_bitwise_identical':row['raw_png_files_bitwise_identical']}
  require('/workspace/' not in (public/'render-manifest.json').read_text() and '/workspace/' not in (public/'metadata-cleanup-binding.json').read_text(),'Private path in public PNG bindings')
  report['images']=png_results;report['source_stl_bitwise_identical']=True;report['source_colour_regions_bitwise_identical']=True;report['source_scene_state_matches']=True
  for logical,row in tracked.items():
   root,rel=logical.split('/',1);p=(qa if root=='independent-qa' else author)/rel;require(p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'Evidence changed during postflight: '+logical)
  require(sha(__file__)==report['postflight_source_sha256'],'Postflight source changed');report['all_read_evidence_unchanged']=True;report['evidence_inventory']=tracked;report['bounded_verification_passed']=True
 except Exception as e:report.update(bounded_verification_passed=False,error_type=type(e).__name__,error=str(e))
 (args.out/'postflight-report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({'bounded_verification_passed':report['bounded_verification_passed'],'error':report.get('error'),'tracked_files':len(tracked)}));return 0 if report['bounded_verification_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
