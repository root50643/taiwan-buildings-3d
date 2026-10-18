"""Run unchanged bounded geometry QA on the fixed six v2 print-oriented STLs.

No original v4 or synthetic control is re-run. No input is repaired or altered.
Each raw CLI exit status remains authoritative; exact flagged-pair diagnosis
is supplementary and never changes the bounded gate into a pass.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
FIXED={
 '01-base-floor1-upright':'bc2ac743cacb4cb9584a62d79df2541b2cb75a463e4bc43d10b2ad9e280f0243',
 '02-floor2-slab-inverted':'4440eeca45530769bf11b8e4094c82a0744e6ba160d692fda7fbf9f8f0f30ddd',
 '03-floor2-upper-upright':'b1d6d8e1ffa61198adc1898d8fe5ff5f47e7ea011fbc67d1b87108075d80d6e6',
 '04-floor3-slab-inverted':'720c05949b35a68535a5aff298507e32b78b2a449335b64a0661eafa749d8957',
 '05-floor3-main-and-tower-upright':'8ecc913447812bc613f469be6572bd56f9fdd1de6555a62886b7927ac3507bd1',
 '06-floor3-diagonal-rail-upright':'c2527780d644eef28a4a5431a40b6027541123d9c29eef0dc60be83da615b8ea',
}
CHECKER='0c0ca4e69386b2a5d7a531415eb4ca3ca16c599177c8ffdd8cfee37ed657b43c'
DIAG='c8e9771b1c9dba285ae796e29d806b9f49fd681e06c098965e3cbccd3141b42c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def execute(script,args,out,prefix):
    command=[sys.executable,'-B',str(ROOT/script),*map(str,args)]
    run=subprocess.run(command,capture_output=True,text=True,encoding='utf8')
    (out/f'{prefix}.stdout.log').write_text(run.stdout,encoding='utf8')
    (out/f'{prefix}.stderr.log').write_text(run.stderr,encoding='utf8')
    (out/f'{prefix}.exit-status.txt').write_text(str(run.returncode)+'\n',encoding='utf8')
    return run.returncode


def inspect_piece(part_id,out):
    work=out/part_id;work.mkdir()
    stl=out/'inputs'/(part_id+'.stl');report=work/'qa-report.json'
    code=execute('independent_geometry_qa.py',[stl,'--json',report],work,'geometry')
    if not report.is_file():
        return {'id':part_id,'stl_sha256':sha(stl),'geometry_exit_status':code,'completed_report':False,'error':'Checker did not produce a valid completed report; inspect retained stderr.'}
    raw=json.loads(report.read_text(encoding='utf8'))
    if raw['sha256']!=FIXED[part_id]:raise ValueError('QA report input binding mismatch')
    flags=raw['self_intersections']['unexpected_contacts_or_intersections']
    diagnosis=None;diag_code=None
    if flags:
        diagnostic=work/'flag-diagnosis.json'
        diag_code=execute('flag_diagnosis.py',[stl,report,'--json',diagnostic],work,'flag-diagnosis')
        if diagnostic.is_file():
            diagnosis=json.loads(diagnostic.read_text(encoding='utf8'))
            execute('summarize_flag_diagnosis.py',[diagnostic,'--json',work/'flag-summary.json'],work,'flag-summary')
    risk_code=execute('measure_print_risks.py',[stl,report,'--json',work/'print-risk-measurement.json'],work,'print-risk')
    topo=raw['topology'];sec=raw['sections']
    result={'id':part_id,'stl_sha256':sha(stl),'completed_report':True,'geometry_exit_status':code,
        'raw_bounded_geometry_gate_passes':raw['passes_bounded_geometry_screen'],
        'topology':topo,'total_triangle_pairs':raw['self_intersections']['total_triangle_pairs'],
        'aabb_candidate_pairs_checked':raw['self_intersections']['aabb_candidate_pairs_checked'],
        'raw_numerical_intersection_flags':len(flags),
        'exact_flag_diagnosis_exit_status':diag_code,
        'exact_flag_classifications':diagnosis['classification_counts'] if diagnosis else None,
        'all_raw_flags_covered_once':diagnosis['all_flags_covered_once'] if diagnosis else None,
        'all_raw_flags_only_expected_contact':diagnosis['all_flagged_pairs_have_only_expected_contact'] if diagnosis else None,
        'exact_diagnostic_guard_errors':diagnosis['guard_errors'] if diagnosis else None,
        'section_count':sec['section_count'],'nonempty_section_count':sec['nonempty_section_count'],
        'invalid_or_open_section_count':sec['invalid_or_open_section_count'],
        'thin_feature_flagged_layer_count':sec['thin_feature_flagged_layer_count'],
        'sampled_thin_feature_screen_passes':sec['passes_sampled_thin_feature_screen'],
        'support_flagged_layer_count':sec['unsupported_envelope_layer_count'],
        'sampled_45_degree_support_screen_passes':sec['passes_sampled_support_screen'],
        'worst_outside_support_envelope_area_mm2':sec['worst_unsupported_envelope_area_mm2'],
        'minimum_print_z_mm':topo['bounds_mm'][0][2],
        'print_risk_measurement_exit_status':risk_code,
        'qa_report_sha256':sha(report),'checker_sha256':sha(ROOT/'independent_geometry_qa.py'),
        'versions':raw['versions'],'input_unchanged':sha(stl)==FIXED[part_id],
        'scope':'Digital mesh and finite layer screening at the supplied print orientation. No slicer, support creation/removal, G-code or physical print.'}
    (work/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--models-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();out=a.out.resolve()
    if not out.is_relative_to(ROOT.resolve()):raise ValueError('Outputs must remain under manufacturing-qa-staging')
    if out.exists():raise ValueError('Refusing to overwrite existing QA attempt directory')
    if sha(ROOT/'independent_geometry_qa.py')!=CHECKER or sha(ROOT/'flag_diagnosis.py')!=DIAG:raise ValueError('Unchanged checker/diagnostic hash guard failed')
    source_report=a.models_dir/'build-report.json';build=json.loads(source_report.read_text(encoding='utf8'))
    if len(build['parts'])!=6:raise ValueError('Requires exactly six fixed parts')
    for part in build['parts']:
        name=part['id'];path=a.models_dir/part['stl']
        if name not in FIXED or sha(path)!=FIXED[name] or part['stl_sha256']!=FIXED[name]:raise ValueError('Fixed input SHA-256 mismatch: '+name)
    out.mkdir();(out/'inputs').mkdir();shutil.copyfile(source_report,out/'source-build-report.json')
    for name in FIXED:shutil.copyfile(a.models_dir/(name+'.stl'),out/'inputs'/(name+'.stl'))
    fixed={'parts':FIXED,'source_build_report_sha256':sha(source_report),'checker_sha256':CHECKER,'flag_diagnosis_sha256':DIAG,
        'thresholds_unchanged':{'layer_height_mm':.2,'angle_from_vertical_degrees':45,'feature_width_mm':.8,'support_area_flag_threshold_mm2':.01,'intersection_tolerance_mm':1e-6},
        'coordinator_script_sha256':sha(Path(__file__)),'original_v4_and_original_controls_not_rerun':True}
    (out/'fixed-inputs.json').write_text(json.dumps(fixed,indent=2)+'\n',encoding='utf8')
    rows=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs={pool.submit(inspect_piece,name,out):name for name in FIXED}
        for future in as_completed(jobs):
            result=future.result();rows.append(result)
            print(json.dumps({'completed':result['id'],'raw_exit_status':result['geometry_exit_status'],'flags':result.get('raw_numerical_intersection_flags'),'thin_layers':result.get('thin_feature_flagged_layer_count'),'support_layers':result.get('support_flagged_layer_count') }),flush=True)
    rows.sort(key=lambda x:x['id'])
    summary={'fixed_inputs':fixed,'parts':rows,
        'all_six_raw_bounded_gates_pass':all(r.get('raw_bounded_geometry_gate_passes',False) for r in rows),
        'all_six_basic_topology_pass':all(r.get('topology',{}).get('passes_basic_solid_checks',False) for r in rows),
        'all_six_sampled_thin_screens_pass':all(r.get('sampled_thin_feature_screen_passes',False) for r in rows),
        'all_six_sampled_support_screens_pass':all(r.get('sampled_45_degree_support_screen_passes',False) for r in rows),
        'all_reported_pair_flags_have_exact_expected_contact':all(r.get('all_raw_flags_only_expected_contact',False) if r.get('raw_numerical_intersection_flags',0) else True for r in rows),
        'raw_failures_remain_unmodified':True,'no_slicer_or_physical_print_performed':True}
    (out/'SIX-PARTS-QA.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('parts','fixed_inputs')},indent=2),flush=True)
    raise SystemExit(0 if summary['all_six_raw_bounded_gates_pass'] else 1)


if __name__=='__main__':main()
