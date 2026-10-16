"""Fresh compact-package replay in retained external evidence, never overwrite archived evidence."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,subprocess,sys,uuid
R=Path(__file__).resolve().parent
MODE=['-B']+(['-O'] if sys.flags.optimize else [])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def verify_original_summary(directory,source_root):
    directory=Path(directory);source_root=Path(source_root)
    try:
        q=json.loads((directory/'qa-summary.json').read_text())
        if any(k in q for k in ['error','error_type']):raise ValueError('summary_has_error')
        keys={'all_gates_explicitly_pass','all_gate_check_flags_true','original_stl_unchanged','all_geometry_reports_bound_to_current_stl','checker_sources_unchanged_during_run','all_reports_bound_to_current_checkers','three_required_layer_offsets','every_original_face_has_ten_rays','zero_short_or_flagged_dense_samples','all_full_detail_artifact_hashes_current','dense_lossless_csv_hash_current'}
        failures={'all_gates_explicitly_pass','all_gate_check_flags_true','zero_short_or_flagged_dense_samples'}
        if set(q.get('checks',{}))!=keys or any(v is not (k not in failures) for k,v in q['checks'].items()):raise ValueError('summary_unexpected_check_state')
        if q.get('passed') is not False or q.get('strict_passed') is not False:raise ValueError('summary_strict_state_changed')
        paths=[('raw',0,'raw/raw-mesh-check.json'),('sections',0,'sections/section-check.json'),('dense',1,'dense/dense-check.json'),('controls',0,'controls/control-check.json')]
        gates=q.get('gate_reports',[])
        if len(gates)!=4:raise ValueError('summary_missing_gate')
        for row,(name,code,path) in zip(gates,paths):
            expected_failed=['all_original_ray_intervals_and_controls_valid'] if name=='dense' else []
            if row.get('gate')!=name or row.get('returncode')!=code or row.get('passed') is not (code==0) or row.get('report_file')!=path or row.get('failed_checks')!=expected_failed:raise ValueError('summary_unexpected_gate_state')
            if sha(directory/path)!=row.get('report_sha256'):raise ValueError('summary_gate_report_hash_changed')
        if q.get('stl_sha256')!=sha(source_root/'model.stl'):raise ValueError('summary_stl_changed')
        inventory={p.name:sha(p) for p in sorted((source_root/'verification').iterdir()) if p.suffix in ['.py','.cpp']}
        if q.get('checker_sources_sha256')!=inventory:raise ValueError('summary_sources_changed')
        expected_details={('sections','detail_file'),('sections','failure_file'),('dense','csv_file'),('dense','short_chords_file'),('dense','flagged_samples_file')}
        details=q.get('evidence_files',[])
        if {(v.get('gate'),v.get('key')) for v in details}!=expected_details or len(details)!=5 or not all(v.get('verified') is True for v in details):raise ValueError('summary_detail_state_changed')
        return {'passed':True,'reasons':[],'qa_summary_sha256':sha(directory/'qa-summary.json')}
    except Exception as e:return {'passed':False,'reasons':[str(e) if isinstance(e,ValueError) else 'summary_read_or_schema_error']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,help='New external directory retaining the exact dense CSV, fresh reports and this run receipt.');a=ap.parse_args()
    from replay_dense_cache import rebuild_cache,verify_cache
    from validate_model import validate
    run_id=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
    D=(a.out if a.out else R.parent/('nccu-full-replay-'+run_id)).resolve()
    if D==R or R in D.parents:raise RuntimeError('Replay output must be outside the distributed package')
    D.mkdir(parents=True,exist_ok=False)
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    receipt={'run_id':run_id,'mode':'fresh-full-science-replay','current_science_replayed':False,'full_evidence_verified':False,'strict_passed':False,'archived_science_strict_passed':False,'stl_sha256':sha(R/'model.stl'),'source_manifest_sha256':sha(R/'freeze-manifest.json'),'stages':[],'fresh_dense_verified':False,'limits':'A complete current replay is separate from archived results. Four original boundary flags remain strict false; no finite test guarantees printability.'}
    def save(): (D/'current-run.json').write_text(json.dumps(receipt,indent=2)+'\n')
    def stage(name,command,expected=0,required=()):
        previous={str(q):q.stat().st_mtime_ns if q.is_file() else None for q in required}
        p=subprocess.run(command,cwd=W,capture_output=True,text=True)
        (D/'logs').mkdir(exist_ok=True);(D/'logs'/f'{len(receipt["stages"]):02d}-{name}.log').write_text(p.stdout+p.stderr)
        row={'stage':name,'returncode':p.returncode,'expected_returncode':expected,'completed':p.returncode==expected and all(q.is_file() and q.stat().st_mtime_ns!=previous[str(q)] for q in required),'fresh_outputs':{str(q.relative_to(W)):sha(q) for q in required if q.is_file()}}
        receipt['stages'].append(row);save()
        if not row['completed']:raise RuntimeError('Required stage failed: '+name)
    try:
        delivery=validate(R,delivery_only=True)
        receipt['delivery_preflight']={'passed':delivery.get('delivery_integrity_passed') is True,'current_science_replayed':False}
        if not receipt['delivery_preflight']['passed']:raise RuntimeError('Current delivered files failed preflight')
        declared=json.loads((R/'distribution-manifest.json').read_text())['files']
        source_before={n:sha(R/n) for n in declared}
        receipt['preflight_source_hashes']=source_before
        cache=D/'cache/dense-original.csv.gz'
        rebuilt=rebuild_cache(R,cache);receipt['fresh_dense_rebuild']=rebuilt
        receipt['stages'].append({'stage':'fresh_dense_rebuild','returncode':0 if rebuilt.get('passed') is True else 1,'expected_returncode':0,'completed':rebuilt.get('passed') is True})
        save()
        if rebuilt.get('passed') is not True:raise RuntimeError('Fresh dense rebuild failed exact audited evidence checks')
        receipt['fresh_dense_verified']=True
        W=D/'evidence';W.mkdir()
        names=json.loads((R/'distribution-manifest.json').read_text())['files']
        for n in names:
            q=W/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,q)
            if sha(q)!=source_before.get(n):raise RuntimeError('Source changed between preflight and working copy')
        # A new original-geometry run produces its own outputs in an initially empty directory.
        G=D/'fresh-original-geometry'
        stage('original_geometry',[sys.executable,*MODE,str(W/'verification/run_qa.py'),'--stl',str(W/'model.stl'),'--out',str(G),'--expected-longest-mm','150'],expected=1)
        second=verify_cache(W,G/'dense/dense-original.csv.gz');receipt['second_fresh_dense_verification']=second
        if second.get('passed') is not True:raise RuntimeError('Current original-geometry run lacks the exact fresh dense CSV')
        necessary=['raw/raw-mesh-check.json','sections/section-check.json','dense/dense-check.json','controls/control-check.json','qa-summary.json']
        if not all((G/n).is_file() for n in necessary):raise RuntimeError('Current original-geometry stage left missing reports')
        canonical=json.loads((R/'qa/dense/dense-check.json').read_text());fresh=json.loads((G/'dense/dense-check.json').read_text())
        if {k:v for k,v in canonical.items() if k!='compiled_executable_sha256'}!={k:v for k,v in fresh.items() if k!='compiled_executable_sha256'}:raise RuntimeError('Fresh dense report differs from the audited numerical evidence')
        for n in ['dense-flagged-samples.json.gz','dense-short-samples.json.gz']:
            if sha(G/'dense'/n)!=sha(R/'qa/dense'/n):raise RuntimeError('Fresh dense exception evidence differs')
        receipt['second_fresh_dense_report_sha256']=sha(G/'dense/dense-check.json')
        receipt['fresh_original_summary']=verify_original_summary(G,W)
        if receipt['fresh_original_summary']['passed'] is not True:raise RuntimeError('Fresh original QA summary is not the exact expected four-flag state')
        for n in necessary[:2]+[necessary[3]]:
            if json.loads((G/n).read_text()).get('strict_passed') is not True:raise RuntimeError('Current non-dense geometry gate failed')
        for p in sorted(G.rglob('*')):
            if p.is_file() and (p.suffix=='.json' or p.name.endswith('.gz')) and str(p.relative_to(G)) not in {'dense/dense-original.csv.gz','dense/dense-check.json','dense/dense-flagged-samples.json.gz','dense/dense-short-samples.json.gz'}:
                q=W/'qa'/p.relative_to(G);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
        # The complete CSV is retained once at cache/, not copied into the distributed payload.
        stage('exact_original_intersections',[sys.executable,*MODE,str(W/'check_original_intersections.py'),'--stl',str(W/'model.stl'),'--out',str(W/'qa/intersections/original-intersections.json')],required=[W/'qa/intersections/original-intersections.json'])
        C=D/'fresh-intersection-controls'
        stage('intersection_controls',[sys.executable,*MODE,str(W/'check_intersection_controls.py'),'--out-dir',str(C)])
        if not (C/'controls-summary.json').is_file():raise RuntimeError('Fresh intersection-control report missing')
        for p in sorted(C.rglob('*')):
            if p.is_file() and (p.suffix=='.json' or p.name.endswith('.gz')):
                q=W/'qa/intersection-controls'/p.relative_to(C);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
        for script,report in [('check_architectural_features.py','architectural-features.json'),('check_verification_gates.py','verification-gates.json'),('diagnose_boundaries.py','qa/boundaries/ray-boundary-evidence.json'),('check_root_repairs.py','qa/boundaries/previous-short-root-evidence.json')]:
            stage(script,[sys.executable,*MODE,str(W/script)],required=[W/report])
        stage('saved_scene',['blender','-b',str(W/'scene.blend'),'-t','1','--python-exit-code','1','--python',str(W/'probe_scene.py')],required=[W/'scene-check.json'])
        stage('isolated_full_replay',[sys.executable,*MODE,str(W/'check_reproducibility.py'),'--render'],required=[W/'reproducibility.json'])
        stage('fresh_artifact_scan',[sys.executable,*MODE,str(W/'check_artifacts.py')],required=[W/'artifact-integrity.json'])
        stage('bind_current_payload',[sys.executable,*MODE,str(W/'write_validation_manifest.py')],required=[W/'validation-inputs.json'])
        stage('pre_control_delivery',[sys.executable,*MODE,str(W/'validate_model.py'),'--delivery-only'],required=[W/'validation.json'])
        stage('aggregate_negative_controls',[sys.executable,*MODE,str(W/'check_aggregate_controls.py'),'--dense-cache',str(cache)],required=[W/'aggregate-controls.json',W/'aggregate-control-evidence.json'])
        stage('rebind_after_controls',[sys.executable,*MODE,str(W/'write_validation_manifest.py')],required=[W/'validation-inputs.json'])
        stage('final_aggregate',[sys.executable,*MODE,str(W/'validate_model.py'),'--dense-cache',str(cache)],expected=1,required=[W/'validation.json'])
        final=json.loads((W/'validation.json').read_text())
        failed={k for k,v in final.get('geometry_checks',{}).items() if not v}
        expected_failures={'no_dense_ambiguity_flags','strict_dense_original_ray_check'}
        ordered=['fresh_dense_rebuild','original_geometry','exact_original_intersections','intersection_controls','check_architectural_features.py','check_verification_gates.py','diagnose_boundaries.py','check_root_repairs.py','saved_scene','isolated_full_replay','fresh_artifact_scan','bind_current_payload','pre_control_delivery','aggregate_negative_controls','rebind_after_controls','final_aggregate']
        receipt['original_source_unchanged']={n:sha(R/n) for n in declared}==source_before and {str(p.relative_to(R)) for p in R.rglob('*') if p.is_file()}==set(declared)
        if not receipt['original_source_unchanged']:raise RuntimeError('Distributed source changed during replay')
        receipt['required_stage_sequence_complete']=[q['stage'] for q in receipt['stages']]==ordered and all(q['completed'] for q in receipt['stages'])
        receipt['full_evidence_verified']=final.get('full_evidence_verified') is True
        receipt['final_aggregate_sha256']=sha(W/'validation.json')
        receipt['current_science_replayed']=receipt['required_stage_sequence_complete'] and receipt['fresh_dense_verified'] and receipt['full_evidence_verified'] and failed==expected_failures and final.get('dense_flagged_samples')==4
        receipt['remaining_strict_failures']=sorted(failed)
        if not receipt['current_science_replayed']:raise RuntimeError('Current replay did not reach the exact bounded final state')
    except Exception as e:
        receipt['current_science_replayed']=False;receipt['failure_type']=type(e).__name__;receipt['failure_stage']=receipt['stages'][-1]['stage'] if receipt['stages'] else 'delivery_preflight'
    save();print(json.dumps(receipt,indent=2))
    # Reproduction success does not clear the four strict geometric flags.
    return 0 if receipt['strict_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
