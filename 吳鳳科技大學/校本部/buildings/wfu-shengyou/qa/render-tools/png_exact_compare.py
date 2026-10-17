"""Exact RGBA8 PNG comparison, preserving original files and metadata evidence.
Only five explicitly named textual time fields may differ. File-byte identity
is reported separately and is never implied by decoded-pixel identity.
"""
import calendar,hashlib,struct,zlib
from pathlib import Path
ALLOWED_TIME_KEYS=frozenset({'Date','RenderTime','cycles.ViewLayer.total_time','cycles.ViewLayer.render_time','cycles.ViewLayer.synchronization_time'})
SANITIZE_TEXT_KEYS=ALLOWED_TIME_KEYS|{'File','Time'}
COLOR_TAGS={b'gAMA',b'cHRM',b'iCCP',b'sRGB',b'sBIT',b'cICP',b'mDCV',b'cLLI',b'PLTE',b'tRNS',b'eXIf'}
def require(v,m):
 if not v:raise RuntimeError(m)
def digest(data):return hashlib.sha256(data).hexdigest()
def paeth(a,b,c):
 p=a+b-c;pa,pb,pc=abs(p-a),abs(p-b),abs(p-c)
 return a if pa<=pb and pa<=pc else b if pb<=pc else c
def unpack_zlib(payload,limit=20000000):
 decoder=zlib.decompressobj();result=decoder.decompress(payload,limit+1)
 require(len(result)<=limit and decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,'Invalid bounded metadata zlib stream')
 return result
def keyword(value):
 require(1<=len(value)<=79 and value[:1]!=b' ' and value[-1:]!=b' ' and b'  ' not in value and all(32<=c<=126 or 161<=c<=255 for c in value),'Invalid PNG text/profile keyword')
 return value.decode('latin1')
def text_payload(tag,payload):
 require(b'\0' in payload,'Invalid text delimiter');key,rest=payload.split(b'\0',1);name=keyword(key)
 if tag==b'tEXt':text=rest
 elif tag==b'zTXt':
  require(len(rest)>=2 and rest[0]==0,'Invalid zTXt compression');text=unpack_zlib(rest[1:])
 else:
  require(len(rest)>=4 and rest[0] in (0,1) and rest[1]==0,'Invalid iTXt compression');flag=rest[0];parts=rest[2:].split(b'\0',2);require(len(parts)==3,'Invalid iTXt fields');language,translated,text=parts
  require(all(48<=c<=57 or 65<=c<=90 or 97<=c<=122 or c==45 for c in language),'Invalid iTXt language');translated.decode('utf8')
  if flag:text=unpack_zlib(text)
  text.decode('utf8')
 require(b'\0' not in text,'NUL in PNG text')
 return name,text
