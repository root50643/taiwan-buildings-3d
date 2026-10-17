"""Frozen-byte Blend privacy profile controls; no Blender or geometry execution."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
SHA='70d8914cefaaceac8572d00c6cfba52b5abbedd18c810175f2deedb47ed2c429'
def require(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--blend',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();require(not a.out.exists(),'Fresh output required');a.out.mkdir(parents=True);require(len(os.sched_getaffinity(0))==1,'Single CPU required');b=a.blend.read_bytes();require(hashlib.sha256(b).hexdigest()==SHA,'Original frozen Blend differs');tool=Path(__file__).with_name('audit_blend_sdna.py');sourcehash=sha(tool);cases=[];positive=None
 def case(name,payload,expected,needle='',expected_hash=SHA,existing=False):
  nonlocal positive
  inp=a.out/(name+'.blend');inp.write_bytes(payload);out=a.out/(name+'.json')
  if existing:out.write_text('{"original":true}\n')
  original_out=out.read_bytes() if existing else None
  args=[sys.executable,'-B',*(['-O'] if sys.flags.optimize else []),str(tool),'--blend',str(inp),'--expected-sha256',expected_hash,'--out',str(out)];cp=subprocess.run(args,capture_output=True,text=True);(a.out/(name+'.stdout.txt')).write_text(cp.stdout);(a.out/(name+'.stderr.txt')).write_text(cp.stderr);okay=(cp.returncode==0) is expected and (expected or needle in cp.stderr);require(okay,'Control outcome differs: '+name)
  if expected:
   positive=json.loads(out.read_text());require(positive['passed'] is True and positive['exact_candidate_generic_fields_only'] is True and positive['source_sha256']==sourcehash,'Positive profile incomplete')
  elif existing:require(out.read_bytes()==original_out,'Existing report changed')
  cases.append({'name':name,'expected_accept':expected,'accepted':cp.returncode==0,'returncode':cp.returncode,'expected_error':needle or None,'passed':okay,'fixture_sha256':sha(inp),'result_sha256':sha(out) if out.exists() else None})
 case('positive',b,True)
 edits=[('ui_home_changed',171624+6,65),('default_render_path_changed',231956+4,88),('inactive_ui_buffer_changed',171624+12,88),('header_changed',0,88)]
 for n,index,value in edits:
  x=bytearray(b);x[index]=value;case(n,bytes(x),False,'Original Blend hash mismatch')
 case('new_private_path_appended',b+b'/' + b'workspace/private',False,'Original Blend hash mismatch')
 case('truncated_blend',b[:-10],False,'Original Blend hash mismatch')
 case('wrong_expected_candidate',b,False,'restricted to the frozen WFU v13 Blend',expected_hash='0'*64)
 case('existing_output_not_overwritten',b,False,'Fresh output required',existing=True)
 require(sha(a.blend)==SHA and sha(tool)==sourcehash,'Original input/tool changed');profile=[]
 for f,label in zip(positive['field_findings'],['generic_file_browser_home','generic_unrendered_output_default']):
  profile.append({'classification':label,'block_code':f['block_code'],'struct':f['struct'],'field':f['field'],'field_type':f['field_type'],'field_absolute_byte_offset':f['field_absolute_byte_offset'],'marker_absolute_byte_offset':f['marker_absolute_byte_offset'],'marker_offset_in_field':f['marker_offset_in_field'],'field_buffer_bytes':f['field_buffer_bytes'],'field_buffer_sha256':f['field_buffer_sha256'],'after_first_nul_nonzero_bytes':f['after_first_nul_nonzero_bytes']})
 result={'passed':True,'optimization_level':sys.flags.optimize,'case_count':len(cases),'cases':cases,'blend_sha256':SHA,'source_sha256':sourcehash,'test_source_sha256':sha(__file__),'positive_report_sha256':sha(a.out/'positive.json'),'all_original_input_and_tool_bytes_unchanged':True,'profile':profile,'scope':'Only the exact frozen Blend is eligible. SDNA locates and hashes both generic non-resource UI/output-default fields, including every NUL tail byte. Every changed candidate byte is rejected. The rest of the binary still requires the independent bounded private-path/credential-pattern scan and full scene resource inspection. No Blender or geometry engine was used.'};(a.out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'optimization_level':sys.flags.optimize,'case_count':len(cases)}))
if __name__=='__main__':main()
