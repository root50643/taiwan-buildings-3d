"""Orchestrate exact original outer-archive verify/extract/readback/rebuild in both modes."""
import ast,hashlib,json,os,stat,subprocess,sys,tempfile,time
from pathlib import Path
q=Path(sys.argv[1]).resolve();runtime=Path(__file__).resolve().parent;py=Path(sys.executable);c=q.parent/'aeust-youxiang-independent-qa/public-v15-r1/qa/controls';toolroot=q/'reuse-preflight-v1'
def need(v,s):
 if not v:raise ValueError(s)
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
 with p.open('x') as f:f.write(json.dumps(d,indent=2)+'\n')
need(len(os.sched_getaffinity(0))==1,'single CPU required')
own_source_hash=h(Path(__file__));env=dict(os.environ);env.pop('PYTHONOPTIMIZE',None)
capture=q/'independent-tools/capture_process.py';need(h(capture)=='f44673ed9c2bc04e21bf907fe19745dab18a25ba59c2241bd227b986710c6244','Controlled runtime launcher source changed')
assignments=[node for node in ast.parse(capture.read_text()).body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='BOOT' for target in node.targets)];need(len(assignments)==1,'One exact original runtime launcher required')
bootstrap=runtime/'runtime_launcher.py';need(not bootstrap.exists(),'Fresh runtime launcher required');bootstrap.write_text(ast.literal_eval(assignments[0].value));runtime_rows=[]
def child(command,record,level):
 target=Path(command[2 if level==0 else 3]);args=command[3 if level==0 else 4:];prefix=command[:2 if level==0 else 3]
 result=subprocess.run(prefix+[str(bootstrap),str(record),str(target),*args],capture_output=True,text=True,env=env)
 need(record.is_file(),'Actual child runtime missing');actual=json.loads(record.read_text());need(type(actual['optimization_level']) is int and actual['optimization_level']==level and actual['cpu_affinity']==list(sorted(os.sched_getaffinity(0))) and actual['target_sha256']==h(target) and actual['target_arguments']==args,'Actual child mode/CPU/source/arguments differ');runtime_rows.append({'record':record.name,'sha256':h(record),'actual':actual});return result