def parse(path):
 data=Path(path).read_bytes();require(data[:8]==b'\x89PNG\r\n\x1a\n','Invalid PNG signature')
 pos=8;chunks=[];idat=[];times={};time_positions=[];stable=[];counts={};ended=False;idat_started=False;idat_ended=False;header=None
 while pos<len(data):
  require(pos+12<=len(data),'Truncated PNG chunk');n=struct.unpack_from('>I',data,pos)[0];tag=data[pos+4:pos+8]
  require(n<=0x7fffffff and pos+12+n<=len(data),'Invalid PNG chunk length')
  require(all(65<=c<=90 or 97<=c<=122 for c in tag) and not(tag[2]&32),'Invalid PNG chunk type')
  payload=data[pos+8:pos+8+n];crc=struct.unpack_from('>I',data,pos+8+n)[0];require(zlib.crc32(tag+payload)&0xffffffff==crc,'PNG CRC mismatch')
  require(not ended,'Trailing data after IEND');counts[tag]=counts.get(tag,0)+1
  if not chunks:require(tag==b'IHDR','PNG must begin with IHDR')
  require(tag in {b'IHDR',b'PLTE',b'IDAT',b'IEND'} or bool(tag[0]&32),'Unknown critical PNG chunk')
  if tag==b'IHDR':
   require(counts[tag]==1 and n==13,'Invalid or repeated IHDR');header=struct.unpack('>IIBBBBB',payload);w,h,depth,color,compression,filtering,interlace=header
   require(w>0 and h>0 and w*h<=20000000,'Unsupported image dimensions')
   require((depth,color,compression,filtering,interlace)==(8,6,0,0,0),'Only noninterlaced 8-bit RGBA PNG is supported')
  elif tag==b'IDAT':
   require(not idat_ended,'Nonconsecutive IDAT chunks');idat_started=True;idat.append(payload)
  else:
   if idat_started:idat_ended=True
   if tag==b'IEND':require(n==0 and idat_started,'Invalid IEND or absent IDAT');ended=True
  if tag in {b'PLTE',b'gAMA',b'cHRM',b'iCCP',b'sRGB',b'sBIT',b'cICP',b'mDCV',b'cLLI'}:require(not idat_started,'Colour metadata occurs after IDAT')
  if tag in {b'PLTE',b'gAMA',b'cHRM',b'iCCP',b'sRGB',b'sBIT',b'cICP',b'mDCV',b'cLLI',b'pHYs',b'eXIf',b'oFFs'}:require(counts[tag]==1,'Repeated singleton metadata')
  require(tag!=b'tRNS','RGBA PNG cannot contain tRNS')
  if tag==b'PLTE':require(n>0 and n<=768 and n%3==0,'Invalid PLTE')
  if tag==b'gAMA':require(n==4 and struct.unpack('>I',payload)[0]>0,'Invalid gAMA')
  if tag==b'cHRM':require(n==32,'Invalid cHRM')
  if tag==b'sRGB':require(n==1 and payload[0]<=3,'Invalid sRGB')
  if tag==b'sBIT':require(n==4 and all(1<=c<=8 for c in payload),'Invalid RGBA sBIT')
  if tag==b'iCCP':
   require(b'\0' in payload,'Invalid iCCP');name,rest=payload.split(b'\0',1);keyword(name);require(len(rest)>1 and rest[0]==0,'Invalid iCCP compression');profile=unpack_zlib(rest[1:]);require(len(profile)>=132 and struct.unpack_from('>I',profile)[0]==len(profile) and profile[36:40]==b'acsp' and profile[16:20]==b'RGB ','Invalid ICC profile header');ntags=struct.unpack_from('>I',profile,128)[0];require(132+12*ntags<=len(profile),'Invalid ICC tag table')
   for k in range(ntags):
    offset,size=struct.unpack_from('>II',profile,136+12*k);require(offset<=len(profile) and size<=len(profile)-offset,'Invalid ICC tag extent')
  if tag==b'oFFs':require(n==9 and payload[-1] in (0,1),'Invalid oFFs')
  if tag==b'eXIf':
   require(n>=8 and payload[:2] in [b'II',b'MM'],'Invalid Exif TIFF header');endian='<' if payload[:2]==b'II' else '>';require(struct.unpack_from(endian+'H',payload,2)[0]==42,'Invalid Exif TIFF marker');offset=struct.unpack_from(endian+'I',payload,4)[0];require(offset+2<=n,'Invalid Exif IFD offset');entries=struct.unpack_from(endian+'H',payload,offset)[0];require(offset+2+12*entries+4<=n,'Invalid Exif IFD length')
  if tag in {b'pHYs',b'oFFs',b'bKGD'}:require(not idat_started,'Metadata must precede IDAT')
  if tag in {b'gAMA',b'cHRM',b'iCCP',b'sRGB',b'sBIT'}:require(b'PLTE' not in counts,'Colour metadata must precede PLTE')
  if tag==b'bKGD':require(n==6 and all(x<=255 for x in struct.unpack('>HHH',payload)),'Invalid RGBA bKGD')
  if tag==b'tIME':
   require(n==7 and counts[tag]==1,'Invalid tIME length/count');year,month,day,hour,minute,second=struct.unpack('>HBBBBB',payload);require(1<=year<=9999 and 1<=month<=12 and 1<=day<=calendar.monthrange(year,month)[1] and hour<=23 and minute<=59 and second<=60,'Invalid tIME date')
  if tag==b'pHYs':require(n==9 and payload[-1] in (0,1),'Invalid pHYs')
  ignored=False
  if tag in [b'tEXt',b'zTXt',b'iTXt']:
   key,value=text_payload(tag,payload)
   require(tag==b'tEXt' or key not in SANITIZE_TEXT_KEYS,'Private/volatile fields in unsupported text container')
   if tag==b'tEXt' and key in ALLOWED_TIME_KEYS:
    require(key not in times,'Duplicate allowed time field');times[key]=value.decode('latin1');time_positions.append((len(stable),'after_idat' if idat_started else 'before_idat',key));ignored=True
  phase='after_idat' if idat_started else 'before_idat'
  if tag!=b'IDAT' and not ignored:stable.append((phase,tag,payload))
  chunks.append((tag,payload));pos+=n+12
 require(ended and pos==len(data),'Missing IEND or trailing bytes');require(not (b'sRGB' in counts and b'iCCP' in counts),'Conflicting sRGB/iCCP profiles')
 expected=h*(1+4*w);compressed=b''.join(idat);decoder=zlib.decompressobj();scanlines=decoder.decompress(compressed,expected+1)
 require(len(scanlines)==expected and decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,'Invalid/truncated/overlong PNG zlib stream')
 stride=4*w;previous=bytearray(stride);pixels=bytearray();cursor=0
 for row in range(h):
  kind=scanlines[cursor];cursor+=1;raw=scanlines[cursor:cursor+stride];cursor+=stride;require(kind<=4,'Unknown PNG row filter')
  if kind==0:reconstructed=bytearray(raw)
  else:
   reconstructed=bytearray(stride)
   for i,v in enumerate(raw):
    a=reconstructed[i-4] if i>=4 else 0;b=previous[i];c=previous[i-4] if i>=4 else 0
    predictor=a if kind==1 else b if kind==2 else (a+b)//2 if kind==3 else paeth(a,b,c)
    reconstructed[i]=(v+predictor)&255
  pixels.extend(reconstructed);previous=reconstructed
 stable_bytes=b''.join(phase.encode()+b'\0'+tag+struct.pack('>I',len(payload))+payload for phase,tag,payload in stable)
 return {'file_sha256':digest(data),'width':w,'height':h,'mode':'RGBA','bit_depth':8,'rgba_bytes':bytes(pixels),'rgba_sha256':digest(pixels),'allowed_time_values':times,'allowed_time_positions':time_positions,'stable_metadata':stable,'nonvolatile_metadata_sha256':digest(stable_bytes),'idat_sha256':digest(compressed),'color_metadata':[{'chunk':tag.decode(),'sha256':digest(payload)} for tag,payload in chunks if tag in COLOR_TAGS],'chunk_types':[tag.decode() for tag,payload in chunks],'chunks':chunks}
