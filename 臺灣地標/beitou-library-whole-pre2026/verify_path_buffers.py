#!/usr/bin/env python3
"""Read-only, recursive Blender SDNA fixed-char-array audit against a real factory file.

All declared fixed char/uchar/int8 arrays are inspected, including embedded structures,
structure arrays, full buffers and bytes after the first NUL. Pointer targets and raw
non-SDNA allocations are not fixed arrays; native media checks remain verify_blend.py's
responsibility. Exact authored names come only from the public component/palette files.
No reference image, network, or private release input is needed.
"""
from pathlib import Path
import argparse,collections,hashlib,json,math,re,struct,subprocess,tempfile

CHAR_TYPES={'char','uchar','int8_t','uint8_t','unsigned char','signed char'}

class BlendDNA:
 def __init__(self,path):
  self.data=Path(path).read_bytes();b=self.data
  assert b[:9]==b'BLENDER-v','Expected uncompressed 64-bit little-endian Blend'
  self.version=b[9:12].decode();self.blocks=[];o=12
  while o+24<=len(b):
   code,n,ptr,idx,count=struct.unpack_from('<4sIQII',b,o)
   assert o+24+n<=len(b),'Truncated block'
   self.blocks.append((code,n,ptr,idx,count,o+24));o+=24+n
   if code==b'ENDB':break
  assert o==len(b),'Trailing or truncated Blend bytes'
  blk=next(x for x in self.blocks if x[0]==b'DNA1');data=b[blk[5]:blk[5]+blk[1]]
  self.dna_sha256=hashlib.sha256(data).hexdigest();assert data[:8]==b'SDNANAME';o=8
  n=struct.unpack_from('<I',data,o)[0];o+=4;names=[]
  for _ in range(n):
   z=data.index(0,o);names.append(data[o:z].decode());o=z+1
  o=(o+3)&~3;assert data[o:o+4]==b'TYPE';o+=4;n=struct.unpack_from('<I',data,o)[0];o+=4;types=[]
  for _ in range(n):
   z=data.index(0,o);types.append(data[o:z].decode());o=z+1
  o=(o+3)&~3;assert data[o:o+4]==b'TLEN';o+=4;lens=struct.unpack_from('<'+str(n)+'H',data,o);o+=2*n;o=(o+3)&~3
  assert data[o:o+4]==b'STRC';o+=4;n=struct.unpack_from('<I',data,o)[0];o+=4;self.structs=[]
  for _ in range(n):
   ty,nf=struct.unpack_from('<HH',data,o);o+=4;fields=[];offset=0
   for _ in range(nf):
    ft,fn=struct.unpack_from('<HH',data,o);o+=4;name=names[fn]
    count=math.prod(int(x)for x in re.findall(r'\[(\d+)\]',name));size=(8 if '*' in name else lens[ft])*count
    fields.append({'type':types[ft],'name':name,'offset':offset,'size':size,'count':count});offset+=size
   self.structs.append({'name':types[ty],'size':lens[ty],'fields':fields,'computed_size':offset})
  self.byname={x['name']:x for x in self.structs};self._cache={};self.records=[];self.structured_blocks=0;self.raw_blocks=0
  for code,n,ptr,idx,count,base in self.blocks:
   if code in (b'DNA1',b'ENDB'):continue
   assert 0<=idx<len(self.structs),'Invalid SDNA index'
   st=self.structs[idx]
   # SDNA index zero is Blender's raw-allocation convention, not a Link struct instance.
   if idx==0 or count==0:
    self.raw_blocks+=1;continue
   assert count*st['size']==n,(code,st['name'],count,st['size'],n)
   self.structured_blocks+=1
   for j in range(count):
    for off,size,field in self.arrays(st['name']):
     pos=base+j*st['size']+off;raw=b[pos:pos+size];assert len(raw)==size
     self.records.append({'field':field,'offset':pos,'bytes':raw})
  assert self.records,'No fixed char arrays found'
 def arrays(self,name):
  if name in self._cache:return self._cache[name]
  st=self.byname[name];assert st['computed_size']==st['size'],('Unknown struct padding',name,st['computed_size'],st['size'])
  rows=[]
  for f in st['fields']:
   if '*' in f['name']:continue
   if f['type'] in CHAR_TYPES and '[' in f['name']:
    rows.append((f['offset'],f['size'],name+'.'+f['name']))
   elif f['type'] in self.byname:
    sub=self.byname[f['type']]
    for j in range(f['count']):
     for off,size,field in self.arrays(f['type']):
      prefix=name+'.'+f['name']+('['+str(j)+']'if f['count']>1 else '')+'/'
      rows.append((f['offset']+j*sub['size']+off,size,prefix+field))
  self._cache[name]=rows;return rows

