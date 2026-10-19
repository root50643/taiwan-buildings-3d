"""Minimal read-only Blender SDNA inspection; no guessed offsets."""
from pathlib import Path
import gzip, io, re, struct, hashlib

def sha(data): return hashlib.sha256(data).hexdigest()

def unpack_file(data):
    if data.startswith(b'BLENDER'): return data,'none'
    if data.startswith(b'\x1f\x8b'): return gzip.decompress(data),'gzip'
    if data.startswith(b'\x28\xb5\x2f\xfd'):
        import zstandard
        with zstandard.ZstdDecompressor().stream_reader(io.BytesIO(data)) as f:return f.read(),'zstd'
    raise ValueError('Unsupported blend compression/header')

def parse(data):
    raw,compression=unpack_file(data)
    assert raw[:7]==b'BLENDER'
    modern=raw[7:9]==b'17'
    if modern:
        assert raw[9:13]==b'-01v'
        pointer=8;endian='<';header=struct.Struct('<4sIQqq');pos=17
    else:
        pointer=8 if raw[7:8]==b'-' else 4
        endian='<' if raw[8:9]==b'v' else '>'
        header=struct.Struct(endian+('4sIQII' if pointer==8 else '4sIIII'));pos=12
    blocks=[]
    while pos<len(raw):
        if modern:code,sdna,old,n,count=header.unpack_from(raw,pos)
        else:code,n,old,sdna,count=header.unpack_from(raw,pos)
        assert n>=0 and pos+header.size+n<=len(raw)
        blocks.append({'code':code.decode('ascii','replace'),'offset':pos,'body_offset':pos+header.size,'length':n,'sdna':sdna,'count':count})
        pos+=header.size+n
        if code==b'ENDB':break
    dna=next(b for b in blocks if b['code']=='DNA1')
    payload=raw[dna['body_offset']:dna['body_offset']+dna['length']]
    assert payload[:8]==b'SDNANAME'
    p=8
    def u32():
        nonlocal p
        v=struct.unpack_from(endian+'I',payload,p)[0];p+=4;return v
    def strings(n):
        nonlocal p
        vals=[]
        for i in range(n):
            end=payload.index(b'\0',p);vals.append(payload[p:end].decode('utf-8'));p=end+1
        p=(p+3)&~3
        return vals
    names=strings(u32());assert payload[p:p+4]==b'TYPE';p+=4
    types=strings(u32());assert payload[p:p+4]==b'TLEN';p+=4
    sizes=list(struct.unpack_from(endian+str(len(types))+'H',payload,p));p+=2*len(types);p=(p+3)&~3
    assert payload[p:p+4]==b'STRC';p+=4
    structures=[]
    for i in range(u32()):
        ti,n=struct.unpack_from(endian+'HH',payload,p);p+=4
        members=[]
        for k in range(n):
            mti,mni=struct.unpack_from(endian+'HH',payload,p);p+=4
            members.append((mti,mni))
        structures.append({'type_index':ti,'type':types[ti],'length':sizes[ti],'members':members})
    bytype={s['type_index']:s for s in structures};aligncache={}
    def alignment(ti,active=None):
        if ti in aligncache:return aligncache[ti]
        active=set() if active is None else active
        if ti in active:raise ValueError('Recursive by-value type')
        if ti not in bytype:return min(max(sizes[ti],1),pointer)
        active.add(ti);a=1
        for mti,mni in bytype[ti]['members']:
            a=max(a,pointer if '*' in names[mni] else alignment(mti,active))
        active.remove(ti);aligncache[ti]=a;return a
    for s in structures:
        offset=0;fields=[]
        for ti,ni in s['members']:
            name=names[ni];a=pointer if '*' in name else alignment(ti)
            offset=(offset+a-1)//a*a
            count=1
            for n in re.findall(r'\[(\d+)\]',name):count*=int(n)
            length=(pointer if '*' in name else sizes[ti])*count
            fields.append({'name':name,'type':types[ti],'offset':offset,'length':length,'pointer': '*' in name})
            offset+=length
        a=alignment(s['type_index']);s['computed_length']=(offset+a-1)//a*a;s['fields']=fields
    return {'raw':raw,'compression':compression,'pointer_size':pointer,'endian':endian,'blocks':blocks,'structures':structures}

def path_findings(parsed):
    raw=parsed['raw']
    patterns={
        'drive_path':re.compile(rb'(?i)(?<![a-z0-9])[a-z]:[\\/]'),
        'private_path_fragment':re.compile(rb'(?i)(?:Users[\\/]|Documents[\\/]|AppData[\\/]|\d{4}-\d{2}-\d{2}[\\/]|task-\d+[\\/])')}
    findings=[]
    for kind,rx in patterns.items():
        for m in rx.finditer(raw):
            block=next((b for b in parsed['blocks'] if b['body_offset']<=m.start()<b['body_offset']+b['length']),None)
            row={'kind':kind,'offset':m.start()}
            if block and block['code']!='DNA1':
                s=parsed['structures'][block['sdna']]
                row.update({'block_code':block['code'],'structure':s['type'],'structure_tlen':s['length'],'computed_length':s['computed_length']})
                local=(m.start()-block['body_offset'])%max(s['length'],1)
                f=next((f for f in s['fields'] if f['offset']<=local<f['offset']+f['length']),None)
                if f:
                    row['field']=f
                    row['leaf_field']=locate_field(parsed,s,local)
            findings.append(row)
    return findings

def locate_field(parsed,structure,local,base=0,prefix=''):
    assert structure['length']==structure['computed_length']
    f=next(f for f in structure['fields'] if f['offset']<=local<f['offset']+f['length'])
    nested=next((s for s in parsed['structures'] if s['type']==f['type']),None)
    if nested and not f['pointer']:
        element=(local-f['offset'])//nested['length']
        return locate_field(parsed,nested,(local-f['offset'])%nested['length'],base+f['offset']+element*nested['length'],prefix+f['name']+'.')
    return {'path':prefix+f['name'],'type':f['type'],'offset_in_block_element':base+f['offset'],'length':f['length'],'pointer':f['pointer']}