expected={'tooling/tools/archive_verify.py':'1af27c8212057503323899b7a5f9f9171de42f78a28ff1e3e07f82d688e021fd','tooling/tools/build_controls_archive.py':'e4b23d35449c6321abbfea94e85f4d733ce58be65658255e1e5ba5065b33f637'}
for rel,sha in expected.items():need(h(toolroot/rel)==sha,'tool identity changed')
index=json.loads((c/'controls-index.json').read_text());package=json.loads((c/'packaging-result.json').read_text());archive_bytes=(c/'controls.tar.xz').read_bytes();archive_sha=hashlib.sha256(archive_bytes).hexdigest();index_sha=h(c/'controls-index.json')
need(package['passed'] is True and archive_sha==index['archive_sha256']==package['archive_sha256'] and index_sha==package['index_sha256'],'archive/index/package identity')
need(archive_sha=='e5c4465705d5e5299c5d9aa7fa7e99f5db44a61437990508ecee72d615e165b9' and index_sha=='157fbf951147405727eb557b167e6db16d9ce3a651012f1c87ee2a5975d0015e' and len(index['members'])==16730,'Exact original completed historical archive required')
need(not (runtime/'replay-verification.json').exists(),'fresh result required')
rows={}
for mode,level in [('normal',0),('optimized',1)]:
 start=time.time();flags=['-B']+(['-O'] if level else [])
 with tempfile.TemporaryDirectory(dir=runtime,prefix='outer-replay-'+mode+'-') as td:
  temp=Path(td);extracted=temp/'extracted';rebuilt=temp/'rebuilt.tar.xz'
  verify_cmd=[str(py),*flags,str(toolroot/'tooling/tools/archive_verify.py'),'--archive',str(c/'controls.tar.xz'),'--index',str(c/'controls-index.json'),'--out',str(extracted)]
  a=child(verify_cmd,runtime/('outer-'+mode+'-verify.runtime.json'),level)
  with (runtime/('outer-'+mode+'-verify.stdout.log')).open('x') as f:f.write(a.stdout)
  with (runtime/('outer-'+mode+'-verify.stderr.log')).open('x') as f:f.write(a.stderr)
  need(a.returncode==0,'original verifier failed');vr=json.loads(a.stdout);need(vr['passed'] is True and vr['extracted'] is True,'safe extraction failed')
  actual=[]
  for p in extracted.rglob('*'):
   s=p.lstat()
   if stat.S_ISDIR(s.st_mode):continue
   need(stat.S_ISREG(s.st_mode),'nonregular extracted member');actual.append(p.relative_to(extracted).as_posix())
  need(sorted(actual)==[r['path'] for r in index['members']],'all-member path set differs')
  for r in index['members']:
   b=(extracted/r['path']).read_bytes();need(len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],'actual extracted member differs')
  for rel,sha in expected.items():need(h(extracted/rel)==sha,'extracted trusted tool differs')
  rebuild_cmd=[str(py),*flags,str(extracted/'tooling/tools/build_controls_archive.py'),'--root',str(extracted),'--index',str(c/'controls-index.json'),'--out',str(rebuilt)]
  b=child(rebuild_cmd,runtime/('outer-'+mode+'-rebuild.runtime.json'),level)
  with (runtime/('outer-'+mode+'-rebuild.stdout.log')).open('x') as f:f.write(b.stdout)
  with (runtime/('outer-'+mode+'-rebuild.stderr.log')).open('x') as f:f.write(b.stderr)
  need(b.returncode==0,'original builder failed');br=json.loads(b.stdout);need(br['passed'] is True,'rebuild report failed');need(rebuilt.read_bytes()==archive_bytes,'rebuilt archive not byte-identical')
  need(br['tar_bytes']<=536870912,'generic USTAR limit exceeded')
  rows[mode]={'optimization_level':level,'safe_validation_and_extraction':vr,'rebuild':br,'rebuilt_archive_byte_identical':True,'all_extracted_original_member_bytes_verified':True,'original_member_count':len(index['members']),'elapsed_seconds':time.time()-start,'verifier_source_sha256':expected['tooling/tools/archive_verify.py'],'rebuild_source_sha256':expected['tooling/tools/build_controls_archive.py'],'source_location':'Trusted original verifier; exact extracted original builder','temporary_extraction_removed_after_complete_verification':True}
  write(runtime/('OUTER-REPLAY-'+mode+'.json'),rows[mode]);print(mode,'outer safe replay completed',flush=True)
need((c/'controls.tar.xz').read_bytes()==archive_bytes and h(c/'controls-index.json')==index_sha,'archive changed during replay')
for rel,sha in expected.items():need(h(toolroot/rel)==sha,'original tool changed')
need(h(Path(__file__))==own_source_hash and h(capture)=='f44673ed9c2bc04e21bf907fe19745dab18a25ba59c2241bd227b986710c6244','Replay orchestration/runtime source changed')
report={'schema':'wfu-inherited-controls-archive-safe-replay-v1','passed':True,'model_go':False,'both_modes_safe_extraction_and_bitwise_rebuild':True,'archive_sha256':archive_sha,'index_sha256':index_sha,'tar_sha256':index['tar_sha256'],'members':len(index['members']),'modes':rows,'all_original_archives_indexes_and_tools_unchanged':True,'generic_decoded_byte_limit_unchanged':536870912,'full_synthetic_suites_rerun_from_final_archive':False,'scope':'Exact historical tool/control archive reuse only. Historical AEUST model identities/results are inactive fixtures and never WFU acceptance. WFU case controls and model science are separately required.','synthetic_evidence_scope':'All complete original synthetic suites were executed in both modes before final packaging. This record verifies safe exact archive restoration and rebuilding, not another synthetic-suite execution.','actual_child_runtime':runtime_rows,'runtime_launcher_source_sha256':h(capture),'orchestration_source_sha256':own_source_hash}
write(runtime/'replay-verification.json',report);print(json.dumps({k:report[k] for k in ['passed','archive_sha256','index_sha256','tar_sha256','members']}))
