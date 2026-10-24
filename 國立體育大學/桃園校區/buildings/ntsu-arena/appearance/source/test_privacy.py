"""Read-only full-buffer audit and temporary negative/false-positive controls."""
from pathlib import Path
import argparse,json,subprocess,sys,tempfile,hashlib
if sys.flags.optimize:raise RuntimeError('Run without optimization')
p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,required=True);p.add_argument('--blender',default='blender');p.add_argument('--report',type=Path,required=True);a=p.parse_args();src=Path(__file__).resolve().parent
original=a.blend.read_bytes();before=hashlib.sha256(original).hexdigest()
def audit(path,out):return subprocess.run([sys.executable,str(src/'verify_path_buffers.py'),'--blend',str(path),'--report',str(out)],capture_output=True,text=True)
with tempfile.TemporaryDirectory(prefix='privacy-controls-')as tmp:
 t=Path(tmp);r=t/'audit.json';good=audit(a.blend,r);assert good.returncode==0,good.stderr;report=json.loads(r.read_text());assert report['all_pass'] and not report.get('factory_baseline_only')
 field=next(f for f in report['fields']if f['field']=='FileSelectParams.file[256]');offset=field['offset'];assert original[offset]==0
 # Prove that hidden data AFTER the visible empty filename is rejected.
 bad=bytearray(original);payload=('/'+'workspace/'+'control-only').encode();bad[offset+1:offset+1+len(payload)]=payload;pbad=t/'tail-control.blend';pbad.write_bytes(bad);assert audit(pbad,t/'tail.json').returncode!=0
 # Prove that a visible absolute path is rejected independently of the NUL-tail rule.
 field2=next(f for f in report['fields']if f['field']=='FileGlobal.filename[1024]');bad=bytearray(original);off=field2['offset'];size=field2['fixed_buffer_bytes'];bad[off:off+size]=payload+b'\0'*(size-len(payload));pbad=t/'head-control.blend';pbad.write_bytes(bad);assert audit(pbad,t/'head.json').returncode!=0
 # Genuine factory startup is a baseline, NOT a privacy exemption or input to the model.
 factory=t/'factory.blend';expr="import bpy; bpy.context.preferences.filepaths.save_version=0; bpy.ops.wm.save_as_mainfile(filepath="+repr(str(factory))+")"
 q=subprocess.run([a.blender,'-b','--factory-startup','--python-expr',expr],capture_output=True,text=True);assert q.returncode==0
 fb=factory.read_bytes();tokens=[b'FileGlobal',b'FileSelectParams',b'filepath',b'render']
 assert all(x in fb and x in original for x in tokens),'Factory structural-token control changed'
 factory_result=audit(factory,t/'factory-report.json')
 # Schema identifiers are not real data paths: blanket matches on file/path/dir are false positives.
 # The candidate still passes every FULL allocated path buffer; no baseline bytes are allowlisted.
 result={'status':'PASS','full_buffer_bytes_checked':sum(f['fixed_buffer_bytes']for f in report['fields']),'allocated_path_buffers_checked':report['buffers_checked'],'post_NUL_hidden_path_negative_control':'REJECTED','visible_absolute_path_negative_control':'REJECTED','factory_startup_baseline_generated':True,'factory_structural_token_false_positive_controls':[x.decode()for x in tokens],'factory_paths_or_stale_tails_not_whitelisted':True,'factory_strict_audit_passed':factory_result.returncode==0,'candidate_strict_audit_passed':True,'no_binary_patching_of_deliverable':True,'original_file_unchanged':hashlib.sha256(a.blend.read_bytes()).hexdigest()==before,'scope':'Full allocated path-like fixed-char buffers plus visible values and every post-NUL byte. Factory schema names are not file references; any real private path or stale tail is rejected.'}
assert result['original_file_unchanged'];a.report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
