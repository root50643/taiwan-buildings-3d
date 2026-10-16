"""Fresh full-payload privacy, whitelist, decoded PNG and chunk CRC audit."""
from pathlib import Path
import gzip,hashlib,json,re,struct,zlib
from PIL import Image
R=Path(__file__).resolve().parent
# Constructed signatures keep the scanner source in its own literal scan.
PATTERNS=[b'/'+b'workspace'+b'/',b'/'+b'home'+b'/',b'/'+b'Users'+b'/',b'/'+b'tmp'+b'/',b'file'+b'://',b'Authorization'+b': Bearer']
WINDOWS=re.compile(rb'(?:^|[^A-Za-z])[A-Za-z]:[\\/]')
def inspect(root):
    bad=[];png=[];unexpected=[];errors=[]
    files=[p for p in sorted(root.rglob('*')) if p.is_file()]
    whitelist=json.loads((root/'distribution-manifest.json').read_text())['files'] if (root/'distribution-manifest.json').is_file() else None
    if whitelist is not None:
        actual={str(p.relative_to(root)) for p in files};unexpected.extend(sorted(actual-set(whitelist)))
        errors.extend('missing:'+n for n in sorted(set(whitelist)-actual))
    for p in files:
        rel=str(p.relative_to(root))
        if '__pycache__' in p.parts or p.suffix in ['.pyc','.blend1','.jpg','.jpeg','.zip','.zst']:unexpected.append(rel)
        try:
            data=p.read_bytes()
            if p.suffix=='.gz':data=gzip.decompress(data)
            if p.suffix=='.blend' and not data.startswith(b'BLENDER'):errors.append('compressed_or_unrecognized_blend:'+rel)
            windows_data=data if p.suffix in ['.py','.cpp','.json','.md','.txt','.gz'] else data[:80] if p.suffix=='.stl' else b''
            # PNG IDAT is binary pixel compression, not a metadata string. Blend
            # Windows-style strings are inspected from actual reopened datablocks.
            if any(q in data for q in PATTERNS) or WINDOWS.search(windows_data):bad.append(rel)
            if p.suffix=='.png':
                raw=p.read_bytes();offset=8;types=[];crc_ok=True
                while offset+12<=len(raw):
                    n=struct.unpack_from('>I',raw,offset)[0];typ=raw[offset+4:offset+8];body=raw[offset+8:offset+8+n]
                    if offset+12+n>len(raw):crc_ok=False;break
                    crc_ok=crc_ok and zlib.crc32(typ+body)==struct.unpack_from('>I',raw,offset+8+n)[0]
                    if typ in [b'pHYs',b'oFFs']:crc_ok=crc_ok and n==9
                    types.append(typ.decode('ascii'));offset+=12+n
                with Image.open(p) as im:im.verify()
                with Image.open(p) as im:im.load();dims=list(im.size);exif=bool(im.getexif())
                clean=raw[:8]==b'\x89PNG\r\n\x1a\n' and offset==len(raw) and crc_ok and types[-1:] == ['IEND'] and set(types)<={'IHDR','IDAT','IEND','pHYs','oFFs'} and not (set(types)&{'tEXt','zTXt','iTXt','eXIf'}) and not exif
                png.append({'path':rel,'dimensions':dims,'chunk_types':sorted(set(types)),'crc_valid':crc_ok,'decoded':True,'clean':bool(clean),'sha256':hashlib.sha256(raw).hexdigest()})
        except Exception as e:errors.append(rel+':'+type(e).__name__)
    checks={'no_private_paths_or_credentials':not bad,'no_reference_images_bytecode_archives_or_backups':not unexpected,
            'whitelist_complete':not errors,'exactly_seven_generated_previews':{q['path'] for q in png}=={'previews/'+n+'.png' for n in ['front','rear','north','east','west','south','top']},
            'all_png_decoded_crc_clean':all(q['clean'] for q in png),
            'one_distributable_stl':len(list(root.rglob('*.stl')))==1}
    return {'passed':all(checks.values()),'checks':checks,'stl_sha256':hashlib.sha256((root/'model.stl').read_bytes()).hexdigest(),'flagged_paths':bad,'unexpected_files':sorted(set(unexpected)),'errors':errors,'pngs':png,'limits':'All file bytes and decompressed gzip bytes scanned, including this scanner. Unsupported archives and compressed Blend are rejected; Blender datablocks checked by saved-scene probe.'}
if __name__=='__main__':
    report=inspect(R);(R/'artifact-integrity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
