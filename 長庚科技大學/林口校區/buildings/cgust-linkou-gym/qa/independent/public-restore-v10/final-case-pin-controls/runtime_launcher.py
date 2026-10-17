import sys,os,json,runpy,hashlib,pathlib
p=pathlib.Path(sys.argv[1]);target=pathlib.Path(sys.argv[2]);args=sys.argv[3:]
p.write_text(json.dumps({'optimization_level':sys.flags.optimize,'cpu_affinity':sorted(os.sched_getaffinity(0)),'python_executable':sys.executable,'target':str(target),'target_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'target_arguments':args},indent=2)+'\n')
sys.path.insert(0,str(target.parent));sys.argv=[str(target),*args]
runpy.run_path(str(target),run_name='__main__')
