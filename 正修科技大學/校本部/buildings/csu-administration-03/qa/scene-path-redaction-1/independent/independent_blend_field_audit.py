"""Independent read-only BLEND SDNA field audit. Never saves a scene."""
from pathlib import Path
import argparse,hashlib,io,json,math,re,struct
import zstandard

def sha(data):return hashlib.sha256(data).hexdigest()
def require(ok,message):
    if not ok:raise RuntimeError(message)
def decoded(raw):
    if raw.startswith(b'BLENDER'):return raw
    require(raw.startswith(b'\x28\xb5\x2f\xfd'),'Expected native BLEND or zstd frame')
    with zstandard.ZstdDecompressor().stream_reader(io.BytesIO(raw),read_across_frames=True) as handle:return handle.read()
def blocks(data):
    require(data[:17]==b'BLENDER17-01v0502','Unexpected BLEND header; do not guess another schema')
    ans=[];offset=17
    while offset<len(data):
        require(offset+32<=len(data),'Short BHead32')
        code,sdna,address,length,count=struct.unpack_from('<4sIQQQ',data,offset)
        start=offset+32;end=start+length
        require(end<=len(data),'BHead payload outside decoded file')
        ans.append({'code':code.rstrip(b'\0').decode('ascii'),'header_offset':offset,'payload_offset':start,
                    'payload_length':length,'address':address,'sdna_index':sdna,'count':count,'payload':data[start:end]})
        offset=end
        if code.rstrip(b'\0')==b'ENDB':break
    require(offset==len(data),'Bytes after ENDB')
    return ans
def dna(payload):
    p=0
    def marker(value):
        nonlocal p
        require(payload[p:p+4]==value,'SDNA marker mismatch');p+=4
    def u32():
        nonlocal p
        value=struct.unpack_from('<I',payload,p)[0];p+=4;return value
    def strings():
        nonlocal p
        count=u32();result=[]
        for _ in range(count):
            stop=payload.index(0,p);result.append(payload[p:stop].decode('ascii'));p=stop+1
        p=(p+3)//4*4;return result
    marker(b'SDNA');marker(b'NAME');names=strings();marker(b'TYPE');types=strings();marker(b'TLEN')
    sizes=list(struct.unpack_from('<'+'H'*len(types),payload,p));p+=2*len(types);p=(p+3)//4*4
    marker(b'STRC');count=u32();structs=[]
    for _ in range(count):
        type_id,n=struct.unpack_from('<HH',payload,p);p+=4;fields=[]
        for __ in range(n):
            field_type,field_name=struct.unpack_from('<HH',payload,p);p+=4;fields.append((field_type,field_name))
        structs.append({'type_id':type_id,'name':types[type_id],'size':sizes[type_id],'fields':fields})
    require(p==len(payload),'Unexpected SDNA tail')
    return {'names':names,'types':types,'sizes':sizes,'structs':structs}
def layout(schema,entry):
    offset=0;fields=[]
    for typ,nam in entry['fields']:
        name=schema['names'][nam];count=math.prod(int(n) for n in re.findall(r'\[(\d+)\]',name))
        count=count or 1;pointer='*' in name
        size=(8 if pointer else schema['sizes'][typ])*count
        fields.append({'name':name,'type':schema['types'][typ],'offset':offset,'size':size,'pointer':pointer})
        offset+=size
    require(offset==entry['size'],'Computed SDNA field-size sum differs; no implicit alignment guessing')
    return fields
def inspect(raw,owner='FileSelectParams',field='dir'):
    data=decoded(raw);heads=blocks(data);dnas=[b for b in heads if b['code']=='DNA1'];require(len(dnas)==1,'Need one SDNA block')
    schema=dna(dnas[0]['payload']);owners=[(i,e) for i,e in enumerate(schema['structs']) if e['name']==owner]
    require(len(owners)==1,'SDNA owner struct absent/ambiguous');index,entry=owners[0];fields=layout(schema,entry)
    choices=[x for x in fields if re.sub(r'\[\d+\]','',x['name'])==field]
    require(len(choices)==1,'Field absent/ambiguous');selected=choices[0]
    require(selected['type']=='char' and not selected['pointer'],'Expected fixed char array')
    regions=[]
    for block in heads:
        if block['sdna_index']!=index or block['code'] in ['DNA1','ENDB']:continue
        require(block['payload_length']==entry['size']*block['count'],'Owner payload/instance stride differs')
        for instance in range(block['count']):
            start=block['payload_offset']+instance*entry['size']+selected['offset'];end=start+selected['size']
            regions.append({'block_code':block['code'],'block_header_offset':block['header_offset'],'instance':instance,
                'field_start':start,'field_end_exclusive':end,'field_capacity':selected['size'],
                'field_type':selected['type'],'field_name':selected['name'],'struct_name':entry['name'],
                'struct_size':entry['size'],'sdna_index':index})
    require(regions,'Owner field block absent')
    hits=[(m.start(),m.end()) for m in re.finditer(rb'[A-Za-z]:[\\/](?:Users|Program Files|Windows)[\\/]',data)]
    return data,regions,hits