def compare(original,rerendered,expected_original_sha256):
 a,b=parse(original),parse(rerendered);require(a['file_sha256']==expected_original_sha256,'Original PNG differs from frozen manifest')
 same_pixels=a['rgba_bytes']==b['rgba_bytes'];same_layout=all(a[k]==b[k] for k in ['width','height','mode','bit_depth']);same_metadata=a['stable_metadata']==b['stable_metadata'];same_time_keys=set(a['allowed_time_values'])==set(b['allowed_time_values']);same_time_positions=a['allowed_time_positions']==b['allowed_time_positions']
 rows=[{'key':key,'original':a['allowed_time_values'].get(key),'rerendered':b['allowed_time_values'].get(key),'values_equal':a['allowed_time_values'].get(key)==b['allowed_time_values'].get(key)} for key in sorted(set(a['allowed_time_values'])|set(b['allowed_time_values']))]
 return {'passed':same_pixels and same_layout and same_metadata and same_time_keys and same_time_positions,'original_png_sha256':a['file_sha256'],'rerendered_png_sha256':b['file_sha256'],'whole_png_file_bytes_identical':a['file_sha256']==b['file_sha256'],'width':a['width'],'height':a['height'],'mode':a['mode'],'bit_depth':a['bit_depth'],'dimensions_and_mode_identical':same_layout,'decoded_rgba_bytes_identical':same_pixels,'original_rgba_sha256':a['rgba_sha256'],'rerendered_rgba_sha256':b['rgba_sha256'],'all_nonvolatile_metadata_identical':same_metadata,'original_nonvolatile_metadata_sha256':a['nonvolatile_metadata_sha256'],'rerendered_nonvolatile_metadata_sha256':b['nonvolatile_metadata_sha256'],'original_color_metadata':a['color_metadata'],'rerendered_color_metadata':b['color_metadata'],'allowed_time_field_sets_identical':same_time_keys,'allowed_time_field_positions_identical':same_time_positions,'allowed_time_metadata':rows,'compressed_idat_bytes_identical':a['idat_sha256']==b['idat_sha256'],'original_chunk_types':a['chunk_types'],'rerendered_chunk_types':b['chunk_types'],'comparison_policy':'Exact decoded noninterlaced RGBA8 channel bytes, dimensions/mode and every non-IDAT/nonvolatile chunk including colour profiles and File metadata. Only the listed tEXt time-field values may differ. This does not assert whole-PNG byte reproducibility.'}

