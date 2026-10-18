"""Verify sanitized integration bytes; no geometry, slicing or physical test."""
from pathlib import Path
from collections import Counter
import ast
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
def evidence(obj):
    leaves=[]
    counts=Counter()
    def walk(x,p):
        if isinstance(x,dict):
            counts['object']+=1
            for k,v in x.items():walk(v,p+'/'+k.replace('~','~0').replace('/','~1'))
        elif isinstance(x,list):
            counts['array']+=1
            for i,v in enumerate(x):walk(v,p+'/'+str(i))
        elif isinstance(x,str):counts['string']+=1
        else:
            name='null' if x is None else 'boolean' if type(x) is bool else 'integer' if type(x) is int else 'number'
            counts[name]+=1
            leaves.append([p,name,x])
    walk(obj,'')
    return dict(sorted(counts.items())),sha(json.dumps(leaves,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8'))
def main():
    manifest=json.loads((ROOT/'integration-source-manifest.json').read_text(encoding='utf-8'))
    count=0
    for row in manifest['source_files']:
        p=ROOT/row['path']
        b=p.read_bytes()
        assert len(b)==row['copied_bytes'] and sha(b)==row['copied_sha256'],row['path']
        if p.suffix=='.json':
            counts,digest=evidence(json.loads(b.decode('utf-8-sig')))
            assert counts==row['json_counts'] and digest==row['json_numeric_boolean_null_sha256'],row['path']
            count+=sum(counts.get(k,0) for k in ['null','boolean','integer','number'])
        if p.suffix=='.py':ast.parse(b.decode('utf-8-sig'),filename=row['path'])
    for row in manifest['integration_additions_with_checksums']:
        b=(ROOT/row['path']).read_bytes()
        assert len(b)==row['bytes'] and sha(b)==row['sha256'],row['path']
    links=[]
    for p in ROOT.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
            if re.match(r'[A-Za-z][A-Za-z0-9+.-]*:',target) or target.startswith('#'):continue
            q=(p.parent/target.split('#')[0])
            assert q.exists(),(p.relative_to(ROOT).as_posix(),target)
            links.append((p.relative_to(ROOT).as_posix(),target))
    print(json.dumps({'pass':True,'source_payload_files':len(manifest['source_files']),'numeric_boolean_null_leaves_verified':count,'local_markdown_links_verified':len(links),'scope':'Integration bytes and numeric digests only; no manufacturing recomputation.'}))
if __name__=='__main__':main()
