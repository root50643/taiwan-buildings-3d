#!/usr/bin/env python3
"""Read-only exact public allowlist, hashes, metadata and private-path audit."""
from pathlib import Path
import sys
if sys.flags.optimize:raise RuntimeError("Run validation without -O")
import argparse,json,hashlib,zipfile,struct,re
p=argparse.ArgumentParser();p.add_argument('package',type=Path,nargs='?',default=Path(__file__).resolve().parent.parent);a=p.parse_args();root=a.package
m=json.loads((root/'MANIFEST.json').read_text());listed={e['path']:e for e in m['files']};actual={str(p.relative_to(root))for p in root.rglob('*')if p.is_file()};assert actual==set(listed)|{'MANIFEST.json','SHA256SUMS'},'Exact public allowlist mismatch'
markers=[('/'+'workspace/').encode(),('/'+'home/agent/').encode(),('/'+'tmp/').encode(),('web'+'dav').encode(),('APPROVED'+'-FACE-CONTRACT').encode(),('verification-'+'20261024').encode(),('model-'+'work-').encode(),('source_'+'archive_receipt').encode(),('Bearer'+' ').encode()]
for name,e in listed.items():
 path=root/name;assert not path.is_symlink();raw=path.read_bytes();assert len(raw)==e['bytes'] and hashlib.sha256(raw).hexdigest()==e['sha256'],name
 assert not any(mark.lower()in raw.lower()for mark in markers),('private marker',name)
 if path.suffix=='.png':
  assert raw[:8]==b'\x89PNG\r\n\x1a\n';i=8
  while i<len(raw):
   n=struct.unpack_from('>I',raw,i)[0];assert raw[i+4:i+8]not in (b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME');i+=12+n
 if path.suffix=='.3mf':
  with zipfile.ZipFile(path)as z:
   assert set(z.namelist())=={'[Content_Types].xml','_rels/.rels','3D/3dmodel.model'}
   for nn in z.namelist():assert not any(mark.lower()in z.read(nn).lower()for mark in markers)
rows={line.split('  ',1)[1]:line.split('  ',1)[0]for line in(root/'SHA256SUMS').read_text().splitlines()};assert set(rows)==set(listed)|{'MANIFEST.json'}
for name,h in rows.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h
images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',(root/'README.md').read_text());assert len(images)==9 and len(set(images))==9 and all((root/i).is_file()for i in images)
assert not any(Path(n).suffix.lower()in ['.stl','.jpg','.jpeg','.pdf','.html','.npz']for n in actual)
print(json.dumps({'status':'PASS','exact_public_files_including_indexes':len(actual),'payload_bytes':sum(x['bytes']for x in listed.values()),'nine_actual_preview_links':True,'private_path_and_source_media_audit':True,'manifest_sha256':hashlib.sha256((root/'MANIFEST.json').read_bytes()).hexdigest()},indent=2))
