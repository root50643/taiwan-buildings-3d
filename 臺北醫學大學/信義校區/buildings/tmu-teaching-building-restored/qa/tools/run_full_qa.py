"""Fresh normal and optimized original-STL QA, exact contacts, and fail-closed binding.
All stages continue after failed geometry to preserve evidence. No waivers exist.
"""
from pathlib import Path
import argparse,hashlib,json,math,subprocess,sys
QA=Path(__file__).resolve().parents[1];VER=QA/'verification'
sys.path.insert(0,str(VER))
from qa_common import require,sha256,write_json,checker_inventory
from run_qa import REQUIRED_CHECKS
from validate_dense_evidence import audit
AGGREGATE_CHECKS = {
    "all_gates_explicitly_pass", "all_gate_check_flags_true",
    "all_required_gate_check_keys_present", "original_stl_unchanged",
    "all_geometry_reports_bound_to_current_stl", "checker_sources_unchanged_during_run",
    "all_reports_bound_to_current_checkers", "three_required_layer_offsets",
    "every_original_face_has_ten_rays", "zero_short_or_flagged_dense_samples",
    "all_full_detail_artifact_hashes_current", "dense_lossless_csv_hash_current"}

def source_inventory():
    return {str(p.relative_to(QA)):sha256(p) for folder in [VER,QA/'tools'] for p in sorted(folder.glob('*')) if p.suffix in ('.py','.cpp')}
def fresh(path): require(not path.exists(),'Output must be new: '+str(path));path.mkdir(parents=True)
def run(command,out,logname):
    result=subprocess.run(command,capture_output=True,text=True)
    (out/(logname+'.stdout.txt')).write_text(result.stdout);(out/(logname+'.stderr.txt')).write_text(result.stderr)
    return result.returncode
def read(path): return json.loads(Path(path).read_text())
def artifact(base,name,digest):
    require(isinstance(name,str) and Path(name).name==name,'Artifact reference must be a basename')
    p=base/name;require(p.is_file() and sha256(p)==digest,'Missing/changed artifact: '+str(p));return p

