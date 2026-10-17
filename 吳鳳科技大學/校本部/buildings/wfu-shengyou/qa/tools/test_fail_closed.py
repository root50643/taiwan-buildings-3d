"""Positive baseline and fail-closed report mutations; never inspects a model."""
from pathlib import Path
import argparse,copy,json,shutil,tempfile
from run_full_qa import inspect_mode,source_inventory,read
from qa_common import checker_inventory,sha256,write_json,require

def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--stl',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    baseline=read(a.baseline/'full-qa-summary.json');require(baseline['passed'] is True and baseline['tool_sources_sha256']==source_inventory(),'Positive baseline/tool binding mismatch')
    digest=sha256(a.stl);expected=baseline['expected_longest_mm'];exits=baseline['modes']['normal']['child_exit_codes'];rows=[]
    cases=[('raw_missing_flag','standard/raw/raw-mesh-check.json',lambda r:r['checks'].pop('exact_coordinate_vertex_links_single_cycles')),
           ('raw_false_flag','standard/raw/raw-mesh-check.json',lambda r:r['checks'].update(single_surface_no_internal_shell=False)),
           ('raw_non_boolean_pass','standard/raw/raw-mesh-check.json',lambda r:r.update(passed='true')),
           ('raw_wrong_stl','standard/raw/raw-mesh-check.json',lambda r:r.update(stl_sha256='0'*64)),
           ('aggregate_missing_checks','standard/qa-summary.json',lambda r:r.update(checks={})),
           ('aggregate_one_required_flag_missing','standard/qa-summary.json',lambda r:r['checks'].pop('all_gate_check_flags_true')),
           ('aggregate_one_false_flag','standard/qa-summary.json',lambda r:r['checks'].update(all_gate_check_flags_true=False)),
           ('dense_short_ray_count','standard/dense/dense-check.json',lambda r:r.update(under_0p8mm_count=1)),
           ('dense_flag_count','standard/dense/dense-check.json',lambda r:r.update(flagged_sample_count=1)),
           ('exact_incomplete','intersections.json',lambda r:r.update(completed=False)),
           ('exact_aabb_incomplete','intersections.json',lambda r:r['broad_phase'].update(all_bbox_overlapping_pairs_completed=False)),
           ('exact_bad_pair','intersections.json',lambda r:r.update(bad_pair_count=1,bad_pairs=[{'bad':True}])),
           ('exact_wrong_source','intersections.json',lambda r:r['tools'].update(source_sha256='0'*64)),
           ('intersection_controls_false','intersection-controls/controls-summary.json',lambda r:r.update(passed=False)),
           ('intersection_controls_empty_broadphase','intersection-controls/controls-summary.json',lambda r:r.update(broad_phase_bruteforce_cases=[])),
           ('intersection_controls_wrong_mode','intersection-controls/controls-summary.json',lambda r:r.update(optimization_level=1))]
    with tempfile.TemporaryDirectory(dir=a.out,prefix='mutation-work-') as temp:
        base=Path(temp)/'normal';shutil.copytree(a.baseline/'normal',base)
        inspect_mode(base,digest,expected,checker_inventory(),0,exits,a.stl)
        rows.append({'case':'unchanged_positive_baseline','expected_accept':True,'passed':True})
        for name,rel,mutate in cases:
            target=base/rel;original=target.read_bytes();r=json.loads(original);mutate(r);write_json(target,r)
            # Keep the per-gate ledger current, so its rejection is substantive.
            ledgerpath=base/'standard/qa-summary.json';oldledger=ledgerpath.read_bytes()
            if rel.startswith('standard/') and rel!='standard/qa-summary.json':
                ledger=json.loads(oldledger)
                for row in ledger['gate_reports']:
                    if 'standard/'+row['report_file']==rel:row['report_sha256']=sha256(target)
                write_json(ledgerpath,ledger)
            write_json(a.out/(name+'.mutated.json'),r)
            try:inspect_mode(base,digest,expected,checker_inventory(),0,exits,a.stl)
            except Exception as error:rows.append({'case':name,'expected_accept':False,'passed':True,'error_type':type(error).__name__,'error':str(error).replace(str(base),'[mutation]')})
            else:raise RuntimeError('Fail-open acceptance: '+name)
            target.write_bytes(original)
            if rel!='standard/qa-summary.json':ledgerpath.write_bytes(oldledger)
        victim=base/'standard/raw/raw-mesh-check.json';original=victim.read_bytes();victim.unlink()
        try:inspect_mode(base,digest,expected,checker_inventory(),0,exits,a.stl)
        except Exception:rows.append({'case':'missing_original_report','expected_accept':False,'passed':True})
        else:raise RuntimeError('Missing report accepted')
        victim.write_bytes(original)
        badexits=dict(exits);badexits['standard']=1
        try:inspect_mode(base,digest,expected,checker_inventory(),0,badexits,a.stl)
        except Exception:rows.append({'case':'nonzero_child_exit','expected_accept':False,'passed':True})
        else:raise RuntimeError('Nonzero exit accepted')
        exit_cases=[('empty_stage_map',{}),('missing_stage_map',{k:v for k,v in exits.items() if k!='dense-evidence'}),('extra_stage_map',dict(exits,unexpected=0)),('boolean_stage_status',dict(exits,standard=False)),('float_stage_status',dict(exits,standard=0.0)),('null_stage_status',dict(exits,standard=None)),('string_stage_status',dict(exits,standard='0'))]
        for name,altered in exit_cases:
            try:inspect_mode(base,digest,expected,checker_inventory(),0,altered,a.stl)
            except Exception as error:rows.append({'case':name,'expected_accept':False,'passed':True,'error':str(error)})
            else:raise RuntimeError('Invalid stage exit map accepted: '+name)
    write_json(a.out/'results.json',{'passed':True,'source_sha256':sha256(__file__),'cases':rows,'case_count':len(rows)})
    print(json.dumps({'passed':True,'case_count':len(rows)}))
if __name__=='__main__':main()
