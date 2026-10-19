"""Portable lossless PNG and SDNA-located Blender host-path metadata cleaner.

No Blender runtime patching, guessed binary offsets, rendering or geometry edits.
Modern blend headers follow Blender's BLO_core_blend_header.hh / BLO_core_bhead.hh.
"""
from pathlib import Path
import hashlib, json, struct, zlib
from blend_dna import parse, path_findings

def sha(data):return hashlib.sha256(data).hexdigest()

def sanitize_png_metadata(path):
    path=Path(path);before=path.read_bytes()
    assert before[:8]==b'\x89PNG\r\n\x1a\n'
    offset=8;retained=[];removed=[];idat=[]
    while offset<len(before):
        n=struct.unpack_from('>I',before,offset)[0];typ=before[offset+4:offset+8];body=before[offset+8:offset+8+n]
        assert struct.unpack_from('>I',before,offset+8+n)[0]==zlib.crc32(typ+body)&0xffffffff
        chunk=before[offset:offset+n+12]
        if typ in {b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'}:
            removed.append({'type':typ.decode(),'key':body.split(b'\0',1)[0].decode('latin-1') if typ in {b'tEXt',b'zTXt',b'iTXt'} else None})
        else:retained.append(chunk)
        if typ==b'IDAT':idat.append(body)
        offset+=n+12
    assert offset==len(before)
    after=before[:8]+b''.join(retained)
    if after!=before:path.write_bytes(after)
    return {'file':path.name,'before_sha256':sha(before),'after_sha256':sha(after),
        'idat_sha256':sha(b''.join(idat)),'all_retained_chunks_byte_equal':True,'removed_chunks':removed}

def _field(parsed,structure,path):
    offset=0;current=structure
    for i,base_name in enumerate(path):
        assert current['length']==current['computed_length'],'SDNA target structure alignment mismatch'
        found=[f for f in current['fields'] if f['name'].split('[',1)[0]==base_name and not f['pointer']]
        assert len(found)==1,'Expected one SDNA field'
        f=found[0];offset+=f['offset']
        if i<len(path)-1:
            current=next(s for s in parsed['structures'] if s['type']==f['type'])
    assert f['type']=='char' and '[' in f['name'],'Only fixed character arrays may be sanitized'
    return offset,f

def sanitize_scene_metadata(path):
    path=Path(path);before=path.read_bytes();parsed=parse(before);original=parsed['raw'];clean=bytearray(original)
    edits=[];fileglobal=[]
    # Local weak append/reuse provenance is metadata; linked Library paths are not modified.
    targets={'FileSelectParams':(('dir',),b''),'Scene':(('r','pic'),b'//previews/front.png'),
             'LibraryWeakReference':(('library_filepath',),b'')}
    for block in parsed['blocks']:
        if block['code'] in {'DNA1','ENDB'}:continue
        structure=parsed['structures'][block['sdna']]
        if block['code']=='GLOB':
            # Normal Blender saves already zero this recovery-only filename.
            offset,f=_field(parsed,structure,('filename',))
            field=original[block['body_offset']+offset:block['body_offset']+offset+f['length']]
            assert not any(field),'Nonempty recovery filename requires separate review'
            fileglobal.append({'field':f['name'],'length':f['length'],'zero_before_and_after':True})
        if structure['type'] not in targets:continue
        field_path,value=targets[structure['type']]
        offset,f=_field(parsed,structure,field_path)
        assert len(value)<f['length']
        for element in range(block['count']):
            begin=block['body_offset']+element*structure['length']+offset;end=begin+f['length']
            assert end<=block['body_offset']+block['length']
            old=original[begin:end];new=value+b'\0'*(f['length']-len(value))
            clean[begin:end]=new
            edits.append({'block_code':block['code'],'structure':structure['type'],'structure_tlen':structure['length'],
                'field':'.'.join(field_path),'field_name':f['name'],'schema_offset_in_element':offset,'absolute_begin':begin,'length':f['length'],
                'before_field_sha256':sha(old),'after_field_sha256':sha(new),'new_value':value.decode('ascii'),'changed':old!=new})
    assert any(e['structure']=='Scene' for e in edits)
    # Compare every byte outside the SDNA-derived target ranges.
    cursor=0
    for e in sorted(edits,key=lambda x:x['absolute_begin']):
        assert original[cursor:e['absolute_begin']]==clean[cursor:e['absolute_begin']]
        cursor=e['absolute_begin']+e['length']
    assert original[cursor:]==clean[cursor:]
    raw_after=bytes(clean)
    checked=parse(raw_after)
    assert not path_findings(checked),'Host path remains outside authorized metadata arrays'
    if parsed['compression']=='zstd':
        import zstandard
        after=zstandard.ZstdCompressor(level=3,write_checksum=True).compress(raw_after)
    elif parsed['compression']=='gzip':
        import gzip
        after=gzip.compress(raw_after,mtime=0)
    else:after=raw_after
    assert parse(after)['raw']==raw_after
    if after!=before:path.write_bytes(after)
    return {'file':path.name,'before_sha256':sha(before),'after_sha256':sha(after),
        'uncompressed_before_sha256':sha(original),'uncompressed_after_sha256':sha(raw_after),
        'compression':parsed['compression'],'schema_derived_edits':edits,'outside_authorized_arrays_byte_equal':True,
        'fileglobal':fileglobal,'remaining_raw_host_path_findings':0,'geometry_bytes_modified':False}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path',type=Path)
    args=parser.parse_args()
    result=sanitize_png_metadata(args.path) if args.path.suffix.lower()=='.png' else sanitize_scene_metadata(args.path)
    print(json.dumps(result,indent=2))
