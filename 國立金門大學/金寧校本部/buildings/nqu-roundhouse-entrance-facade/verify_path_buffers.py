#!/usr/bin/env python3
"""Read-only Blender 4.3 fixed-buffer audit using embedded DNA declarations, not string-prefix guesses."""
from pathlib import Path
import struct,re,json,argparse,math
p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,default=Path(__file__).resolve().parent/'nqu-roundhouse-entrance-facade.blend');p.add_argument('--report',type=Path);args=p.parse_args()
b=args.blend.read_bytes();assert b[:7]==b'BLENDER' and b[7:9]==b'-v','Expected uncompressed 64-bit little-endian Blend'
o=12;blocks=[]
while o+24<=len(b):
 code,n,ptr,idx,count=struct.unpack_from('<4sIQII',b,o);blocks.append((code,n,ptr,idx,count,o+24));o+=24+n
 if code==b'ENDB':break
blk=next(x for x in blocks if x[0]==b'DNA1');data=b[blk[5]:blk[5]+blk[1]];assert data[:8]==b'SDNANAME';o=8
n=struct.unpack_from('<I',data,o)[0];o+=4;names=[]
for _ in range(n):z=data.index(0,o);names.append(data[o:z].decode());o=z+1
o=(o+3)&~3;assert data[o:o+4]==b'TYPE';o+=4;n=struct.unpack_from('<I',data,o)[0];o+=4;types=[]
for _ in range(n):z=data.index(0,o);types.append(data[o:z].decode());o=z+1
o=(o+3)&~3;assert data[o:o+4]==b'TLEN';o+=4;lens=struct.unpack_from('<'+str(n)+'H',data,o);o+=2*n;o=(o+3)&~3;assert data[o:o+4]==b'STRC';o+=4;n=struct.unpack_from('<I',data,o)[0];o+=4;structs=[];byname={}
for _ in range(n):
 t,nf=struct.unpack_from('<HH',data,o);o+=4;fields=[];offset=0
 for _ in range(nf):
  ft,fn=struct.unpack_from('<HH',data,o);o+=4;name=names[fn];size=(8 if '*' in name else lens[ft])*math.prod(int(x)for x in re.findall(r'\[(\d+)\]',name));fields.append({'type':types[ft],'name':name,'offset':offset,'size':size});offset+=size
 rec={'name':types[t],'size':lens[t],'fields':fields,'computed_size':offset};structs.append(rec);byname[types[t]]=rec
for name in ('FileSelectParams','RenderData','Scene'):assert byname[name]['computed_size']==byname[name]['size'],name
reports=[]
def check(offset,size,expected,field):
 raw=b[offset:offset+size];assert len(raw)==size;head,sep,tail=raw.partition(b'\0');assert sep and head==expected,(field,head)
 assert all(x in (0,95)for x in tail),f'{field}: non-neutral bytes remain after NUL'
 reports.append({'field':field,'offset':offset,'fixed_buffer_bytes':size,'visible_value':head.decode(),'tail_only_NUL_or_neutral_padding':True,'tail_NUL_bytes':tail.count(0),'tail_padding_bytes':tail.count(95)})
fp=next(f for f in byname['FileSelectParams']['fields']if f['name']=='dir[1090]')
rp=next(f for f in byname['RenderData']['fields']if f['name']=='pic[1024]')
scene_r=next(f for f in byname['Scene']['fields']if f['type']=='RenderData' and f['name']=='r')
for code,n,ptr,idx,count,base in blocks:
 if code in (b'DNA1',b'ENDB'):continue
 st=structs[idx]
 if st['name']=='FileSelectParams':
  for j in range(count):check(base+j*st['size']+fp['offset'],fp['size'],b'//','FileSelectParams.dir')
 if st['name']=='Scene':
  for j in range(count):check(base+j*st['size']+scene_r['offset']+rp['offset'],rp['size'],b'//previews/front.png','Scene.r.pic')
assert reports and any(r['field']=='FileSelectParams.dir'for r in reports) and any(r['field']=='Scene.r.pic'for r in reports)
result={'method':'Read-only embedded SDNA field offsets; inspect entire declared fixed buffers including NUL tail','buffers_checked':len(reports),'all_pass':True,'fields':reports}
if args.report:args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
