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
 if path.name in ['MANIFEST.json','SHA256SUMS']:continue
 if path.suffix in ['.blend','.json','.md','.csv','.stl','.py','.txt']:
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
D=np.load(r/'mesh-data.npz');pal=json.loads((r/'palette.json').read_text());assert len(pal)==8
unknown=int((D['materials']==0).sum());rules=json.loads((r/'mapping-rules.json').read_text())['rules'];assert np.all((D['materials']>=0)&(D['materials']<len(pal)));assert np.all((D['rule_indices']>=0)&(D['rule_indices']<len(rules)))
assert all(json.loads((r/'qa'/name).read_text()) for name in ['geometry-validation.json','3mf-validation.json','blend-validation.json','path-buffer-audit.json','rebuild-validation.json','feature-validation.json','visual-review.json','readme-gallery-validation.json'])
G=json.loads((r/'qa/geometry-validation.json').read_text());assert G['watertight'] and G['winding_consistent'] and G['edge_manifold_all_incidence_2'] and G['vertex_manifold_all_links_single_cycles'];assert G['connected_components']==1 and G['degenerate_triangles']==0 and G['duplicate_triangles']==0
for name in ['feature-validation.json','self-intersection-validation.json','path-buffer-audit.json','readme-gallery-validation.json']:assert json.loads((r/'qa'/name).read_text())['all_pass']
M=json.loads((r/'qa/3mf-validation.json').read_text());assert M['strict'] and M['warnings']==0 and M['actual_material_edit_write_strict_reopen'] and M['actual_vertex_edit_write_strict_reopen']
B=json.loads((r/'qa/blend-validation.json').read_text());assert B['coordinates_face_order_and_material_assignments_exact'] and B['real_material_and_vertex_edit_saved_reopened']
C=json.loads((r/'qa/rebuild-validation.json').read_text());assert all(C['authoritative_arrays_exact'].values()) and C['stl_bytes_exact'] and len(C['views'])==9 and all(x['pixel_exact']for x in C['views'])
report={'public_file_scope':'Independent geometry, colors, source URLs, scripts, numerical QA and model renders only. No source photograph/PDF/texture/raw log.','preview_count':len(previews),'previews':previews,'relative_readme_links_checked':len(links),'private_path_scanned_payloads':len(scanned),'private_paths_found':0,'png_text_exif_time_metadata_absent':True,'three_mf_embedded_source_pixels':False,'material_count':len(pal),'unknown_triangle_count':unknown,'unknown_material_ids':['N00'],'unknown_material_scope':'Neutral ground-room/core filling and cut passage surfaces; source organization retained without claiming observed internal finish.','all_checks_passed':True}
(r/'qa'/'package-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
