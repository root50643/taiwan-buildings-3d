from pathlib import Path
import struct,json,hashlib,re,argparse,sys
def require(value,message):
 if not value:raise RuntimeError(message)
ap=argparse.ArgumentParser();ap.add_argument('--blend',type=Path,required=True);ap.add_argument('--expected-sha256',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();require(not args.out.exists(),'Fresh output required')
p=args.blend;b=p.read_bytes();require(args.expected_sha256=='70d8914cefaaceac8572d00c6cfba52b5abbedd18c810175f2deedb47ed2c429','This audit is restricted to the frozen WFU v13 Blend');require(hashlib.sha256(b).hexdigest()==args.expected_sha256,'Original Blend hash mismatch');require(b[:7]==b'BLENDER' and b[7:8] in (b'-',b'_') and b[8:9] in (b'v',b'V'),'Invalid Blender header');end='<' if b[8:9]==b'v' else '>';ptr=8 if b[7:8]==b'-' else 4;fmt=end+'4sI'+('Q' if ptr==8 else 'I')+'II';hlen=struct.calcsize(fmt);at=12;blocks=[]
while at+hlen<=len(b):
 code,n,addr,sdna,count=struct.unpack_from(fmt,b,at);blocks.append({'code':code.decode('ascii','replace'),'length':n,'start':at+hlen,'sdna':sdna,'count':count});at+=hlen+n
 if code==b'ENDB':break
dna=next(x for x in blocks if x['code']=='DNA1');d=b[dna['start']:dna['start']+dna['length']];at=0
def tag(s):
 global at
 require(d[at:at+len(s)]==s,'Invalid SDNA tag');at+=len(s)
def u32():
 global at
 v=struct.unpack_from(end+'I',d,at)[0];at+=4;return v
def strings(n):
 global at
 out=[]
 for i in range(n):
  j=d.index(0,at);out.append(d[at:j].decode());at=j+1
 at=(at+3)//4*4;return out
tag(b'SDNANAME');names=strings(u32());tag(b'TYPE');types=strings(u32());tag(b'TLEN');lens=list(struct.unpack_from(end+str(len(types))+'H',d,at));at+=len(types)*2;at=(at+3)//4*4;tag(b'STRC');structs=[]
for _ in range(u32()):
 ty,n=struct.unpack_from(end+'HH',d,at);at+=4;fields=[]
 for i in range(n):
  fty,fn=struct.unpack_from(end+'HH',d,at);at+=4;fields.append((fty,names[fn]))
 structs.append((ty,fields))
bytype={t:f for t,f in structs};cache={}
def layout(t):
 if t in cache:return cache[t]
 if t not in bytype:return (min(lens[t],8) if lens[t] else 1,[])
 off=0;maxal=1;fields=[]
 for ft,name in bytype[t]:
  pointer='*' in name;al=ptr if pointer else layout(ft)[0];size=ptr if pointer else lens[ft]
  for x in re.findall(r'\[(\d+)\]',name):size*=int(x)
  off=(off+al-1)//al*al;fields.append({'type':types[ft],'name':name,'start':off,'end':off+size});off+=size;maxal=max(maxal,al)
 total=(off+maxal-1)//maxal*maxal;require(total==lens[t],str((types[t],total,lens[t])));cache[t]=(maxal,fields);return cache[t]
findings=[]
for marker in [b'/' + b'home/agent',b'/' + b'tmp/',b'/' + b'workspace/',b'/' + b'Users/']:
 pos=0
 while True:
  i=b.find(marker,pos)
  if i<0:break
  pos=i+len(marker);bl=next(x for x in blocks if x['start']<=i<x['start']+x['length']);t,fs=structs[bl['sdna']];al,fields=layout(t);offset=(i-bl['start'])%lens[t];f=next(x for x in fields if x['start']<=offset<x['end']);st=bl['start']+(i-bl['start'])//lens[t]*lens[t]+f['start'];field_path=f['name']
  while f['type'] in types and types.index(f['type']) in bytype and '*' not in f['name']:
   ft=types.index(f['type']);suboffset=i-st;subf=next(x for x in layout(ft)[1] if x['start']<=suboffset<x['end']);st+=subf['start'];field_path+='.'+subf['name'];f=subf
  raw=b[st:st+f['end']-f['start']];value=raw.split(b'\0',1)[0].decode('utf8','replace');findings.append({'marker':marker.decode(),'block_code':bl['code'],'struct':types[t],'field':field_path,'field_type':f['type'],'field_offset':f['start'],'field_absolute_byte_offset':st,'marker_absolute_byte_offset':i,'field_buffer_bytes':len(raw),'field_buffer_sha256':hashlib.sha256(raw).hexdigest(),'marker_offset_in_field':i-st,'field_effective_before_first_nul':value,'after_first_nul_nonzero_bytes':sum(x!=0 for x in raw[len(value.encode())+1:]),'interpretation':'Generic runtime home UI location or unrendered default output directory; not a linked resource.'})
expected=[('FileSelectParams','dir[1090]',171624,1090,'2d1dc02e846e766c501535dfda01be83adbdea6d8e03a42e4e5df5377da744d1'),('Scene','r.pic[1024]',231956,1024,'a27bf0cff013ac91d264ac7f6b87fe91b392cee0ed657588929e56c4f0b4d07d')]
actual=[(x['struct'],x['field'],x['field_absolute_byte_offset'],x['field_buffer_bytes'],x['field_buffer_sha256']) for x in findings]
require(actual==expected and all(x['marker_offset_in_field']==0 for x in findings),'Unexpected path field, location or buffer bytes')
r={'blend_sha256':hashlib.sha256(b).hexdigest(),'version':b[9:12].decode(),'pointer_bytes':ptr,'byte_order':'little' if end=='<' else 'big','blocks':len(blocks),'field_findings':findings,'scope':'Read-only SDNA field interpretation of the original final Blend; generic UI/default output paths are not linked resource claims. The final scene-inspection report separately checks actual external images and hidden geometry.'};r['passed']=True;r['exact_candidate_generic_fields_only']=True;r['optimization_level']=sys.flags.optimize;r['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();require(p.read_bytes()==b,'Original Blend changed');args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
