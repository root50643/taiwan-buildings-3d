#!/usr/bin/env python3
"""Independent STL/NPZ/3MF check; no builder imports and no geometry mutation."""
from pathlib import Path
import argparse,collections,csv,hashlib,json,struct,zipfile,xml.etree.ElementTree as ET
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--input',type=Path);a=p.parse_args();root=a.out;source=a.input or root.parent/'model.stl'
sha=lambda b:hashlib.sha256(b).hexdigest()
b=source.read_bytes();assert sha(b)=='ebecf2597fbc17fd0faf5a8bcd3ac13d1d9511d70a9600c5c09084ddbd26d879'
n=struct.unpack_from('<I',b,80)[0];assert n==4694 and len(b)==84+n*50
tri=np.array([struct.unpack_from('<9f',b,84+50*i+12) for i in range(n)],dtype='<f4').reshape(n,3,3);t=tri.astype(float)
D=np.load(root/'mesh-data.npz');v=D['vertices'];f=D['faces'];mi=D['materials'];assert v[f].tobytes()==tri.tobytes()
# Independent envelope interpolation + single interval test, all THREE vertices.
xs=np.linspace(-57,57,81);z=42+np.sqrt(108**2-xs**2)-np.sqrt(108**2-57**2);lo=t.min(1);hi=t.max(1);cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(cross,axis=1)/2;normal=cross/(2*area[:,None]);e=3e-4
roof=(np.max(abs(t[:,:,2]-np.interp(t[:,:,0],xs,z)),axis=1)<e)&np.any((lo[:,0,None]>=xs[None,:-1]-e)&(hi[:,0,None]<=xs[None,1:]+e),axis=1)&(lo[:,1]>=-37-e)&(hi[:,1]<=63+e)&(normal[:,2]>.8)&(abs(normal[:,1])<e)
assert roof.sum()==1206 and np.array_equal(mi,roof.astype(np.int32));ids=np.flatnonzero(roof).tolist();contract=json.loads((root/'roof-face-contract.json').read_text());assert ids==contract['face_indices_0_based']
records=list(csv.DictReader((root/'face-materials.csv').open()));assert len(records)==n
for i,r in enumerate(records):assert int(r['original_stl_triangle_index'])==i and int(r['material_index'])==int(mi[i]) and r['ordered_float32_le_sha256']==sha(tri[i].tobytes())
# Connectedness and exact edge manifold/orientation check.
edges=collections.defaultdict(list);roof_edges=collections.defaultdict(list)
for i,face in enumerate(f):
 for a1,b1 in ((0,1),(1,2),(2,0)):
  x,y=int(face[a1]),int(face[b1]);key=tuple(sorted((x,y)));edges[key].append((i,x,y))
  if roof[i]:roof_edges[key].append(i)
assert all(len(vv)==2 and vv[0][1:]==tuple(reversed(vv[1][1:])) for vv in edges.values())
parent=list(range(n))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for vv in edges.values():parent[find(vv[0][0])]=find(vv[1][0])
assert len({find(i) for i in range(n)})==1
parent=list(range(n))
for vv in roof_edges.values():
 if len(vv)==2:parent[find(vv[0])]=find(vv[1])
roof_components=len({find(i) for i in ids});assert roof_components==1
volume=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6);assert volume>0
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
with zipfile.ZipFile(root/'cjcu-gymnasium-roof-illustration.3mf') as z:
 assert set(z.namelist())=={'[Content_Types].xml','_rels/.rels','3D/3dmodel.model'};xml=ET.fromstring(z.read('3D/3dmodel.model'))
assert xml.attrib['unit']=='millimeter';vertices=xml.findall('.//m:vertex',ns);faces=xml.findall('.//m:triangle',ns)
vx=np.array([[float(q.attrib[k]) for k in ('x','y','z')] for q in vertices],dtype='<f4');fx=np.array([[int(q.attrib[k]) for k in ('v1','v2','v3')] for q in faces]);mx=[]
for q in faces:assert q.attrib['pid']=='1' and q.attrib['p1']==q.attrib['p2']==q.attrib['p3'];mx.append(int(q.attrib['p1']))
assert vx.tobytes()==v.tobytes() and fx.tobytes()==f.astype(fx.dtype).tobytes() and vx[fx].tobytes()==tri.tobytes() and np.array_equal(mx,mi)
# Decimal doubles equal original values too, not just loosely rounded float32.
for q,vec in zip(vertices,v):assert [float(q.attrib[k]) for k in ('x','y','z')]==[float(x) for x in vec]
palette=json.loads((root/'palette.json').read_text());assert len(palette)==2 and palette[0]['blender_linear_rgba']==[.69,.64,.54,1] and palette[1]['hex']=='#8C8C8C'
for d in palette:assert (d['metallic'],d['roughness'],d['emission'],d['transmission'])==(0,.65,0,0)
bases=xml.findall('.//m:base',ns);assert [x.attrib['displaycolor'] for x in bases]==[d['hex']+'FF' for d in palette]
report={'original_mesh_exact_float32_face_sequence':True,'three_mf_exact_float32_and_double_coordinate_values':True,'three_mf_exact_face_order_winding_and_material_indices':True,'three_mf_core_basematerials_opaque_colors':True,'triangles':n,'vertices':len(v),'positive_volume_mm3':volume,'all_edges_two_oppositely_oriented_incident_faces':True,'single_connected_mesh':True,'roof_faces':len(ids),'roof_connected_components':roof_components,'roof_area_mm2':float(area[roof].sum()),'roof_area_fraction':float(area[roof].sum()/area.sum()),'other_faces_original_preview_only':int((~roof).sum()),'changed_or_subdivided_geometry':False,'independent_all_vertex_interpolation_matches_author_mapping':True,'all_4694_csv_indices_and_ordered_signatures_verified':True,'palette_matches_nonphotometric_limits':True,'no_printability_or_material_specification_claim':True}
(root/'qa').mkdir(exist_ok=True);(root/'qa'/'independent-format-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
