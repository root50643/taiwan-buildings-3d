#!/usr/bin/env python3
"""Final read-only format/privacy/link checks, then write one compact QA record.
Recreate manifests separately after any changed content, including this report.
"""
from pathlib import Path
import argparse,json,re,zipfile,struct,hashlib
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=a.out
files=[x for x in r.rglob('*')if x.is_file()];assert not any(x.suffix in ['.jpg','.jpeg','.webp','.pdf','.log']for x in files)
private_markers=[('/'+'workspace/').encode(),('/'+'home/agent/').encode(),('/'+'tmp/').encode()]
scanned=[]
for path in files:
 if path.suffix in ['.py','.txt'] or path.name in ['MANIFEST.json','SHA256SUMS']:continue
 if path.suffix in ['.blend','.json','.md','.csv','.stl']:
  data=path.read_bytes();assert not any(marker in data for marker in private_markers),path.name;scanned.append(str(path.relative_to(r)))
 if path.suffix=='.3mf':
  with zipfile.ZipFile(path)as z:
   assert not any(n.lower().endswith(('.jpg','.jpeg','.png','.webp'))for n in z.namelist())
   for name in z.namelist():assert not any(marker in z.read(name) for marker in private_markers)
previews=[]
for path in sorted((r/'previews').glob('*.png')):
 raw=path.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';o=8;tags=[]
 while o<len(raw):
  n=struct.unpack_from('>I',raw,o)[0];tag=raw[o+4:o+8];tags.append(tag.decode());assert tag not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'];o+=n+12
 im=Image.open(path);assert im.size==(1200,900);assert np.std(np.array(im)[:,:,:3])>15
 previews.append({'file':path.name,'size_px':list(im.size),'chunks':sorted(set(tags)),'sha256':hashlib.sha256(raw).hexdigest()})
assert len(previews)==9
links=[]
for url in re.findall(r'\]\(([^)]+)\)',(r/'README.md').read_text()):
 if '://' in url:continue
 target=r/url;assert target.is_file(),url;links.append(url)
D=np.load(r/'mesh-data.npz');pal=json.loads((r/'palette.json').read_text());assert len(pal)==7
unknown=int((D['rule_indices']==0).sum());assert np.all(np.isin(D['materials'][D['rule_indices']==0],[0,6]))
assert np.all(D['rule_indices'][np.isin(D['materials'],[0,6])]==0)
assert all(json.loads((r/'qa'/name).read_text()) for name in ['geometry-validation.json','3mf-validation.json','blend-validation.json','path-buffer-audit.json','rebuild-validation.json'])
report={'public_file_scope':'Independent geometry, colors, source URLs, scripts, numerical QA and model renders only. No source photograph/PDF/texture/raw log.','preview_count':len(previews),'previews':previews,'relative_readme_links_checked':len(links),'private_path_scanned_payloads':len(scanned),'private_paths_found':0,'png_text_exif_time_metadata_absent':True,'three_mf_embedded_source_pixels':False,'material_count':len(pal),'unknown_triangle_count':unknown,'unknown_material_ids':['N00','N01'],'unknown_roof_hues':'Neutral capped roof rectangles; no courtyard claim. Inferred lower central rear has subdued brick-neutral color.','all_checks_passed':True}
(r/'qa'/'package-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
