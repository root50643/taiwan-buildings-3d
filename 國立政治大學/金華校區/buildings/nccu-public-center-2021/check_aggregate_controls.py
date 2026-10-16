"""Disposable delivery/cache mutations prove the compact package fails closed."""
from pathlib import Path
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SOURCES=['check_aggregate_controls.py','validate_model.py','check_artifacts.py','write_validation_manifest.py','run_checks.py','replay_dense_cache.py']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dense-cache',type=Path,required=True);a=ap.parse_args()
    from replay_dense_cache import verify_cache
    if verify_cache(R,a.dense_cache).get('passed') is not True:raise RuntimeError('Control baseline requires the exact complete dense cache')
    rows=[];evidence=[]
    with tempfile.TemporaryDirectory(prefix='nccu-compact-controls-') as td:
        D=Path(td)/'package';shutil.copytree(R,D)
        def validate(scope='delivery',cache=None):
            cmd=[sys.executable,'-B','-O',str(D/'validate_model.py')]
            if scope=='delivery':cmd+=['--delivery-only']
            elif cache is not None:cmd+=['--dense-cache',str(cache),'--integrity-only']
            p=subprocess.run(cmd,capture_output=True,text=True)
            report=json.loads((D/'validation.json').read_text()) if (D/'validation.json').is_file() else {}
            return p,report
        def record(name,rel,p,rep,reason,mutation,science=False):
            state=rep.get('full_evidence_verified') is False and rep.get('current_science_replayed') is False
            rejected=p.returncode!=0 and bool(reason) and (state if science else rep.get('delivery_integrity_passed') is False)
            rows.append({'control':name,'rejected':bool(rejected),'returncode':p.returncode,'target':rel,'science_failure_control':science})
            target=D/rel if rel else None
            def clean(s):return s.replace(str(a.dense_cache),'<external-cache>').replace(str(D),'.').replace(td,'<temporary>').replace(str(R),'<package>')
            evidence.append({'control':name,'mutation':mutation,'mutated_target_sha256':sha(target) if target and target.is_file() else None,'report':rep,'stdout':clean(p.stdout),'stderr':clean(p.stderr)})
        p,rep=validate()
        if p.returncode!=0 or rep.get('delivery_integrity_passed') is not True or rep.get('full_evidence_verified') is not False:raise RuntimeError('Delivery-only baseline failed or overstated science')
        for name,rel in [('readme_changed','README.md'),('preview_changed','previews/front.png'),('checker_changed','verification/check_raw_mesh.py'),('stl_changed','model.stl'),('report_changed','qa/raw/raw-mesh-check.json')]:
            target=D/rel;old=target.read_bytes();target.write_bytes(old+b'\nExpected stale evidence mutation\n');p,rep=validate()
            record(name,rel,p,rep,rep.get('checks',{}).get('exact_current_distributable_inventory') is False,{'append':'Expected stale evidence mutation','original_sha256':hashlib.sha256(old).hexdigest()});target.write_bytes(old)
        for rel in ['qa/nested/validation.json','qa/nested/freeze-manifest.json']:
            target=D/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('{}');p,rep=validate()
            record('nested_excluded_name:'+rel,rel,p,rep,rep.get('checks',{}).get('exact_current_distributable_inventory') is False,{'create':'empty JSON object'});target.unlink()
        rel='qa/compressed-private-control.json.gz';target=D/rel;target.write_bytes(gzip.compress(('/'+'Users'+'/private-control/file').encode(),mtime=0))
        subprocess.run([sys.executable,'-B',str(D/'write_validation_manifest.py')],check=True,capture_output=True)
        p,rep=validate();reason=rep.get('artifact_scan',{}).get('checks',{}).get('no_private_paths_or_credentials') is False and rel in rep.get('artifact_scan',{}).get('flagged_paths',[])
        record('compressed_private_path',rel,p,rep,reason,{'create':'gzip containing a constructed synthetic user-home path'});target.unlink()
        from PIL import Image,PngImagePlugin
        rel='previews/front.png';target=D/rel;old=target.read_bytes();im=Image.open(target);im.load();meta=PngImagePlugin.PngInfo();meta.add_text('unexpected_metadata','control');im.save(target,pnginfo=meta)
        subprocess.run([sys.executable,'-B',str(D/'write_validation_manifest.py')],check=True,capture_output=True)
        p,rep=validate();reason=rep.get('artifact_scan',{}).get('checks',{}).get('all_png_decoded_crc_clean') is False
        record('fresh_png_metadata',rel,p,rep,reason,{'add_png_text':{'unexpected_metadata':'control'}});target.write_bytes(old)
        # Restore the exact source manifest before cache-specific controls.
        shutil.copyfile(R/'validation-inputs.json',D/'validation-inputs.json')
        p,rep=validate('science')
        record('missing_complete_dense_cache',None,p,rep,'missing_dense_cache' in rep.get('cache_verification',{}).get('reasons',[]),{'omit':'external complete dense cache'},True)
        wrong=Path(td)/'wrong.csv.gz';wrong.write_bytes(a.dense_cache.read_bytes()[:-1]+bytes([a.dense_cache.read_bytes()[-1]^1]))
        p,rep=validate('science',wrong)
        record('wrong_complete_dense_cache',None,p,rep,'external_dense_cache_gzip_sha256_mismatch' in rep.get('cache_verification',{}).get('reasons',[]),{'corrupt':'one final byte in external gzip'},True)
        rel='compact-cache.json';target=D/rel;old=target.read_bytes();metadata=json.loads(old)
        # Change every exact canonical gzip digest occurrence, irrespective of schema nesting.
        expected=json.loads((D/'qa/dense/dense-check.json').read_text())['csv_gzip_sha256']
        target.write_bytes(old.replace(expected.encode(),sha(wrong).encode()))
        if target.read_bytes()==old:raise RuntimeError('Fake metadata control did not mutate the digest')
        subprocess.run([sys.executable,'-B',str(D/'write_validation_manifest.py')],check=True,capture_output=True)
        p,rep=validate('science',wrong)
        record('forged_cache_metadata_after_rebind',rel,p,rep,rep.get('cache_contract',{}).get('passed') is False,{'replace_canonical_gzip_digest':sha(wrong),'rebind_current_manifest':True},True);target.write_bytes(old)
        shutil.copyfile(R/'validation-inputs.json',D/'validation-inputs.json')
        (D/'validation.json').write_text(json.dumps({'passed':True,'strict_passed':True,'full_evidence_verified':True,'current_science_replayed':True}))
        p,rep=validate('science')
        record('stale_success_report_without_cache','validation.json',p,rep,'missing_dense_cache' in rep.get('cache_verification',{}).get('reasons',[]),{'replace_prior_output_with_fake_success':True},True)
        from run_checks import verify_original_summary
        summary_path=D/'qa/qa-summary.json';summary_original=summary_path.read_bytes()
        if verify_original_summary(D/'qa',D).get('passed') is not True:raise RuntimeError('Summary-control baseline failed')
        for name,mutation in [('summary_error_after_child_outputs','error'),('summary_unexpected_dense_failure','dense'),('summary_missing_gate','gate')]:
            q=json.loads(summary_original)
            if mutation=='error':q['error']='synthetic late aggregation error'
            elif mutation=='dense':q['gate_reports'][2]['failed_checks']=['synthetic_other_failure']
            else:q['gate_reports'].pop()
            summary_path.write_text(json.dumps(q));observed=verify_original_summary(D/'qa',D)
            rows.append({'control':name,'rejected':observed.get('passed') is False,'control_type':'in_process_fresh_summary_predicate','target':'qa/qa-summary.json','science_failure_control':True})
            evidence.append({'control':name,'mutation':mutation,'report':observed,'mutated_target_sha256':sha(summary_path)})
            summary_path.write_bytes(summary_original)
        # An unrelated exit 1 caused by a missing compiler cannot become a rebuilt cache.
        output=Path(td)/'failed-rebuild'/'dense-original.csv.gz';env=dict(os.environ);env['PATH']='';env['PYTHONDONTWRITEBYTECODE']='1'
        p=subprocess.run([sys.executable,'-B','-O',str(D/'replay_dense_cache.py'),'--out',str(output)],capture_output=True,text=True,env=env)
        try:rep=json.loads(p.stdout)
        except json.JSONDecodeError:rep={}
        rejected=p.returncode!=0 and rep.get('passed') is False and not output.exists() and rep.get('current_science_replayed') is False and rep.get('observed_original_checker_exit')==1 and rep.get('fresh_original_dense_report',{}).get('error')=='Existing g++ compiler not found; nothing will be installed' and rep.get('fresh_original_dense_report',{}).get('checks',{}).get('completed_without_error') is False and bool(rep.get('fresh_original_dense_report_sha256'))
        rows.append({'control':'unrelated_dense_exit1_not_accepted','rejected':rejected,'returncode':p.returncode,'target':'external atomic cache destination','science_failure_control':True})
        evidence.append({'control':'unrelated_dense_exit1_not_accepted','mutation':{'PATH':'empty for subprocess only'},'report':rep,'destination_created':output.exists(),'stdout':p.stdout.replace(str(D),'.').replace(td,'<temporary>'),'stderr':p.stderr.replace(str(D),'.').replace(td,'<temporary>')})
    (R/'aggregate-control-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    out={'passed':all(q['rejected'] for q in rows),'stl_sha256':sha(R/'model.stl'),'evidence_sha256':sha(R/'aggregate-control-evidence.json'),'checker_sources_sha256':{n:sha(R/n) for n in SOURCES},'delivery_baseline_passed':True,'optimized_python':True,'production_unchanged':True,'controls':rows,'limits':'Delivery-only mode cannot claim full evidence verification or science replay. Missing/wrong cache and unrelated dense exit failures must be rejected.'}
    (R/'aggregate-controls.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if out['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
