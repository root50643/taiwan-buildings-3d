#!/usr/bin/env python3
"""Read-only rendered-preview privacy check; no source photographs are expected."""
import argparse, pathlib, json, struct, hashlib, zlib
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);a=p.parse_args();root=a.out
forbidden={b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'}
records=[]
for path in sorted((root/'previews').glob('*.png')):
 raw=path.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';at=8;tags=[];dimensions=None
 while at<len(raw):
  assert at+12<=len(raw)
  n=struct.unpack_from('>I',raw,at)[0];tag=raw[at+4:at+8];payload=raw[at+8:at+8+n];assert len(payload)==n
  assert at+n+12<=len(raw)
  crc=struct.unpack_from('>I',raw,at+n+8)[0];assert (zlib.crc32(tag+payload)&0xffffffff)==crc
  assert tag not in forbidden,(path.name,tag)
  tags.append(tag.decode('ascii'))
  if tag==b'IHDR':dimensions=list(struct.unpack_from('>II',payload))
  at+=n+12
  if tag==b'IEND':break
 assert at==len(raw) and tags[0]=='IHDR' and tags[-1]=='IEND' and dimensions
 records.append({'file':'previews/'+path.name,'dimensions':dimensions,'png_chunk_types':sorted(set(tags)),'forbidden_metadata_chunks':0,'all_chunk_crcs_valid':True,'trailing_bytes':0,'sha256':hashlib.sha256(raw).hexdigest()})
assert len(records)==9
report={'all_pass':True,'preview_count':len(records),'excluded_chunks':['tEXt','zTXt','iTXt','eXIf','tIME'],'method':'Parse each delivered PNG through IEND; validate chunk CRCs and reject text/EXIF/time metadata or trailing bytes. This is metadata validation, not a copyright or visual-content classifier.','previews':records}
(root/'qa').mkdir(exist_ok=True);(root/'qa/png-metadata-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
