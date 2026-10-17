"""Exercise the control-fixture SDNA decoder with authenticated changed bytes.
These cases reach the structural/field gates, not only the frozen model SHA gate.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys

def require(v,m):
 if not v:raise RuntimeError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--blend',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();require(not a.out.exists() and len(os.sched_getaffinity(0))==1,'Fresh output and single CPU required');a.out.mkdir(parents=True);original=a.blend.read_bytes();require(sha(original)=='e3ec3b7f00c8ae33b9734a3f6d10b7bc7ab1ff24fae3f0f97349616dabe8e67a','Unexpected base fixture');tool=Path(__file__).with_name('audit_control_blend_sdna.py');toolhash=sha(tool.read_bytes());rows=[]
 def case(name,data,expected,needle='',wrong_hash=False,existing=False):
  inp=a.out/(name+'.blend');inp.write_bytes(data);out=a.out/(name+'.json')
  if existing:out.write_text('{"original":true}\n')
  before=out.read_bytes() if existing else None
  cp=subprocess.run([sys.executable,'-B',*(['-O'] if sys.flags.optimize else []),str(tool),'--blend',str(inp),'--expected-sha256','0'*64 if wrong_hash else sha(data),'--out',str(out)],capture_output=True,text=True);(a.out/(name+'.stdout.txt')).write_text(cp.stdout);(a.out/(name+'.stderr.txt')).write_text(cp.stderr);passed=(cp.returncode==0) is expected and (expected or needle in cp.stderr);require(passed,'Control differs '+name)
  if existing:require(out.read_bytes()==before,'Existing evidence overwritten')
  rows.append({'name':name,'expected_accept':expected,'accepted':cp.returncode==0,'returncode':cp.returncode,'expected_error':needle or None,'passed':passed,'fixture_sha256':sha(data),'result_sha256':sha(out.read_bytes()) if out.exists() else None})
 case('positive',original,True)
 for name,index,value in [('changed_home_buffer',171624+6,65),('changed_output_buffer',231956+4,88),('changed_inactive_ui_tail',171624+12,88)]:
  b=bytearray(original);b[index]=value;case(name,bytes(b),False,'Unexpected path field')
 b=bytearray(original);marker=b'/' + b'workspace/x';b[171624+100:171624+100+len(marker)]=marker;case('new_private_marker_inside_buffer',bytes(b),False,'Unexpected path field')
 case('trailing_block_bytes',original+b'/',False,'Incomplete or trailing Blender block stream')
 case('truncated_block_stream',original[:-10],False,'Incomplete or trailing Blender block stream')
 b=bytearray(original);b[9:12]=b'404';case('wrong_format_version',bytes(b),False,'Unsupported control Blend SDNA format')
 b=bytearray(original);b[0]=88;case('wrong_header',bytes(b),False,'Invalid Blender header')
 case('wrong_declared_hash',original,False,'Original Blend hash mismatch',wrong_hash=True)
 case('existing_output',original,False,'Fresh output required',existing=True)
 require(a.blend.read_bytes()==original and sha(tool.read_bytes())==toolhash,'Original fixture/tool changed');report={'passed':True,'optimization_level':sys.flags.optimize,'case_count':len(rows),'cases':rows,'base_blend_sha256':sha(original),'source_sha256':toolhash,'test_source_sha256':sha(Path(__file__).read_bytes()),'all_original_input_and_tool_bytes_unchanged':True,'scope':'Independent decoder controls for exact control-fixture binary privacy profiles; changed bytes are authenticated to exercise SDNA structural and fixed field-buffer gates. No geometry/Blender engine or model acceptance.'};(a.out/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'optimization_level':sys.flags.optimize,'case_count':len(rows)}))
if __name__=='__main__':main()
