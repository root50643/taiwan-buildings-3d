"""Additional read-only all-record structure/math review of fresh WFU v12 evidence.
Consumes the exact frozen author helper after independent controls. Does not
replace fresh original geometry computation or the original strict=False.
"""
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,json,sys
HELPER='3a1c5ecf34dbe7b90d747cc191ecf9cf536878e6143362f083f1ad4a76c23d14'
def require(v,m):
 if not v:raise RuntimeError(m)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();require(not a.out.exists(),'Fresh output required');a.out.mkdir(parents=True);r=a.run.resolve();helper=r/'frozen/qa/postflight-tools/artifact_structure.py';require(sha(helper)==HELPER,'Frozen independently reviewed helper differs');spec=importlib.util.spec_from_file_location('structure',helper);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 tracked={};summary={'passed':False,'optimization_level':sys.flags.optimize,'helper_sha256':HELPER,'reviewer_sha256':sha(__file__),'scope':'Additional read-only structural/math consistency check of all original independent section polygons, exact recorded rays and exact contact records. Fresh core predicates and all source/render bindings remain required separately. Original strict=False remains unchanged.'}
 def track(p):
  h=sha(p);k=str(p.relative_to(r));v={'sha256':h,'bytes':p.stat().st_size};require(k not in tracked or tracked[k]==v,'Evidence changed during read');tracked[k]=v;return h
 def read(p,gz=False):
  b=p.read_bytes();require(hashlib.sha256(b).hexdigest()==track(p),'Read changed');return json.loads(gzip.decompress(b) if gz else b)
 try:
  execution=read(r/'independent-execution-summary.json');require(execution['completed'] is True and execution['all_frozen_inputs_and_tools_unchanged'] is True,'Incomplete frozen run');track(helper);results={}
  for mode in ['normal','optimized']:
   b=r/'geometry'/mode;std=b/'standard';section=read(std/'sections/section-check.json');details_path=std/'sections'/section['detail_file'];failures_path=std/'sections'/section['failure_file'];require(track(details_path)==section['detail_sha256'] and track(failures_path)==section['failure_sha256'],'Section detail hash differs');sec=m.validate_sections(section,read(details_path,True),read(failures_path,True))
   dense=read(std/'dense/dense-check.json');flags_path=std/'dense'/dense['flagged_samples_file'];require(track(flags_path)==dense['flagged_samples_sha256'],'Flags hash differs');flags=read(flags_path,True)
   exact=read(b/'exact-recorded-rays/exact-recorded-ray-summary.json');exact_path=b/'exact-recorded-rays'/exact['detail_file'];require(track(exact_path)==exact['detail_sha256'],'Exact rows hash differs')
   with gzip.open(exact_path,'rt') as f:rows=[json.loads(line) for line in f]
   ex=m.validate_exact_rows(rows,flags)
   inter=read(b/'intersections.json');contacts=b/inter['all_actual_intersections']['path'];require(track(contacts)==inter['all_actual_intersections']['sha256'],'Contact rows hash differs')
   with gzip.open(contacts,'rt') as f:contact=m.validate_intersection_contacts(inter,(json.loads(line) for line in f))
   results[mode]={'sections':sec,'exact_recorded_rays':ex,'exact_contacts':contact}
  require(results['normal']==results['optimized'],'Structural/math results differ between independent modes');require(sha(__file__)==summary['reviewer_sha256'],'Reviewer changed');require(all((r/k).stat().st_size==v['bytes'] and sha(r/k)==v['sha256'] for k,v in tracked.items()),'Input changed during read-only review');summary.update(passed=True,all_inputs_unchanged=True,modes=results,evidence_inventory=tracked)
 except Exception as e:summary.update(error_type=type(e).__name__,error=str(e))
 (a.out/'artifact-structure-review.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n');print(json.dumps({'passed':summary['passed'],'optimization_level':sys.flags.optimize,'error':summary.get('error')}));return 0 if summary['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
