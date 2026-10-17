"""Actual Blender source-module cache probe; only tiny controlled fixture is loaded."""
from pathlib import Path
import sys,os,json,hashlib,types,importlib.machinery,marshal,struct

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
args=sys.argv[sys.argv.index('--')+1:];expect=args[0]=='disabled';root=Path(args[1]);assert not root.exists();root.mkdir(parents=True);os.chdir(root)
source=Path('fixture.py');source.write_text('VALUE = 713\ndef value():\n    return VALUE\n');os.utime(source,(0,0))
before=sha(source);runtime=sys.dont_write_bytecode;module=types.ModuleType('cache_fixture');loader=importlib.machinery.SourceFileLoader('cache_fixture','fixture.py');loader.exec_module(module)
caches=sorted(Path('.').glob('__pycache__/*.pyc'));correct=module.value()==713 and module.value.__code__.co_filename=='fixture.py' and sha(source)==before and runtime is expect and len(caches)==(0 if expect else 1) and sorted(os.sched_getaffinity(0))==[0]
rows=[{'path':p.as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [source,*caches]]
r={'passed':bool(correct),'case':'explicit_runtime_guard' if expect else 'environment_only_negative_control','optimization_level':sys.flags.optimize,'cpu_affinity':sorted(os.sched_getaffinity(0)),'ignore_environment':sys.flags.ignore_environment,'environment_requested_no_bytecode':os.environ.get('PYTHONDONTWRITEBYTECODE')=='1','runtime_dont_write_bytecode':runtime,'cache_count':len(caches),'module_value':module.value(),'code_filename':module.value.__code__.co_filename,'source_unchanged':sha(source)==before,'files':rows,'source_sha256':sha(__file__),'scope':'Actual import/cache control only. Does not open a Blend scene or render images.'};Path('results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':bool(correct),'runtime_dont_write_bytecode':runtime,'cache_count':len(caches)}))
if not correct:raise RuntimeError('Actual Blender cache control failed')
