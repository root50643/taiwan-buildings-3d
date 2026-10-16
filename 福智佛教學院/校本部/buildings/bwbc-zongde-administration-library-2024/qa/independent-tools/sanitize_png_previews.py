"""Make publication PNG copies by removing only reviewed nonvisual text chunks.
Preserves all raw input files, exact IDAT bytes, RGBA pixels and colour metadata.
"""
import argparse,hashlib,json
from pathlib import Path
from png_exact_compare import sanitize,require,SANITIZE_TEXT_KEYS
VIEWS={'front','rear','local-plus-y','local-minus-y','local-plus-x','local-minus-x','top','court-open','court-high-wings','entry','court-stair'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--expected-manifest-sha256',required=True);ap.add_argument('--expected-stl-sha256',required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();require(not a.out.exists(),'Refusing existing output');a.out.mkdir(parents=True)
 report={'passed':False,'source_manifest_sha256':sha(a.manifest),'stl_sha256':a.expected_stl_sha256,'sanitizer_sha256':sha(Path(__file__).with_name('png_exact_compare.py')),'batch_source_sha256':sha(__file__),'removal_whitelist':sorted(SANITIZE_TEXT_KEYS),'views':{}}
 try:
  require(report['source_manifest_sha256']==a.expected_manifest_sha256,'Manifest hash mismatch');source=json.loads(a.manifest.read_text());require(source['stl_sha256']==a.expected_stl_sha256 and set(source['views'])==VIEWS,'Manifest candidate/view set differs');manifest={'stl_sha256':source['stl_sha256'],'source_raw_manifest_sha256':report['source_manifest_sha256'],'metadata_policy':'Only explicit nonvisual text whitelist removed; IDAT and every surviving complete chunk are unchanged.','views':{}}
  for name,row in source['views'].items():
   result=sanitize(a.manifest.parent/(name+'.png'),a.out/(name+'.png'),row['sha256']);report['views'][name]=result;manifest['views'][name]={'sha256':result['sanitized_png_sha256'],'original_raw_png_sha256':row['sha256'],'decoded_rgba_sha256':result['sanitized_rgba_sha256'],'camera':row['camera']}
  require(sha(a.manifest)==report['source_manifest_sha256'] and sha(__file__)==report['batch_source_sha256'] and sha(Path(__file__).with_name('png_exact_compare.py'))==report['sanitizer_sha256'],'Inputs/tools changed during cleanup')
  (a.out/'render-manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n');report['public_manifest_sha256']=sha(a.out/'render-manifest.json');report['passed']=len(report['views'])==11 and all(r['passed'] for r in report['views'].values())
 except Exception as e:report.update(passed=False,error_type=type(e).__name__,error=str(e))
 (a.out/'metadata-cleanup-binding.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({'passed':report['passed'],'views':len(report['views']),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