def sanitize(original,output,expected_original_sha256):
 original=Path(original);output=Path(output);require(not output.exists(),'Refusing to overwrite PNG output');a=parse(original);require(a['file_sha256']==expected_original_sha256,'Original PNG differs from frozen hash')
 data=original.read_bytes();require(digest(data)==a['file_sha256'],'Original PNG changed during read');pos=8;kept=[data[:8]];removed=[];kept_records=[]
 while pos<len(data):
  size=struct.unpack_from('>I',data,pos)[0];tag=data[pos+4:pos+8];payload=data[pos+8:pos+8+size];record=data[pos:pos+size+12];remove=False
  if tag==b'tEXt':
   key,value=text_payload(tag,payload);remove=key in SANITIZE_TEXT_KEYS
   if remove:removed.append({'key':key,'original_payload_sha256':digest(payload),'removed_chunk_bytes':len(record)})
  if not remove:kept.append(record);kept_records.append((tag,payload))
  pos+=size+12
 cleaned=b''.join(kept);output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(cleaned);b=parse(output)
 checks={'original_file_unchanged':digest(original.read_bytes())==a['file_sha256'],'all_surviving_chunks_including_crc_unchanged':digest(output.read_bytes())==digest(cleaned) and b['chunks']==kept_records,'idat_compressed_bytes_unchanged':a['idat_sha256']==b['idat_sha256'],'decoded_rgba_bytes_unchanged':a['rgba_bytes']==b['rgba_bytes'],'dimensions_mode_unchanged':all(a[k]==b[k] for k in ['width','height','mode','bit_depth']),'all_colour_metadata_unchanged':a['color_metadata']==b['color_metadata'],'all_whitelisted_fields_absent':not any(tag in [b'tEXt',b'zTXt',b'iTXt'] and text_payload(tag,payload)[0] in SANITIZE_TEXT_KEYS for tag,payload in b['chunks'])}
 require(all(checks.values()),'PNG metadata-only proof failed')
 return {'passed':True,'original_png_sha256':a['file_sha256'],'sanitized_png_sha256':b['file_sha256'],'original_rgba_sha256':a['rgba_sha256'],'sanitized_rgba_sha256':b['rgba_sha256'],'width':a['width'],'height':a['height'],'mode':a['mode'],'bit_depth':a['bit_depth'],'removal_whitelist':sorted(SANITIZE_TEXT_KEYS),'removed_fields':removed,'checks':checks,'method':'Copy original PNG signature and every surviving complete chunk including CRC verbatim. Remove only whitelisted tEXt chunks. No IDAT recompression, pixel reencoding, colour conversion or image editing.'}
