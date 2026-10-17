"""Fixed WFU v12 frozen STL 83482136 read-only postflight branch, preserving numerical strict=false.
Generic predicate/control inspection is copied from the verified run_full_qa
inspect_mode. Exact recorded-line requirements follow the verified Zongde
postflight branch, with this frozen input, actual counts and current dense audit.
No producer report, original sample, flag, tolerance or geometric tool is edited.
"""
from run_full_qa import *
import gzip
from fractions import Fraction
def inspect_mode(base,stl_hash,expected_longest,inventory,opt,exits,stl_path=None):
    std=base/'standard'; summary=read(std/'qa-summary.json')
    require(summary.get('passed') is False and summary.get('strict_passed') is False,'Original numerical aggregate strict=false must remain false')
    expected_false={'all_gates_explicitly_pass','all_gate_check_flags_true','zero_short_or_flagged_dense_samples'}
    require(set(summary.get('checks',{}))==AGGREGATE_CHECKS and all(type(v) is bool and v is (k not in expected_false) for k,v in summary['checks'].items()),'Unexpected aggregate flag semantics')
    require(summary.get('stl_sha256')==stl_hash and summary.get('checker_sources_sha256')==inventory and summary.get('optimized_python') is bool(opt),'Standard aggregate binding/mode mismatch')
    require(type(exits) is dict and set(exits)=={'standard','intersections','intersection-controls','dense-evidence'} and len(exits)==4,'Incomplete or unexpected child stage exit map')
    require(all(type(code) is int and code==(1 if name=='standard' else 0) for name,code in exits.items()),'Unexpected typed child stage exit')
    reports={};required={k:set(v) for k,v in REQUIRED_CHECKS.items()};required['raw'].add('requested_longest_extent_mm')
    paths={'raw':'raw-mesh-check.json','sections':'section-check.json','dense':'dense-check.json','controls':'control-check.json'}
    require(len(summary.get('gate_reports',[]))==4 and {r['gate'] for r in summary['gate_reports']}==set(paths),'Incomplete standard gate ledger')
    for name,file in paths.items():
        path=std/name/file;r=read(path);reports[name]=r
        ledger=next(x for x in summary['gate_reports'] if x['gate']==name)
        require(ledger['report_sha256']==sha256(path) and type(ledger['returncode']) is int and ledger['returncode']==(1 if name=='dense' else 0) and ledger['passed'] is (name!='dense'),'Standard gate ledger differs')
        require(r.get('passed') is (name!='dense') and r.get('strict_passed') is (name!='dense') and set(r.get('checks',{}))==required[name] and all(type(v) is bool and v is (not(name=='dense' and k=='all_original_ray_intervals_and_controls_valid')) for k,v in r['checks'].items()),'Gate incomplete or unexpected failure: '+name)
        require(r.get('checker_sources_sha256')==inventory,'Gate checker sources mismatch')
        if name!='controls': require(r.get('stl_sha256')==stl_hash,'Gate is for another STL')
    raw,sec,dense=reports['raw'],reports['sections'],reports['dense']
    require(raw.get('expected_longest_mm')==expected_longest and raw.get('surface_shells')==1,'Raw dimension/surface binding differs')
    for fk,hk in [('detail_file','detail_sha256'),('failure_file','failure_sha256')]:artifact(std/'sections',sec[fk],sec[hk])
    d=audit(std/'dense/dense-check.json',stl_path)
    require(d['csv_rows_verified']==10*raw['triangles']==209460 and dense['flagged_sample_count']==33 and dense['under_0p8mm_count']==0 and d['original_numerical_strict_passed'] is False,'Dense original coverage/flag semantics fail')
    control=reports['controls'];require(control['control_runs']==len(control['controls']) and control['control_runs']>0,'Generic control run count differs')
    for row in control['controls']:
        p=std/'controls'/row['report_file'];require(p.is_file() and sha256(p)==row['report_sha256'],'Generic control child hash differs')
        r=read(p);expect=row['expected_pass'];require(type(expect) is bool and row['expectation_verified'] is True and r.get('passed') is expect and r.get('strict_passed') is expect and row['returncode']==(0 if expect else 1),'Generic control outcome differs')
        require(row['expected_false_check'] is None or r.get('checks',{}).get(row['expected_false_check']) is False,'Negative control rejected for another reason')
    inter=read(base/'intersections.json')
    require(all(inter.get(k) is True for k in ['passed','strict_passed','completed','input_unchanged_during_check']),'Exact intersections incomplete/failed')
    require(inter['stl_sha256']==inter['stl_sha256_after_check']==stl_hash and inter['original_face_count']==raw['triangles'] and inter['bad_pair_count']==0 and inter['bad_pairs']==[] and inter['degenerate_original_faces']==[],'Exact contact/input/count failure')
    require(inter['broad_phase'].get('all_bbox_overlapping_pairs_completed') is True and inter['tools']['source_sha256']==inventory['check_original_intersections.py'] and inter['tools']['optimization_level']==opt,'Exact contact completeness/source/mode mismatch')
    contact=inter['all_actual_intersections'];artifact(base,contact['path'],contact['sha256']);require(contact['record_count']==inter['actual_intersection_pair_count'],'Contact record count mismatch')
    ic=read(base/'intersection-controls/controls-summary.json')
    require(ic.get('passed') is True and ic['checker_sha256']==inventory['check_original_intersections.py'] and ic['controls_source_sha256']==inventory['check_intersection_controls.py'] and ic['optimization_level']==opt,'Intersection controls binding/mode mismatch')
    require(ic['predicate_case_count']==len(ic['predicate_cases'])>0 and ic['subprocess_execution_count']==len(ic['subprocess_executions'])>0 and len(ic['broad_phase_bruteforce_cases'])==36 and all(x['matches_bruteforce'] is True for x in ic['broad_phase_bruteforce_cases']),'Incomplete intersection controls')
    for row in ic['subprocess_executions']:
        p=artifact(base/'intersection-controls',row['report'],row['report_sha256']);r=read(p);expect=row['expected_pass']
        require(type(expect) is bool and r['passed'] is expect and r['strict_passed'] is expect and row['exit_code']==(0 if expect else 2 if 'error_type' in r else 1),'Intersection control child outcome differs')
    require(stl_hash=='8348213614296746732da6a8024821ff48536e847419fe13545dc1ab20730ca0' and expected_longest==220.0,'This case audit is only for the WFU v12 frozen STL 83482136 input')
    require(raw['triangles']==20946 and raw['extents_mm']==[220.0,186.0,114.5] and sec['sampled_layers']==1718 and sec['original_polygon_count']==7752,'Frozen case counts differ')
    require(sec['failed_layer_count']==sec['failed_polygon_count']==0 and dense['minimum_first_chord_mm']==1.0,'Unexpected geometric failure or minimum')
    exactdir=base/'exact-recorded-rays';ex=read(exactdir/'exact-recorded-ray-summary.json')
    required_exact=['completed','all_selected_rays_exactly_classified','all_selected_first_chords_ge_0p8mm','all_original_inputs_and_sources_unchanged','original_raw_and_exact_intersection_prerequisites_passed','full_original_csv_exact_face_sample_coverage','all_flagged_samples_selected','all_selected_descriptors_match_original_full_csv']
    require(all(ex.get(k) is True for k in required_exact) and 'error' not in ex,'Exact original-ray classification incomplete')
    require(ex['optimization_level']==opt and ex['full_original_csv_rows_verified']==209460 and ex['total_flagged_samples']==ex['selected_samples']==33 and ex['original_numerical_strict_passed'] is False,'Exact-ray coverage or strict semantics differ')
    bind={'stl':Path(stl_path),'flags':std/'dense'/dense['flagged_samples_file'],'dense_report':std/'dense/dense-check.json','raw_report':std/'raw/raw-mesh-check.json','intersections_report':base/'intersections.json','exact_core_source':QA/'tools/exact_ray_diagnosis.py','diagnostic_source':QA/'tools/diagnose_recorded_cpp_rays.py','original_csv':std/'dense'/dense['csv_file']}
    require(set(ex['input_and_tool_sha256'])==set(bind) and all(sha256(p)==ex['input_and_tool_sha256'][k] for k,p in bind.items()),'Exact-ray input/source binding differs')
    detail=artifact(exactdir,ex['detail_file'],ex['detail_sha256'])
    with gzip.open(detail,'rt') as stream: exactrows=[json.loads(line) for line in stream]
    flags=json.loads(gzip.decompress(bind['flags'].read_bytes()));key=lambda r:(r['original_face_index'],r['sample_index'])
    require(len(exactrows)==len(flags)==33 and len({key(r) for r in exactrows})==33 and {key(r) for r in exactrows}=={key(r) for r in flags},'Exact selected rows do not cover original flags')
    require({key(r) for r in flags}=={(7016, 0), (6426, 0), (12518, 0), (18705, 0), (5178, 0), (16658, 0), (17056, 0), (16659, 4), (3285, 0), (2838, 0), (16659, 7), (12520, 0), (18687, 0), (6478, 0), (6960, 0), (2948, 0), (16631, 0), (11223, 0), (2842, 0), (16659, 0), (12275, 0), (7006, 0), (5619, 0), (17480, 0), (17057, 0), (12519, 0), (18675, 0), (2949, 0), (12290, 0), (5612, 0), (17957, 0), (17059, 0), (16634, 0)},'Frozen WFU original flagged event differs')
    flagmap={key(r):r for r in flags}
    for row in exactrows:
        require(all(row.get(k) is True for k in ['exact_classification_completed','supplied_lossless_descriptor_line_classified','original_run_lossless_descriptor_used','conservative_first_solid_chord_ge_0p8mm']),'Exact row incomplete')
        require(row['original_cpp_descriptor']==flagmap[key(row)]['original_cpp_row'] and row['original_numerical_reasons']==flagmap[key(row)]['reasons'],'Exact row is not the original recorded event')
        require(Fraction(row['conservative_first_solid_chord_squared_mm2_exact'])>=Fraction(16,25),'Exact first chord is short')
        intervals=row['classified_open_intervals'];require(intervals[0]['state']=='outside' and intervals[1]['state']=='inside' and intervals[-1]['state']=='outside','Exact interval ordering fails')
    require(json.loads(gzip.decompress((std/'dense'/dense['short_chords_file']).read_bytes()))==[] and json.loads(gzip.decompress((std/'sections'/sec['failure_file']).read_bytes()))==[],'Geometric failure details are nonempty')
    return {'triangles':raw['triangles'],'extents_mm':raw['extents_mm'],'surface_shells':raw['surface_shells'],'sections_detail_sha256':sec['detail_sha256'],'sections_failure_sha256':sec['failure_sha256'],'dense_csv_decoded_sha256':dense['uncompressed_csv_sha256'],'dense_flags_sha256':dense['flagged_samples_sha256'],'dense_short_sha256':dense['short_chords_sha256'],'exact_contacts_sha256':contact['sha256'],'candidate_sequence_sha256':inter['broad_phase']['candidate_sequence_sha256'],'dense_original_descriptors_verified':d['lossless_descriptors_verified'],'original_numerical_strict_passed':False,'exact_flag_count':len(exactrows),'exact_detail_sha256':ex['detail_sha256'],'minimum_flagged_exact_chord_mm_approx':min(r['conservative_first_solid_chord_mm_approx'] for r in exactrows)}
