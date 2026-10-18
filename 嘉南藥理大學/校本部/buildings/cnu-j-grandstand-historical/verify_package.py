"""Verify every package file against MANIFEST.sha256; standard library only."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent

def verify(root=R):
    expected={}
    for line in (root/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
        h,name=line.split('  ',1);expected[name]=h
    actual={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256' and '__pycache__' not in p.parts}
    failed=sorted(name for name in expected if actual.get(name)!=expected[name])
    extra=sorted(set(actual)-set(expected))
    return {'files_checked':len(expected),'mismatched_or_missing':failed,'unexpected_files':extra,'pass':not failed and not extra}

if __name__=='__main__':
    result=verify();print(json.dumps(result,indent=2));raise SystemExit(0 if result['pass'] else 1)
