#!/usr/bin/env python3
"""Validate public appearance package without requiring private images or evidence files."""
from pathlib import Path
import argparse,json,hashlib,struct,csv,re,zipfile
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--stl',type=Path,required=True);p.add_argument('--write-report',action='store_true');a=p.parse_args();r=a.root
b=a.stl.read_bytes();P=json.loads((r/'parameters.json').read_text());assert hashlib.sha256(b).hexdigest()==P['original_stl_sha256'] and len(b)==155784
D=np.load(r/'mesh-data.npz');tri=np.frombuffer(b,dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),offset=84)['v'];assert np.array_equal(D['vertices'][D['faces']],tri) and len(tri)==3114
m=np.zeros(3114,dtype=int)
for g in P['groups']:m[g['original_face_ids']]=g['material_index']
assert np.array_equal(m,D['materials']) and np.bincount(m).tolist()==[2916,2,36,160]
rows=list(csv.DictReader((r/'face-materials.csv').open()));assert len(rows)==3114 and all(int(x['original_stl_triangle_index'])==i and int(x['material_index'])==m[i] for i,x in enumerate(rows))
manifest=json.loads((r/'qa/render-manifest.json').read_text());expected={x['name']+'.png'for x in manifest['views']};assert len(expected)==9
assert {x.name for x in (r/'previews').glob('*.png')}==expected
images=[]
for path in sorted((r/'previews').glob('*.png')):
 raw=path.read_bytes();offset=8;tags=[];assert raw[:8]==b'\x89PNG\r\n\x1a\n'
 while offset<len(raw):
  n=struct.unpack_from('>I',raw,offset)[0];tag=raw[offset+4:offset+8];tags.append(tag.decode());assert tag not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'];offset+=n+12
 im=Image.open(path);assert im.size==(1200,900)
 images.append({'name':path.name,'pixels':[1200,900],'chunks':tags,'private_metadata_absent':True,'sha256':hashlib.sha256(raw).hexdigest()})
readme=(r/'README.md').read_text();links=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',readme);assert len(links)==9 and {Path(x).name for x in links}==expected and all((r/x).is_file()for x in links)
assert sum(line.count('![')==3 for line in readme.splitlines())==3
# Package privacy: no logs, backups, image inputs or machine-local path prefixes.
for path in r.rglob('*'):
 if not path.is_file():continue
 assert path.suffix not in ['.log','.jpg','.html','.blend1','.pyc'],path.name
 raw=path.read_bytes()
 if path.suffix not in ['.png','.npz','.3mf']:
  for marker in [('/'+'workspace/').encode(),('/'+'home/').encode(),('/'+'tmp/').encode(),b'file:'+b'///']:
   assert marker not in raw,path.name
with zipfile.ZipFile(r/'ntin-xinxin-appearance.3mf')as z:
 assert not any('texture' in x.lower()for x in z.namelist())
 for name in z.namelist():
  data=z.read(name)
  for marker in [('/'+'workspace/').encode(),('/'+'home/').encode(),('/'+'tmp/').encode(),b'file:'+b'///']:
   assert marker not in data
for name in ['face-containment.json','geometry-validation.json','3mf-validation.json','blend-validation.json','path-buffer-audit.json','rebuild-validation.json','visual-review.json']:
 assert (r/'qa'/name).exists(),name
report={'source_stl_sha256_exact':True,'all_original_face_coordinates_and_order_exact':True,'material_counts':{'neutral':2916,'roof':2,'window_backs':36,'shaft_front_arcs':160},'nine_direct_images_in_three_column_tables':True,'pngs':images,'raw_sources_external_textures_logs_backups_private_paths_absent':True,'no_original_package_mutation_required':True,'not_physical_print_validation':True}
if a.write_report:(r/'qa/package-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'PASS','faces':3114,'assigned':198,'neutral':2916,'previews':9}))