def utf8_limit(s,n):
 raw=s.encode()[:n]
 while True:
  try:return raw.decode().encode()
  except UnicodeDecodeError:raw=raw[:-1]

def authored_heads(root):
 info=json.loads((root/'editable-parts.json').read_text());parts=json.loads((root/'construction-parts.json').read_text())
 final='Beitou Library — unified printable material mesh'
 names=[x['name']for x in parts]+[final]
 allowed=collections.defaultdict(set)
 def add(path,*values):allowed[path].update(x.encode()for x in values)
 for ty,prefix in [('Object','OB'),('Mesh','ME')]:
  allowed[ty+'.id/ID.name[66]'].update(prefix.encode()+utf8_limit(n,63)for n in names)
 add('Object.id/ID.name[66]','OBCamera','OBKey','OBFill')
 add('Camera.id/ID.name[66]','CACamera','CACamera.001')
 add('Lamp.id/ID.name[66]','LAKey','LAFill')
 add('Collection.id/ID.name[66]','GREDITABLE authored components (hidden; overlaps pre-union)')
 allowed['Material.id/ID.name[66]'].update(b'MA'+utf8_limit(x['id'],63)for x in info['palette'])
 add('FileSelectParams.dir[1090]','//')
 add('Scene.r/RenderData.pic[1024]','//previews/front.png')
 add('Scene.r/RenderData.engine[32]','CYCLES')
 add('Scene.r/RenderData.im_format/ImageFormatData.linear_colorspace_settings/ColorManagedColorspaceSettings.name[64]','sRGB')
 add('Scene.view_settings/ColorManagedViewSettings.view_transform[64]','Standard')
 add('Scene.view_settings/ColorManagedViewSettings.look[64]','None')
 add('IDProperty.name[64]','RNA_struct_idprops','evidence','source_evidence','samples','seed','scope','print_note','use_denoising')
 add('CustomDataLayer.name[68]','material_index')
 for path in ('bNodeSocket.identifier[64]','bNodeSocket.name[64]'):add(path,'Coat Roughness','Coat Normal')
 return allowed

def audit(records,baseline,allowed):
 counts=collections.Counter();groups=collections.defaultdict(collections.Counter);fail=[];authored=collections.Counter()
 for r in records:
  field=r['field'];raw=r['bytes'];factory=baseline.get(field,set());head,sep,tail=raw.partition(b'\0')
  if raw in factory:kind='exact_factory_buffer'
  elif all(x==0 for x in raw):kind='all_zero_buffer'
  elif sep and head in allowed.get(field,set()):
   # Changed public string: every remaining byte must be neutral or at the exact same
   # byte position in one single factory buffer, never arbitrary substring matching.
   k=len(head)+1
   candidates=[q for q in factory if len(q)==len(raw)]or[bytes(len(raw))]
   matched=any(all(x in (0,95)or x==q[k+i] for i,x in enumerate(tail))for q in candidates)
   if matched:
    kind='public_authored_value_with_verified_full_tail';authored[(field,head.decode('utf-8'))]+=1
   else:kind='unexpected_tail';fail.append({'field':field,'offset':r['offset'],'bytes':len(raw),'reason':kind,'buffer_sha256':hashlib.sha256(raw).hexdigest()})
  else:
   kind='unexpected_buffer';fail.append({'field':field,'offset':r['offset'],'bytes':len(raw),'reason':kind,'buffer_sha256':hashlib.sha256(raw).hexdigest()})
  counts[kind]+=1;groups[field][kind]+=1
 return {'all_pass':not fail,'buffers_checked':len(records),'total_fixed_buffer_bytes':sum(len(r['bytes'])for r in records),'classification_counts':dict(counts),'field_groups':[{'field':k,'buffers':sum(v.values()),'classifications':dict(v)}for k,v in sorted(groups.items())],'public_authored_values':[{'field':k[0],'value':k[1],'count':v}for k,v in sorted(authored.items())],'violations':fail}

