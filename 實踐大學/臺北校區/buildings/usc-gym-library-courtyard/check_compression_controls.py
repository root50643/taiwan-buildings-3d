"""Exercise both CSV writer formats and reject missing/corrupt/mislabeled evidence."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
from verification.qa_common import open_compressed_csv,require
R=Path(__file__).resolve().parent;out=R/'qa/compression-controls';out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
fixture=R/'qa/current/controls/python_B/normal_box/fixture.stl'
mode=['-B']+(['-'+'O'*sys.flags.optimize] if sys.flags.optimize else [])
reports={};results=[]
def verify(path,q):
 require(path.stat().st_size==q['csv_compressed_bytes'],'Compressed byte count mismatch')
 require(sha(path)==q['csv_compressed_sha256'],'Compressed SHA256 mismatch')
 with open_compressed_csv(path,q['csv_compression']) as f:
  h=hashlib.sha256();n=0
  while b:=f.read(1024*1024):h.update(b);n+=len(b)
 require(h.hexdigest()==q['uncompressed_csv_sha256'] and n==q['uncompressed_csv_bytes'],'CSV SHA256 or byte count mismatch')
def test(name,path,q,expected):
 try:verify(path,q);observed=True;error=None
 except Exception as e:observed=False;error=type(e).__name__+': '+str(e).replace(str(R),'[candidate]')
 results.append({'case':name,'expected_valid':expected,'observed_valid':observed,'control_passed':observed is expected,'error':error})
for fmt in ['gzip','xz']:
 d=out/fmt;cmd=[sys.executable,*mode,'verification/check_dense_surface.py','--stl',str(fixture.relative_to(R)),'--out',str(d.relative_to(R)),'--csv-compression',fmt]
 p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
 q=json.loads((d/'dense-check.json').read_text()) if (d/'dense-check.json').is_file() else {}
 require(p.returncode==0 and q.get('passed') is True,'Real format-writer control failed')
 reports[fmt]=q;test('real_writer_'+fmt,d/q['csv_file'],q,True)
require(reports['gzip']['uncompressed_csv_sha256']==reports['xz']['uncompressed_csv_sha256'],'Writer formats changed CSV bytes')
q=reports['xz'];original=out/'xz'/q['csv_file']
test('missing_file',out/'missing.csv.xz',q,False)
for field in ['csv_compressed_sha256','uncompressed_csv_sha256']:
 altered=dict(q);altered[field]='0'*64;test('wrong_'+field,original,altered,False)
altered=dict(q);altered['csv_compression']='gzip';test('wrong_declared_format',original,altered,False)
altered=dict(q);altered['csv_compression']='unknown';test('unsupported_format',original,altered,False)
renamed=out/'wrong_extension.csv.gz';shutil.copy2(original,renamed);test('wrong_extension',renamed,q,False)
corrupt=out/'corrupt.csv.xz';data=bytearray(original.read_bytes());data[-15]^=1;corrupt.write_bytes(data);altered=dict(q);altered['csv_compressed_sha256']=sha(corrupt);test('corrupt_with_matching_outer_hash',corrupt,altered,False)
wrong=out/'gzip_disguised.csv.xz';shutil.copy2(out/'gzip'/reports['gzip']['csv_file'],wrong);altered=dict(q);altered['csv_compressed_sha256']=sha(wrong);altered['csv_compressed_bytes']=wrong.stat().st_size;test('gzip_disguised_as_xz_with_matching_outer_hash',wrong,altered,False)
q={'passed':all(x['control_passed'] for x in results),'python_optimization_level':sys.flags.optimize,'controls':results,'same_csv_hash_both_real_writers':reports['gzip']['uncompressed_csv_sha256'],'reader_source_sha256':sha(R/'verification/qa_common.py'),'writer_source_sha256':sha(R/'verification/check_dense_surface.py'),'control_source_sha256':sha(__file__),'scope':'Synthetic small-box writer and container-integrity controls; current model evidence is separately checked.'}
(R/'compression-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));raise SystemExit(0 if q['passed'] else 1)
