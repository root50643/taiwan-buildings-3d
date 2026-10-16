"""Verify the entire delivered package by SHA-256 without rebuilding geometry."""
from pathlib import Path, PurePosixPath
import hashlib,json,sys

def main():
    root=Path(__file__).resolve().parent
    manifest_path=root/'PACKAGE-MANIFEST.json'
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    rows=manifest['files']
    if not isinstance(rows,list):raise RuntimeError('Manifest files must be a list')
    expected=set()
    for row in rows:
        rel=row['path'];p=PurePosixPath(rel)
        if p.is_absolute() or '..' in p.parts or str(p)!=rel or rel in expected:
            raise RuntimeError('Unsafe or duplicate manifest path: '+rel)
        expected.add(rel)
        target=root/rel
        if target.is_symlink() or not target.is_file():raise RuntimeError('Missing/nonregular file: '+rel)
        with target.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
        if target.stat().st_size!=row['bytes'] or digest!=row['sha256']:
            raise RuntimeError('Size or SHA-256 differs: '+rel)
    actual=set()
    for p in root.rglob('*'):
        if p.is_symlink():raise RuntimeError('Unexpected symlink: '+str(p.relative_to(root)))
        if p.is_file():actual.add(p.relative_to(root).as_posix())
    if actual!=expected|{'PACKAGE-MANIFEST.json'}:
        raise RuntimeError('Package file set differs: '+str(sorted(actual^(expected|{'PACKAGE-MANIFEST.json'}))))
    print(json.dumps({'passed':True,'files_verified':len(rows),'manifest_self_hash_included':False,'scope':'Byte integrity only; no geometry, render, source-truth or physical-print claim.'},indent=2))
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as error:
        print(json.dumps({'passed':False,'error':str(error)},indent=2),file=sys.stderr)
        sys.exit(1)