def compare(old_raw,new_raw):
    old,regions,before=inspect(old_raw);new,newregions,after=inspect(new_raw)
    require(len(old)==len(new),'Decoded file size changed');require(regions==newregions,'Decoded SDNA/block/field layout changed')
    differences=[i for i,(a,b) in enumerate(zip(old,new)) if a!=b]
    touched=[r for r in regions if any(r['field_start']<=p<r['field_end_exclusive'] for p in differences)]
    covered=all(any(r['field_start']<=p<r['field_end_exclusive'] for r in touched) for p in differences)
    a=bytearray(old);b=bytearray(new)
    for r in touched:a[r['field_start']:r['field_end_exclusive']]=b'\0'*r['field_capacity'];b[r['field_start']:r['field_end_exclusive']]=b'\0'*r['field_capacity']
    rows=[]
    for r in touched:
        start,end=r['field_start'],r['field_end_exclusive'];original=old[start:end];replacement=new[start:end]
        rows.append(dict(r,original_nonzero_prefix_length=original.find(b'\0'),
            source_field_sha256=sha(original),delivered_field_sha256=sha(replacement),
            replacement_is_double_slash_then_NULs=replacement==b'//'+b'\0'*(r['field_capacity']-2),
            original_private_findings_in_field=sum(start<=p<end for p,_ in before)))
    checks={'exactly_one_changed_FileSelectParams_dir_array':len(touched)==1,
        'all_decoded_difference_bytes_within_that_array':bool(differences) and covered,
        'all_other_decoded_bytes_identical':a==b,'replacement_relative_double_slash_and_NUL_padding':all(x['replacement_is_double_slash_then_NULs'] for x in rows),
        'old_decoded_binary_scan_detects_one_private_host_path':len(before)==1,
        'new_decoded_binary_scan_has_no_private_host_path':not after}
    return {'passed':all(checks.values()),'checks':checks,'source_compressed_sha256':sha(old_raw),'delivered_compressed_sha256':sha(new_raw),
        'source_decoded_sha256':sha(old),'delivered_decoded_sha256':sha(new),'decoded_length':len(old),
        'decoded_changed_byte_count':len(differences),'changed_field_regions':rows,
        'source_binary_scan_passed':not before,'source_binary_scan_findings':len(before),
        'delivered_binary_scan_passed':not after,'delivered_binary_scan_findings':len(after),
        'masked_decoded_sha256':sha(a),'method':'Independent BHead32 walk and SDNA NAME/TYPE/TLEN/STRC interpretation; exact field-size sums and byte comparison. No scene save, repair, rendering or inherited checker call.',
        'limits':'This byte audit excludes no data besides the exact named char array. Blender semantic signatures must be compared separately. Earlier raw-byte-only hygiene results did not inspect decompressed BLEND internals.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--old',type=Path,required=True);p.add_argument('--new',type=Path);p.add_argument('--report',type=Path);a=p.parse_args()
    raw=a.old.read_bytes()
    if a.new:r=compare(raw,a.new.read_bytes())
    else:
        data,regions,hits=inspect(raw);r={'compressed_sha256':sha(raw),'decoded_sha256':sha(data),'decoded_length':len(data),
            'field_regions':regions,'decoded_private_hostpath_count':len(hits),'scope':'Read-only original field layout; no correction or final validation performed.'}
    if a.report:
        require(not a.report.exists(),'Refuse to overwrite report');a.report.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r,indent=2));return 0 if not a.new or r['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
