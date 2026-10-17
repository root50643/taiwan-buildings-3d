"""Check the exact two Blender command insertions and reject any other AST change."""
from pathlib import Path
import ast,argparse,copy,hashlib,json,os,sys
OLD='538625810f924812964d965b6b440b056b7dab528c4fcfdd02a000c295476197'
NEW='531fff0d8167cd88695f1a6a76772a373536f2871397608543bf1b8b71f2d156'
EXPR='import sys; sys.dont_write_bytecode = True'
NAMES={'source-scene-state-reproduction','saved-blend-nine-rerenders'}
def require(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(old,new):
 a=ast.parse(old);b=ast.parse(new);seen=set()
 for n in ast.walk(b):
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='run' and len(n.args)>=2 and isinstance(n.args[0],ast.Constant) and n.args[0].value in NAMES:
   label=n.args[0].value;require(label not in seen,'Duplicate target stage');seen.add(label);lst=n.args[1];require(isinstance(lst,ast.List),'Command must remain a list')
   values=[x.value if isinstance(x,ast.Constant) else None for x in lst.elts]
   prefix=['blender','--background','--threads','1','--python-exit-code','1','--python-expr',EXPR,'--python']
   require(values[:len(prefix)]==prefix,'Exact Blender guard command differs');del lst.elts[6:8]
 require(seen==NAMES,'Incomplete target stages')
 require(ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False),'Non-command runner AST changed')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--original',type=Path,required=True);ap.add_argument('--adapted',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);x=ap.parse_args();require(not x.out.exists() and len(os.sched_getaffinity(0))==1,'Fresh output and one CPU required');x.out.mkdir(parents=True)
 require(sha(x.original)==OLD and sha(x.adapted)==NEW,'Pinned source mismatch');original=x.original.read_text();adapted=x.adapted.read_text();rows=[]
 changes=[('exact_two_guard_insertions',adapted,True),('missing_one_guard',adapted.replace("'--python-expr','"+EXPR+"',",'',1),False),('false_guard',adapted.replace(EXPR,'import sys; sys.dont_write_bytecode = False',1),False),('unexpected_source_change',adapted.replace("summary['elapsed_seconds']=time.time()-start","summary['elapsed_seconds']=0"),False),('changed_cpu_threads',adapted.replace("'--threads','1'","'--threads','2'",1),False),('extra_expression',adapted.replace(EXPR,EXPR+'; print(1)',1),False)]
 for name,value,expected in changes:
  accepted=False;error=None
  try:verify(original,value);accepted=True
  except RuntimeError as e:error=str(e)
  require(accepted is expected,'Unexpected control result: '+name);rows.append({'case':name,'expected_accept':expected,'accepted':accepted,'rejection':error,'passed':True})
 require(sha(x.original)==OLD and sha(x.adapted)==NEW,'Sources changed');r={'passed':True,'optimization_level':sys.flags.optimize,'cpu_affinity':sorted(os.sched_getaffinity(0)),'source_sha256':sha(__file__),'original_runner_sha256':OLD,'adapted_runner_sha256':NEW,'all_sources_unchanged':True,'cases':rows,'scope':'Exact command-only runner adaptation controls; no geometry, source rebuild, scene load or render executes in these AST controls.'};(x.out/'results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'case_count':len(rows)}))
if __name__=='__main__':main()
