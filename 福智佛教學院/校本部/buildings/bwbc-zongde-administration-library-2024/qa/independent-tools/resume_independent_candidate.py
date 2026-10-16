"""Resume an interrupted frozen-candidate run without overwriting its evidence.
Normal raw/section outputs are explicitly referenced by hash, not claimed rerun.
Stops the new child if the old incomplete CSV changes or disappears.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,signal,subprocess,sys,time

def require(v,m):
 if not v:raise RuntimeError(m)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--checkpoint',type=Path,required=True);ap.add_argument('--author-root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--watch-old-csv',type=Path,required=True);a=ap.parse_args()
 require(not a.out.exists(),'Refusing existing resume output');a.out.mkdir(parents=True);out=a.out.resolve();old=a.checkpoint.resolve();author=a.author_root.resolve();frozen=old/'frozen';ver=frozen/'verification';ind=frozen/'independent-tools'
 env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
 records=[];source_hash=sha(__file__);summary={'completed':False,'strict_passed':False,'scope':'Resumed execution inventory only. No overall model pass is inferred from completion. Original numerical strict failures are unchanged.','resume_source_sha256':source_hash,'executions':records};began=time.time()
 require(a.watch_old_csv.is_file(),'Old partial CSV absent; review recovery conditions first');watch=(a.watch_old_csv.stat().st_size,a.watch_old_csv.stat().st_mtime_ns)
 def watch_check():
  require(a.watch_old_csv.is_file() and (a.watch_old_csv.stat().st_size,a.watch_old_csv.stat().st_mtime_ns)==watch,'Old interrupted CSV changed/disappeared; stop duplicate work and coordinate')
 def run(name,command):
  watch_check();start=time.time();log=out/'execution-logs'/(name+'.log');log.parent.mkdir(exist_ok=True);command=[str(x) for x in command]
  with log.open('w') as f:
   p=subprocess.Popen(command,stdout=f,stderr=subprocess.STDOUT,env=env,start_new_session=True);write(out/'running-stage.json',{'stage':name,'pid_in_execution_namespace':p.pid,'command':command,'started_epoch':start,'state':'running'});tick=start
   try:
    while p.poll() is None:
     time.sleep(1);watch_check()
     if time.time()-tick>=30:
      print(json.dumps({'stage':name,'elapsed_seconds':round(time.time()-start),'heartbeat':True}),flush=True);tick=time.time()
   except BaseException:
    if p.poll() is None:
     os.killpg(p.pid,signal.SIGTERM)
     try:p.wait(timeout=10)
     except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
    raise
  row={'name':name,'returncode':p.returncode,'elapsed_seconds':time.time()-start,'command':command,'log_file':str(log.relative_to(out)),'log_sha256':sha(log)};records.append(row);write(out/'executions.json',records);write(out/'running-stage.json',dict(row,state='finished'));print(json.dumps(row),flush=True);return p.returncode
 try:
  manifest=json.loads((old/'author-freeze-manifest.json').read_text());version=manifest['version'];expected=manifest['stl_sha256'];manifest_sha=sha(old/'author-freeze-manifest.json');summary.update(candidate_version=version,stl_sha256=expected,author_freeze_manifest_sha256=manifest_sha)
  require(manifest_sha=='4c83b113598bff1053087caf4208d0382f80b9bc855aade37e27c347b73c1890','Unexpected frozen manifest');require(expected=='96481addb2b9ac4144cb5f012f19b57e047106021e93adb5c34df2c00770e1a3','Unexpected frozen STL')
  for row in manifest['files']:require((author/row['path']).stat().st_size==row['bytes'] and sha(author/row['path'])==row['sha256'],'Author frozen input changed: '+row['path'])
  frozen_inventory=json.loads((old/'frozen-input-inventory.json').read_text());ind_inventory=json.loads((old/'independent-tool-inventory.json').read_text())
  def frozen_checks():
   for relative,digest in frozen_inventory.items():
    p=frozen/relative
    if not p.is_file():p=frozen/'documentation'/relative
    require(sha(p)==digest,'Frozen snapshot changed: '+relative)
   for name,digest in ind_inventory.items():require(sha(ind/name)==digest,'Frozen independent tool changed: '+name)
  frozen_checks();stl=frozen/'models'/version/'model.stl';require(sha(stl)==expected,'Frozen STL changed')
  status=json.loads((old/'interruption/interruption-status.json').read_text());base=out/'geometry'/'normal';standard=base/'standard';standard.mkdir(parents=True);referenced=[]
  for gate,report_name,key in [('raw','raw-mesh-check.json','normal_raw_report_sha256'),('sections','section-check.json','normal_sections_report_sha256')]:
   source=old/'geometry/normal/standard'/gate;report=json.loads((source/report_name).read_text());require(sha(source/report_name)==status[key] and report.get('passed') is True and report.get('strict_passed') is True and report.get('stl_sha256')==expected,'Completed stage binding failed: '+gate)
   shutil.copytree(source,standard/gate);files={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()};require(all(sha(standard/gate/name)==digest for name,digest in files.items()),'Completed-stage copy differs');referenced.append({'gate':gate,'original_report_sha256':sha(source/report_name),'files_sha256':files,'execution_status':'Completed before transport interruption; copied by hash, not rerun'})
  write(out/'referenced-completed-stages.json',{'stl_sha256':expected,'source_checkpoint':'final-v17','stages':referenced,'old_process_state':'Direct PID status unavailable; old session is unknown and partial CSV is unchanged. This run monitors the partial CSV and stops its own child if it changes.'})
  py=[sys.executable,'-B'];run('normal-dense',[*py,ver/'check_dense_surface.py','--stl',stl,'--out',standard/'dense']);require(run('normal-generic-controls',[*py,ver/'check_controls.py','--out',standard/'controls'])==0,'Normal generic controls failed')
  # Recovery ledger explicitly validates schemas/evidence but preserves false gates.
  sys.path.insert(0,str(ver));from run_qa import REQUIRED_CHECKS
  from qa_common import checker_inventory,open_compressed_csv
  reports={gate:json.loads((standard/gate/name).read_text()) for gate,name in [('raw','raw-mesh-check.json'),('sections','section-check.json'),('dense','dense-check.json'),('controls','control-check.json')]};required={k:set(v) for k,v in REQUIRED_CHECKS.items()};required['raw'].add('requested_longest_extent_mm');inventory=checker_inventory()
  binding={'all_required_check_keys_exact':all(set(reports[k]['checks'])==required[k] for k in required),'all_checker_inventories_match':all(r['checker_sources_sha256']==inventory for r in reports.values()),'all_geometry_stl_hashes_match':all(reports[k]['stl_sha256']==expected for k in ['raw','sections','dense']),'dense_sample_count_complete':reports['dense']['samples']==10*reports['raw']['triangles'],'three_slice_offsets_and_pitch':reports['sections']['offsets_from_z_min_mm']==[.031,.071,.137] and reports['sections']['pitch_mm']==.2}
  for gate,filekey,hashkey in [('sections','detail_file','detail_sha256'),('sections','failure_file','failure_sha256'),('dense','csv_file','csv_compressed_sha256'),('dense','short_chords_file','short_chords_sha256'),('dense','flagged_samples_file','flagged_samples_sha256')]:binding[gate+'_'+filekey+'_hash']=sha(standard/gate/reports[gate][filekey])==reports[gate][hashkey]
  with open_compressed_csv(standard/'dense'/reports['dense']['csv_file'],reports['dense']['csv_compression']) as f:binding['decoded_dense_csv_sha256']=hashlib.file_digest(f,'sha256').hexdigest()==reports['dense']['uncompressed_csv_sha256']
  strict=all(r.get('passed') is True and r.get('strict_passed') is True and all(v is True for v in r['checks'].values()) for r in reports.values()) and all(binding.values());write(standard/'recovered-stage-summary.json',{'passed':strict,'strict_passed':strict,'all_evidence_bindings_valid':all(binding.values()),'binding_checks':binding,'stl_sha256':expected,'checker_sources_sha256':inventory,'gate_report_sha256':{k:sha(standard/k/n) for k,n in [('raw','raw-mesh-check.json'),('sections','section-check.json'),('dense','dense-check.json'),('controls','control-check.json')]},'scope':'Explicit staged recovery, not a completed run_qa invocation. Normal raw/sections were completed before interruption; dense/controls executed in this fresh recovery directory. Original dense strict=false is not changed.'});require(all(binding.values()),'Recovered normal evidence binding failed')
  for mode,options in [('normal',[]),('optimized',['-O'])]:
   base=out/'geometry'/mode;py=[sys.executable,'-B',*options]
   if mode=='optimized':run('optimized-standard',[*py,ver/'run_qa.py','--stl',stl,'--out',base/'standard','--expected-longest-mm','210'])
   require(run(mode+'-exact-intersections',[*py,ver/'check_original_intersections.py','--stl',stl,'--expected-sha256',expected,'--out',base/'intersections.json','--progress'])==0,'Exact intersections failed')
   require(run(mode+'-intersection-controls',[*py,ver/'check_intersection_controls.py','--out-dir',base/'intersection-controls'])==0,'Exact intersection controls failed')
   dense=base/'standard/dense';d=json.loads((dense/'dense-check.json').read_text());require(d['under_0p8mm_count']==0,'Original sampled short chord found')
   if d['flagged_sample_count']:
    require(run(mode+'-exact-recorded-rays',[*py,ind/'diagnose_recorded_cpp_rays.py','--stl',stl,'--flags',dense/d['flagged_samples_file'],'--dense-report',dense/'dense-check.json','--raw-report',base/'standard/raw/raw-mesh-check.json','--intersections-report',base/'intersections.json','--expected-sha256',expected,'--out',base/'exact-recorded-rays'])==0,'Exact original flagged-ray diagnosis failed; do not proceed to expensive rendering')
  repro=out/'reproduction';(repro/'source').mkdir(parents=True)
  for name in ['build_model.py','upper_wing_fin_positions.json','render_preview.py']:shutil.copyfile(frozen/'models'/version/name,repro/'source'/name)
  shutil.copyfile(frozen/'models'/version/'parameters.json',repro/'parameters.json');require(run('source-stl-reproduction',[sys.executable,'-B',repro/'source/build_model.py','--output-dir',repro/'models'/version])==0,'Source build failed');recreated=repro/'models'/version
  summary['source_rebuild']={'stl_bitwise_identical':sha(recreated/'model.stl')==expected,'colour_regions_bitwise_identical':sha(recreated/'color-regions.json')==sha(frozen/'models'/version/'color-regions.json')};require(all(summary['source_rebuild'].values()),'Rebuilt STL/colour regions differ')
  require(run('source-scene-state-reproduction',['blender','--background','--threads','1','--python-exit-code','1','--python',ind/'compare_source_scene.py','--','--source',repro/'source/render_preview.py','--version',version,'--original-blend',frozen/'models'/version/'scene.blend','--manifest',frozen/'previews'/version/'render-manifest.json','--expected-stl-sha256',expected,'--out',out/'source-scene-reproduction'])==0,'Source scene comparison failed')
  require(run('saved-blend-eleven-rerenders',['blender','--background','--threads','1','--python-exit-code','1','--python',ind/'inspect_and_rerender_blend.py','--','--blend',frozen/'models'/version/'scene.blend','--stl',stl,'--manifest',frozen/'previews'/version/'render-manifest.json','--expected-sha256',expected,'--out',out/'saved-blend-rerenders'])==0,'Saved Blend/render verification failed')
  require(run('public-png-metadata-cleanup',[sys.executable,'-B',ind/'sanitize_png_previews.py','--manifest',frozen/'previews'/version/'render-manifest.json','--expected-manifest-sha256',sha(frozen/'previews'/version/'render-manifest.json'),'--expected-stl-sha256',expected,'--out',out/'public-previews'])==0,'Public PNG metadata cleanup failed')
  frozen_checks();require(sha(__file__)==source_hash,'Resume runner changed');require(sha(author/'frozen-inputs-v17.json')==manifest_sha,'Author freeze manifest changed')
  rechecked={row['path']:sha(author/row['path'])==row['sha256'] for row in manifest['files']};require(all(rechecked.values()),'Author frozen inputs changed');watch_check();summary.update(completed=True,all_frozen_inputs_and_tools_unchanged=True,author_input_rechecks=rechecked,all_executions_exit_zero=all(r['returncode']==0 for r in records))
 except Exception as e:summary.update(completed=False,error_type=type(e).__name__,error=str(e));print(json.dumps({'error':str(e)}),flush=True)
 summary['elapsed_seconds']=time.time()-began;write(out/'resumed-execution-summary.json',summary);return 0 if summary['completed'] else 1
if __name__=='__main__':raise SystemExit(main())