def main():
 p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,default=Path(__file__).resolve().parent/'beitou-library-whole-pre2026.blend');p.add_argument('--report',type=Path);p.add_argument('--blender',default='blender');args=p.parse_args()
 model=BlendDNA(args.blend);original=hashlib.sha256(model.data).hexdigest();allowed=authored_heads(args.blend.parent)
 with tempfile.TemporaryDirectory(prefix='blend-factory-audit-')as tmp:
  tmp=Path(tmp);script=tmp/'save_factory.py';base=tmp/'factory.blend'
  script.write_text("import bpy,sys\nbpy.ops.wm.save_as_mainfile(filepath=sys.argv[-1],compress=False)\n")
  run=subprocess.run([args.blender,'--factory-startup','--python-exit-code','1','--background','--python',str(script),'--',str(base)],capture_output=True,text=True)
  assert run.returncode==0,'Factory Blender baseline creation failed'
  factory=BlendDNA(base);assert factory.version==model.version and factory.dna_sha256==model.dna_sha256,'Factory/model SDNA mismatch'
  baseline=collections.defaultdict(set)
  for r in factory.records:baseline[r['field']].add(r['bytes'])
  result=audit(model.records,baseline,allowed)
  controls=[]
  r=audit(factory.records,baseline,allowed);assert r['all_pass'];controls.append({'control':'actual_untouched_factory_file','expected_pass':True,'actual_pass':True})
  for field,kind in [('Scene.r/RenderData.pic[1024]','post_NUL_stale_text'),('Scene.r/RenderData.im_format/ImageFormatData.linear_colorspace_settings/ColorManagedColorspaceSettings.name[64]','nested_struct_private_value')]:
   rec=next(x for x in model.records if x['field']==field);bad=dict(rec);raw=bytearray(rec['bytes'])
   if kind=='post_NUL_stale_text':at=raw.index(0)+1;marker=b'SYNTHETIC_PRIVATE_TAIL!!';raw[at:at+len(marker)]=marker
   else:raw[:24]=b'SYNTHETIC_PRIVATE_VALUE\0'
   bad['bytes']=bytes(raw);check=audit([bad],baseline,allowed);assert not check['all_pass'];controls.append({'control':kind,'field':field,'expected_pass':False,'actual_pass':False})
  result.update({'method':'Recursive embedded SDNA field offsets over every structured block instance and embedded structure/array; every fixed char array including its complete NUL tail; compare exact whole buffers with an actual newly saved --factory-startup Blender file, then narrowly declared public names/settings with full tail checking. No prefix-only grep or field-name-only path scan.','scope':'Declared non-pointer fixed arrays of char/uchar/int8_t/uint8_t; raw pointer allocations, float geometry, and media are separate native/artifact checks.','model_blend_sha256':original,'blender_file_version':model.version,'sdna_sha256':model.dna_sha256,'actual_factory_file_created':True,'factory_blend_sha256':hashlib.sha256(factory.data).hexdigest(),'factory_fixed_buffers':len(factory.records),'structured_blocks_checked':model.structured_blocks,'raw_non_structured_blocks_outside_fixed_array_scope':model.raw_blocks,'distinct_fixed_fields':len(result['field_groups']),'synthetic_negative_controls':controls,'deliverable_modified':False})
 assert hashlib.sha256(args.blend.read_bytes()).hexdigest()==original,'Deliverable changed during audit'
 if args.report:args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({k:v for k,v in result.items()if k not in ('field_groups','public_authored_values')},indent=2));assert result['all_pass'],'Unexpected fixed-buffer contents; see hashed violation records'
if __name__=='__main__':main()
