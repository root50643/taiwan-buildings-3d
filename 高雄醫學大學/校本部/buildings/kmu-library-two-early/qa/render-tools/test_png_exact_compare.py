"""Fresh synthetic positive/negative controls for the reused PNG exact checker.
No previous building's image, test result, threshold or waiver is used.
"""
import argparse, hashlib, json, struct, zlib
from pathlib import Path
from png_exact_compare import parse, compare, sanitize, SANITIZE_TEXT_KEYS

def require(value, message):
    if not value: raise RuntimeError(message)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def chunk(tag, data): return struct.pack('>I', len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
def png(pixel=12, stable=b'keep-me', private=True, ztext=False):
    result=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',2,1,8,6,0,0,0))
    result+=chunk(b'gAMA',struct.pack('>I',45455))+chunk(b'pHYs',struct.pack('>IIB',1000,1000,1))
    result+=chunk(b'tEXt',b'Comment\0'+stable)+chunk(b'vpAg',b'opaque-ancillary')
    if private:
        for key in sorted(SANITIZE_TEXT_KEYS):result+=chunk(b'tEXt',key.encode()+b'\0fixture-only')
    if ztext:result+=chunk(b'zTXt',b'File\0\0'+zlib.compress(b'private'))
    result+=chunk(b'IDAT',zlib.compress(bytes([0,pixel,22,33,255,44,55,66,255])))+chunk(b'IEND',b'')
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    require(not a.out.exists(),'Refuse overwrite');a.out.mkdir(parents=True);checks={}
    for name,kwargs in [('original',{}),('pixel-change',{'pixel':13}),('metadata-change',{'stable':b'changed'}),('forbidden-ztext',{'ztext':True})]:
        (a.out/(name+'.png')).write_bytes(png(**kwargs))
    original=a.out/'original.png'; cleaned=a.out/'cleaned.png'; result=sanitize(original,cleaned,sha(original))
    before,after=parse(original),parse(cleaned)
    checks['whitelist_only_cleanup_proved']=result['passed'] and {x['key'] for x in result['removed_fields']}==SANITIZE_TEXT_KEYS
    checks['unknown_chunk_preserved']=(b'vpAg',b'opaque-ancillary') in after['chunks']
    checks['stable_comment_preserved']=(b'tEXt',b'Comment\0keep-me') in after['chunks']
    checks['compressed_idat_and_pixels_preserved']=before['idat_sha256']==after['idat_sha256'] and before['rgba_bytes']==after['rgba_bytes']
    checks['positive_exact_comparison_passes']=compare(original,original,sha(original))['passed']
    checks['pixel_mutation_fails']=not compare(original,a.out/'pixel-change.png',sha(original))['passed']
    checks['metadata_mutation_fails']=not compare(original,a.out/'metadata-change.png',sha(original))['passed']
    try: parse(a.out/'forbidden-ztext.png')
    except RuntimeError: checks['unsupported_private_container_rejected']=True
    else: checks['unsupported_private_container_rejected']=False
    corrupted=bytearray(original.read_bytes());corrupted[-1]^=1;(a.out/'bad-crc.png').write_bytes(corrupted)
    try: parse(a.out/'bad-crc.png')
    except RuntimeError: checks['bad_crc_rejected']=True
    else: checks['bad_crc_rejected']=False
    try: sanitize(original,cleaned,sha(original))
    except RuntimeError: checks['existing_output_rejected']=True
    else: checks['existing_output_rejected']=False
    report={'passed':all(checks.values()),'checks':checks,'cleanup':result,'test_source_sha256':sha(Path(__file__)),'png_tool_sha256':sha(Path(__file__).with_name('png_exact_compare.py'))}
    (a.out/'control-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(checks)}));return 0 if report['passed'] else 1
if __name__=='__main__': raise SystemExit(main())
