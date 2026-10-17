"""Exact common-argv guard peer: unchanged author-wrapper AST after two literal removal."""
from pathlib import Path
import ast,argparse,hashlib,json,os,sys
OLD='127c3762746bd2ade2a5c27090116793bf2c6e2fd7eb8471a6badcd78daf69d0'
NEW='de4565114c476031a899ad03db1c53af15c773490836f391b5a7a36e3b15cf3a'
EXPR='import sys; sys.dont_write_bytecode = True'
def require(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(old,new):
 a=ast.parse(old);b=ast.parse(new);seen=0
 for n in ast.walk(b):
  if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='common':
   seen+=1;require(isinstance(n.value,ast.List),'Common must remain list');values=[x.value if isinstance(x,ast.Constant) else None for x in n.value.elts]
   require(values==['blender','--background','--threads','1','--python-exit-code','1','--python-expr',EXPR,'--python'],'Exact guard differs');del n.value.elts[6:8]
 require(seen==1,'One common command required');require(ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False),'Other wrapper AST changed')
def main():
 p=argparse.ArgumentParser();p.add_argument('--original',type=Path,required=True);p.add_argument('--adapted',type=Path,required=True);p.add_argument('--out',type=Path,required=True);x=p.parse_args();require(not x.out.exists() and len(os.sched_getaffinity(0))==1,'Fresh output and one CPU required');x.out.mkdir(parents=True);require(sha(x.original)==OLD and sha(x.adapted)==NEW,'Pinned wrapper differs');a=x.original.read_text();b=x.adapted.read_text();rows=[]
 cases=[('exact_single_common_guard',b,True),('missing_guard',b.replace("'--python-expr','"+EXPR+"',",''),False),('false_guard',b.replace(EXPR,'import sys; sys.dont_write_bytecode = False'),False),('changed_threads',b.replace("'--threads','1'","'--threads','2'"),False),('removed_inspect_only',b.replace("'--inspect-only'","'--other'"),False),('extra_expression',b.replace(EXPR,EXPR+'; print(1)'),False)]
 for name,s,expected in cases:
  ok=False;error=None
  try:verify(a,s);ok=True
  except RuntimeError as e:error=str(e)
  require(ok is expected,'Control differs: '+name);rows.append({'case':name,'expected_accept':expected,'accepted':ok,'rejection':error,'passed':True})
 unchanged=sha(x.original)==OLD and sha(x.adapted)==NEW;require(unchanged,'Wrapper changed');r={'passed':True,'optimization_level':sys.flags.optimize,'cpu_affinity':sorted(os.sched_getaffinity(0)),'source_sha256':sha(__file__),'original_wrapper_sha256':OLD,'adapted_wrapper_sha256':NEW,'all_sources_unchanged':unchanged,'cases':rows,'scope':'Author wrapper exact argv-only adaptation peer controls. Source/scene/PNG predicates and inspect-only default remain identical; real shared runtime cache controls are separate.'};(x.out/'results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'case_count':len(rows)}))
if __name__=='__main__':main()
