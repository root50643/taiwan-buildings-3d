"""Run the unchanged FD-safe public-layout restorer in both real Python modes.
No decompression, geometry, rendering or archive framework. Temporary derived
copies are reauthenticated completely before automatic removal; originals stay.
"""
from pathlib import Path
import argparse,ast,hashlib,json,os,subprocess,sys,tempfile
MAP_SHA='bf66ffc5ec94fa955af0294e627e2afd78e55ad6c700683a499f01f13ae10fb4'
PINS={'qa/restore_scientific_layout.py':'60b9e1f3b6974e8884501e7f7a5b18446dea04a15886ed864ff7c2de2ab2581e','qa/roster_primitives.py':'7211c544e258dd4855ca9747837845aa683d6c28c3939ea0b9a08cb271d69273','qa/independent-tools/capture_process.py':'f44673ed9c2bc04e21bf907fe19745dab18a25ba59c2241bd227b986710c6244'}
def require(v,m):
 if not v:raise ValueError(m)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--public-root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();root=a.public_root.absolute();out=a.out.absolute();own=sha(__file__)
 require(len(os.sched_getaffinity(0))==1,'Single CPU required');require(not out.is_relative_to(root) and out.parent.is_dir() and not out.exists(),'Fresh private result directory required')
 require(all(sha(root/p)==h for p,h in PINS.items()),'Original controlled source differs');mapping=root/'qa/PUBLIC-COPY-MAP.json';require(sha(mapping)==MAP_SHA,'Exact canonical map differs');d=json.loads(mapping.read_text());require(len(d['files'])==543 and len(d['copy_map'])==1528,'Exact map counts differ');out.mkdir()
 source=root/'qa/independent-tools/capture_process.py';nodes=[n for n in ast.parse(source.read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='BOOT' for t in n.targets)];require(len(nodes)==1,'Exact original BOOT absent');boot=out/'runtime_launcher.py';boot.write_text(ast.literal_eval(nodes[0].value));env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1');env.pop('PYTHONOPTIMIZE',None);rows=[]
 target=root/'qa/restore_scientific_layout.py'
 for mode,level in [('normal',0),('optimized',1)]:
  with tempfile.TemporaryDirectory(dir=out,prefix='derived-'+mode+'-') as temp:
   runtime=out/(mode+'.runtime.json');resultpath=out/(mode+'.result.json');args=['--public-root',str(root),'--copy-map','qa/PUBLIC-COPY-MAP.json','--out',str(Path(temp)/'restored')]
   command=[sys.executable,'-B',*(['-O'] if level else []),str(boot),str(runtime),str(target),*args]
   p=subprocess.run(command,capture_output=True,text=True,env=env)
   for label,value in [('stdout',p.stdout),('stderr',p.stderr)]:
    with (out/(mode+'.'+label+'.log')).open('x') as f:f.write(value)
   (out/(mode+'.exit.txt')).write_text(str(p.returncode)+'\n');require(p.returncode==0,'Original public restorer failed')
   actual=json.loads(runtime.read_text());require(type(actual['optimization_level']) is int and actual['optimization_level']==level and actual['cpu_affinity']==sorted(os.sched_getaffinity(0)) and actual['python_executable']==sys.executable and actual['target']==str(target) and actual['target_sha256']==PINS['qa/restore_scientific_layout.py'] and actual['target_arguments']==args,'Actual child runtime differs')
   result=json.loads(p.stdout);require(result['passed'] is True and result['all_written_bytes_reauthenticated'] is True and result['canonical_files_verified']==543 and result['logical_files_restored']==1528 and result['copy_map_sha256']==MAP_SHA and result['restore_source_sha256']==PINS['qa/restore_scientific_layout.py'],'Complete actual restoration absent');dump(resultpath,result)
   rows.append({'mode':mode,'actual_optimization_level':level,'actual_cpu_affinity':actual['cpu_affinity'],'returncode':p.returncode,'result':result,'result_sha256':sha(resultpath),'runtime_record_sha256':sha(runtime),'stdout_sha256':sha(out/(mode+'.stdout.log')),'stderr_sha256':sha(out/(mode+'.stderr.log')),'runtime_record_original_retained_privately':True,'temporary_derived_tree_reauthenticated_before_removal':True})
 require(rows[0]['result']==rows[1]['result'],'Actual mode results differ');require(sha(mapping)==MAP_SHA and all(sha(root/p)==h for p,h in PINS.items()) and sha(__file__)==own,'Original source or map changed')
 report={'passed':True,'both_actual_modes_passed':True,'copy_map_sha256':MAP_SHA,'canonical_files':543,'logical_files':1528,'all_written_bytes_reauthenticated':True,'source_sha256':own,'original_tool_source_sha256':PINS,'executions':rows,'original_sources_and_map_unchanged':True,'temporary_derived_trees_removed_after_full_verification':True,'publication_go':False,'scope':'Actual public canonical payload to declared logical layout in both modes. Omitted private originals and private metadata do not become reconstructible; projected public JSON stays projected. No archive decoding or new model/render check.'}
 dump(out/'public-restore-proof.json',report);print(json.dumps({'passed':True,'modes':2,'canonical':543,'logical':1528}))
if __name__=='__main__':main()
