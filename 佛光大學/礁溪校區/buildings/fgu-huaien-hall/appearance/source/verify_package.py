#!/usr/bin/env python3
"""Independent byte/triangle/material/edge/package verification; no mesh repair.
Python 3 + numpy. --out creates QA directories, not replacement geometry.
"""
from pathlib import Path
import argparse,json,hashlib,zipfile,xml.etree.ElementTree as ET,struct
import numpy as np
from build_appearance import original,ORIGINAL_SHA256
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--stl',type=Path,default=Path(__file__).resolve().parents[2]/'model.stl');a=ap.parse_args();root=a.out;root.mkdir(parents=True,exist_ok=True);(root/'qa').mkdir(exist_ok=True)
b,v,f,t=original(a.stl);d=np.load(root/'mesh-data.npz');assert np.array_equal(d['vertices'],v);assert np.array_equal(d['faces'],f)
fm=json.loads((root/'face-materials.json').read_text());ids=np.full(len(f),255,dtype=np.uint8)
for i,g in enumerate(fm['face_groups']):
 ix=g['original_face_ids'];assert len(ix)==g['face_count'];assert (ids[ix]==255).all();ids[ix]=i
assert np.array_equal(ids,d['materials']);assert (ids!=255).all();assert sum(x['face_count'] for x in fm['registered_glazing_rows'])==int((ids==3).sum())
with zipfile.ZipFile(root/'fgu-huaien-hall-materials.3mf') as z:
 assert not any('texture' in name.lower() for name in z.namelist());xml=ET.fromstring(z.read('3D/3dmodel.model'))
 xv=np.array([[float(e.get(k)) for k in ('x','y','z')] for e in xml.findall('.//{*}vertices/{*}vertex')],dtype=np.float64);xt=xml.findall('.//{*}triangles/{*}triangle');xf=np.array([[int(e.get(k)) for k in ('v1','v2','v3')] for e in xt]);default=xml.find('.//{*}object').get('pindex');xm=np.array([int(e.get('p1',default)) for e in xt]);assert np.array_equal(xv,v.astype(np.float64));assert np.array_equal(xf,f);assert np.array_equal(xm,ids)
 edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);sorted_edges=np.sort(edges,axis=1);unique,inv,count=np.unique(sorted_edges,axis=0,return_inverse=True,return_counts=True);assert (count==2).all();signed=np.where(edges[:,0]<edges[:,1],1,-1);tot=np.bincount(inv,weights=signed);assert (tot==0).all()
 parent=np.arange(len(v))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for x,y in unique:
  x,y=find(x),find(y)
  if x!=y:parent[y]=x
 components=len(set(find(i) for i in range(len(v))));assert components==1
 volume=float(np.einsum('ij,ij->i',t[:,0].astype(float),np.cross(t[:,1].astype(float),t[:,2].astype(float))).sum()/6);assert volume>0
 leaks=[]
 for p in root.rglob('*'):
  if not p.is_file() or p.suffix=='.py' or '__pycache__' in p.parts:continue
  data=p.read_bytes()
  for marker in (b'/workspace/',b'/home/agent/',b'/tmp/',b'Bearer ',b'BEGIN PRIVATE KEY'):
   if marker in data:leaks.append({'file':str(p.relative_to(root)),'marker':marker.decode()})
 assert not leaks,leaks
 qa={'original_stl_sha256':ORIGINAL_SHA256,'original_bytes_preserved':True,'npz_triangle_coordinates_order_winding_exact':True,'3mf_xml_vertex_decimal_coordinates_exact':True,'3mf_xml_faces_and_material_indices_exact':True,'triangles':len(f),'vertices':len(v),'unique_edges':len(unique),'all_edges_incidence_two':True,'opposite_edge_winding':True,'connected_components':components,'positive_signed_volume_mm3':volume,'euler_characteristic':len(v)-len(unique)+len(f),'private_path_or_secret_markers':leaks,'no_texture_parts':True,'printability_scope':'Original geometry topology checks only. No slicer, toolpaths, global wall-thickness assessment or actual print.'}
 (root/'qa'/'package-verification.json').write_text(json.dumps(qa,indent=2)+'\n');print(json.dumps(qa,indent=2))
