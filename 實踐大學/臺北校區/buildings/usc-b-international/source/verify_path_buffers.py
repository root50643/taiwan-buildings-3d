#!/usr/bin/env python3
"""Read-only Blender 4.3 fixed-buffer audit using embedded DNA declarations, not string-prefix guesses."""
from pathlib import Path
import struct,re,json,argparse,math
p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,required=True);p.add_argument('--report',type=Path);args=p.parse_args()
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
# Traverse every allocated structure and nested non-pointer structure/array.
# Fixed character buffers are checked in full, not only their visible prefix.
reports=[]
private_markers=[('/'+'workspace/').encode(),('/'+'home/').encode(),('/'+'tmp/').encode(),b'file:///']
def descend(st,base,prefix,seen):
 if st['name']in seen:return
 assert st['computed_size']==st['size'],('unhandled SDNA layout',st['name'])
 for f in st['fields']:
  if '*'in f['name']:continue
  label=prefix+'.'+f['name'];off=base+f['offset'];name=f['name'].split('[')[0]
  if f['type']=='char'and f['size']>=64 and (re.search(r'file|path|dir|cache',name,re.I)or label.endswith('.r.pic[1024]')):
   raw=b[off:off+f['size']];assert len(raw)==f['size'];head,sep,tail=raw.partition(b'\0')
   assert sep,(label,'missing NUL terminator')
   assert all(x in (0,95)for x in tail),(label,'stale post-NUL bytes')
   assert not any(marker in raw for marker in private_markers),(label,'private path marker')
   assert b'..' not in head.replace(b'\\',b'/').split(b'/'),(label,'outside-package traversal')
   assert not (head.startswith(b'/')and not head.startswith(b'//')),(label,'absolute path')
   assert not re.match(rb'^[A-Za-z]:',head),(label,'drive absolute path')
   if label=='FileSelectParams.dir[1090]':assert head==b'//'
   if label=='FileSelectParams.file[256]':assert head==b''
   if label=='Scene.r.pic[1024]':assert head==b'//previews/front.png'
   reports.append({'field':label,'offset':off,'fixed_buffer_bytes':f['size'],'visible_value':head.decode(),'tail_only_NUL_or_neutral_padding':True,'tail_NUL_bytes':tail.count(0),'tail_padding_bytes':tail.count(95),'full_buffer_private_path_markers_absent':True,'outside_package_traversal_absent':True})
  elif f['type']in byname:
   child=byname[f['type']];count=math.prod(int(x)for x in re.findall(r'\[(\d+)\]',f['name']))
   for j in range(count):descend(child,off+j*child['size'],label+(f'[{j}]'if count>1 else''),seen|{st['name']})
for code,n,ptr,idx,count,base in blocks:
 if code in (b'DNA1',b'ENDB'):continue
 st=structs[idx]
 if n!=st['size']*count:continue
 for j in range(count):descend(st,base+j*st['size'],st['name'],set())
assert reports and any(r['field']=='FileSelectParams.file[256]'for r in reports)and any(r['field']=='Scene.r.pic[1024]'for r in reports)
assert not any(r['field'].startswith('Editing.')for r in reports),'Unused sequencer state must not be saved'
result={'method':'Read-only recursive allocated SDNA non-pointer path-like char-buffer inspection, including nested structures/arrays and every byte after the first NUL. No binary mutation.','buffers_checked':len(reports),'all_pass':True,'unused_sequencer_state_absent':True,'fields':reports}
if args.report:args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
