if __name__ == '__main__':
    raise SystemExit('Historical provenance only. This fixed-review script depends on the old snapshot and external receipts; do not rerun it against the published package or overwrite archived evidence.')

from pathlib import Path
import hashlib,io,json,re
from PIL import Image
ROOT=Path(__file__).resolve().parent
ORIGINAL=ROOT.parent/'csu-76681'
IMPORTED=Path('<MODEL_ROOT>/qa/independent-76681')
manifest=json.loads((IMPORTED/'import-manifest.json').read_text(encoding='utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
rows=[]
def numbers(v,path=''):
    if isinstance(v,dict):return {k2:v2 for k,val in v.items() for k2,v2 in numbers(val,path+'.'+k).items()}
    if isinstance(v,list):return {k2:v2 for i,val in enumerate(v) for k2,v2 in numbers(val,path+f'[{i}]').items()}
    return {path:v} if isinstance(v,(int,float,bool)) or v is None else {}
for r in manifest['files']:
    source=r['source_path']
    if not source:continue
    part=source.split('task-7/csu-76681/',1)
    if len(part)!=2:continue
    old=ORIGINAL/part[1];dest=IMPORTED/r['destination_path'];a=old.read_bytes();b=dest.read_bytes()
    row={'path':r['destination_path'],'original_matches_recorded_source_SHA':sha(a)==r['source_sha256'],'delivered_matches_recorded_SHA':sha(b)==r['delivered_sha256'],'exact_bytes_unchanged':a==b}
    if old.suffix.lower()=='.json':
        ja,jb=json.loads(a.decode('utf-8')),json.loads(b.decode('utf-8'))
        row['all_numeric_boolean_null_values_same']=numbers(ja)==numbers(jb)
    if old.suffix.lower()=='.md':row['report_text_exact_bytes_unchanged']=a==b
    if old.suffix.lower()=='.png':
        ia,ib=Image.open(io.BytesIO(a)),Image.open(io.BytesIO(b));ia.load();ib.load()
        row['decoded_pixels_exactly_unchanged']=ia.size==ib.size and ia.mode==ib.mode and ia.tobytes()==ib.tobytes()
    rows.append(row)
report={'fixed_original_review_commit':manifest['fixed_review_commit'],'original_source_manifest_hash_matches_own_manifest':sha((ORIGINAL/'evidence-manifest.json').read_bytes())==manifest['source_manifest_sha256'],'checked_source_files':len(rows),'files':rows,'all_original_and_delivered_SHA_bindings_match':all(r['original_matches_recorded_source_SHA'] and r['delivered_matches_recorded_SHA'] for r in rows),'all_JSON_scientific_numeric_bool_null_values_preserved':all(r.get('all_numeric_boolean_null_values_same',True) for r in rows),'all_imported_Markdown_reports_exact_original_bytes':all(r.get('report_text_exact_bytes_unchanged',True) for r in rows),'independent_render_pixels_preserved':all(r.get('decoded_pixels_exactly_unchanged',True) for r in rows),'scope':'Checks the imported reviewer evidence against the reviewer original directory; path-redacted scripts are not executed and no original report is rewritten.'}
(ROOT/'imported-evidence-crosscheck.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
assert report['all_original_and_delivered_SHA_bindings_match'] and report['all_JSON_scientific_numeric_bool_null_values_preserved'] and report['all_imported_Markdown_reports_exact_original_bytes'] and report['independent_render_pixels_preserved']
print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))
