"""Fresh small controls for the fixed WFU v12 postflight branch only.
Use genuine completed normal evidence. Mock only the already-verified dense-audit
return value, so policy mutations do not rerun geometry or duplicate the original
CSV predicate work. Final postflight always invokes the real dense audit.
All reports/files on disk remain unchanged.
"""
from pathlib import Path
import argparse,copy,gzip,hashlib,importlib.util,io,json,sys

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(v,m):
 if not v:raise RuntimeError(m)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();require(not a.out.exists(),'Fresh output required');a.out.mkdir(parents=True);r=a.run.resolve();f=r/'frozen';sys.path[:0]=[str(f/'qa/tools'),str(f/'qa/verification'),str(Path(__file__).parent)]
 import inspect_flagged_wfu_mode as mod
 from qa_common import checker_inventory
 version=json.loads((r/'independent-execution-summary.json').read_text())['version'];base=r/'geometry/normal';stl=f/'models'/version/'model.stl';expected='8348213614296746732da6a8024821ff48536e847419fe13545dc1ab20730ca0';require(sha(stl)==expected,'Case STL mismatch')
 cached=json.loads((base/'dense-evidence.json').read_text());require(cached['passed'] is True and cached['completed'] is True and cached['all_expected_flag_indices_and_reasons_match'] is True and cached['original_numerical_strict_passed'] is False,'Genuine cached audit required')
 mod.audit=lambda *args:copy.deepcopy(cached)
 original_read=mod.read;original_open=mod.gzip.open;exits={'standard':1,'intersections':0,'intersection-controls':0,'dense-evidence':0};cases=[]
 def case(name,expected_pass,needle='',mutate=None,ledger=None,row_mutate=None):
  def read(path):
   value=original_read(path)
   if mutate:mutate(Path(path).name,value)
   return value
  def op(path,*args,**kwargs):
   if Path(path).name=='exact-recorded-ray-details.jsonl.gz' and row_mutate:
    with original_open(path,'rt') as stream:values=[json.loads(x) for x in stream]
    row_mutate(values)
    return io.StringIO(''.join(json.dumps(x)+'\n' for x in values))
   return original_open(path,*args,**kwargs)
  mod.read=read;mod.gzip.open=op;accepted=False;error=''
  try:mod.inspect_mode(base,expected,220.0,checker_inventory(),0,exits if ledger is None else ledger,stl);accepted=True
  except Exception as e:error=str(e)
  finally:mod.read=original_read;mod.gzip.open=original_open
  verified=accepted is expected_pass and (expected_pass or needle in error);cases.append({'case':name,'expected_accept':expected_pass,'accepted':accepted,'expected_rejection_reason':needle or None,'reason_matched':expected_pass or needle in error,'passed':verified});require(verified,'Control failed: '+name)
 def mutate_file(filename,field,value):
  return lambda n,d:d.__setitem__(field,value) if n==filename else None
 case('genuine_strict_false_and_complete_exact_evidence',True)
 for name,ledger in [('missing_stage',{}),('extra_stage',{**exits,'surprise':0}),('missing_dense_stage',{k:v for k,v in exits.items() if k!='dense-evidence'})]:case(name,False,'Incomplete or unexpected child stage exit map',ledger=ledger)
 for name,value in [('boolean',True),('float',1.),('string','1'),('zero',0),('unexpected',2)]:case('standard_exit_'+name,False,'Unexpected typed child stage exit',ledger={**exits,'standard':value})
 case('false_exact_exit',False,'Unexpected typed child stage exit',ledger={**exits,'intersections':False})
 case('aggregate_strict_upgraded',False,'strict=false must remain false',mutate=mutate_file('qa-summary.json','strict_passed',True))
 case('dense_strict_upgraded',False,'Gate incomplete or unexpected failure',mutate=mutate_file('dense-check.json','strict_passed',True))
 case('incomplete_exact_classification',False,'classification incomplete',mutate=mutate_file('exact-recorded-ray-summary.json','completed',False))
 case('partial_flag_selection',False,'classification incomplete',mutate=mutate_file('exact-recorded-ray-summary.json','all_flagged_samples_selected',False))
 case('wrong_exact_flag_count',False,'coverage or strict semantics',mutate=mutate_file('exact-recorded-ray-summary.json','selected_samples',34))
 case('upgraded_exact_strict',False,'coverage or strict semantics',mutate=mutate_file('exact-recorded-ray-summary.json','original_numerical_strict_passed',True))
 case('wrong_exact_source_binding',False,'input/source binding differs',mutate=lambda n,d:d['input_and_tool_sha256'].__setitem__('diagnostic_source','0'*64) if n=='exact-recorded-ray-summary.json' else None)
 case('missing_exact_detail_row',False,'do not cover original flags',row_mutate=lambda rows:rows.pop())
 case('duplicate_exact_detail_row',False,'do not cover original flags',row_mutate=lambda rows:rows.append(copy.deepcopy(rows[0])))
 case('incomplete_exact_detail_row',False,'Exact row incomplete',row_mutate=lambda rows:rows[0].__setitem__('exact_classification_completed',False))
 case('substituted_original_ray_descriptor',False,'not the original recorded event',row_mutate=lambda rows:rows[0]['original_cpp_descriptor'].__setitem__('origin_x_hex','0x0p+0'))
 case('changed_original_flag_reasons',False,'not the original recorded event',row_mutate=lambda rows:rows[0].__setitem__('original_numerical_reasons',[]))
 case('short_exact_first_chord',False,'Exact first chord is short',row_mutate=lambda rows:rows[0].__setitem__('conservative_first_solid_chord_squared_mm2_exact','1/4'))
 case('wrong_first_interval_state',False,'Exact interval ordering fails',row_mutate=lambda rows:rows[0]['classified_open_intervals'][0].__setitem__('state','inside'))
 report={'passed':all(x['passed'] for x in cases),'optimization_level':sys.flags.optimize,'cases':cases,'case_count':len(cases),'source_sha256':sha(__file__),'case_policy_source_sha256':sha(Path(mod.__file__)),'baseline_stl_sha256':expected,'baseline_dense_audit_sha256':sha(base/'dense-evidence.json'),'scope':'Postflight policy controls only. A genuine completed dense-audit result is cached for these tests. Full final read-only reviews invoke the unchanged actual dense audit; no model geometry is rerun, original file modified, or original strict=false waived.'}
 (a.out/'case-controls.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'cases':len(cases)}))
if __name__=='__main__':main()