def inspect_mode(base,stl_hash,expected_longest,inventory,opt,exits,stl_path=None):
    std=base/'standard'; summary=read(std/'qa-summary.json')
    require(summary.get('passed') is True and summary.get('strict_passed') is True,'Standard aggregate did not strictly pass')
    require(set(summary.get('checks',{}))==AGGREGATE_CHECKS and all(v is True for v in summary['checks'].values()),'False/missing standard aggregate flags')
    require(summary.get('stl_sha256')==stl_hash and summary.get('checker_sources_sha256')==inventory and summary.get('optimized_python') is bool(opt),'Standard aggregate binding/mode mismatch')
    require(type(exits) is dict and set(exits)=={'standard','intersections','intersection-controls','dense-evidence'} and len(exits)==4,'Incomplete or unexpected child stage exit map')
    require(all(type(code) is int and code==0 for code in exits.values()),'Child stage exit must be explicit integer zero')
    reports={};required={k:set(v) for k,v in REQUIRED_CHECKS.items()};required['raw'].add('requested_longest_extent_mm')
    paths={'raw':'raw-mesh-check.json','sections':'section-check.json','dense':'dense-check.json','controls':'control-check.json'}
    require(len(summary.get('gate_reports',[]))==4 and {r['gate'] for r in summary['gate_reports']}==set(paths),'Incomplete standard gate ledger')
    for name,file in paths.items():
        path=std/name/file;r=read(path);reports[name]=r
        ledger=next(x for x in summary['gate_reports'] if x['gate']==name)
        require(ledger['report_sha256']==sha256(path) and ledger['returncode']==0 and ledger['passed'] is True,'Standard gate ledger differs')
        require(r.get('passed') is True and r.get('strict_passed') is True and set(r.get('checks',{}))==required[name] and all(v is True for v in r['checks'].values()),'Gate incomplete or false: '+name)
        require(r.get('checker_sources_sha256')==inventory,'Gate checker sources mismatch')
        if name!='controls': require(r.get('stl_sha256')==stl_hash,'Gate is for another STL')
    raw,sec,dense=reports['raw'],reports['sections'],reports['dense']
    require(raw.get('expected_longest_mm')==expected_longest and raw.get('surface_shells')==1,'Raw dimension/surface binding differs')
    for fk,hk in [('detail_file','detail_sha256'),('failure_file','failure_sha256')]:artifact(std/'sections',sec[fk],sec[hk])
    d=audit(std/'dense/dense-check.json',stl_path)
    require(d['csv_rows_verified']==10*raw['triangles'] and dense['flagged_sample_count']==dense['under_0p8mm_count']==0,'Dense coverage/strict flags fail')
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
    return {'triangles':raw['triangles'],'extents_mm':raw['extents_mm'],'surface_shells':raw['surface_shells'],'sections_detail_sha256':sec['detail_sha256'],'sections_failure_sha256':sec['failure_sha256'],'dense_csv_decoded_sha256':dense['uncompressed_csv_sha256'],'dense_flags_sha256':dense['flagged_samples_sha256'],'dense_short_sha256':dense['short_chords_sha256'],'exact_contacts_sha256':contact['sha256'],'candidate_sequence_sha256':inter['broad_phase']['candidate_sequence_sha256'],'dense_original_descriptors_verified':d['lossless_descriptors_verified']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stl',type=Path,required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--expected-longest-mm',type=float,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    fresh(a.out);a.stl=a.stl.resolve();before=source_inventory();inv=checker_inventory();report={'passed':False,'strict_passed':False,'completed':False,'stl_sha256':a.expected_sha256,'expected_longest_mm':a.expected_longest_mm,'tool_sources_sha256':before,'checks':{},'modes':{},'scope':'Original raw STL, finite original XY sections/normal rays and exact original triangle pairs only. No waivers, architecture approval, source/render audit, global wall guarantee or physical print guarantee.'}
    try:
        require(math.isfinite(a.expected_longest_mm) and a.expected_longest_mm>0,'Expected extent must be finite and positive');require(sha256(a.stl)==a.expected_sha256,'Input hash differs before QA')
        for mode,flags,opt in [('normal',['-B'],0),('optimized',['-B','-O'],1)]:
            base=a.out/mode;base.mkdir();prefix=[sys.executable,*flags]
            commands={'standard':prefix+[str(VER/'run_qa.py'),'--stl',str(a.stl),'--out',str(base/'standard'),'--expected-longest-mm',str(a.expected_longest_mm)],'intersections':prefix+[str(VER/'check_original_intersections.py'),'--stl',str(a.stl),'--expected-sha256',a.expected_sha256,'--out',str(base/'intersections.json'),'--progress'],'intersection-controls':prefix+[str(VER/'check_intersection_controls.py'),'--out-dir',str(base/'intersection-controls')],'dense-evidence':prefix+[str(QA/'tools/validate_dense_evidence.py'),'--dense-report',str(base/'standard/dense/dense-check.json'),'--stl',str(a.stl),'--out',str(base/'dense-evidence.json')]}
            exits={}
            for name,command in commands.items():
                exits[name]=run(command,base,name);print(json.dumps({'mode':mode,'stage':name,'exit':exits[name]}),flush=True)
            state={'child_exit_codes':exits,'strict_passed':False}
            try: state['science']=inspect_mode(base,a.expected_sha256,a.expected_longest_mm,inv,opt,exits,a.stl);state['strict_passed']=True
            except Exception as error: state.update(error_type=type(error).__name__,error=str(error))
            report['modes'][mode]=state;write_json(a.out/'full-qa-progress.json',report)
        checks={'both_modes_strictly_pass':all(r['strict_passed'] is True for r in report['modes'].values()),'normal_optimized_scientific_evidence_identical':all('science' in r for r in report['modes'].values()) and report['modes']['normal'].get('science')==report['modes']['optimized'].get('science'),'original_stl_unchanged':sha256(a.stl)==a.expected_sha256,'tool_sources_unchanged':source_inventory()==before}
        report.update(completed=True,checks=checks,passed=all(checks.values()),strict_passed=all(checks.values()))
    except Exception as error:report.update(error_type=type(error).__name__,error=str(error))
    report['evidence_inventory']={str(p.relative_to(a.out)):{'bytes':p.stat().st_size,'sha256':sha256(p)} for p in sorted(a.out.rglob('*')) if p.is_file()}
    write_json(a.out/'full-qa-summary.json',report);print(json.dumps({'passed':report['passed'],'summary':str(a.out/'full-qa-summary.json')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
