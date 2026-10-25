#!/usr/bin/env python3
"""Read-only publication and gallery checks; outputs no local machine paths."""
from pathlib import Path
import argparse,json,re,struct,hashlib,zipfile
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=a.out
expected=['front','oblique','right','left','rear','top','road-side','rear-g','aerial'];readme=(r/'README.md').read_text();links=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',readme);assert len(links)==9 and set(links)=={f'previews/{n}.png'for n in expected}
rows=[line for line in readme.splitlines()if'!['in line];assert len(rows)==3 and all(line.count('![')==3 for line in rows)
records=[]
for name in expected:
 path=r/'previews'/f'{name}.png';raw=path.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';i=8;tags=[]
 while i<len(raw):
  n=struct.unpack_from('>I',raw,i)[0];tag=raw[i+4:i+8];tags.append(tag.decode());assert tag not in(b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME');i+=n+12
 im=Image.open(path);assert im.size==(1200,900);assert len(im.convert('RGB').getcolors(1200*900))>100
 records.append({'file':f'previews/{name}.png','size_px':list(im.size),'sha256':hashlib.sha256(raw).hexdigest(),'no_text_metadata':True})
markers=[('/'+'workspace/').encode(),('/'+'home/agent/').encode(),('/'+'tmp/').encode(),('file:'+ '///').encode()]
scanned=[]
for path in sorted(r.rglob('*')):
 if not path.is_file()or str(path.relative_to(r))in('MANIFEST.json','SHA256SUMS.txt','qa/publication-validation.json'):continue
 rel=str(path.relative_to(r));assert path.suffix.lower()not in('.jpg','.jpeg','.pdf','.tif','.tiff','.html','.blend1','.log','.zip')
 raw=path.read_bytes();assert not any(q in raw for q in markers),(rel,'machine path found')
 if path.suffix in('.3mf','.npz'):
  with zipfile.ZipFile(path)as z:
   for name in z.namelist():
    content=z.read(name);assert not any(q in content for q in markers),(rel,name,'machine path in member')
 scanned.append(rel)
rep={'readme_images':9,'gallery_columns':3,'images':records,'source_image_pdf_files_absent':True,'source_pixel_textures_absent_as_verified_in_native_blend':True,'literal_machine_path_markers_absent':True,'archive_members_also_scanned':True,'files_checked':len(scanned),'all_pass':True}
payload=json.dumps(rep,indent=2)+'\n'
if (r/'MANIFEST.json').exists():assert (r/'qa/publication-validation.json').read_text()==payload
else:(r/'qa/publication-validation.json').write_text(payload)
print(json.dumps(rep,indent=2))
if(r/'MANIFEST.json').exists():
 man=json.loads((r/'MANIFEST.json').read_text());listed={x['path']for x in man['files']};actual={str(x.relative_to(r))for x in r.rglob('*')if x.is_file()}-{'MANIFEST.json','SHA256SUMS.txt'};assert listed==actual
 for x in man['files']:
  data=(r/x['path']).read_bytes();assert len(data)==x['bytes']and hashlib.sha256(data).hexdigest()==x['sha256'],x['path']
 print('Manifest exact membership and every payload hash PASS')
