"""Remove only PNG text/EXIF/time metadata, preserving compressed image pixels.
No crop, recolor or rerender. Keeps PNG color-space chunks for consistent display.
"""
from pathlib import Path
import hashlib,json,struct,zlib
from PIL import Image
R=Path(__file__).resolve().parents[1]
def chunks(b):
 assert b[:8]==b'\x89PNG\r\n\x1a\n';i=8
 while i<len(b):
  n=struct.unpack_from('>I',b,i)[0];typ=b[i+4:i+8];data=b[i+8:i+8+n];crc=struct.unpack_from('>I',b,i+8+n)[0];assert zlib.crc32(typ+data)&0xffffffff==crc
  yield typ,data,b[i:i+n+12];i+=n+12
 assert i==len(b)
def main():
 records=[]
 for p in sorted((R/'previews').glob('*.png')):
  b=p.read_bytes();before=Image.open(p).convert('RGBA');px=before.tobytes();removed=[];out=[b[:8]];idat=[]
  for typ,data,raw in chunks(b):
   if typ in [b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME']:removed.append(typ.decode())
   else:out.append(raw)
   if typ==b'IDAT':idat.append(data)
  p.write_bytes(b''.join(out));after=Image.open(p).convert('RGBA');assert before.size==after.size==(1400,1000) and px==after.tobytes();assert idat==[data for typ,data,_ in chunks(p.read_bytes()) if typ==b'IDAT']
  assert after.getchannel('A').getextrema()==(255,255);records.append({'path':str(p.relative_to(R)),'resolution':list(after.size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'RGBA_pixel_sha256':hashlib.sha256(px).hexdigest(),'removed_chunk_types':sorted(set(removed)),'retained_chunk_types':sorted({t.decode() for t,_,_ in chunks(p.read_bytes())}),'pixels_and_IDAT_bytes_unchanged':True})
 assert len(records)==4 and len({r['RGBA_pixel_sha256'] for r in records})==4
 (R/'qa/preview-validation.json').write_text(json.dumps({'method':'PNG text/EXIF/time chunks removed, image IDAT and RGBA bytes unchanged. Color-space chunks preserved.','files':records,'manual_pixel_review':'Recorded separately in source-appearance-review.json; not automatically asserted by this script.','original_photos_embedded':False},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'previews':len(records),'pixels_unchanged':True,'removed_types':sorted({x for r in records for x in r['removed_chunk_types']})}))
if __name__=='__main__':main()
