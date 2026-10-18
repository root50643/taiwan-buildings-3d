"""Read-only manual zstd block framing and seek-table validation."""
import hashlib,struct
import zstandard
def require(ok,message):
    if not ok:raise RuntimeError(message)
def sha(value):return hashlib.sha256(value).hexdigest()
def parse(raw):
    pos=0;expanded=0;rows=[]
    while pos<len(raw):
        begin=pos;require(pos+8<=len(raw),'Short frame header')
        magic=struct.unpack_from('<I',raw,pos)[0]
        if magic&0xfffffff0==0x184d2a50:
            size=struct.unpack_from('<I',raw,pos+4)[0];end=pos+8+size;require(end<=len(raw),'Short skippable frame')
            rows.append({'kind':'skippable','start':begin,'end':end,'raw':raw[begin:end],'expanded_start':expanded,'data':b''})
            pos=end;continue
        require(magic==0xfd2fb528,'Unexpected zstd magic')
        descriptor=raw[pos+4];require(not descriptor&0x18,'Reserved zstd frame descriptor bits set')
        single=bool(descriptor&0x20);checksum=bool(descriptor&4);flag=descriptor>>6
        dictionary_size=(0,1,2,4)[descriptor&3]
        fcs_size=(1 if single else 0,2,4,8)[flag]
        pos+=5+(0 if single else 1)+dictionary_size+fcs_size
        blocks=[]
        while True:
            require(pos+3<=len(raw),'Short zstd block header');header=int.from_bytes(raw[pos:pos+3],'little');pos+=3
            last=bool(header&1);kind=(header>>1)&3;length=header>>3
            require(kind!=3,'Reserved zstd block type')
            payload_length=1 if kind==1 else length;require(pos+payload_length<=len(raw),'Short zstd block')
            blocks.append({'kind':kind,'declared_size':length,'last':last});pos+=payload_length
            if last:break
        if checksum:pos+=4
        require(pos<=len(raw),'Short zstd checksum')
        piece=raw[begin:pos];data=zstandard.ZstdDecompressor().decompress(piece)
        rows.append({'kind':'data','start':begin,'end':pos,'raw':piece,'data':data,
                     'expanded_start':expanded,'blocks':blocks,'checksum':checksum,'single_segment':single})
        expanded+=len(data)
    require(pos==len(raw),'Frame walk did not consume all bytes')
    tables=[r for r in rows if r['kind']=='skippable'];require(len(tables)==1 and rows[-1] is tables[0],'Need final seek table')
    table=tables[0]['raw'];magic,size=struct.unpack_from('<II',table);count,descriptor,footer=struct.unpack_from('<IBI',table,len(table)-9)
    require(magic==0x184d2a5e and footer==0x8f92eab1,'Seek table magic mismatch')
    require(descriptor==0 and size==8*count+9,'Unsupported seek-table descriptor')
    dataframes=[r for r in rows if r['kind']=='data'];require(count==len(dataframes),'Seek frame count mismatch')
    entries=[struct.unpack_from('<II',table,8+i*8) for i in range(count)]
    require(entries==[(r['end']-r['start'],len(r['data'])) for r in dataframes],'Seek sizes differ from manual frame walk')
    return rows
def compare(old,new,field_start,field_end):
    a=parse(old);b=parse(new);require(len(a)==len(b),'Frame count changed');rows=[]
    for i,(x,y) in enumerate(zip(a,b)):
        require(x['kind']==y['kind'],'Frame kind/order changed')
        require(x['expanded_start']==y['expanded_start'] and len(x['data'])==len(y['data']),'Expanded frame boundary changed')
        different=x['data']!=y['data'];lo=x['expanded_start'];hi=lo+len(x['data'])
        if x['kind']=='data' and not different:require(x['raw']==y['raw'],'Unchanged data frame was recompressed')
        if different:require(lo<=field_start<field_end<=hi,'Changed data frame does not contain the allowed field')
        rows.append({'index':i,'kind':x['kind'],'expanded_range':[lo,hi],'old_compressed_bytes':len(x['raw']),
            'new_compressed_bytes':len(y['raw']),'old_frame_sha256':sha(x['raw']),'new_frame_sha256':sha(y['raw']),
            'decoded_payload_changed':different,'untouched_data_frame_byte_identical':x['kind']!='data' or different or x['raw']==y['raw']})
    oldtable=a[-1]['raw'];newtable=b[-1]['raw']
    require(oldtable[:8]==newtable[:8] and oldtable[-9:]==newtable[-9:],'Seek-table header/footer changed')
    return {'passed':True,'method':'Manually walk zstd frame descriptor and three-byte block headers, then decompress each bounded frame; independently check seek-table count/size entries against actual frame spans.',
        'frame_count':len(a),'data_frame_count':sum(r['kind']=='data' for r in a),'frames':rows,
        'seek_table_original_and_new_entries_match_actual_frames':True,
        'seek_table_header_footer_identical':True,
        'all_untouched_data_frames_byte_identical':all(r['untouched_data_frame_byte_identical'] for r in rows)}
