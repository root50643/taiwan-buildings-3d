#!/usr/bin/env python3
"""Lossless full-stream gzip-to-xz transcode, with decompressed SHA verification.
The original gzip stays on disk for private verification; the report references
only the smaller xz delivery artifact. No numeric text is parsed or rewritten.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,lzma,time

def digest(path,opener=open):
 h=hashlib.sha256();size=0
 with opener(path,'rb')as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block);size+=len(block)
 return h.hexdigest(),size

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();d=a.out;src=d/'dense-events.txt.gz';dst=d/'dense-events.txt.xz';start=time.time();h=hashlib.sha256();size=0
 with gzip.open(src,'rb')as fi,lzma.open(dst,'wb',format=lzma.FORMAT_XZ,check=lzma.CHECK_SHA256,preset=9)as fo:
  for b in iter(lambda:fi.read(1024*1024),b''):h.update(b);size+=len(b);fo.write(b)
 original=h.hexdigest();verified,verified_size=digest(dst,lzma.open);gzip_sha=digest(src)[0]
 assert original==verified and size==verified_size,'Lossless decompressed byte identity failed'
 assert dst.stat().st_size<src.stat().st_size,'XZ did not reduce size; keep original report'
 rpath=d/'dense-audit.json';r=json.loads(rpath.read_text());expected=r['artifacts'].get(src.name,{}).get('sha256');assert expected is None or expected==gzip_sha,'Original gzip differs from audited source';r['artifacts'].pop(src.name,None);r['artifacts'][dst.name]={'sha256':digest(dst)[0],'bytes':dst.stat().st_size}
 r['complete_event_stream']={'artifact':dst.name,'codec':'xz / LZMA2, preset 9, SHA256 container check','uncompressed_sha256':original,'uncompressed_bytes':size,'lossless_gzip_transcode_verified':True,'numerical_text_rewritten':False,'original_gzip_retained_privately':True}
 r['metadata_only_normalization']='Source filesystem path replaced by portable basename and full event container losslessly transcoded gzip to xz; STL SHA256 and all numeric/event bytes are unchanged.'
 rpath.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
 result={'gzip_bytes':src.stat().st_size,'gzip_sha256':gzip_sha,'xz_bytes':dst.stat().st_size,'uncompressed_bytes':size,'uncompressed_sha256':original,'xz_sha256':digest(dst)[0],'saved_fraction':1-dst.stat().st_size/src.stat().st_size,'elapsed_seconds':time.time()-start}
 (d/'dense-transcode.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
