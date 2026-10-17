"""Rebuild tiny PNG fixture bytes in memory, without rerunning checker suites."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,types
from pathlib import Path
PINS={'png_exact_compare.py':'8534792905d7fb329e40ccc0277690e2c658ae5f5636b3d2dcb53c2e50ba0cdb','test_png_exact_compare.py':'3e7ac5287c7407226778075268c5a70d8e862b2eeed4743efcc60b5b6c4c75cc'}
def digest(b):return hashlib.sha256(b).hexdigest()
def require(v,m):
 if not v:raise ValueError(m)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--author-root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 modules={};sources=[]
 for name,pin in PINS.items():
  p=a.author_root/'qa/render-tools'/name;b=p.read_bytes();require(digest(b)==pin,'Original generator/tool source mismatch');m=types.ModuleType(Path(name).stem);m.__file__=name;sys.modules[m.__name__]=m;exec(compile(b,name,'exec'),m.__dict__);modules[name]=m;sources.append({'logical_path':'author/qa/render-tools/'+name,'bytes':len(b),'sha256':pin})
 g=modules['test_png_exact_compare.py'];raw=g.png();bad=bytearray(raw);bad[-1]^=1
 fixtures={'original.png':raw,'pixel-change.png':g.png(pixel=13),'metadata-change.png':g.png(stable=b'changed'),'forbidden-ztext.png':g.png(ztext=True),'cleaned.png':g.png(private=False),'bad-crc.png':bytes(bad)}
 rows=[]
 for mode in ('normal','optimized'):
  for name,b in fixtures.items():
   rel='qa/render-check/v10-author/png-controls-'+mode+'/'+name;original=(a.author_root/rel).read_bytes();require(original==b,'Rebuilt bytes mismatch '+rel);rows.append({'restore_path':'author/'+rel,'bytes':len(b),'sha256':digest(b),'actual_bitwise_comparison':True,'fixture_retained_privately':True})
 out={'schema':'cgust-private-png-fixture-actual-rebuild-v1','passed':True,'optimization_level':sys.flags.optimize,'fixture_count':len(rows),'sources':sources,'fixtures':rows,'new_fixture_files_written':0,'generic_checker_suites_rerun':False,'scope':'Exact tiny fixture byte reconstruction only. This does not rerun PNG tests, render images, waive private payload scanning or approve a model.'}
 with a.out.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
 print(json.dumps({'passed':True,'fixture_count':len(rows),'optimization_level':sys.flags.optimize}))
if __name__=='__main__':main()
