#!/usr/bin/env python3
"""Compare a fresh --out appearance rebuild with its reference outputs."""
from pathlib import Path
import argparse,json,hashlib,zipfile,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--original',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--rebuilt',type=Path,required=True);p.add_argument('--report',type=Path);a=p.parse_args();left=a.original;right=a.rebuilt
A=np.load(left/'mesh-data.npz');B=np.load(right/'mesh-data.npz');arrays={k:bool(np.array_equal(A[k],B[k]))for k in A.files};assert all(arrays.values())
texts={name:(left/name).read_bytes()==(right/name).read_bytes()for name in ['palette.json','mapping-rules.json','face-materials.csv']};assert all(texts.values())
rows=[]
for q in sorted((left/'previews').glob('*.png')):
 a1=np.array(Image.open(q).convert('RGB'));b1=np.array(Image.open(right/'previews'/q.name).convert('RGB'));assert a1.shape==b1.shape;delta=np.abs(a1.astype(int)-b1.astype(int));assert not delta.any(),q.name
 rows.append({'view':q.stem,'exact_pixels_equal':True,'max_channel_delta':int(delta.max()),'pixel_sha256':hashlib.sha256(a1.tobytes()).hexdigest()})
assert len(rows)==9
with zipfile.ZipFile(left/'ntus-changqi-appearance.3mf')as za,zipfile.ZipFile(right/'ntus-changqi-appearance.3mf')as zb:
 assert set(za.namelist())==set(zb.namelist());xml={};ignored=[]
 for n in za.namelist():
  one,two=za.read(n),zb.read(n)
  if one!=two:
   aa,bb=ET.fromstring(one),ET.fromstring(two)
   for tree in (aa,bb):
    for node in tree.iter():
     for key in list(node.attrib):
      if key=='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}UUID':node.attrib.pop(key)
   assert ET.tostring(aa)==ET.tostring(bb),n
   ignored.append({'entry':n,'ignored_only':'lib3mf-generated production UUID values; no geometry, material, transform or name ignored'})
  xml[n]=True
result={'fresh_output_directory':True,'source_geometry_rebuilt':False,'arrays_exact':arrays,'mapping_files_byte_identical':texts,'3mf_package_semantics_identical':xml,'3mf_nondeterministic_metadata':ignored,'pixel_hash_format':'RGB uint8 row-major','all_nine_render_pixels_exact':True,'previews':rows}
report=a.report or left/'qa'/'fresh-rebuild-comparison.json';report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
