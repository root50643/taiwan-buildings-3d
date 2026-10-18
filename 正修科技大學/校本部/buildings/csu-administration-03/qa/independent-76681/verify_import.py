"""Verify delivered bytes, original-manifest mapping, links and fixed STL hashes."""
from pathlib import Path
import argparse,hashlib,json,re,struct,zlib
HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args()
    manifest=json.loads((HERE/'import-manifest.json').read_text(encoding='utf-8'))
    original=json.loads((HERE/'evidence-manifest.json').read_text(encoding='utf-8'))
    checks={};files=[]
    for row in manifest['files']:
        path=HERE/row['destination_path'];same=path.is_file() and path.stat().st_size==row['delivered_bytes'] and sha(path)==row['delivered_sha256']
        files.append({'path':row['destination_path'],'matches_delivered_manifest':same})
    checks['all_delivered_files_match_bytes_and_SHA256']=all(x['matches_delivered_manifest'] for x in files)
    checks['original_manifest_preserved']=sha(HERE/'evidence-manifest.json')==manifest['source_manifest_sha256']
    imported={r['destination_path']:r for r in manifest['files']}
    checks['all_original_manifest_rows_bound_to_original_hashes']=all(name['path'] in imported and imported[name['path']]['source_sha256']==name['sha256'] and imported[name['path']]['source_bytes']==name['bytes'] for name in original)
    checks['fixed_review_conclusions_preserved']=sha(HERE/'final-verification.json')==manifest['original_final_verification_sha256']
    bad=[];private=[]
    for path in HERE.rglob('*'):
        if path.is_file() and path.suffix.lower() in ['.md','.json','.py','.txt','.log','.ini']:
            text=path.read_text(encoding='utf-8')
            if re.search(r'[A-Za-z]:[\\/](?:Users|Program Files|Windows)',text):private.append(path.relative_to(HERE).as_posix())
            if path.suffix=='.md':
                for link in re.findall(r'\]\(([^)]+)\)',text):
                    if link.startswith(('http:','https:','mailto:','#')):continue
                    target=link.split('#',1)[0]
                    if not (path.parent/target).exists():bad.append({'file':path.relative_to(HERE).as_posix(),'target':target})
        elif path.is_file() and path.suffix.lower()=='.png':
            raw=path.read_bytes();offset=8;IDAT=[]
            while offset<len(raw):
                size=struct.unpack_from('>I',raw,offset)[0];kind=raw[offset+4:offset+8];data=raw[offset+8:offset+8+size]
                if zlib.crc32(kind+data)&0xffffffff!=struct.unpack_from('>I',raw,offset+8+size)[0]:raise RuntimeError('PNG CRC differs')
                if kind==b'IDAT':IDAT.append(data)
                if kind in [b'tEXt',b'iTXt',b'zTXt',b'eXIf'] and re.search(rb'[A-Za-z]:[\\/](?:Users|Program Files|Windows)',data):
                    private.append(path.relative_to(HERE).as_posix())
                offset+=size+12
            proof=manifest.get('PNG_pixel_preservation',{}).get(path.relative_to(HERE).as_posix())
            if proof:
                current=hashlib.sha256(b''.join(IDAT)).hexdigest()
                checks['PNG_IDAT_payloads_match_original']=current==proof['source_IDAT_payload_sha256']==proof['delivered_IDAT_payload_sha256']
    checks['no_private_host_paths']=not private;checks['all_local_Markdown_links_resolve']=not bad
    pkg=HERE.parents[1]
    actual={name:sha(pkg/'models/v2'/name) for name in manifest['core_STL_SHA256_before']}
    checks['fixed_core_STL_SHA256_unchanged']=actual==manifest['core_STL_SHA256_before']==manifest['core_STL_SHA256_after']
    result={'passed':all(checks.values()),'checks':checks,'files':files,'broken_links':bad,'private_path_files':private,
            'actual_core_STL_SHA256':actual,'interpretation':'Import integrity and fixed geometry binding only. Does not rerun full independent review, change historical flags, or establish physical print/removal success.'}
    if a.output:
        if a.output.exists():raise RuntimeError('Refuse to overwrite validation output')
        a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
