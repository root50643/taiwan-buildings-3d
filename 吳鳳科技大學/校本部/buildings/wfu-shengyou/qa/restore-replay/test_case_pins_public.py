"""Reject an incorrect copy-map in both actual interpreter modes.
Uses the unchanged runtime launcher and original pinned dependency bytes.
"""
from pathlib import Path
import argparse,ast,hashlib,json,os,subprocess,sys
HERE=Path(__file__).absolute().parent
TARGET=HERE/'replay_public_restore.py'
TARGET_SHA='7862d7e1cfefe921fbaaef0389aae8d10b3a2b7dbf735f4924388acc765429d5'
def require(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def main():
    require(sha(TARGET)==TARGET_SHA and len(os.sched_getaffinity(0))==1,'Source/CPU precondition differs')
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--public-root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    public=a.public_root.absolute();out=a.out.absolute();require(not out.is_relative_to(public) and out.parent.is_dir() and not out.exists(),'Fresh external output required');out.mkdir();root=out/'fixture';root.mkdir()
    pins={'qa/restore_scientific_layout.py':(public/'qa/restore_scientific_layout.py','60b9e1f3b6974e8884501e7f7a5b18446dea04a15886ed864ff7c2de2ab2581e'),'qa/roster_primitives.py':(public/'qa/roster_primitives.py','7211c544e258dd4855ca9747837845aa683d6c28c3939ea0b9a08cb271d69273'),'qa/independent-tools/capture_process.py':(public/'qa/independent-tools/capture_process.py','f44673ed9c2bc04e21bf907fe19745dab18a25ba59c2241bd227b986710c6244')}
    for name,(source,h) in pins.items():
        require(sha(source)==h,'Original dependency differs');p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(source.read_bytes());require(sha(p)==h,'Fixture copy differs')
    (root/'qa/PUBLIC-COPY-MAP.json').write_bytes(b'{}\n')
    capture=root/'qa/independent-tools/capture_process.py'
    nodes=[n for n in ast.parse(capture.read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='BOOT' for t in n.targets)]
    require(len(nodes)==1,'Original BOOT absent');boot=out/'runtime_launcher.py';boot.write_text(ast.literal_eval(nodes[0].value))
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None);rows=[]
    for name,level in [('normal',0),('optimized',1)]:
        runtime=out/(name+'.runtime.json');destination=out/(name+'-forbidden-output')
        args=['--public-root',str(root),'--out',str(destination)]
        command=[sys.executable,'-B',*(['-O'] if level else []),str(boot),str(runtime),str(TARGET),*args]
        run=subprocess.run(command,capture_output=True,text=True,env=env)
        for label,value in [('stdout',run.stdout),('stderr',run.stderr)]:
            with (out/(name+'.'+label+'.log')).open('x') as f:f.write(value)
        (out/(name+'.exit.txt')).write_text(str(run.returncode)+'\n')
        record=json.loads(runtime.read_text())
        require(record['optimization_level']==level and type(record['optimization_level']) is int and record['cpu_affinity']==sorted(os.sched_getaffinity(0)) and record['target_sha256']==TARGET_SHA and record['target_arguments']==args,'Actual runtime differs')
        require(run.returncode==1 and 'Exact canonical map differs' in run.stderr and not destination.exists(),'Wrong map was not rejected before output creation')
        rows.append({'mode':name,'actual_optimization_level':level,'actual_cpu_affinity':record['cpu_affinity'],'returncode':run.returncode,'exact_map_pin_rejected':True,'no_output_created':True,'runtime_sha256':sha(runtime),'stderr_sha256':sha(out/(name+'.stderr.log'))})
    require(sha(TARGET)==TARGET_SHA,'Target changed')
    report={'passed':True,'scope':'Negative exact copy-map binding only; the unchanged generic safe-restorer controls remain separately required. This negative test does not execute the separately required positive full restoration.','source_sha256':TARGET_SHA,'test_source_sha256':sha(Path(__file__)),'runtime_launcher_sha256':sha(boot),'dependencies':{k:h for k,(_,h) in pins.items()},'executions':rows,'original_sources_unchanged':True}
    dump(out/'controls.json',report);print(json.dumps({'passed':True,'actual_modes':2,'controls_sha256':sha(out/'controls.json')}))
if __name__=='__main__':main()
