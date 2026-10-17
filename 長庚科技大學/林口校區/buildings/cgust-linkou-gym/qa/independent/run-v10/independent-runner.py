"""Freeze a supplied Tianmu candidate and run fresh sequential one-thread evidence.
The execution ledger is not an acceptance verdict. Never replaces an old run.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,signal,subprocess,sys,time
VIEWS={'front','rear','west','east','south','north','top','courtyard-gallery','courtyard-arcade'}
def require(v,m):
    if not v:raise RuntimeError(m)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--author-root',type=Path,required=True);ap.add_argument('--version',required=True);ap.add_argument('--stl-sha256',required=True);ap.add_argument('--freeze-manifest',type=Path,required=True);ap.add_argument('--freeze-sha256',required=True);ap.add_argument('--expected-longest-mm',type=float,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    require(not a.out.exists(),'Refuse any existing run directory');a.out.mkdir(parents=True)
    out=a.out.resolve();author=a.author_root.resolve();frozen=out/'frozen';rows=[];inventory={};start=time.time();active=None
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',BLENDER_THREADS='1',PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(out/'temporary'))
    env.pop('PYTHONOPTIMIZE',None);(out/'temporary').mkdir();(out/'execution-logs').mkdir()
    shutil.copyfile(__file__,out/'independent-runner.py');require(sha(out/'independent-runner.py')==sha(__file__),'Independent runner snapshot differs')
    summary={'completed':False,'strict_passed':False,'version':a.version,'stl_sha256':a.stl_sha256,'expected_longest_mm':a.expected_longest_mm,'runner_sha256':sha(__file__),'executions':rows,'scope':'Fresh execution ledger only. Inspect all scientific gates and bindings separately; no numerical strict result is waived.'}
    def run(name,command):
        nonlocal active
        begin=time.time();log=out/'execution-logs'/(name+'.log');state={'name':name,'command':command,'started_unix':begin,'finished':False,'log_file':str(log.relative_to(out))}
        write(out/'running-stage.json',state)
        with log.open('w') as f:
            active=subprocess.Popen(command,stdout=f,stderr=subprocess.STDOUT,env=env,start_new_session=True);state['process_id']=active.pid;write(out/'running-stage.json',state);code=active.wait();active=None
        state.update(finished=True,returncode=code,elapsed_seconds=time.time()-begin,log_sha256=sha(log));rows.append(state);write(out/'executions.json',rows);write(out/'running-stage.json',state);print(json.dumps({'stage':name,'returncode':code}),flush=True);return code
    def interrupted(signum,frame):
        state={'interrupted':True,'signal':signum,'at_unix':time.time(),'active_process_id':active.pid if active else None,'partial_evidence_retained':True}
        write(out/'interruption-status.json',state)
        if active:
            try:os.killpg(active.pid,signal.SIGTERM)
            except ProcessLookupError:pass
        raise RuntimeError('Execution interrupted; retain run and partial evidence without overwrite')
    signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
    try:
        require(sha(a.freeze_manifest)==a.freeze_sha256,'Author freeze hash mismatch');manifest=json.loads(a.freeze_manifest.read_text());require(manifest['version']==a.version and manifest['stl_sha256']==a.stl_sha256,'Candidate identity mismatch')
        for r in manifest['files']:
            rel=r['path'];p=Path(rel);require(not p.is_absolute() and '..' not in p.parts and rel not in inventory,'Invalid or duplicate frozen path')
            src=author/p;require(src.is_file() and not src.is_symlink() and src.stat().st_size==r['bytes'] and sha(src)==r['sha256'],'Frozen input mismatch: '+rel)
            dst=frozen/p;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);require(sha(dst)==r['sha256'],'Frozen copy differs: '+rel);inventory[rel]={'sha256':r['sha256'],'bytes':r['bytes']}
        shutil.copyfile(a.freeze_manifest,out/'author-freeze-manifest.json');write(out/'frozen-input-inventory.json',inventory)
        model=frozen/'models'/a.version;preview=frozen/'previews'/a.version;qa=frozen/'qa';ver=qa/'verification';tool=qa/'tools';render=qa/'render-tools';stl=model/'model.stl'
        require(sha(stl)==a.stl_sha256,'Frozen STL differs')
        for relative,snapshot in [('source/build_model.py','build_model.py'),('source/render_preview.py','render_preview.py'),('parameters.json','parameters.json')]:require(sha(frozen/relative)==sha(model/snapshot),'Canonical source differs from version snapshot: '+relative)
        pm=json.loads((preview/'render-manifest.json').read_text());require(set(pm['views'])==VIEWS and pm['stl_sha256']==a.stl_sha256 and pm['blend_sha256']==sha(model/'scene.blend'),'Preview manifest binding differs')
        for name,row in pm['views'].items():require(sha(preview/(name+'.png'))==row['sha256'],'Original raw PNG differs: '+name)
        write(out/'author-freeze-validation.json',{'passed':True,'file_count':len(inventory),'manifest_sha256':a.freeze_sha256,'stl_sha256':a.stl_sha256})
        for mode,opts in [('normal',[]),('optimized',['-O'])]:
            base=out/'geometry'/mode;base.mkdir(parents=True);py=[sys.executable,'-B',*opts]
            run(mode+'-standard',py+[str(ver/'run_qa.py'),'--stl',str(stl),'--out',str(base/'standard'),'--expected-longest-mm',str(a.expected_longest_mm)])
            run(mode+'-exact-intersections',py+[str(ver/'check_original_intersections.py'),'--stl',str(stl),'--expected-sha256',a.stl_sha256,'--out',str(base/'intersections.json'),'--progress'])
            run(mode+'-intersection-controls',py+[str(ver/'check_intersection_controls.py'),'--out-dir',str(base/'intersection-controls')])
            run(mode+'-dense-evidence',py+[str(tool/'validate_dense_evidence.py'),'--stl',str(stl),'--dense-report',str(base/'standard/dense/dense-check.json'),'--out',str(base/'dense-evidence.json')])
            dense=json.loads((base/'standard/dense/dense-check.json').read_text())
            if dense.get('flagged_sample_count',0)>0:
                run(mode+'-exact-recorded-rays',py+[str(tool/'diagnose_recorded_cpp_rays.py'),'--stl',str(stl),'--expected-sha256',a.stl_sha256,'--flags',str(base/'standard/dense'/dense['flagged_samples_file']),'--dense-report',str(base/'standard/dense/dense-check.json'),'--raw-report',str(base/'standard/raw/raw-mesh-check.json'),'--intersections-report',str(base/'intersections.json'),'--out',str(base/'exact-recorded-rays')])
        reproduction=out/'reproduction';(reproduction/'source').mkdir(parents=True)
        for name in ['build_model.py','render_preview.py']:shutil.copyfile(model/name,reproduction/'source'/name)
        shutil.copyfile(model/'parameters.json',reproduction/'parameters.json')
        code=run('source-stl-reproduction',[sys.executable,'-B',str(reproduction/'source/build_model.py'),'--output-dir',str(reproduction/'models'/a.version)])
        recreated=reproduction/'models'/a.version;summary['source_rebuild']={'returncode':code,'original_stl_bitwise_identical':(recreated/'model.stl').is_file() and sha(recreated/'model.stl')==sha(stl),'original_color_regions_bitwise_identical':(recreated/'color-regions.json').is_file() and sha(recreated/'color-regions.json')==sha(model/'color-regions.json')};write(out/'source-rebuild-binding.json',summary['source_rebuild'])
        run('source-scene-state-reproduction',['blender','--background','--threads','1','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode = True','--python',str(render/'compare_source_scene.py'),'--','--source',str(reproduction/'source/render_preview.py'),'--version',a.version,'--original-blend',str(model/'scene.blend'),'--manifest',str(preview/'render-manifest.json'),'--expected-stl-sha256',a.stl_sha256,'--out',str(out/'source-scene-reproduction')])
        run('saved-blend-nine-rerenders',['blender','--background','--threads','1','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode = True','--python',str(render/'inspect_and_rerender_blend.py'),'--','--blend',str(model/'scene.blend'),'--stl',str(stl),'--manifest',str(preview/'render-manifest.json'),'--expected-sha256',a.stl_sha256,'--out',str(out/'saved-blend-rerenders')])
        run('public-png-metadata-cleanup',[sys.executable,'-B',str(render/'sanitize_png_previews.py'),'--manifest',str(preview/'render-manifest.json'),'--expected-manifest-sha256',sha(preview/'render-manifest.json'),'--expected-stl-sha256',a.stl_sha256,'--out',str(out/'public-previews')])
        rechecks={rel:sha(author/rel)==r['sha256'] and sha(frozen/rel)==r['sha256'] for rel,r in inventory.items()};rechecks['author_manifest']=sha(a.freeze_manifest)==a.freeze_sha256;rechecks['independent_runner']=sha(__file__)==summary['runner_sha256']
        summary.update(completed=True,all_frozen_inputs_and_tools_unchanged=all(rechecks.values()),input_and_tool_rechecks=rechecks)
    except Exception as e:summary.update(error_type=type(e).__name__,error=str(e))
    summary['elapsed_seconds']=time.time()-start;write(out/'independent-execution-summary.json',summary)
    return 0 if summary['completed'] and summary.get('all_frozen_inputs_and_tools_unchanged') else 1
if __name__=='__main__':raise SystemExit(main())
