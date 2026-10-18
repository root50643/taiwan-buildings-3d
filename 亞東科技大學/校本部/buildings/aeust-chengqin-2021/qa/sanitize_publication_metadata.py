"""Remove workstation metadata without changing STL, pixels or scene geometry.

PNG: remove only the tEXt File field, preserve IDAT and every other chunk.
Blender 5.2 file format 17: parse SDNA and clear only FileSelectParams.dir[1282],
the saved file-browser directory. Every decompressed byte outside that field
must be unchanged. Logs: replace known workstation-root text with placeholders.
Requires Pillow and zstandard for this publication-only metadata operation.
"""
from pathlib import Path
import hashlib,io,json,re,struct,zlib
import zstandard
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def png_clean(data):
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    out=data[:8];offset=8;removed=[];idat_before=[];idat_after=[]
    while offset<len(data):
        size=struct.unpack_from('>I',data,offset)[0]
        kind=data[offset+4:offset+8];value=data[offset+8:offset+8+size]
        chunk=data[offset:offset+size+12]
        assert zlib.crc32(kind+value)&0xffffffff==struct.unpack('>I',chunk[-4:])[0]
        if kind==b'IDAT':idat_before.append(value)
        if kind==b'tEXt' and value.split(b'\0',1)[0]==b'File':
            removed.append('tEXt:File')
        else:
            out+=chunk
            if kind==b'IDAT':idat_after.append(value)
        offset+=size+12
    assert offset==len(data) and idat_before==idat_after
    before=Image.open(io.BytesIO(data)).convert('RGBA').tobytes()
    after=Image.open(io.BytesIO(out)).convert('RGBA').tobytes()
    assert before==after
    return out,{'removed':removed,'idat_bytes_unchanged':True,'decoded_rgba8_sha256':sha(before),'pixels_unchanged':True}


def dna_strings(data,offset,tag):
    assert data[offset:offset+4]==tag
    count=struct.unpack_from('<I',data,offset+4)[0];offset+=8;items=[]
    for _ in range(count):
        end=data.index(0,offset);items.append(data[offset:end].decode('ascii'));offset=end+1
    return items,(offset+3)&~3


def blend_clean(data):
    raw=zstandard.ZstdDecompressor().stream_reader(io.BytesIO(data)).read()
    assert raw.startswith(b'BLENDER17-01v0502')
    offset=17;blocks=[];dna=None
    while offset+32<=len(raw):
        code,sdna,address,size,count,flags=struct.unpack_from('<4sIQQII',raw,offset)
        assert offset+32+size<=len(raw)
        blocks.append((code,sdna,offset+32,size))
        if code==b'DNA1':dna=raw[offset+32:offset+32+size]
        offset+=32+size
        if code==b'ENDB':break
    assert offset==len(raw) and blocks[-1][0]==b'ENDB' and dna.startswith(b'SDNA')
    names,k=dna_strings(dna,4,b'NAME');types,k=dna_strings(dna,k,b'TYPE')
    assert dna[k:k+4]==b'TLEN';k+=4
    lengths=struct.unpack_from('<'+str(len(types))+'H',dna,k);k=(k+len(types)*2+3)&~3
    assert dna[k:k+4]==b'STRC';n=struct.unpack_from('<I',dna,k+4)[0];k+=8;structs=[]
    for _ in range(n):
        t,c=struct.unpack_from('<HH',dna,k);k+=4;fields=[]
        for _ in range(c):
            ft,fn=struct.unpack_from('<HH',dna,k);k+=4;fields.append((types[ft],names[fn]))
        structs.append((types[t],lengths[t],fields))
    modified=bytearray(raw);ranges=[]
    for code,sdna,start,size in blocks:
        if code==b'DATA' and structs[sdna][0]=='FileSelectParams':
            typename,total,fields=structs[sdna]
            assert fields[:2]==[('char','title[96]'),('char','dir[1282]')]
            assert total==size==2280
            a,b=start+96,start+96+1282
            old=raw[a:b]
            new=b'//\0'+b'\0'*(1282-3)
            if old!=new:
                modified[a:b]=new;ranges.append((a,b))
    if not ranges:
        return data,{'changed_fields':[],'already_sanitized':True}
    cursor=0
    for a,b in ranges:
        assert raw[cursor:a]==modified[cursor:a];cursor=b
    assert raw[cursor:]==modified[cursor:]
    assert b'c:\\users\\' not in bytes(modified).lower()
    out=zstandard.ZstdCompressor(level=3).compress(bytes(modified))
    assert zstandard.ZstdDecompressor().decompress(out)==modified
    return out,{'changed_fields':['FileSelectParams.dir[1282]'],'parsed_blocks':len(blocks),
                'decompressed_length_unchanged':True,'every_other_decompressed_byte_unchanged':True,
                'original_decompressed_sha256':sha(raw),'public_decompressed_sha256':sha(modified)}


def main():
    report_path=ROOT/'qa/publication-metadata.json'
    previous=json.loads(report_path.read_text(encoding='utf8')) if report_path.exists() else {'files':[]}
    records={r['path']:r for r in previous['files']}
    package=str(ROOT)
    workspace=str(ROOT.parents[4])
    home=str(Path.home())
    replacements=[(package,'<MODEL_PACKAGE>'),(workspace,'<BUILD_WORKSPACE>'),(home,'<USER_HOME>')]
    variants=[]
    for value,label in replacements:
        variants += [(value,label),(value.replace('\\','\\\\'),label),(value.replace('\\','/'),label)]
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or path==report_path:continue
        before=path.read_bytes();after=before;detail={}
        if path.suffix=='.png':after,detail=png_clean(before)
        elif path.suffix=='.blend':after,detail=blend_clean(before)
        elif path.suffix in ['.log','.txt']:
            text=before.decode('utf8',errors='surrogateescape')
            for old,new in variants:text=text.replace(old,new)
            after=text.encode('utf8',errors='surrogateescape')
            detail={'changed':'Workstation directory prefixes only; numerical values and failure text preserved'}
        if after!=before:
            relative=path.relative_to(ROOT).as_posix()
            row={'path':relative,'original_sha256':sha(before),'public_sha256':sha(after),**detail}
            if relative in records:row['earlier_public_metadata_record']=records[relative]
            records[relative]=row;path.write_bytes(after)
    report={'scope':'Publication-only privacy cleanup; frozen candidate commit and its Library v0 remain original. No STL, parameters, generator, pixel, material, camera or scene geometry change.',
            'candidate_commit':'4116148c135d8a67a444ce8bf33fb64aba3e06a3',
            'files':list(records.values())}
    report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    manifest_path=ROOT/'previews/v1/render-manifest.json'
    manifest=json.loads(manifest_path.read_text(encoding='utf8'))
    manifest['scene_sha256']=sha((ROOT/'models/v1/scene.blend').read_bytes())
    for view in manifest['views']:view['png_sha256']=sha((ROOT/'previews/v1'/(view['name']+'.png')).read_bytes())
    manifest['publication_metadata_cleanup']='Only File PNG text and saved Blender file-browser directory removed. All image IDAT/decoded pixels and all other decompressed Blend bytes preserved; see qa/publication-metadata.json.'
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'changed_or_recorded_files':len(records),'stl_sha256':sha((ROOT/'models/v1/model.stl').read_bytes()),'scene_sha256':manifest['scene_sha256']}))


if __name__=='__main__':main()
