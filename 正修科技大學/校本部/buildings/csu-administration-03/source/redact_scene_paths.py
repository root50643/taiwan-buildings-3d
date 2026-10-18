"""Redact only the independently verified FileSelectParams.dir char array.

This tool writes staged scenes and reports outside the input deliverable.
No Blender save, geometry rebuild, render, or slicer operation is used.
Requirements: Python 3, zstandard (exact installed version recorded).
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import struct
import zstandard as zstd

EXPECTED = {
    'models/v1/scene.blend':'18736d0ee70384fba9a20f83d3632b9a237c0f1d01f1d4eaf28ec85bf837e750',
    'models/v2/scene.blend':'b9b0cf0a1411b4c29a69656888610223d5952a6b0fbb8b91c58b30bf6908c056'}
PRIVATE = re.compile(rb'[A-Za-z]:[\\/]+Users[\\/]+', re.I)
HEADER = b'BLENDER17-01v0502'
FIELD_START, FIELD_BYTES = 176332, 1282


def sha(data):
    return hashlib.sha256(data).hexdigest()


def split_frames(raw):
    frames=[]; compressed_offset=0; expanded_offset=0
    while compressed_offset<len(raw):
        rest=raw[compressed_offset:]
        magic=struct.unpack_from('<I',rest)[0]
        if magic & 0xfffffff0 == 0x184d2a50:
            size=struct.unpack_from('<I',rest,4)[0]
            assert magic==0x184d2a5e and compressed_offset+8+size==len(raw)
            frames.append({'compressed':rest[:8+size],'data':b'',
                'compressed_offset':compressed_offset,'expanded_offset':expanded_offset,
                'skippable_seek_table':True})
            compressed_offset+=8+size
            continue
        params=zstd.get_frame_parameters(rest)
        decoder=zstd.ZstdDecompressor().decompressobj()
        data=decoder.decompress(rest)
        assert decoder.eof
        consumed=len(rest)-len(decoder.unused_data)
        assert consumed>0 and params.dict_id==0
        frames.append({'compressed':rest[:consumed], 'data':data,
            'compressed_offset':compressed_offset, 'expanded_offset':expanded_offset,
            'skippable_seek_table':False,
            'content_size':params.content_size, 'window_size':params.window_size,
            'has_checksum':params.has_checksum, 'dict_id':params.dict_id})
        compressed_offset+=consumed; expanded_offset+=len(data)
    return frames


def update_seek_table(raw,frames,pieces):
    magic,size=struct.unpack_from('<II',raw)
    count,descriptor,footer_magic=struct.unpack_from('<IBI',raw,len(raw)-9)
    assert magic==0x184d2a5e and footer_magic==0x8f92eab1
    assert descriptor==0 and count==len(frames)==len(pieces) and size==8*count+9
    original=[struct.unpack_from('<II',raw,8+8*i) for i in range(count)]
    assert original==[(len(f['compressed']),len(f['data'])) for f in frames]
    entries=b''.join(struct.pack('<II',len(piece),len(f['data'])) for f,piece in zip(frames,pieces))
    return raw[:8]+entries+raw[-9:]


def blocks(data):
    assert data.startswith(HEADER)
    result=[]; pos=len(HEADER)
    while pos<len(data):
        code,sdna,oldptr,length,count=struct.unpack_from('<4sIQQQ',data,pos)
        payload=pos+32; end=payload+length
        assert end<=len(data)
        result.append({'code':code,'sdna':sdna,'header':pos,'payload':payload,
                       'length':length,'count':count})
        pos=end
        if code==b'ENDB':
            assert pos==len(data)
            break
    assert result[-1]['code']==b'ENDB'
    return result


def dna_structures(data):
    pos=data.index(b'SDNANAME')+8
    count=struct.unpack_from('<I',data,pos)[0];pos+=4;names=[]
    for _ in range(count):
        end=data.index(0,pos);names.append(data[pos:end].decode());pos=end+1
    pos=(pos+3)&~3;assert data[pos:pos+4]==b'TYPE';pos+=4
    count=struct.unpack_from('<I',data,pos)[0];pos+=4;types=[]
    for _ in range(count):
        end=data.index(0,pos);types.append(data[pos:end].decode());pos=end+1
    pos=(pos+3)&~3;assert data[pos:pos+4]==b'TLEN';pos+=4
    lengths=struct.unpack_from('<'+'H'*count,data,pos);pos+=2*count
    pos=(pos+3)&~3;assert data[pos:pos+4]==b'STRC';pos+=4
    count=struct.unpack_from('<I',data,pos)[0];pos+=4;result={}
    for index in range(count):
        typ,n=struct.unpack_from('<HH',data,pos);pos+=4;fields=[]
        for _ in range(n):
            t,f=struct.unpack_from('<HH',data,pos);pos+=4
            fields.append([types[t],names[f]])
        result[types[typ]]={'sdna':index,'bytes':lengths[typ],'fields':fields}
    return result


def diff_runs(before,after):
    runs=[]; start=None
    for index,(a,b) in enumerate(zip(before,after)):
        if a!=b and start is None:start=index
        elif a==b and start is not None:runs.append([start,index]);start=None
    if start is not None:runs.append([start,len(before)])
    return runs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-root',type=Path,required=True)
    parser.add_argument('--staging-root',type=Path,required=True)
    parser.add_argument('--private-root',type=Path,required=True)
    args=parser.parse_args()
    source=args.input_root.resolve();stage=args.staging_root.resolve();private=args.private_root.resolve()
    assert not stage.is_relative_to(source) and not private.is_relative_to(source)
    stage.mkdir(parents=True,exist_ok=True);private.mkdir(parents=True,exist_ok=True)
    manifest={'tool':'redact_scene_paths.py','tool_sha256':sha(Path(__file__).read_bytes()),
        'zstandard_version':zstd.__version__,'new_compression_level_for_changed_frames':3,
        'original_compression_level':'Unknown; not claimed to be reproduced',
        'replacement':'// followed by NUL fill of FileSelectParams.dir[1282]',
        'scope':'Staging only; input deliverable scenes remain untouched', 'files':[]}
    private_records=[]
    for relative,expected in EXPECTED.items():
        path=source/relative;raw=path.read_bytes();assert sha(raw)==expected
        frames=split_frames(raw);data=b''.join(f['data'] for f in frames)
        parsed=blocks(data);dna=dna_structures(data)
        assert len(parsed)==1983
        assert dna['FileSelectParams']=={'sdna':849,'bytes':2280,
            'fields':dna['FileSelectParams']['fields']}
        assert dna['FileSelectParams']['fields'][:2]==[['char','title[96]'],['char','dir[1282]']]
        block=[b for b in parsed if b['header']==176204][0]
        assert block=={'code':b'DATA','sdna':849,'header':176204,'payload':176236,'length':2280,'count':1}
        assert data[block['payload']:FIELD_START].split(b'\0',1)[0]==b'Save As Blender File'
        field=data[FIELD_START:FIELD_START+FIELD_BYTES]
        value=field.split(b'\0',1)[0]
        assert len(value)==30 and PRIVATE.match(value)
        assert len(list(PRIVATE.finditer(data)))==1
        glob=[b for b in parsed if b['code']==b'GLOB'][0]
        assert glob['payload']==345 and glob['sdna']==171 and dna['FileGlobal']['fields'][13]==['char','filename[1024]']
        assert data[425:1449].split(b'\0',1)[0]==b''
        replacement=b'//'+b'\0'*(FIELD_BYTES-2)
        edited=data[:FIELD_START]+replacement+data[FIELD_START+FIELD_BYTES:]
        assert len(data)==len(edited) and not PRIVATE.search(edited)
        assert data[:FIELD_START]==edited[:FIELD_START]
        assert data[FIELD_START+FIELD_BYTES:]==edited[FIELD_START+FIELD_BYTES:]
        runs=diff_runs(data,edited)
        assert all(FIELD_START<=lo<hi<=FIELD_START+FIELD_BYTES for lo,hi in runs)
        pieces=[];frame_records=[]
        for index,frame in enumerate(frames):
            lo=frame['expanded_offset'];hi=lo+len(frame['data'])
            new_data=edited[lo:hi]
            if frame['skippable_seek_table']:
                compressed=update_seek_table(frame['compressed'],frames[:index],pieces)
            elif new_data==frame['data']:
                compressed=frame['compressed']
            else:
                compressor=zstd.ZstdCompressor(level=3,
                    write_content_size=frame['content_size']!=zstd.CONTENTSIZE_UNKNOWN,
                    write_checksum=frame['has_checksum'],write_dict_id=False)
                compressed=compressor.compress(new_data)
            pieces.append(compressed)
            frame_records.append({'index':index,'expanded_range':[lo,hi],
                'original_compressed_offset':frame['compressed_offset'],
                'original_compressed_bytes':len(frame['compressed']),'delivered_compressed_bytes':len(compressed),
                'original_compressed_sha256':sha(frame['compressed']),'delivered_compressed_sha256':sha(compressed),
                'kind':'skippable_seek_table' if frame['skippable_seek_table'] else 'zstd_data_frame',
                'seek_table_updated':frame['skippable_seek_table'],
                'content_changed':new_data!=frame['data'],
                'unaffected_data_frame_preserved':frame['skippable_seek_table'] or new_data!=frame['data'] or compressed==frame['compressed'],
                'original_frame_content_size':frame.get('content_size'),
                'original_frame_window_size':frame.get('window_size'),'original_frame_checksum':frame.get('has_checksum')})
        delivered=b''.join(pieces)
        rebuilt=split_frames(delivered)
        assert len(rebuilt)==len(frames)
        assert [f['expanded_offset'] for f in rebuilt]==[f['expanded_offset'] for f in frames]
        assert [len(f['data']) for f in rebuilt]==[len(f['data']) for f in frames]
        assert b''.join(f['data'] for f in rebuilt)==edited
        dest=stage/relative;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert dest.read_bytes()==delivered
        else:dest.write_bytes(delivered)
        original_copy=private/relative;original_copy.parent.mkdir(parents=True,exist_ok=True)
        if original_copy.exists():assert original_copy.read_bytes()==raw
        else:shutil.copyfile(path,original_copy)
        assert sha(path.read_bytes())==expected and sha(original_copy.read_bytes())==expected
        manifest['files'].append({'path':relative,'original_bytes':len(raw),'original_sha256':sha(raw),
            'delivered_bytes':len(delivered),'delivered_sha256':sha(delivered),
            'expanded_bytes':len(data),'original_expanded_sha256':sha(data),'delivered_expanded_sha256':sha(edited),
            'field':{'structure':'FileSelectParams','name':'dir[1282]','sdna_index':849,
                     'block_header_offset':176204,'block_payload_offset':176236,'structure_bytes':2280,
                     'field_relative_offset':96,'expanded_range':[FIELD_START,FIELD_START+FIELD_BYTES],
                     'original_value_bytes':len(value),'original_value_sha256':sha(value),
                     'original_field_sha256':sha(field),'delivered_field_sha256':sha(replacement),
                     'delivered_value':'//','nul_filled':True},
            'FileGlobal_filename':{'expanded_range':[425,1449],'effective_value_empty':True},
            'changed_byte_count':sum(hi-lo for lo,hi in runs),'expanded_diff_ranges':runs,
            'all_expanded_bytes_outside_field_identical':True,
            'frame_count_before':len(frames),'frame_count_after':len(rebuilt),
            'data_frame_count_before':sum(not f['skippable_seek_table'] for f in frames),
            'data_frame_count_after':sum(not f['skippable_seek_table'] for f in rebuilt),
            'seek_table_updated_for_new_compressed_sizes':True,
            'expanded_frame_boundaries_identical':True,'frames':frame_records,
            'input_file_unchanged':sha(path.read_bytes())==expected})
        private_records.append({'path':relative,'original_copy_task_relative':original_copy.relative_to(Path.cwd().resolve()).as_posix(),
                                'actual_original_directory':value.decode('utf8'),
                                'original_scene_sha256':expected})
    manifest['passed']=all(f['all_expanded_bytes_outside_field_identical'] and f['input_file_unchanged'] for f in manifest['files'])
    (stage/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    (private/'private-path-report.json').write_text(json.dumps({'private_only':True,'files':private_records},indent=2)+'\n',encoding='utf8')
    print(json.dumps({'staging_root':stage.name,'manifest':'manifest.json','zstandard_version':zstd.__version__,
        'files':[{k:f[k] for k in ['path','original_sha256','delivered_bytes','delivered_sha256','changed_byte_count','frame_count_before','frame_count_after']} for f in manifest['files']],
        'passed':manifest['passed']},indent=2))


if __name__=='__main__':main()
