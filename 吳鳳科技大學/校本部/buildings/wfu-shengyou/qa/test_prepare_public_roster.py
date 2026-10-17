"""Small synthetic negative controls for the explicit roster sealer."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,copy,hashlib,json,tempfile,types
HERE=Path(__file__).absolute().parent
raw=(HERE/'prepare_public_roster.py').read_bytes();P=types.ModuleType('tested_sealer');P.__file__=str(HERE/'prepare_public_roster.py');exec(compile(raw,P.__file__,'exec'),P.__dict__)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();cases=[]
 with tempfile.TemporaryDirectory() as tmp:
  base=Path(tmp);source=base/'source';source.mkdir();(source/'proof.json').write_text('{"passed":true,"strict_passed":false}\n');(source/'same.json').write_bytes((source/'proof.json').read_bytes());(source/'path.json').write_text('{"path":"original/item","strict_passed":false,"exit":1}\n')
  def row(path,out):return {'source_root':'test','source_relative_path':path,'public_path':'qa/'+out,'restore_path':'author/'+path,'new_controls_member':True}
  plan={'schema':'wfu-public-qa-explicit-roster-v1','stl_sha256':'0'*64,'original_numerical_strict_passed':False,'awaiting_assignments':[],'required_gates':[{'source_root':'test','source_relative_path':'proof.json','checks':[{'pointer':'/passed','equals':True},{'pointer':'/strict_passed','equals':False}]}],'items':[row('proof.json','proof.json'),row('same.json','same.json'),dict(row('path.json','path.json'),changes=[{'pointer':'/path','old':'original/item','new':'logical/item'}])],'omissions':[]}
  def case(name,mutation=None,accept=False):
   candidate=copy.deepcopy(plan)
   if mutation:mutation(candidate)
   out=base/('out-'+name);caught=None
   try:result=P.seal(candidate,{'test':source},out);accepted=True
   except (ValueError,OSError,KeyError,TypeError) as e:accepted=False;caught=type(e).__name__
   if accepted!=accept:raise RuntimeError('Control failed '+name)
   if not accepted and out.exists():raise RuntimeError('Output appeared before rejection '+name)
   cases.append({'case':name,'expected_accept':accept,'accepted':accepted,'passed':True,'caught_type':caught})
   return out
  out=case('complete_exact_roster',accept=True)
  value=json.loads((out/'PUBLIC-COPY-MAP.json').read_text())
  if len(value['files'])!=2 or len(value['copy_map'])!=3 or value['publication_go'] is not False:raise RuntimeError('Incorrect dedup or GO')
  stage=json.loads((out/'NEW-CONTROLS-STAGING-MAP.json').read_text())
  P.M.validated_map(stage)
  if stage['files'] != value['files'] or stage['copy_map'] != value['copy_map']:raise RuntimeError('Staging selection differs')
  case('unresolved_assignment',lambda p:p['awaiting_assignments'].append('awaited'))
  case('strict_upgrade',lambda p:p.update(original_numerical_strict_passed=True))
  case('failed_gate',lambda p:p['required_gates'][0]['checks'][0].update(equals=False))
  case('gate_bool_int_confusion',lambda p:p['required_gates'][0]['checks'][0].update(equals=1))
  case('missing_gate',lambda p:p['required_gates'][0].update(source_relative_path='absent'))
  case('missing_payload',lambda p:p['items'][0].update(source_relative_path='absent'))
  case('unsafe_source_path',lambda p:p['items'][0].update(source_relative_path='../proof.json'))
  case('unsafe_public_path',lambda p:p['items'][0].update(public_path='../escape'))
  case('duplicate_restore_target',lambda p:p['items'][1].update(restore_path=p['items'][0]['restore_path']))
  case('conflicting_canonical_target',lambda p:p['items'][2].update(public_path=p['items'][0]['public_path']))
  case('expected_hash_mismatch',lambda p:p['items'][0].update(expected={'bytes':(source/'proof.json').stat().st_size,'sha256':'0'*64}))
  case('unresolved_projection',lambda p:p['items'][2].update(projection_status='awaiting'))
  case('projection_source_drift',lambda p:p['items'][2]['changes'][0].update(old='wrong'))
  case('projection_science_upgrade',lambda p:p['items'][2].update(changes=[{'pointer':'/strict_passed','old':False,'new':True}]))
  # Keep all original fifteen cases; add precise key-label/omission controls.
  (source/'keys.json').write_text('{"files":{"original/key":{"bytes":1,"sha256":"abc","strict":false},"occupied":{"exit":1}}}\n')
  def keyplan(p,changes):
   p['items'].append(dict(row('keys.json','keys.json'),key_changes=changes))
  validkey={'parent_pointer':'/files','old':'original/key','new':'public/key'}
  out=case('exact_key_label_alias',lambda p:keyplan(p,[validkey]),accept=True)
  keymap=json.loads((out/'PUBLIC-COPY-MAP.json').read_text())
  keyproof=keymap['projection_bindings'][-1]
  if keyproof['key_changes'] != [{'parent_json_pointer':'/files','original_key_sha256':P.M.digest(b'original/key'),'public_key':'public/key'}]:raise RuntimeError('Key-label binding differs')
  if 'original/key' in json.dumps(keyproof):raise RuntimeError('Private original key leaked through public binding')
  def kmutate(field,value):
   v=dict(validkey);v[field]=value;return lambda p:keyplan(p,[v])
  case('key_unknown_parent',kmutate('parent_pointer','/absent'))
  case('key_nondict_parent',kmutate('parent_pointer','/files/occupied/exit'))
  case('key_unknown_original',kmutate('old','absent'))
  case('key_destination_collision',kmutate('new','occupied'))
  case('key_boolean_label',kmutate('new',True))
  case('key_unchanged_label',kmutate('new','original/key'))
  case('key_duplicate_instruction',lambda p:keyplan(p,[validkey,validkey]))
  case('key_unknown_instruction',lambda p:keyplan(p,[dict(validkey,extra=True)]))
  omission={'original_root':'test','original_relative_path':'old-label/input','bytes':1,'sha256':'0'*64,'retained_privately':True,'public_original_reconstruction_claimed':False,'public_relative_path_alias':'logical/input'}
  out=case('exact_omission_label_alias',lambda p:p['omissions'].append(omission),accept=True)
  om=json.loads((out/'PUBLIC-COPY-MAP.json').read_text())['omissions'][0]
  if om['original_relative_path']!='logical/input' or om['original_relative_path_label_sha256']!=P.M.digest(b'old-label/input') or om['original_relative_path_is_public_logical_alias'] is not True or om['bytes']!=1:raise RuntimeError('Omission alias metadata differs')
  case('omission_traversal_alias',lambda p:p['omissions'].append(dict(omission,public_relative_path_alias='../escape')))
  case('omission_boolean_alias',lambda p:p['omissions'].append(dict(omission,public_relative_path_alias=True)))
  case('omission_unchanged_alias',lambda p:p['omissions'].append(dict(omission,public_relative_path_alias='old-label/input')))
  case('omission_binding_collision',lambda p:p['omissions'].append(dict(omission,original_relative_path_label_sha256='0'*64)))
 result={'passed':True,'optimization_level':sys.flags.optimize,'case_count':len(cases),'cases':cases,'prepare_source_sha256':hashlib.sha256(raw).hexdigest(),'restore_source_sha256':hashlib.sha256((HERE/'restore_scientific_layout.py').read_bytes()).hexdigest(),'test_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'original_evidence_read':False,'publication_go':False}
 with a.out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({'passed':True,'case_count':len(cases)}))
if __name__=='__main__':main()
